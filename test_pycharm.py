import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD
import time

model_name = "fashion_mnist"

# Forcer l'utilisation de tous les threads (Donc du GPU)
# tf.config.threading.set_intra_op_parallelism_threads(0)  # 0 = tous les cœurs
# tf.config.threading.set_inter_op_parallelism_threads(0)  # 0 = optimal automatique

# Démarrer le chronomètre
start_time = time.time()
print("🚀 Début de l'entraînement...")

data = tf.keras.datasets.fashion_mnist
(training_images, training_labels), (test_images, test_labels) = data.load_data()


training_images = training_images / 255.0
test_images = test_images / 255.0


training_labels = tf.keras.utils.to_categorical(training_labels)
test_labels = tf.keras.utils.to_categorical(test_labels)

training_images = training_images.reshape((60000, 28, 28, 1))
test_images = test_images.reshape((10000, 28, 28, 1))

model = Sequential(
    [
        # Extraction de caractéristiques
        tf.keras.layers.Conv2D(
            filters=64,
            kernel_size=(3, 3),
            padding="same",
            activation="relu",
            input_shape=(28, 28, 1),
        ),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(2, 2),
        # applatir
        tf.keras.layers.Flatten(),
        # Dense
        tf.keras.layers.Dense(units=128, activation="relu"),
        tf.keras.layers.Dense(units=10, activation="softmax"),
    ]
)

model_ckp = tf.keras.callbacks.ModelCheckpoint(
    filepath=f"best_model_{model_name}.keras",
    monitor="val_accuracy",
    mode="max",
    save_best_only=True,
)
stop = tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=7)


model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])


h = model.fit(
    training_images,
    training_labels,
    epochs=2,
    validation_data=(test_images, test_labels),
    callbacks=[model_ckp, stop],
)

import pickle

with open(f"training_history_{model_name}.pkl", "wb") as f:
    pickle.dump(h.history, f)

# Calculer et afficher le temps d'exécution
end_time = time.time()
execution_time = end_time - start_time

# You can optionally save the training history or evaluate the model further here
# For example:
import pandas as pd

history_df = pd.DataFrame(h.history)
print("\nTraining History:")
print(history_df)

# Evaluate the model after training
print("Résultat final:")
loss, accuracy = model.evaluate(test_images, test_labels)
print(f"\nTest Loss: {loss:.4f}")
print(f"Test Accuracy: {accuracy:.4f}")

# Convertir en format HH:MM:SS.ms
hours = int(execution_time // 3600)
minutes = int((execution_time % 3600) // 60)
seconds = execution_time % 60

print("=" * 50)
print("⏱️  TEMPS D'EXÉCUTION")
print("=" * 50)
print(f"Temps total: {hours:02d}:{minutes:02d}:{seconds:05.2f}")
print("=" * 50)
