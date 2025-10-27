"""
Script pour télécharger des fichiers depuis Google Drive
Utilise l'API Google Drive v3
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Définir les scopes nécessaires
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class GoogleDriveDownloader:
    def __init__(self, credentials_file="credentials.json", token_file="token.pickle"):
        """
        Initialise le téléchargeur Google Drive

        Args:
            credentials_file: Fichier JSON des credentials OAuth2
            token_file: Fichier pour sauvegarder le token d'authentification
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authentifie l'utilisateur avec Google Drive API"""
        creds = None

        # Charger le token existant si disponible
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token:
                creds = pickle.load(token)

        # Si pas de credentials valides, demander l'authentification
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print("🔧 CONFIGURATION NÉCESSAIRE:")
                    print("=" * 50)
                    print("1. Allez sur https://console.cloud.google.com/")
                    print("2. Créez un projet ou sélectionnez-en un")
                    print("3. Activez l'API Google Drive")
                    print("4. Créez des credentials OAuth2 (Application de bureau)")
                    print("5. Téléchargez le JSON et renommez-le 'credentials.json'")
                    print("6. IMPORTANT: Ajoutez votre email dans 'Test users' !")
                    print("=" * 50)
                    raise FileNotFoundError(
                        f"Fichier credentials non trouvé: {self.credentials_file}\n"
                        "Suivez les instructions ci-dessus"
                    )

                print("🚀 Démarrage de l'authentification...")
                print(
                    "⚠️  Si vous voyez l'erreur 'app en cours de test', suivez les étapes ci-dessous:"
                )
                print("   1. Cliquez sur 'Paramètres avancés'")
                print("   2. Cliquez sur 'Accéder à get-drive (non sécurisé)'")
                print(
                    "   3. Ou ajoutez votre email comme testeur dans Google Cloud Console"
                )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Sauvegarder les credentials pour la prochaine fois
            with open(self.token_file, "wb") as token:
                pickle.dump(creds, token)

        self.service = build("drive", "v3", credentials=creds)
        print("✅ Authentification réussie avec Google Drive")

    def search_files(self, query):
        """
        Recherche des fichiers dans Google Drive

        Args:
            query: Requête de recherche (ex: "name contains 'mon_fichier'")

        Returns:
            Liste des fichiers trouvés
        """
        try:
            results = (
                self.service.files()
                .list(
                    q=query,
                    pageSize=10,
                    fields="nextPageToken, files(id, name, size, mimeType)",
                )
                .execute()
            )

            items = results.get("files", [])
            return items
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return []

    def download_file(self, file_id, destination_path=None):
        """
        Télécharge un fichier depuis Google Drive

        Args:
            file_id: ID du fichier Google Drive
            destination_path: Chemin de destination (optionnel)

        Returns:
            Chemin du fichier téléchargé
        """
        try:
            # Obtenir les métadonnées du fichier
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_name = file_metadata["name"]

            if destination_path is None:
                destination_path = file_name

            print(f"📥 Téléchargement de '{file_name}'...")

            # Télécharger le fichier
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"⏳ Progression: {int(status.progress() * 100)}%")

            # Sauvegarder le fichier
            with open(destination_path, "wb") as f:
                f.write(fh.getvalue())

            print(f"✅ Fichier téléchargé: {destination_path}")
            return destination_path

        except Exception as e:
            print(f"❌ Erreur lors du téléchargement: {e}")
            return None

    def download_by_name(self, file_name, destination_path=None):
        """
        Télécharge un fichier par son nom

        Args:
            file_name: Nom du fichier à rechercher
            destination_path: Chemin de destination (optionnel)

        Returns:
            Chemin du fichier téléchargé ou None
        """
        # Rechercher le fichier
        query = f"name = '{file_name}'"
        files = self.search_files(query)

        if not files:
            print(f"❌ Aucun fichier trouvé avec le nom: {file_name}")
            return None

        if len(files) > 1:
            print(f"⚠️  Plusieurs fichiers trouvés avec le nom '{file_name}':")
            for i, file in enumerate(files):
                print(f"  {i+1}. {file['name']} (ID: {file['id']})")

            try:
                choice = (
                    int(input("Choisissez le numéro du fichier à télécharger: ")) - 1
                )
                selected_file = files[choice]
            except (ValueError, IndexError):
                print("❌ Choix invalide")
                return None
        else:
            selected_file = files[0]

        return self.download_file(selected_file["id"], destination_path)


def main():
    """Fonction principale pour tester le téléchargeur"""
    try:
        # Initialiser le téléchargeur
        downloader = GoogleDriveDownloader()

        # Exemple d'utilisation
        print("\n📁 Options disponibles:")
        print("1. Télécharger par nom de fichier")
        print("2. Télécharger par ID de fichier")
        print("3. Rechercher des fichiers")

        choice = input("\nChoisissez une option (1-3): ")

        if choice == "1":
            file_name = input("Nom du fichier à télécharger: ")
            destination = input("Dossier de destination (Entrée pour dossier actuel): ")
            if not destination:
                destination = None
            downloader.download_by_name(file_name, destination)

        elif choice == "2":
            file_id = input("ID du fichier Google Drive: ")
            destination = input("Chemin de destination (Entrée pour nom original): ")
            if not destination:
                destination = None
            downloader.download_file(file_id, destination)

        elif choice == "3":
            search_term = input("Terme de recherche: ")
            query = f"name contains '{search_term}'"
            files = downloader.search_files(query)

            if files:
                print(f"\n📄 Fichiers trouvés ({len(files)}):")
                for file in files:
                    size = (
                        int(file.get("size", 0)) / (1024 * 1024)
                        if file.get("size")
                        else 0
                    )
                    print(
                        f"  • {file['name']} (ID: {file['id']}, Taille: {size:.2f} MB)"
                    )
            else:
                print("❌ Aucun fichier trouvé")

        else:
            print("❌ Option invalide")

    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    main()
