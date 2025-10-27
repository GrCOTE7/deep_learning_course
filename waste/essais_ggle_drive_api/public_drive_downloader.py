"""
Téléchargeur pour fichier Google Drive public
Utilise l'ID direct du fichier partagé
"""

import os
import requests
from urllib.parse import urlparse


def telecharger_fichier_public_google_drive(
    file_id, nom_fichier="WASTE.zip", destination="./datasets/"
):
    """
    Télécharge un fichier Google Drive partagé publiquement

    Args:
        file_id: ID du fichier Google Drive
        nom_fichier: Nom pour sauvegarder le fichier
        destination: Dossier de destination

    Returns:
        Chemin du fichier téléchargé ou None en cas d'erreur
    """

    print(f"🚀 TÉLÉCHARGEMENT FICHIER PUBLIC GOOGLE DRIVE")
    print("=" * 50)
    print(f"📄 Fichier: {nom_fichier}")
    print(f"🔗 ID: {file_id}")
    print(f"📁 Destination: {destination}")
    print()

    # Créer le dossier de destination
    os.makedirs(destination, exist_ok=True)
    chemin_complet = os.path.join(destination, nom_fichier)

    # URL pour fichiers publics Google Drive
    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    try:
        print("🔍 Vérification du fichier...")

        # Première requête pour gérer les gros fichiers
        session = requests.Session()
        response = session.get(url, stream=True)

        # Pour les gros fichiers, Google demande une confirmation
        if (
            "virus scan warning" in response.text.lower()
            or "download anyway" in response.text.lower()
        ):
            print("⚠️  Fichier volumineux détecté - Contournement de l'avertissement...")

            # Chercher le token de confirmation
            for line in response.text.split("\n"):
                if "confirm=" in line and "id=" in line:
                    import re

                    confirm = re.search(r"confirm=([^&]+)", line)
                    if confirm:
                        confirm_token = confirm.group(1)
                        url = f"https://drive.google.com/uc?export=download&confirm={confirm_token}&id={file_id}"
                        response = session.get(url, stream=True)
                        break

        response.raise_for_status()

        # Obtenir la taille du fichier si disponible
        total_size = int(response.headers.get("content-length", 0))

        if total_size > 0:
            print(f"📊 Taille du fichier: {total_size / (1024*1024):.1f} MB")
        else:
            print("📊 Taille inconnue - Téléchargement en cours...")

        # Télécharger avec barre de progression
        downloaded_size = 0
        chunk_size = 1024 * 1024  # 1MB par chunk

        print("📥 Téléchargement en cours...")

        with open(chemin_complet, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"⏳ Progression: {progress:.1f}%", end="\r")
                    else:
                        print(
                            f"⏳ Téléchargé: {downloaded_size / (1024*1024):.1f} MB",
                            end="\r",
                        )

        print()  # Nouvelle ligne après la progression

        # Vérifier que le fichier a été téléchargé
        if os.path.exists(chemin_complet):
            taille_finale = os.path.getsize(chemin_complet)
            print(f"✅ TÉLÉCHARGEMENT RÉUSSI!")
            print(f"📄 Fichier: {chemin_complet}")
            print(f"📊 Taille finale: {taille_finale / (1024*1024):.1f} MB")

            return chemin_complet
        else:
            print("❌ Erreur: Fichier non créé")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de réseau: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return None


def extraire_id_depuis_url(url):
    """Extrait l'ID du fichier depuis une URL Google Drive"""
    if "drive.google.com/file/d/" in url:
        return url.split("/d/")[1].split("/")[0]
    elif "id=" in url:
        return url.split("id=")[1].split("&")[0]
    else:
        return url.strip()


