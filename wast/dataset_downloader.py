"""
Téléchargeur Google Drive optimisé pour les datasets
Gère les chemins de dossiers et les gros fichiers
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import time

# Scopes pour accès en lecture seule
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class DatasetDownloader:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authentification Google Drive"""
        creds = None

        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        self.service = build("drive", "v3", credentials=creds)
        print("✅ Connecté à Google Drive")

    def chercher_dans_dossier(self, nom_dossier):
        """Trouve l'ID d'un dossier par son nom"""
        query = (
            f"name='{nom_dossier}' and mimeType='application/vnd.google-apps.folder'"
        )

        try:
            results = (
                self.service.files().list(q=query, fields="files(id, name)").execute()
            )

            dossiers = results.get("files", [])
            return dossiers
        except Exception as e:
            print(f"❌ Erreur recherche dossier: {e}")
            return []

    def lister_fichiers_dossier(self, dossier_id):
        """Liste tous les fichiers dans un dossier"""
        query = f"'{dossier_id}' in parents"

        try:
            results = (
                self.service.files()
                .list(q=query, fields="files(id, name, size, mimeType)", pageSize=100)
                .execute()
            )

            return results.get("files", [])
        except Exception as e:
            print(f"❌ Erreur listage dossier: {e}")
            return []

    def chercher_par_chemin(self, chemin):
        """
        Cherche un fichier par son chemin complet
        Ex: 'data/archive.zip' ou 'MyDrive/data/archive.zip'
        """
        # Nettoyer le chemin
        if chemin.startswith("MyDrive/"):
            chemin = chemin[8:]  # Enlever 'MyDrive/'

        parties = chemin.split("/")
        nom_fichier = parties[-1]
        dossiers = parties[:-1]

        print(f"🔍 Recherche: {' → '.join(dossiers)} → {nom_fichier}")

        # Si pas de dossiers, recherche directe
        if not dossiers:
            return self.chercher_fichier_simple(nom_fichier)

        # Chercher dans les dossiers
        dossier_actuel_id = None

        for nom_dossier in dossiers:
            print(f"📁 Recherche du dossier: {nom_dossier}")

            if dossier_actuel_id is None:
                # Recherche dans la racine
                query = f"name='{nom_dossier}' and mimeType='application/vnd.google-apps.folder'"
            else:
                # Recherche dans le dossier parent
                query = f"name='{nom_dossier}' and mimeType='application/vnd.google-apps.folder' and '{dossier_actuel_id}' in parents"

            try:
                results = (
                    self.service.files()
                    .list(q=query, fields="files(id, name)")
                    .execute()
                )

                dossiers_trouves = results.get("files", [])

                if not dossiers_trouves:
                    print(f"❌ Dossier '{nom_dossier}' non trouvé")
                    return []

                if len(dossiers_trouves) > 1:
                    print(f"⚠️  Plusieurs dossiers '{nom_dossier}' trouvés:")
                    for i, d in enumerate(dossiers_trouves):
                        print(f"  {i+1}. {d['name']} (ID: {d['id']})")

                    try:
                        choice = int(input("Choisissez le numéro: ")) - 1
                        dossier_actuel_id = dossiers_trouves[choice]["id"]
                    except (ValueError, IndexError):
                        print("❌ Choix invalide")
                        return []
                else:
                    dossier_actuel_id = dossiers_trouves[0]["id"]
                    print(f"✅ Dossier '{nom_dossier}' trouvé")

            except Exception as e:
                print(f"❌ Erreur: {e}")
                return []

        # Maintenant chercher le fichier dans le dernier dossier
        print(f"📄 Recherche du fichier: {nom_fichier}")
        query = f"name='{nom_fichier}' and '{dossier_actuel_id}' in parents"

        try:
            results = (
                self.service.files()
                .list(q=query, fields="files(id, name, size, mimeType)")
                .execute()
            )

            return results.get("files", [])

        except Exception as e:
            print(f"❌ Erreur recherche fichier: {e}")
            return []

    def chercher_fichier_simple(self, nom_fichier):
        """Recherche simple par nom de fichier"""
        query = f"name='{nom_fichier}'"

        try:
            results = (
                self.service.files()
                .list(q=query, fields="files(id, name, size, mimeType)", pageSize=10)
                .execute()
            )

            return results.get("files", [])
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return []

    def telecharger_fichier(self, file_id, nom_fichier, destination="./"):
        """Télécharge un fichier avec gestion des gros fichiers"""

        try:
            print(f"📥 Téléchargement de '{nom_fichier}'...")

            # Créer le dossier de destination
            os.makedirs(destination, exist_ok=True)
            chemin_complet = os.path.join(destination, nom_fichier)

            # Obtenir les métadonnées pour la taille
            metadata = self.service.files().get(fileId=file_id, fields="size").execute()
            taille = int(metadata.get("size", 0))

            if taille > 0:
                print(f"📊 Taille du fichier: {taille / (1024*1024):.1f} MB")

            # Téléchargement avec retry
            max_retries = 3
            for tentative in range(max_retries):
                try:
                    request = self.service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(
                        fh,
                        request,
                        chunksize=1024 * 1024 * 10,  # 10MB chunks pour gros fichiers
                    )

                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                        if status:
                            percent = int(status.progress() * 100)
                            print(f"⏳ Progression: {percent}%", end="\r")

                    # Sauvegarder le fichier
                    with open(chemin_complet, "wb") as f:
                        f.write(fh.getvalue())

                    print(f"\n✅ Téléchargé: {chemin_complet}")
                    return chemin_complet

                except Exception as e:
                    print(f"\n⚠️  Tentative {tentative + 1} échouée: {e}")
                    if tentative < max_retries - 1:
                        print("🔄 Nouvelle tentative dans 5 secondes...")
                        time.sleep(5)
                    else:
                        print("❌ Échec après plusieurs tentatives")
                        return None

        except Exception as e:
            print(f"❌ Erreur générale: {e}")
            return None

    def telecharger_dataset(self, chemin_fichier, destination="./datasets/"):
        """
        Fonction principale pour télécharger un dataset

        Args:
            chemin_fichier: Chemin du fichier (ex: 'data/archive.zip' ou 'MyDrive/data/archive.zip')
            destination: Dossier de destination

        Returns:
            Chemin du fichier téléchargé ou None
        """

        print(f"🎯 Recherche du dataset: {chemin_fichier}")

        # Chercher le fichier
        fichiers = self.chercher_par_chemin(chemin_fichier)

        if not fichiers:
            print(f"❌ Aucun fichier trouvé pour: {chemin_fichier}")
            print("\n💡 Suggestions:")
            print("   1. Vérifiez l'orthographe du nom")
            print("   2. Vérifiez que le fichier est partagé avec vous")
            print("   3. Essayez de rechercher juste le nom du fichier")
            return None

        # Si plusieurs fichiers
        if len(fichiers) > 1:
            print(f"📋 {len(fichiers)} fichiers trouvés:")
            for i, f in enumerate(fichiers):
                taille = int(f.get("size", 0)) / (1024 * 1024) if f.get("size") else 0
                print(f"  {i+1}. {f['name']} ({taille:.1f} MB)")

            try:
                choice = int(input("Choisissez le numéro: ")) - 1
                fichier_choisi = fichiers[choice]
            except (ValueError, IndexError):
                print("❌ Choix invalide")
                return None
        else:
            fichier_choisi = fichiers[0]

        # Télécharger
        return self.telecharger_fichier(
            fichier_choisi["id"], fichier_choisi["name"], destination
        )


