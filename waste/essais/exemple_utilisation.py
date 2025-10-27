"""
Exemple d'utilisation du GoogleDriveDownloader
"""

from get_drive_file import GoogleDriveDownloader


# Exemple simple d'utilisation
def telecharger_mon_fichier():
    """Exemple de fonction pour télécharger un fichier spécifique"""

    try:
        # Initialiser le téléchargeur
        downloader = GoogleDriveDownloader()

        # Méthode 1: Télécharger par nom
        file_path = downloader.download_by_name(
            file_name="mon_dataset.csv", destination_path="./data/dataset.csv"
        )

        if file_path:
            print(f"Fichier téléchargé avec succès: {file_path}")
            return file_path
        else:
            print("Échec du téléchargement")
            return None

    except Exception as e:
        print(f"Erreur: {e}")
        return None


# Exemple avec ID de fichier
def telecharger_par_id():
    """Télécharger en utilisant l'ID du fichier Google Drive"""

    downloader = GoogleDriveDownloader()

    # Remplacez par l'ID réel de votre fichier
    file_id = "1234567890abcdefghijklmnop"

    file_path = downloader.download_file(
        file_id=file_id, destination_path="./mon_fichier_telecharge.txt"
    )

    return file_path


if __name__ == "__main__":
    # Testez ici vos fonctions
    print("Téléchargement en cours...")
    # telecharger_mon_fichier()
