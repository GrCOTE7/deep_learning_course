"""
Explorateur du dataset téléchargé
Analyse la structure et les statistiques du dataset
"""

import os
from collections import Counter

def explorer_dataset(chemin_base="./datasets/extracted/DATASET"):
    """Explore et analyse le dataset"""
    
    print("🔍 EXPLORATION DU DATASET")
    print("=" * 30)
    
    if not os.path.exists(chemin_base):
        print(f"❌ Dossier non trouvé: {chemin_base}")
        return
    
    # Explorer TRAIN
    train_path = os.path.join(chemin_base, "TRAIN")
    test_path = os.path.join(chemin_base, "TEST")
    
    for split, path in [("TRAIN", train_path), ("TEST", test_path)]:
        if os.path.exists(path):
            print(f"\n📁 {split}:")
            
            for classe in os.listdir(path):
                classe_path = os.path.join(path, classe)
                if os.path.isdir(classe_path):
                    nb_fichiers = len([f for f in os.listdir(classe_path) 
                                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))])
                    print(f"  📊 Classe {classe}: {nb_fichiers} images")
    
    # Statistiques globales
    print(f"\n📈 STATISTIQUES:")
    
    total_train = 0
    total_test = 0
    
    if os.path.exists(train_path):
        for classe in os.listdir(train_path):
            classe_path = os.path.join(train_path, classe)
            if os.path.isdir(classe_path):
                total_train += len([f for f in os.listdir(classe_path) 
                                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))])
    
    if os.path.exists(test_path):
        for classe in os.listdir(test_path):
            classe_path = os.path.join(test_path, classe)
            if os.path.isdir(classe_path):
                total_test += len([f for f in os.listdir(classe_path) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))])
    
    print(f"  🎯 Total TRAIN: {total_train} images")
    print(f"  🎯 Total TEST: {total_test} images")
    print(f"  🎯 TOTAL: {total_train + total_test} images")
    
    # Code pour utiliser le dataset
    print(f"\n🐍 CODE POUR CHARGER LE DATASET:")
    print(f"import os")
    print(f"from tensorflow.keras.preprocessing.image import ImageDataGenerator")
    print(f"")
    print(f"# Générateurs de données")
    print(f"train_datagen = ImageDataGenerator(rescale=1./255)")
    print(f"test_datagen = ImageDataGenerator(rescale=1./255)")
    print(f"")
    print(f"# Charger les données")
    print(f"train_generator = train_datagen.flow_from_directory(")
    print(f"    './datasets/extracted/DATASET/TRAIN',")
    print(f"    target_size=(224, 224),")
    print(f"    batch_size=32,")
    print(f"    class_mode='categorical')")
    print(f"")
    print(f"test_generator = test_datagen.flow_from_directory(")
    print(f"    './datasets/extracted/DATASET/TEST',")
    print(f"    target_size=(224, 224),")
    print(f"    batch_size=32,")
    print(f"    class_mode='categorical')")

if __name__ == "__main__":
    explorer_dataset()