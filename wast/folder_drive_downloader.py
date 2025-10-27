"""
Téléchargeur Google Drive par dossier et nom de fichier
Optimisé pour télécharger des fichiers dans des dossiers spécifiques
"""

import os
import pickle
import time
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Scopes pour accès en lecture seule
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class GoogleDriveFolderDownloader:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authentification avec Google Drive"""
        creds = None

        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("credentials.json"):
                    print("❌ Fichier credentials.json manquant")
                    return False

                print("🚀 Authentification en cours...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)

        self.service = build("drive", "v3", credentials=creds)
        print("✅ Connexion à Google Drive réussie")
        return True

    def lister_contenu_dossier(self, folder_id):
        """Liste le contenu d'un dossier Google Drive"""
        try:
            print(f"📁 Exploration du dossier {folder_id}...")

            query = f"'{folder_id}' in parents and trashed=false"
            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=100,
                    fields="files(id, name, mimeType, size, parents)",
                )
                .execute()
            )

            files = results.get("files", [])

            if not files:
                print("❌ Dossier vide ou inaccessible")
                return []

            print(f"📋 Contenu du dossier ({len(files)} éléments):")
            for file in files:
                file_type = (
                    "📁"
                    if file["mimeType"] == "application/vnd.google-apps.folder"
                    else "📄"
                )
                size = (
                    f" ({int(file.get('size', 0))/(1024*1024):.1f} MB)"
                    if file.get("size")
                    else ""
                )
                print(f"  {file_type} {file['name']}{size}")

            return files

        except Exception as e:
            print(f"❌ Erreur lors de l'exploration: {e}")
            return []

    def telecharger_fichier_du_dossier(self, folder_id, nom_fichier, destination="./"):
        """Télécharge un fichier spécifique d'un dossier"""

        # Lister le contenu du dossier
        files = self.lister_contenu_dossier(folder_id)

        if not files:
            return None

        # Chercher le fichier
        fichier_trouve = None
        for file in files:
            if file["name"].lower() == nom_fichier.lower():
                fichier_trouve = file
                break

        if not fichier_trouve:
            print(f"❌ Fichier '{nom_fichier}' non trouvé dans le dossier")
            print("📋 Fichiers disponibles:")
            for file in files:
                if file["mimeType"] != "application/vnd.google-apps.folder":
                    print(f"  • {file['name']}")
            return None

        # Télécharger le fichier
        return self.telecharger_fichier(
            fichier_trouve["id"], fichier_trouve["name"], destination
        )

    def telecharger_fichier(self, file_id, nom_fichier, destination="./"):
        """Télécharge un fichier par son ID avec retry automatique"""

        print(f"📥 Démarrage du téléchargement: {nom_fichier}")

        # Créer le dossier de destination
        os.makedirs(destination, exist_ok=True)
        chemin_destination = os.path.join(destination, nom_fichier)

        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"🔄 Tentative {attempt + 1}/{max_retries}")

                # Configurer le téléchargement avec timeout plus long
                request = self.service.files().get_media(fileId=file_id)
                fh = io.BytesIO()

                downloader = MediaIoBaseDownload(
                    fh, request, chunksize=1024 * 1024 * 10
                )  # 10MB chunks

                done = False
                derniere_progression = -1

                while done is False:
                    try:
                        status, done = downloader.next_chunk()
                        if status:
                            progression = int(status.progress() * 100)
                            if progression != derniere_progression:
                                print(f"⏳ Progression: {progression}%")
                                derniere_progression = progression
                    except Exception as chunk_error:
                        print(f"⚠️  Erreur de chunk: {chunk_error}")
                        time.sleep(2)
                        continue

                # Sauvegarder le fichier
                print("💾 Sauvegarde en cours...")
                with open(chemin_destination, "wb") as f:
                    f.write(fh.getvalue())

                # Vérifier la taille
                taille_fichier = os.path.getsize(chemin_destination)
                print(f"✅ Téléchargement réussi!")
                print(f"📄 Fichier: {chemin_destination}")
                print(f"📊 Taille: {taille_fichier/(1024*1024):.1f} MB")

                return chemin_destination

            except Exception as e:
                print(f"❌ Tentative {attempt + 1} échouée: {e}")
                if attempt < max_retries - 1:
                    temps_attente = (attempt + 1) * 5
                    print(f"⏸️  Attente {temps_attente}s avant nouvelle tentative...")
                    time.sleep(temps_attente)
                else:
                    print("💥 Échec de tous les téléchargements")
                    return None

        return None


def telecharger_archive_dataset():
    """Fonction spécifique pour télécharger archive.zip du dossier donné"""

    print("🎯 TÉLÉCHARGEMENT DU DATASET ARCHIVE.ZIP")
    print("=" * 50)

    # ID du dossier depuis l'URL fournie
    folder_id = "1hcYg33Be-WQbk7XPOpkcnit2c0Djtde9"
    nom_fichier = "archive.zip"
    destination = "./datasets/"

    downloader = GoogleDriveFolderDownloader()

    if not downloader.service:
        print("❌ Échec de l'authentification")
        return None

    resultat = downloader.telecharger_fichier_du_dossier(
        folder_id=folder_id, nom_fichier=nom_fichier, destination=destination
    )

    if resultat:
        print(f"\n🎉 SUCCÈS ! Dataset téléchargé: {resultat}")

        # Informations additionnelles
        taille = os.path.getsize(resultat)
        print(f"📊 Taille finale: {taille/(1024*1024):.1f} MB")

        # Suggérer l'extraction
        if resultat.endswith(".zip"):
            print(f"\n💡 Pour extraire le fichier:")
            print(f"   import zipfile")
            print(f"   with zipfile.ZipFile('{resultat}', 'r') as zip_ref:")
            print(f"       zip_ref.extractall('./datasets/extracted/')")

        return resultat
    else:
        print("\n💥 Échec du téléchargement")
        return None


def main():
    """Interface principale"""
    print("🌟 TÉLÉCHARGEUR GOOGLE DRIVE - DOSSIERS SPÉCIFIQUES")
    print("=" * 55)

    choice = input(
        """
📋 Options disponibles:
1. Télécharger archive.zip (votre dataset)
2. Télécharger un autre fichier d'un dossier
3. Explorer un dossier

Votre choix (1-3): """
    )

    downloader = GoogleDriveFolderDownloader()

    if choice == "1":
        telecharger_archive_dataset()

    elif choice == "2":
        folder_id = input("🔗 ID du dossier Google Drive: ")
        nom_fichier = input("📄 Nom du fichier: ")
        destination = input("📁 Dossier de destination (Entrée = './downloads/'): ")
        if not destination:
            destination = "./downloads/"

        resultat = downloader.telecharger_fichier_du_dossier(
            folder_id, nom_fichier, destination
        )
        if resultat:
            print(f"✅ Fichier téléchargé: {resultat}")

    elif choice == "3":
        folder_id = input("🔗 ID du dossier à explorer: ")
        downloader.lister_contenu_dossier(folder_id)

    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()
