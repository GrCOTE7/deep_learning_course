"""
Téléchargeur d'un fichier Google Drive Public
Gère correctement les gros fichiers avec confirmation
Indiquer ci-dessous l'ID et le nom du fichier à télécharger
"""

import os
import requests
import re

# Votre fichier
file_id = "1yFznBUAro3uE1d1utg6GjDsBpAuxsOn3"
nom_fichier = "archive.zip"

def telecharger_fichier_google_drive(
    file_id, nom_fichier="DATASET.zip", destination="./datasets/"
):
    """
    Télécharge un fichier Google Drive public avec gestion des gros fichiers
    """

    print(f"🚀 TÉLÉCHARGEUR GOOGLE DRIVE OPTIMISÉ")
    print("=" * 45)
    print(f"📄 Fichier: {nom_fichier}")
    print(f"🔗 ID: {file_id}")
    print(f"📁 Destination: {destination}")
    print()

    # Créer le dossier de destination
    os.makedirs(destination, exist_ok=True)
    chemin_complet = os.path.join(destination, nom_fichier)

    session = requests.Session()

    try:
        print("🔍 Étape 1: Vérification du fichier...")

        # URL initiale
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = session.get(url, stream=True)

        # Vérifier si c'est un gros fichier nécessitant confirmation
        if "virus scan warning" in response.text.lower():
            print("⚠️  Gros fichier détecté (>25MB)")

            # Extraire les informations du formulaire
            confirm_match = re.search(r'name="confirm" value="([^"]+)"', response.text)
            uuid_match = re.search(r'name="uuid" value="([^"]+)"', response.text)

            if confirm_match and uuid_match:
                confirm_token = confirm_match.group(1)
                uuid_value = uuid_match.group(1)

                print(f"🔑 Token de confirmation trouvé")
                print(f"🔄 Étape 2: Téléchargement avec confirmation...")

                # URL de téléchargement direct avec confirmation
                download_url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm={confirm_token}&uuid={uuid_value}"

                response = session.get(download_url, stream=True)

            else:
                print("❌ Impossible de trouver les tokens de confirmation")
                return None
        else:
            print("✅ Fichier de taille normale")

        response.raise_for_status()

        # Vérifier que nous avons bien le fichier (pas une page HTML)
        content_type = response.headers.get("content-type", "")
        if "text/html" in content_type:
            print("❌ Réponse HTML reçue au lieu du fichier")
            print("🔧 Le fichier nécessite peut-être des permissions spéciales")
            return None

        # Obtenir la taille du fichier
        total_size = int(response.headers.get("content-length", 0))

        if total_size > 0:
            print(f"📊 Taille du fichier: {total_size / (1024*1024):.1f} MB")
        else:
            print("📊 Taille inconnue - Téléchargement en cours...")

        # Télécharger le fichier
        downloaded_size = 0
        chunk_size = 8192  # 8KB chunks pour une meilleure réactivité

        print("📥 Téléchargement en cours...")

        with open(chemin_complet, "wb") as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)

                    if total_size > 0:
                        progress = (downloaded_size / total_size) * 100
                        print(f"⏳ {progress:.1f}%", end="\r")
                    else:
                        mb_downloaded = downloaded_size / (1024 * 1024)
                        print(f"⏳ {mb_downloaded:.1f} MB", end="\r")

        print()  # Nouvelle ligne

        # Vérification finale
        if os.path.exists(chemin_complet):
            taille_finale = os.path.getsize(chemin_complet)

            if taille_finale > 0:
                print(f"✅ TÉLÉCHARGEMENT RÉUSSI!")
                print(f"📄 Fichier: {chemin_complet}")
                print(f"📊 Taille: {taille_finale / (1024*1024):.2f} MB")
                return chemin_complet
            else:
                print("❌ Fichier téléchargé mais vide")
                os.remove(chemin_complet)
                return None
        else:
            print("❌ Fichier non créé")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de réseau: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


