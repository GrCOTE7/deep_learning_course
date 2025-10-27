"""
Téléchargeur optimisé de datasets Google Drive
Télécharge, extrait et organise automatiquement les datasets
"""

import os
import re
import zipfile
import requests

# Configuration du fichier à télécharger
file_id = "1yFznBUAro3uE1d1utg6GjDsBpAuxsOn3"
file_name = "WASTE.zip"

# Pour les tests (fichier plus petit)
# file_id = "1jFxX8wxwAXes8UJxG0tJbK3Xt99rDZlu"
# file_name = "WASTE_COURT.zip"

# Configuration automatique des chemins
DATASET_NAME = os.path.splitext(file_name)[0]
DESTINATION = f"./datasets/{DATASET_NAME}/"


def telecharger_google_drive(file_id, file_name, destination):
    """Télécharge un fichier Google Drive public avec gestion des gros fichiers"""
    print(f"🚀 Téléchargement: {file_name} → {destination}")

    os.makedirs(destination, exist_ok=True)
    chemin_complet = os.path.join(destination, file_name)

    with requests.Session() as session:
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = session.get(url, stream=True)

        # Gestion des gros fichiers
        if "virus scan warning" in response.text.lower():
            print("⚠️  Gros fichier - Récupération du token...")
            tokens = re.findall(r'name="(confirm|uuid)" value="([^"]+)"', response.text)
            if len(tokens) != 2:
                return None
            confirm, uuid = dict(tokens)["confirm"], dict(tokens)["uuid"]
            url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm={confirm}&uuid={uuid}"
            response = session.get(url, stream=True)

        response.raise_for_status()

        if "text/html" in response.headers.get("content-type", ""):
            print("❌ Erreur: Page HTML reçue")
            return None

        # Téléchargement avec progression
        total = int(response.headers.get("content-length", 0))
        downloaded = 0

        print("📥 Téléchargement...")
        with open(chemin_complet, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        print(f"⏳ {(downloaded/total)*100:.1f}%", end="\r")

        print(f"\n✅ {os.path.getsize(chemin_complet)/(1024*1024):.2f} MB téléchargés")
        return chemin_complet


def extraire_zip(chemin_zip, destination):
    """Extrait le ZIP en supprimant les dossiers racine redondants"""
    print(f"\n📦 Extraction: {os.path.basename(chemin_zip)}")

    with zipfile.ZipFile(chemin_zip, "r") as zip_ref:
        fichiers = zip_ref.namelist()
        print(f"📋 {len(fichiers)} fichiers")

        # Détection dossier racine
        racine = None
        if fichiers and "/" in fichiers[0]:
            possible = fichiers[0].split("/")[0] + "/"
            if all(
                f.startswith(possible) or f == possible.rstrip("/") for f in fichiers
            ):
                racine = possible
                print(f"🔍 Suppression dossier racine: {racine}")

        # Extraction
        for i, fichier in enumerate(fichiers):
            if racine and fichier.startswith(racine):
                ajuste = fichier[len(racine) :]
                if not ajuste:
                    continue
                final = os.path.join(destination, ajuste)
            else:
                final = os.path.join(destination, fichier)

            if fichier.endswith("/"):
                os.makedirs(final, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(final), exist_ok=True)
                with zip_ref.open(fichier) as src, open(final, "wb") as dst:
                    dst.write(src.read())

            if i % 50 == 0 or i == len(fichiers) - 1:
                print(f"⏳ {((i+1)/len(fichiers))*100:.0f}%", end="\r")

    os.remove(chemin_zip)
    print(f"\n✅ Extraction terminée - ZIP supprimé")


def dataset_complet(dossier):
    """Vérifie présence des dossiers TEST/ et TRAIN/"""
    return (
        os.path.exists(dossier)
        and os.path.isdir(os.path.join(dossier, "TEST"))
        and os.path.isdir(os.path.join(dossier, "TRAIN"))
    )


def afficher_arbre(dossier):
    """Affiche la structure du dataset"""
    if not os.path.exists(dossier):
        return

    print(f"\n🌳 STRUCTURE DATASET:")
    print("=" * 25)

    dossiers = sorted(
        [d for d in os.listdir(dossier) if os.path.isdir(os.path.join(dossier, d))]
    )

    for i, item in enumerate(dossiers):
        is_last = i == len(dossiers) - 1
        prefix = "└── " if is_last else "├── "
        print(f"{prefix}{item}\\")

        # Sous-dossiers
        chemin = os.path.join(dossier, item)
        sous = sorted(
            [d for d in os.listdir(chemin) if os.path.isdir(os.path.join(chemin, d))]
        )

        for j, sub in enumerate(sous):
            is_last_sub = j == len(sous) - 1
            prefix_sub = (
                "    └── "
                if is_last
                else (
                    "│   └── "
                    if is_last_sub
                    else ("    ├── " if is_last else "│   ├── ")
                )
            )

            # Comptage fichiers
            nb = len(
                [
                    f
                    for f in os.listdir(os.path.join(chemin, sub))
                    if os.path.isfile(os.path.join(chemin, sub, f))
                ]
            )

            type_img = "organiques" if sub == "O" else "recyclables"
            type_set = "test" if item == "TEST" else "train"

            print(f"{prefix_sub}{sub}\\ # {nb} {type_img} {type_set}")

        if not is_last:
            print("│")


def main():
    """Workflow principal"""
    print("🎯 DATASET WASTE - AUTOMATISÉ")
    print("=" * 30)
    print(f"📄 {file_name} → {DESTINATION}")

    dest = DESTINATION.rstrip("/")

    # Vérification dataset existant
    if dataset_complet(dest):
        print("\n✅ Dataset complet détecté!")
        print("🚀 Téléchargement non nécessaire")
        afficher_arbre(dest)
        return

    print("\n🔍 Téléchargement requis...")

    # Téléchargement et extraction
    zip_path = telecharger_google_drive(file_id, file_name, DESTINATION)
    if zip_path:
        extraire_zip(zip_path, DESTINATION)
        afficher_arbre(dest)
    else:
        print("❌ Échec téléchargement")


if __name__ == "__main__":
    main()
