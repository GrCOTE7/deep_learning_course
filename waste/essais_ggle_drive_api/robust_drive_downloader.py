"""
Version robuste du téléchargeur Google Drive
Avec gestion améliorée des timeouts et retry automatique
"""

import os
import pickle
import time
import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import socket

# Configuration
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
socket.setdefaulttimeout(30)  # Timeout de 30 secondes


class RobustDriveDownloader:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authentification avec retry"""
        creds = None

        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Rafraîchissement du token...")
                creds.refresh(Request())
            else:
                print("🚀 Authentification requise...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "waste/essais/credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        self.service = build("drive", "v3", credentials=creds)
        print("✅ Connecté à Google Drive")

    def rechercher_avec_retry(self, query, max_retries=3):
        """Recherche avec retry automatique"""
        for tentative in range(max_retries):
            try:
                print(f"🔍 Recherche... (tentative {tentative + 1})")

                results = (
                    self.service.files()
                    .list(
                        q=query,
                        fields="files(id, name, size, mimeType, parents)",
                        pageSize=50,
                    )
                    .execute()
                )

                return results.get("files", [])

            except Exception as e:
                print(f"⚠️  Tentative {tentative + 1} échouée: {str(e)[:100]}...")
                if tentative < max_retries - 1:
                    wait_time = (tentative + 1) * 5
                    print(f"⏳ Attente {wait_time}s avant nouvelle tentative...")
                    time.sleep(wait_time)
                else:
                    print("❌ Échec après plusieurs tentatives")
                    return []

    def lister_tous_fichiers(self, nom_partiel=""):
        """Liste tous les fichiers contenant le nom partiel"""
        if nom_partiel:
            query = f"name contains '{nom_partiel}'"
        else:
            query = "mimeType != 'application/vnd.google-apps.folder'"

        print(f"📋 Recherche de fichiers contenant: '{nom_partiel}'")
        return self.rechercher_avec_retry(query)

    def telecharger_avec_retry(self, file_id, nom_fichier, destination="./datasets/"):
        """Télécharge avec gestion robuste des erreurs"""

        os.makedirs(destination, exist_ok=True)
        chemin_complet = os.path.join(destination, nom_fichier)

        print(f"📥 Téléchargement de '{nom_fichier}'...")

        # Méthode 1: API Google Drive standard
        for tentative in range(3):
            try:
                # Obtenir l'URL de téléchargement direct
                request = self.service.files().get_media(fileId=file_id)

                # Télécharger par chunks
                with open(chemin_complet, "wb") as f:
                    chunk_size = 1024 * 1024  # 1MB chunks

                    while True:
                        chunk = request.execute()
                        if not chunk:
                            break
                        f.write(chunk)
                        print(".", end="", flush=True)

                print(f"\n✅ Téléchargé: {chemin_complet}")
                return chemin_complet

            except Exception as e:
                print(f"\n⚠️  Méthode standard échouée (tentative {tentative + 1}): {e}")
                if tentative < 2:
                    time.sleep(5)

        # Méthode 2: Téléchargement direct via requests
        print("🔄 Essai avec méthode alternative...")

        try:
            # Obtenir les métadonnées du fichier
            metadata = self.service.files().get(fileId=file_id).execute()

            # Créer l'URL de téléchargement
            download_url = f"https://drive.google.com/uc?id={file_id}&export=download"

            # Télécharger avec requests
            session = requests.Session()
            response = session.get(download_url, stream=True, timeout=60)

            # Gérer la confirmation pour gros fichiers
            if "confirm=" in response.text:
                # Extraire le token de confirmation
                for line in response.text.split("\n"):
                    if "confirm=" in line:
                        confirm_token = (
                            line.split("confirm=")[1].split("&")[0].split('"')[0]
                        )
                        break

                download_url = (
                    f"https://drive.google.com/uc?id={file_id}&confirm={confirm_token}"
                )
                response = session.get(download_url, stream=True, timeout=60)

            # Sauvegarder le fichier
            with open(chemin_complet, "wb") as f:
                total_size = 0
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
                        print(
                            f"\r📊 Téléchargé: {total_size / (1024*1024):.1f} MB",
                            end="",
                        )

            print(f"\n✅ Téléchargement réussi: {chemin_complet}")
            return chemin_complet

        except Exception as e:
            print(f"\n❌ Méthode alternative échouée: {e}")
            return None

    def rechercher_et_telecharger(self, terme_recherche, destination="./datasets/"):
        """Interface principale pour rechercher et télécharger"""

        print(f"🎯 Recherche de: '{terme_recherche}'")

        # Rechercher les fichiers
        fichiers = self.lister_tous_fichiers(terme_recherche)

        if not fichiers:
            print(f"❌ Aucun fichier trouvé contenant: '{terme_recherche}'")

            # Suggérer une recherche plus large
            print("\n💡 Essayons une recherche plus large...")
            mots = terme_recherche.split("/")
            for mot in mots:
                if len(mot) > 2:
                    print(f"🔍 Recherche de '{mot}'...")
                    fichiers_alternatifs = self.lister_tous_fichiers(mot)
                    if fichiers_alternatifs:
                        print(
                            f"✅ Trouvé {len(fichiers_alternatifs)} fichiers avec '{mot}'"
                        )
                        fichiers = fichiers_alternatifs[:10]  # Limiter à 10
                        break

            if not fichiers:
                return None

        # Filtrer et afficher les fichiers trouvés
        print(f"\n📋 {len(fichiers)} fichier(s) trouvé(s):")
        for i, f in enumerate(fichiers):
            taille = ""
            if f.get("size"):
                taille_mb = int(f["size"]) / (1024 * 1024)
                taille = f" ({taille_mb:.1f} MB)"

            print(f"  {i+1}. {f['name']}{taille}")

        # Sélection du fichier
        if len(fichiers) == 1:
            fichier_choisi = fichiers[0]
            print(f"✅ Sélection automatique: {fichier_choisi['name']}")
        else:
            try:
                choice = (
                    int(input(f"\nChoisissez un fichier (1-{len(fichiers)}): ")) - 1
                )
                if 0 <= choice < len(fichiers):
                    fichier_choisi = fichiers[choice]
                else:
                    print("❌ Choix invalide")
                    return None
            except ValueError:
                print("❌ Veuillez entrer un numéro")
                return None

        # Télécharger le fichier sélectionné
        return self.telecharger_avec_retry(
            fichier_choisi["id"], fichier_choisi["name"], destination
        )


def main():
    """Interface principale"""
    print("🛡️  TÉLÉCHARGEUR GOOGLE DRIVE ROBUSTE")
    print("=" * 40)

    try:
        downloader = RobustDriveDownloader()

        print("\n💡 Exemples de recherche:")
        print("   • archive")
        print("   • dataset")
        print("   • .zip")
        print("   • mnist")

        terme = input("\n🔍 Terme de recherche: ")
        if not terme:
            print("❌ Terme de recherche requis")
            return

        destination = input("📁 Dossier destination (Entrée = ./datasets/): ")
        if not destination:
            destination = "./datasets/"

        print(f"\n🚀 Recherche et téléchargement...")
        resultat = downloader.rechercher_et_telecharger(terme, destination)

        if resultat:
            print(f"\n🎉 Succès ! Fichier disponible: {resultat}")

            if os.path.exists(resultat):
                taille = os.path.getsize(resultat) / (1024 * 1024)
                print(f"📊 Taille: {taille:.1f} MB")
        else:
            print("\n💥 Téléchargement échoué")

    except KeyboardInterrupt:
        print("\n🛑 Interruption utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


if __name__ == "__main__":
    main()
