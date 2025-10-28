import os
import time
import tensorflow as tf
import matplotlib.pyplot as plt


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


configure_gpu()
diagnostic_gpu()
