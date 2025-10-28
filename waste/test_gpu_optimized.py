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
data_dir = f"../datasets/{model_name.upper()}/"
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
# GÉNÉRATEURS DE DONNÉES OPTIMISÉS
# ============================================================================

# Générateurs avec prefetch et cache pour optimiser le pipeline
train_data_generator = ImageDataGenerator(
    rescale=1.0 / 255,
    rotation_range=20,  # Augmentation des données
    width_shift_range=0.1,
    height_shift_range=0.1,
    horizontal_flip=True,
)

test_data_generator = ImageDataGenerator(rescale=1.0 / 255)

# Batch size plus important si GPU disponible
batch_size = 64 if gpus else 32

train_generator = train_data_generator.flow_from_directory(
    directory=train_dir,
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode="binary",
)

test_generator = test_data_generator.flow_from_directory(
    directory=test_dir,
    target_size=(224, 224),
    batch_size=batch_size,
    class_mode="binary",
)

print(f"📊 Batch size: {batch_size}")
print(f"📂 Classes trouvées: {train_generator.class_indices}")

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
    optimizer=tf.keras.optimizers.AdamW(learning_rate=0.001, weight_decay=0.01),
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
    train_generator,
    epochs=10,  # Plus d'epochs pour observer
    validation_data=test_generator,
    callbacks=callbacks,
    verbose=1,
)

training_time = time.time() - start_time

print(f"\n✅ Entraînement terminé en {training_time:.2f}s")

# ============================================================================
# ÉVALUATION
# ============================================================================

print("\n📊 ÉVALUATION FINALE:")
loss, accuracy = model.evaluate(test_generator, verbose=1)
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
