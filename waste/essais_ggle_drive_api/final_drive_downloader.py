"""
SOLUTION FINALE: Téléchargement Google Drive Multi-approches
Combine plusieurs méthodes pour maximiser les chances de succès
"""

import os
import pickle
import requests
import webbrowser
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

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


def telecharger_par_id_direct(file_id, nom_fichier="archive.zip"):
    """Télécharge directement avec l'ID du fichier"""

    print(f"🚀 TÉLÉCHARGEMENT DIRECT PAR ID")
    print("=" * 40)
    print(f"📄 Fichier: {nom_fichier}")
    print(f"🔗 ID: {file_id}")
    print()

    try:
        creds = obtenir_credentials()

        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
        headers = {"Authorization": f"Bearer {creds.token}"}

        print("📥 Démarrage du téléchargement...")

        response = requests.get(url, headers=headers, stream=True, timeout=(60, 600))
        response.raise_for_status()

        # Créer le dossier datasets
        os.makedirs("datasets", exist_ok=True)
        chemin_fichier = os.path.join("datasets", nom_fichier)

        total_size = int(response.headers.get("content-length", 0))
        downloaded_size = 0

        print(f"📊 Taille: {total_size/(1024*1024):.1f} MB")

        with open(chemin_fichier, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"⏳ {progress:.1f}%", end="\r")

        print(f"\n✅ SUCCÈS! Fichier téléchargé: {chemin_fichier}")
        return chemin_fichier

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def ouvrir_dossier_google_drive():
    """Ouvre le dossier Google Drive dans le navigateur"""
    url_dossier = (
        "https://drive.google.com/drive/folders/1hcYg33Be-WQbk7XPOpkcnit2c0Djtde9"
    )
    print(f"🌐 Ouverture du dossier Google Drive...")
    webbrowser.open(url_dossier)
    return url_dossier


def guide_obtenir_id_fichier():
    """Guide pour obtenir l'ID d'un fichier"""
    print("📋 COMMENT OBTENIR L'ID DU FICHIER:")
    print("=" * 40)
    print("1. Je vais ouvrir votre dossier Google Drive")
    print("2. Cliquez droit sur 'archive.zip'")
    print("3. Sélectionnez 'Obtenir le lien' ou 'Get link'")
    print("4. L'URL ressemble à: https://drive.google.com/file/d/ID_DU_FICHIER/view")
    print("5. Copiez la partie ID_DU_FICHIER")
    print()

    input("⏵ Appuyez sur Entrée pour ouvrir Google Drive...")
    ouvrir_dossier_google_drive()

    print()
    file_id = input("🔗 Collez l'ID du fichier archive.zip ici: ").strip()

    if file_id:
        # Nettoyer l'ID si l'utilisateur a collé l'URL complète
        if "drive.google.com/file/d/" in file_id:
            file_id = file_id.split("/d/")[1].split("/")[0]

        print(f"✅ ID nettoyé: {file_id}")
        return file_id

    return None


def telecharger_manuellement():
    """Instructions pour téléchargement manuel"""
    print("📥 TÉLÉCHARGEMENT MANUEL:")
    print("=" * 30)
    print("1. Je vais ouvrir votre dossier Google Drive")
    print("2. Cliquez sur 'archive.zip'")
    print("3. Cliquez sur l'icône de téléchargement (↓)")
    print("4. Sauvegardez dans le dossier 'datasets'")
    print()

    input("⏵ Appuyez sur Entrée pour ouvrir Google Drive...")
    ouvrir_dossier_google_drive()

    print("\n💡 Une fois téléchargé manuellement:")
    print("   - Placez le fichier dans: d:\\dl\\datasets\\")
    print("   - Renommez-le 'archive.zip' si nécessaire")


def main():
    """Interface principale avec toutes les options"""
    print("🎯 TÉLÉCHARGEUR GOOGLE DRIVE - SOLUTION COMPLÈTE")
    print("=" * 55)
    print(
        "📁 Dossier cible: https://drive.google.com/drive/folders/1hcYg33Be-WQbk7XPOpkcnit2c0Djtde9"
    )
    print("📄 Fichier cible: archive.zip")
    print()

    choix = input(
        """
🔧 MÉTHODES DISPONIBLES:

1. 🚀 Téléchargement automatique par ID (Recommandé)
   → Vous obtenez l'ID du fichier, je télécharge automatiquement

2. 📥 Téléchargement manuel guidé
   → Je vous guide pour télécharger manuellement

3. 🔗 Ouvrir seulement le dossier Google Drive
   → Pour voir le contenu et faire ce que vous voulez

Votre choix (1-3): """
    )

    if choix == "1":
        print("\n🎯 TÉLÉCHARGEMENT AUTOMATIQUE")
        print("=" * 35)

        file_id = guide_obtenir_id_fichier()

        if file_id:
            resultat = telecharger_par_id_direct(file_id)

            if resultat:
                print(f"\n🎉 MISSION ACCOMPLIE!")
                print(f"📄 Fichier: {resultat}")

                taille = os.path.getsize(resultat)
                print(f"📊 Taille: {taille/(1024*1024):.1f} MB")

                print(f"\n🔧 Code pour extraire le ZIP:")
                print(f"import zipfile")
                print(f"with zipfile.ZipFile('{resultat}', 'r') as zip_ref:")
                print(f"    zip_ref.extractall('./datasets/extracted/')")

            else:
                print("\n💥 Échec - Essayez le téléchargement manuel (option 2)")
        else:
            print("❌ ID non fourni")

    elif choix == "2":
        print("\n📥 TÉLÉCHARGEMENT MANUEL GUIDÉ")
        print("=" * 35)
        telecharger_manuellement()

    elif choix == "3":
        print("\n🔗 OUVERTURE DU DOSSIER")
        print("=" * 25)
        ouvrir_dossier_google_drive()
        print("✅ Dossier ouvert dans votre navigateur")

    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()
