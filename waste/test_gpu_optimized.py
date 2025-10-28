#!/usr/bin/env python3
"""
Script de test CNN optimisé pour GPU avec diagnostic complet
"""
import os
import time
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# ============================================================================
# CONFIGURATION GPU AGGRESSIVE 🔥
# ============================================================================


def configure_gpu():
    """Configuration GPU maximale pour TensorFlow"""
    print("🔧 Configuration GPU...")

    # Forcer l'utilisation de tous les threads disponibles
    tf.config.threading.set_intra_op_parallelism_threads(0)  # 0 = tous les cœurs
    tf.config.threading.set_inter_op_parallelism_threads(0)  # 0 = optimal automatique

    # Activer le mixed precision pour plus de performance
    try:
        policy = tf.keras.mixed_precision.Policy("mixed_float16")
        tf.keras.mixed_precision.set_global_policy(policy)
        print("✅ Mixed precision activé (float16)")
    except Exception as e:
        print(f"⚠️  Mixed precision non activé: {e}")

    # Configuration mémoire GPU (si disponible)
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"✅ {len(gpus)} GPU(s) configuré(s) avec croissance mémoire")
        except RuntimeError as e:
            print(f"❌ Erreur configuration GPU: {e}")
    else:
        print("⚠️  Aucun GPU détecté - Utilisation CPU")

    return gpus


def diagnostic_gpu():
    """Diagnostic complet du GPU"""
    print("\n🔍 DIAGNOSTIC GPU/CPU:")
    print(f"  • TensorFlow version: {tf.__version__}")
    print(f"  • GPU disponibles: {len(tf.config.list_physical_devices('GPU'))}")
    print(f"  • CPU logiques: {tf.config.threading.get_intra_op_parallelism_threads()}")
    print(
        f"  • Threads inter-op: {tf.config.threading.get_inter_op_parallelism_threads()}"
    )

    # Test de calcul pour vérifier l'activité
    with tf.device(
        "/CPU:0" if not tf.config.list_physical_devices("GPU") else "/GPU:0"
    ):
        start = time.time()
        a = tf.random.normal([1000, 1000])
        b = tf.random.normal([1000, 1000])
        c = tf.matmul(a, b)
        device_time = time.time() - start
        device_name = "GPU" if tf.config.list_physical_devices("GPU") else "CPU"
        print(
            f"  • Test {device_name}: {device_time:.3f}s pour multiplication 1000x1000"
        )


# ============================================================================
# CONFIGURATION MODÈLE
# ============================================================================

model_name = "waste"

# Configuration GPU
gpus = configure_gpu()
diagnostic_gpu()

# Define data directories
data_dir = "D:/dl/datasets/WASTE/"
train_dir = os.path.join(data_dir, "TRAIN")
test_dir = os.path.join(data_dir, "TEST")

# Vérification des répertoires
if not os.path.exists(train_dir) or not os.path.exists(test_dir):
    print(f"❌ Erreur: Répertoires manquants!")
    print(f"   Recherché: {train_dir}")
    print(f"   Recherché: {test_dir}")
    exit(1)

print(f"✅ Données trouvées dans: {data_dir}")

# ============================================================================
# PIPELINE DE DONNÉES TF.DATA OPTIMISÉ
# ============================================================================

batch_size = 16  # Réduit de 64 à 16 pour éviter les erreurs de mémoire GPU
img_height = 224
img_width = 224

# Création des datasets
train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    labels='inferred',
    label_mode='binary',
    image_size=(img_height, img_width),
    batch_size=batch_size)

val_ds = tf.keras.utils.image_dataset_from_directory(
    test_dir,
    labels='inferred',
    label_mode='binary',
    image_size=(img_height, img_width),
    batch_size=batch_size)

class_names = train_ds.class_names
print(f"📂 Classes trouvées: {class_names}")

# Création d'une couche pour l'augmentation des données
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.2),
    tf.keras.layers.RandomZoom(0.2),
])