def main():
    """Interface pour télécharger des datasets"""
    print("📊 TÉLÉCHARGEUR DE DATASETS GOOGLE DRIVE")
    print("=" * 45)

    try:
        downloader = DatasetDownloader()

        print("\n📝 Exemples de chemins valides:")
        print("   • archive.zip")
        print("   • data/archive.zip")
        print("   • MyDrive/data/archive.zip")
        print("   • datasets/mnist/data.csv")

        chemin = input("\n📄 Chemin du dataset: ")
        if not chemin:
            print("❌ Chemin requis")
            return

        destination = input("📁 Dossier de destination (Entrée = ./datasets/): ")
        if not destination:
            destination = "./datasets/"

        print(f"\n🚀 Démarrage du téléchargement...")
        resultat = downloader.telecharger_dataset(chemin, destination)

        if resultat:
            print(f"\n🎉 Succès ! Dataset disponible: {resultat}")

            # Afficher des infos sur le fichier
            if os.path.exists(resultat):
                taille = os.path.getsize(resultat) / (1024 * 1024)
                print(f"📊 Taille finale: {taille:.1f} MB")
        else:
            print("\n💥 Échec du téléchargement")

    except KeyboardInterrupt:
        print("\n🛑 Téléchargement interrompu")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")


if __name__ == "__main__":
    main()
