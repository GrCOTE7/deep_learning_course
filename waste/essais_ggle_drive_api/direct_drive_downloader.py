"""
Solution alternative: Téléchargement direct via l'ID du fichier
Contourne les problèmes de timeout des recherches
"""

import os
import pickle
import requests
import time
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def obtenir_credentials():
    
    """Obtient les credentials Google Drive"""
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def telecharger_via_requests(file_id, nom_fichier, destination="./datasets/"):
    """Télécharge un fichier en utilisant requests (plus robuste)"""

    print(f"🚀 Téléchargement alternatif de {nom_fichier}")
    print("=" * 50)

    # Obtenir les credentials
    creds = obtenir_credentials()

    # URL de téléchargement direct Google Drive
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

    # Headers avec authentification
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "User-Agent": "Python-Dataset-Downloader/1.0",
    }

    # Créer le dossier de destination
    os.makedirs(destination, exist_ok=True)
    chemin_complet = os.path.join(destination, nom_fichier)

    max_retries = 3

    for attempt in range(max_retries):
        try:
            print(f"🔄 Tentative {attempt + 1}/{max_retries}")

            # Configuration de la session avec timeout étendu
            session = requests.Session()
            session.headers.update(headers)

            # Faire la requête avec streaming
            response = session.get(
                url, stream=True, timeout=(30, 300)
            )  # 30s connect, 300s read
            response.raise_for_status()

            # Obtenir la taille du fichier
            total_size = int(response.headers.get("content-length", 0))
            print(f"📊 Taille du fichier: {total_size/(1024*1024):.1f} MB")

            # Télécharger avec barre de progression
            downloaded_size = 0
            chunk_size = 1024 * 1024  # 1MB chunks

            with open(chemin_complet, "wb") as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"⏳ Progression: {progress:.1f}%", end="\r")

            print(f"\n✅ Téléchargement réussi: {chemin_complet}")

            # Vérifier la taille finale
            taille_finale = os.path.getsize(chemin_complet)
            print(f"📄 Taille finale: {taille_finale/(1024*1024):.1f} MB")

            return chemin_complet

        except requests.exceptions.Timeout:
            print(f"⏰ Timeout lors de la tentative {attempt + 1}")
        except requests.exceptions.ConnectionError:
            print(f"🔌 Erreur de connexion lors de la tentative {attempt + 1}")
        except Exception as e:
            print(f"❌ Erreur lors de la tentative {attempt + 1}: {e}")

        if attempt < max_retries - 1:
            temps_attente = (attempt + 1) * 10
            print(f"⏸️  Attente {temps_attente}s avant nouvelle tentative...")
            time.sleep(temps_attente)

    print("💥 Échec de tous les téléchargements")
    return None


def rechercher_fichier_dans_dossier_simple(folder_id, nom_fichier):
    """Recherche simple d'un fichier dans un dossier"""

    try:
        creds = obtenir_credentials()
        service = build("drive", "v3", credentials=creds)

        print(f"🔍 Recherche de '{nom_fichier}' dans le dossier...")

        # Recherche avec timeout court
        query = f"'{folder_id}' in parents and name = '{nom_fichier}' and trashed=false"
        results = (
            service.files()
            .list(q=query, pageSize=10, fields="files(id, name)")
            .execute()
        )

        files = results.get("files", [])

        if files:
            print(f"✅ Fichier trouvé: {files[0]['name']} (ID: {files[0]['id']})")
            return files[0]["id"]
        else:
            print(f"❌ Fichier '{nom_fichier}' non trouvé")
            return None

    except Exception as e:
        print(f"❌ Erreur de recherche: {e}")
        return None


def telecharger_archive_direct():
    """Télécharge archive.zip directement"""

    print("🎯 TÉLÉCHARGEMENT DIRECT DU DATASET")
    print("=" * 40)

    folder_id = "1hcYg33Be-WQbk7XPOpkcnit2c0Djtde9"
    nom_fichier = "archive.zip"

    # Option 1: Rechercher le fichier
    print("📋 Option 1: Recherche du fichier...")
    file_id = rechercher_fichier_dans_dossier_simple(folder_id, nom_fichier)

    if file_id:
        return telecharger_via_requests(file_id, nom_fichier)

    # Option 2: Si vous connaissez l'ID direct du fichier
    print("\n📋 Option 2: ID direct du fichier")
    print("💡 Si vous connaissez l'ID direct du fichier archive.zip,")
    print("   vous pouvez l'entrer maintenant pour éviter la recherche.")

    file_id_direct = input("🔗 ID direct du fichier (Entrée pour passer): ").strip()

    if file_id_direct:
        return telecharger_via_requests(file_id_direct, nom_fichier)

    print("❌ Impossible de télécharger le fichier")
    return None


def main():
    """Interface principale"""
    print("🌟 TÉLÉCHARGEUR GOOGLE DRIVE - SOLUTION ROBUSTE")
    print("=" * 50)

    print("🎯 Ce script va télécharger archive.zip de votre dossier Google Drive")
    print(
        "📁 Dossier: https://drive.google.com/drive/folders/1hcYg33Be-WQbk7XPOpkcnit2c0Djtde9"
    )
    print()

    input("⏵ Appuyez sur Entrée pour commencer...")

    resultat = telecharger_archive_direct()

    if resultat:
        print(f"\n🎉 SUCCÈS ! Dataset téléchargé: {resultat}")
        print("\n💡 Étapes suivantes:")
        print("   1. Extrayez le fichier ZIP")
        print("   2. Explorez les données")
        print("   3. Commencez votre analyse !")

        # Code d'extraction automatique
        print(f"\n🔧 Code pour extraire:")
        print(f"import zipfile")
        print(f"with zipfile.ZipFile('{resultat}', 'r') as zip_ref:")
        print(f"    zip_ref.extractall('./datasets/extracted/')")

    else:
        print("\n💡 SOLUTIONS ALTERNATIVES:")
        print("1. Téléchargez manuellement depuis le navigateur")
        print("2. Vérifiez les permissions du dossier")
        print("3. Utilisez l'ID direct du fichier si vous l'avez")


if __name__ == "__main__":
    main()
