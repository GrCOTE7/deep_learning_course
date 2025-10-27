"""
Version simplifiée du téléchargeur Google Drive
Avec gestion améliorée des erreurs d'authentification
"""

import os
import pickle
import webbrowser
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Scopes pour accès en lecture seule
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def setup_google_drive_access():
    """
    Guide interactif pour configurer l'accès Google Drive
    """
    print("🔧 CONFIGURATION GOOGLE DRIVE")
    print("=" * 40)

    if not os.path.exists("credentials.json"):
        print("❌ Fichier credentials.json manquant")
        print("\n📋 ÉTAPES NÉCESSAIRES :")
        print("1. Allez sur Google Cloud Console")
        print("2. Créez un projet")
        print("3. Activez l'API Google Drive")
        print("4. Créez des credentials OAuth2")
        print("5. Téléchargez le JSON → renommez 'credentials.json'")

        response = input("\n💻 Ouvrir Google Cloud Console maintenant ? (o/n): ")
        if response.lower() == "o":
            webbrowser.open("https://console.cloud.google.com/")

        print(
            "\n⏳ Placez le fichier 'credentials.json' dans ce dossier puis relancez le script"
        )
        return False

    return True


def authenticate_google_drive():
    """
    Authentification avec gestion des erreurs
    """
    creds = None

    # Charger token existant
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # Vérifier si authentification nécessaire
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Rafraîchissement du token...")
            creds.refresh(Request())
        else:
            print("\n🚀 Authentification requise...")
            print("⚠️  IMPORTANT : Si vous voyez 'App en cours de test' :")
            print("   → Cliquez 'Paramètres avancés'")
            print("   → Cliquez 'Accéder à [nom] (non sécurisé)'")
            print("   → C'est normal et sécurisé pour votre propre app !")

            input("\n⏵ Appuyez sur Entrée pour continuer...")

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

                print("✅ Authentification réussie !")

            except Exception as e:
                print(f"❌ Erreur d'authentification: {e}")
                print("\n🔧 SOLUTIONS :")
                print(
                    "1. Vérifiez que votre email est dans 'Test users' (Google Cloud Console)"
                )
                print("2. Réessayez en navigation privée")
                print("3. Supprimez 'token.pickle' et réessayez")
                return None

        # Sauvegarder le token
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def telecharger_fichier_simple(nom_fichier, dossier_destination="./"):
    """
    Fonction simplifiée pour télécharger un fichier par son nom

    Args:
        nom_fichier: Nom du fichier à rechercher
        dossier_destination: Dossier où sauvegarder

    Returns:
        Chemin du fichier téléchargé ou None
    """

    # Vérification de la configuration
    if not setup_google_drive_access():
        return None

    # Authentification
    creds = authenticate_google_drive()
    if not creds:
        return None

    try:
        # Connexion à l'API
        service = build("drive", "v3", credentials=creds)
        print("🔗 Connexion à Google Drive réussie")

        # Recherche du fichier
        print(f"🔍 Recherche de '{nom_fichier}'...")
        query = f"name = '{nom_fichier}'"
        results = (
            service.files()
            .list(q=query, pageSize=10, fields="files(id, name, size)")
            .execute()
        )

        files = results.get("files", [])

        if not files:
            print(f"❌ Aucun fichier trouvé avec le nom: {nom_fichier}")
            return None

        # Si plusieurs fichiers
        if len(files) > 1:
            print(f"⚠️  {len(files)} fichiers trouvés :")
            for i, file in enumerate(files):
                print(f"  {i+1}. {file['name']} (ID: {file['id']})")

            try:
                choice = int(input("Choisissez le numéro: ")) - 1
                selected_file = files[choice]
            except (ValueError, IndexError):
                print("❌ Choix invalide")
                return None
        else:
            selected_file = files[0]

        # Téléchargement
        file_id = selected_file["id"]
        file_name = selected_file["name"]

        print(f"📥 Téléchargement de '{file_name}'...")

        request = service.files().get_media(fileId=file_id)
        destination_path = os.path.join(dossier_destination, file_name)

        # Créer le dossier si nécessaire
        os.makedirs(dossier_destination, exist_ok=True)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            percent = int(status.progress() * 100)
            print(f"⏳ {percent}%", end="\r")

        # Sauvegarder
        with open(destination_path, "wb") as f:
            f.write(fh.getvalue())

        print(f"\n✅ Fichier téléchargé: {destination_path}")
        return destination_path

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def main():
    """Interface simple pour tester"""
    print("🌟 TÉLÉCHARGEUR GOOGLE DRIVE SIMPLIFIÉ")
    print("=" * 40)

    nom = input("📄 Nom du fichier à télécharger: ")
    if not nom:
        print("❌ Nom de fichier requis")
        return

    dossier = input("📁 Dossier de destination (Entrée = dossier actuel): ")
    if not dossier:
        dossier = "./"

    resultat = telecharger_fichier_simple(nom, dossier)

    if resultat:
        print(f"\n🎉 Succès ! Fichier disponible: {resultat}")
    else:
        print("\n💥 Échec du téléchargement")


if __name__ == "__main__":
    main()