# Normalisation et prefetching
AUTOTUNE = tf.data.AUTOTUNE

def prepare(ds, shuffle=False, augment=False):
    # Redimensionnement et normalisation
    rescale = tf.keras.layers.Rescaling(1./255)
    ds = ds.map(lambda x, y: (rescale(x), y), num_parallel_calls=AUTOTUNE)

    if shuffle:
        ds = ds.shuffle(1000)

    # Augmentation des données
    if augment:
        ds = ds.map(lambda x, y: (data_augmentation(x, training=True), y), num_parallel_calls=AUTOTUNE)

    # Utiliser le prefetch pour de meilleures performances
    return ds.cache().prefetch(buffer_size=AUTOTUNE)

train_ds = prepare(train_ds, shuffle=True, augment=True)
val_ds = prepare(val_ds)

print(f"📊 Batch size: {batch_size}")

# ============================================================================
# MODÈLE CNN OPTIMISÉ
# ============================================================================


def create_optimized_model():
    """Crée un modèle CNN optimisé pour GPU"""
    model = tf.keras.models.Sequential(
        [
            # Extraction de caractéristiques - Plus de filtres
            tf.keras.layers.Conv2D(
                filters=64,  # Plus de filtres
                kernel_size=(3, 3),
                padding="same",
                activation="relu",
                input_shape=(224, 224, 3),
            ),
            tf.keras.layers.BatchNormalization(),  # Normalisation batch
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation="relu"),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(filters=256, kernel_size=(3, 3), activation="relu"),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(filters=256, kernel_size=(3, 3), activation="relu"),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D(2, 2),
            # Classification
            tf.keras.layers.GlobalAveragePooling2D(),  # Plus efficace que Flatten
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(units=128, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(
                units=1, activation="sigmoid", dtype="float32"
            ),  # Force float32 pour la sortie
        ]
    )

    return model


# Création du modèle
model = create_optimized_model()

# Compilation avec optimiseur plus moderne
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)

print("🏗️  Modèle créé:")
model.summary()

# ============================================================================
# CALLBACKS OPTIMISÉS
# ============================================================================

callbacks = [
    tf.keras.callbacks.ModelCheckpoint(
        filepath="best_model_gpu.h5",
        monitor="val_accuracy",
        mode="max",
        save_best_only=True,
        verbose=1,
    ),
    tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=5, restore_best_weights=True, verbose=1
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=3, min_lr=1e-7, verbose=1
    ),
]

# ============================================================================
# ENTRAÎNEMENT
# ============================================================================

print("\n🚀 DÉMARRAGE ENTRAÎNEMENT:")
print("   ⚠️  SURVEILLEZ LE GESTIONNAIRE DE TÂCHES!")
print("   📊 CPU/GPU usage devrait être élevé")

start_time = time.time()

# Entraînement avec plus d'epochs pour voir l'activité
history = model.fit(
    train_ds,
    epochs=1,  # Plus d'epochs pour observer
    validation_data=val_ds,
    callbacks=callbacks,
    verbose=1,
)

training_time = time.time() - start_time

print(f"\n✅ Entraînement terminé en {training_time:.2f}s")

# ============================================================================
# ÉVALUATION
# ============================================================================

print("\n📊 ÉVALUATION FINALE:")
loss, accuracy = model.evaluate(val_ds, verbose=1)
print(f"   • Loss: {loss:.4f}")
print(f"   • Accuracy: {accuracy:.4f}")

# Affichage de l'historique
import pandas as pd

history_df = pd.DataFrame(history.history)
print("\n📈 Historique d'entraînement:")
print(history_df)

print("\n🔍 VÉRIFIEZ MAINTENANT LE GESTIONNAIRE DE TÂCHES!")
print("   • Processus Python doit avoir utilisé beaucoup de ressources")
print("   • Si GPU: 'nvidia-smi' doit montrer de l'activité")