def telecharger_archive_dataset():
    """Télécharge spécifiquement le dataset archive.zip"""

    # Votre ID de fichier
    file_id = "1Wq_Dj9Sx0OWZzfeAzLVlOqtcHTGZf40B"

    print("🎯 TÉLÉCHARGEMENT DU DATASET ARCHIVE.ZIP")
    print("=" * 45)
    print("🔗 Fichier partagé publiquement")
    print(f"🆔 ID: {file_id}")
    print()

    resultat = telecharger_fichier_public_google_drive(
        file_id=file_id, nom_fichier="archive.zip", destination="./datasets/"
    )

    if resultat:
        print(f"\n🎉 SUCCÈS TOTAL!")
        print("=" * 20)

        # Informations sur le fichier
        taille = os.path.getsize(resultat)
        print(f"📁 Localisation: {os.path.abspath(resultat)}")
        print(f"📊 Taille: {taille / (1024*1024):.2f} MB")

        # Code pour extraire
        print(f"\n💡 ÉTAPES SUIVANTES:")
        print(f"1. Extraire le fichier ZIP:")
        print(f"   import zipfile")
        print(f"   with zipfile.ZipFile('{resultat}', 'r') as zip_ref:")
        print(f"       zip_ref.extractall('./datasets/extracted/')")
        print(f"")
        print(f"2. Explorer les données:")
        print(f"   import os")
        print(f"   os.listdir('./datasets/extracted/')")

        # Proposer d'extraire automatiquement
        choix = input(f"\n🔧 Voulez-vous extraire automatiquement le ZIP ? (o/n): ")
        if choix.lower() == "o":
            extraire_zip(resultat)

        return resultat
    else:
        print("\n💥 ÉCHEC DU TÉLÉCHARGEMENT")
        print("🔧 Solutions alternatives:")
        print("1. Vérifiez votre connexion internet")
        print("2. Téléchargez manuellement depuis le navigateur")
        print("3. Vérifiez que le lien est toujours valide")
        return None


def extraire_zip(chemin_zip):
    """Extrait automatiquement le fichier ZIP"""
    try:
        import zipfile

        dossier_extraction = "./datasets/extracted/"
        os.makedirs(dossier_extraction, exist_ok=True)

        print(f"📦 Extraction de {chemin_zip}...")

        with zipfile.ZipFile(chemin_zip, "r") as zip_ref:
            zip_ref.extractall(dossier_extraction)

        print(f"✅ Extraction réussie dans: {dossier_extraction}")

        # Lister le contenu extrait
        contenu = os.listdir(dossier_extraction)
        print(f"📋 Contenu extrait ({len(contenu)} éléments):")
        for item in contenu[:10]:  # Afficher max 10 éléments
            print(f"  • {item}")

        if len(contenu) > 10:
            print(f"  ... et {len(contenu) - 10} autres éléments")

    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")


def main():
    """Interface principale"""
    print("🌟 TÉLÉCHARGEUR GOOGLE DRIVE - FICHIER PUBLIC")
    print("=" * 50)
    print("📄 Fichier cible: archive.zip")
    print(
        "🔗 Lien: https://drive.google.com/file/d/1Wq_Dj9Sx0OWZzfeAzLVlOqtcHTGZf40B/view"
    )
    print("🌐 Accès: Public (pas besoin d'authentification)")
    print()

    choix = input(
        """
🔧 OPTIONS DISPONIBLES:

1. 🚀 Télécharger archive.zip (Automatique)
2. 🔗 Télécharger un autre fichier public par URL/ID
3. ℹ️  Afficher les informations sur le script

Votre choix (1-3): """
    )

    if choix == "1":
        telecharger_archive_dataset()

    elif choix == "2":
        print("\n🔗 TÉLÉCHARGEMENT PERSONNALISÉ")
        print("=" * 30)

        url_ou_id = input("🔗 URL complète ou ID du fichier: ").strip()
        nom_fichier = input("📄 Nom du fichier (ex: mon_dataset.zip): ").strip()

        if not nom_fichier:
            nom_fichier = "fichier_telecharge.zip"

        file_id = extraire_id_depuis_url(url_ou_id)

        if file_id:
            resultat = telecharger_fichier_public_google_drive(file_id, nom_fichier)
            if resultat:
                print(f"✅ Fichier téléchargé: {resultat}")
            else:
                print("❌ Échec du téléchargement")
        else:
            print("❌ ID de fichier invalide")

    elif choix == "3":
        print("\n ℹ️ INFORMATIONS SUR LE SCRIPT")
        print("=" * 30)
        print("• Ce script télécharge des fichiers Google Drive publics")
        print("• Pas besoin d'authentification OAuth")
        print("• Fonctionne avec les liens 'Partagé avec tous ceux qui ont le lien'")
        print("• Gère automatiquement les gros fichiers")
        print("• Peut extraire automatiquement les fichiers ZIP")

    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    main()
