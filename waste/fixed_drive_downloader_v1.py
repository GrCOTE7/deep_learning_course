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
nom_fichier = "WASTE.zip"

# Pour les tests (fichier plus petit)
file_id = "1jFxX8wxwAXes8UJxG0tJbK3Xt99rDZlu"
nom_fichier = "WASTE_COURT.zip"

# Calcul automatique du dossier basé sur le nom du fichier
# Supprime l'extension et garde en majuscules pour le dataset final
nom_base = os.path.splitext(nom_fichier)[0]  # WASTE_COURT ou WASTE
dataset_name = "WASTE"  # Nom du dataset final (toujours WASTE)
folder = f"./datasets/{dataset_name}/"  # Dossier global au niveau du projet dl/
# print(f"📁 Dossier calculé: {folder}")
# print(f"📄 Fichier: {nom_fichier}")


def telecharger_fichier_google_drive(
    file_id, nom_fichier="archive.zip", destination="./datasets/"
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


def extraire_zip_automatique(chemin_zip, dossier_extraction="./datasets/extracted/"):
    """Extrait automatiquement un fichier ZIP dans le dossier spécifié"""
    try:
        import zipfile

        print(f"\n📦 EXTRACTION AUTOMATIQUE")
        print("=" * 25)

        # Utiliser le dossier d'extraction fourni
        os.makedirs(dossier_extraction, exist_ok=True)

        print(f"🔓 Extraction de {os.path.basename(chemin_zip)}...")
        
        with zipfile.ZipFile(chemin_zip, "r") as zip_ref:
            # Obtenir la liste des fichiers
            fichiers = zip_ref.namelist()
            print(f"📋 {len(fichiers)} fichiers à extraire")

            # Détecter si tous les fichiers sont dans un dossier racine unique
            dossier_racine = None
            if fichiers:
                # Prendre le premier élément pour détecter le dossier racine
                premier_fichier = fichiers[0]
                if '/' in premier_fichier:
                    possible_racine = premier_fichier.split('/')[0] + '/'
                    # Vérifier si TOUS les fichiers commencent par ce dossier
                    if all(f.startswith(possible_racine) or f == possible_racine.rstrip('/') for f in fichiers):
                        dossier_racine = possible_racine
                        print(f"🔍 Dossier racine détecté: {dossier_racine}")

            # Extraire avec progression et ajustement des chemins
            for i, fichier in enumerate(fichiers):
                # Ajuster le chemin si dossier racine détecté
                if dossier_racine and fichier.startswith(dossier_racine):
                    # Supprimer le dossier racine du chemin
                    chemin_ajuste = fichier[len(dossier_racine):]
                    if chemin_ajuste:  # Ignorer le dossier racine lui-même
                        chemin_destination = os.path.join(dossier_extraction, chemin_ajuste)
                        
                        # Si c'est un dossier (se termine par /)
                        if fichier.endswith('/'):
                            os.makedirs(chemin_destination, exist_ok=True)
                        else:
                            # C'est un fichier
                            # Créer les dossiers parents si nécessaire
                            os.makedirs(os.path.dirname(chemin_destination), exist_ok=True)
                            
                            # Extraire le fichier
                            with zip_ref.open(fichier) as source, open(chemin_destination, 'wb') as f_dest:
                                f_dest.write(source.read())
                else:
                    # Extraction normale
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

        # Supprimer le fichier ZIP source après extraction réussie
        try:
            os.remove(chemin_zip)
            print(f"🗑️  Fichier ZIP source supprimé: {os.path.basename(chemin_zip)}")
        except Exception as e:
            print(f"⚠️  Impossible de supprimer le ZIP: {e}")

        return dossier_extraction

    except zipfile.BadZipFile:
        print("❌ Le fichier n'est pas un ZIP valide")
        return None
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction: {e}")
        return None


def afficher_arbre_dataset(dossier_racine):
    """Affiche la structure du dataset sous forme d'arbre ASCII"""
    try:
        if not os.path.exists(dossier_racine):
            return
        
        print(f"\n🌳 STRUCTURE FINALE DU DATASET:")
        print("=" * 35)
        
        # Parcourir la structure
        contenu_racine = sorted(os.listdir(dossier_racine))
        
        for i, item in enumerate(contenu_racine):
            chemin_item = os.path.join(dossier_racine, item)
            is_last_root = i == len(contenu_racine) - 1
            
            if os.path.isdir(chemin_item):
                # Afficher le dossier racine (TEST ou TRAIN)
                prefix_root = "└── " if is_last_root else "├── "
                
                # Compter les fichiers dans les sous-dossiers
                sous_dossiers = []
                try:
                    sous_contenu = sorted(os.listdir(chemin_item))
                    for sous_item in sous_contenu:
                        sous_chemin = os.path.join(chemin_item, sous_item)
                        if os.path.isdir(sous_chemin):
                            nb_fichiers = len([f for f in os.listdir(sous_chemin) 
                                             if os.path.isfile(os.path.join(sous_chemin, f))])
                            sous_dossiers.append((sous_item, nb_fichiers))
                except:
                    pass
                
                print(f"{prefix_root}{item}\\")
                
                # Afficher les sous-dossiers (O et R)
                for j, (sous_dossier, nb_fichiers) in enumerate(sous_dossiers):
                    is_last_sub = j == len(sous_dossiers) - 1
                    
                    if is_last_root:
                        prefix_sub = "    └── " if is_last_sub else "    ├── "
                        comment_prefix = "    "
                    else:
                        prefix_sub = "│   └── " if is_last_sub else "│   ├── "
                        comment_prefix = "│   "
                    
                    # Déterminer le type d'images
                    type_image = "images organiques" if sous_dossier == "O" else "images recyclables"
                    type_dataset = "test" if item == "TEST" else "train"
                    
                    print(f"{prefix_sub}{sous_dossier}\\          # {nb_fichiers} {type_image} {type_dataset}")
                
                # Ligne vide entre TEST et TRAIN
                if not is_last_root:
                    print("│")
        
        print()
        
    except Exception as e:
        print(f"⚠️  Impossible d'afficher l'arbre: {e}")


def main(telech=True, extract=True):
    """Télécharge le dataset avec dossier calculé automatiquement"""

    print("🎯 TÉLÉCHARGEMENT DATASET")
    print("=" * 30)

    print(f"🔗 Lien: https://drive.google.com/file/d/{file_id}/view")
    print(f"📄 Fichier: {nom_fichier}")
    print(f"📁 Dossier calculé: {folder}")
    print(f"🌐 Type: Fichier public Google Drive")
    print()

    # Chemin complet du fichier à télécharger/extraire
    chemin_fichier = os.path.join(folder, nom_fichier)

    if telech:
        # Télécharger avec le dossier calculé
        resultat = telecharger_fichier_google_drive(file_id, nom_fichier, folder)

        if resultat:
            print(f"\n🎉 TÉLÉCHARGEMENT RÉUSSI!")
            print("=" * 30)

            taille = os.path.getsize(resultat) / (1024 * 1024)
            print(f"📁 Emplacement: {os.path.abspath(resultat)}")
            print(f"📊 Taille: {taille:.2f} MB")

            # Si extraction demandée après téléchargement
            if extract and resultat.endswith(".zip"):
                # Proposer l'extraction
                # if extract and resultat.endswith(".zip"):
                #     choix = input(f"\n🔧 Extraire automatiquement le ZIP ? (o/n): ")
                #     if choix.lower() in ["o", "oui", "y", "yes"]:
                #         # Extraction dans le dossier calculé
                #         dossier_extraction = folder + "extracted/"
                #         dossier_extrait = extraire_zip_automatique(
                #             resultat, dossier_extraction
                #         )
                #         if dossier_extrait:
                #             print(f"\n💡 Données prêtes à utiliser dans: {dossier_extrait}")

                dossier_extraction = folder  # On reste dans le même dossier
                dossier_extrait = extraire_zip_automatique(resultat, dossier_extraction)
                if dossier_extrait:
                    print(f"\n💡 Données prêtes à utiliser dans: {dossier_extrait}")

        else:
            print(f"\n� ÉCHEC DU TÉLÉCHARGEMENT")
            print("🔧 SOLUTIONS:")
            print("1. Vérifiez votre connexion internet")
            print("2. Le fichier est peut-être restreint")
            print("3. Téléchargez manuellement:")
            print(f"   https://drive.google.com/file/d/{file_id}/view")

    elif extract:
        # Pas de téléchargement, mais extraction demandée
        print("🔍 Mode extraction seule - Vérification du fichier existant...")
        
        # Vérifier plusieurs emplacements possibles
        chemins_possibles = [
            chemin_fichier,  # ../datasets/WASTE/WASTE_COURT.zip
            os.path.join("../datasets", dataset_name, nom_fichier),  # ../datasets/WASTE/WASTE_COURT.zip
            os.path.join("datasets", dataset_name, nom_fichier),  # datasets/WASTE/WASTE_COURT.zip (si lancé depuis dl/)
        ]
        
        fichier_trouve = None
        for chemin in chemins_possibles:
            if os.path.exists(chemin):
                fichier_trouve = chemin
                break
        
        if fichier_trouve:
            print(f"✅ Fichier trouvé: {fichier_trouve}")
            taille = os.path.getsize(fichier_trouve) / (1024 * 1024)
            print(f"📊 Taille: {taille:.2f} MB")
            
            if fichier_trouve.endswith(".zip"):
                dossier_extraction = folder  # On extrait dans le même dossier que le ZIP
                dossier_extrait = extraire_zip_automatique(fichier_trouve, dossier_extraction)
                if dossier_extrait:
                    print(f"\n💡 Données prêtes à utiliser dans: {dossier_extrait}")
            else:
                print("⚠️  Le fichier n'est pas un ZIP - pas d'extraction possible")
        else:
            print(f"❌ Fichier non trouvé dans les emplacements suivants:")
            for chemin in chemins_possibles:
                print(f"   • {os.path.abspath(chemin)}")
            print("💡 Suggestions:")
            print("1. Lancez d'abord avec main(telech=True, extract=False)")
            print("2. Vérifiez que le nom_fichier et folder sont corrects")

    else:
        print("🤷 Aucune action demandée (telech=False, extract=False)")

    # Afficher la structure finale du dataset sous forme d'arbre
    afficher_arbre_dataset(folder.rstrip("/"))


if __name__ == "__main__":
    main(1, 1)