def extraire_zip_automatique(chemin_zip):
    """Extrait automatiquement un fichier ZIP"""
    try:
        import zipfile

        print(f"\n📦 EXTRACTION AUTOMATIQUE")
        print("=" * 25)

        dossier_extraction = "./datasets/"
        os.makedirs(dossier_extraction, exist_ok=True)

        print(f"🔓 Extraction de {os.path.basename(chemin_zip)}...")

        with zipfile.ZipFile(chemin_zip, "r") as zip_ref:
            # Obtenir la liste des fichiers
            fichiers = zip_ref.namelist()
            print(f"📋 {len(fichiers)} fichiers à extraire")

            # Extraire avec progression
            for i, fichier in enumerate(fichiers):
                zip_ref.extract(fichier, dossier_extraction)
                if i % 100 == 0 or i == len(fichiers) - 1:
                    progress = ((i + 1) / len(fichiers)) * 100
                    print(f"⏳ Extraction: {progress:.1f}%", end="\r")

        print(f"\n✅ Extraction terminée!")
        print(f"📁 Dossier: {os.path.abspath(dossier_extraction)}")

        # Afficher un aperçu du contenu
        contenu = os.listdir(dossier_extraction)
        print(f"📋 Contenu ({len(contenu)} éléments):")
        for item in contenu[:5]:
            chemin_item = os.path.join(dossier_extraction, item)
            if os.path.isdir(chemin_item):
                print(f"  📁 {item}/")
            else:
                taille = os.path.getsize(chemin_item) / 1024
                print(f"  📄 {item} ({taille:.1f} KB)")

        if len(contenu) > 5:
            print(f"  ... et {len(contenu) - 5} autres éléments")

        return dossier_extraction

    except zipfile.BadZipFile:
        print("❌ Le fichier n'est pas un ZIP valide")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        return None


def main():
    """Télécharge le dataset archive.zip"""

    print("🎯 TÉLÉCHARGEMENT DATASET ARCHIVE.ZIP")
    print("=" * 40)

    print(f"🔗 Lien: https://drive.google.com/file/d/{file_id}/view")
    print(f"📄 Fichier: {nom_fichier}")
    print(f"🌐 Type: Fichier public Google Drive")
    print()

    # Télécharger
    resultat = telecharger_fichier_google_drive(file_id, nom_fichier)

    if resultat:
        print(f"\n🎉 TÉLÉCHARGEMENT RÉUSSI!")
        print("=" * 30)

        taille = os.path.getsize(resultat) / (1024 * 1024)
        print(f"📁 Emplacement: {os.path.abspath(resultat)}")
        print(f"📊 Taille: {taille:.2f} MB")

        # Proposer l'extraction
        if resultat.endswith(".zip"):
            choix = input(f"\n🔧 Extraire automatiquement le ZIP ? (o/n): ")
            if choix.lower() in ["o", "oui", "y", "yes"]:
                dossier_extrait = extraire_zip_automatique(resultat)
                if dossier_extrait:
                    print(f"\n💡 Données prêtes à utiliser dans: {dossier_extrait}")

        print(f"\n🐍 CODE PYTHON POUR UTILISER LE DATASET:")
        print(f"import os")
        print(f"import pandas as pd")
        print(f"")
        print(f"# Lister le contenu")
        print(f"os.listdir('./datasets/extracted/')")
        print(f"")
        print(f"# Charger un fichier CSV par exemple")
        print(f"# df = pd.read_csv('./datasets/extracted/data.csv')")

    else:
        print(f"\n💥 ÉCHEC DU TÉLÉCHARGEMENT")
        print("🔧 SOLUTIONS:")
        print("1. Vérifiez votre connexion internet")
        print("2. Le fichier est peut-être restreint")
        print("3. Téléchargez manuellement:")
        print(f"   https://drive.google.com/file/d/{file_id}/view")


if __name__ == "__main__":
    main()
