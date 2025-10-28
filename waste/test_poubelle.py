import os
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.preprocessing.image import ImageDataGenerator

model_name = "waste"

# Forcer l'utilisation de tous les threads (Donc du GPU)
tf.config.threading.set_intra_op_parallelism_threads(0)  # 0 = tous les cœurs
tf.config.threading.set_inter_op_parallelism_threads(0)  # 0 = optimal automatique

# Define data directories (adjust paths if needed)
data_dir = f"./datasets/{model_name.upper()}/"  # Dataset is in parent directory
train_dir = os.path.join(data_dir, "TRAIN")
test_dir = os.path.join(data_dir, "TEST")

# Check if data directories exist (important for local execution)
if not os.path.exists(train_dir) or not os.path.exists(test_dir):
    print(
        f"Error: ../datasets/{model_name.upper()}/TRAIN or ../datasets/{model_name.upper()}/TEST directories not found."
    )
    print("Please make sure the DATASET folder is in the same directory as your script")
    print("or update the 'data_dir' variable with the correct path.")
    exit()  # Exit the script if directories are not found

# ImageDataGenerator for data loading and preprocessing
train_data_generator = ImageDataGenerator(rescale=1.0 / 255)
test_data_generator = ImageDataGenerator(rescale=1.0 / 255)

train_generator = train_data_generator.flow_from_directory(
    directory=train_dir, target_size=(224, 224), batch_size=32, class_mode="binary"
)

test_generator = test_data_generator.flow_from_directory(
    directory=test_dir, target_size=(224, 224), batch_size=32, class_mode="binary"
)

# Define the model
model = tf.keras.models.Sequential(
    [
        # Extraction de caractéristiques
        tf.keras.layers.Conv2D(
            filters=32,
            kernel_size=(3, 3),
            padding="same",
            activation="relu",
            input_shape=(224, 224, 3),
        ),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Conv2D(filters=64, kernel_size=(3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(2, 2),
        tf.keras.layers.Conv2D(filters=128, kernel_size=(3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(2, 2),
        # applatir
        tf.keras.layers.Flatten(),
        # Dense
        tf.keras.layers.Dense(units=128, activation="relu"),
        tf.keras.layers.Dense(units=1, activation="sigmoid"),
    ]
)

# Compile the model
model.compile(
    optimizer=tf.keras.optimizers.RMSprop(learning_rate=0.001),
    loss="binary_crossentropy",
    metrics=["accuracy"],
)

# Model Checkpoint and Early Stopping Callbacks
model_ckp = tf.keras.callbacks.ModelCheckpoint(
    filepath="best_model.h5", monitor="val_accuracy", mode="max", save_best_only=True
)
stop = tf.keras.callbacks.EarlyStopping(
    monitor="val_accuracy", patience=7, restore_best_weights=True
)

# Train the model
print("\nStarting model training...")
h = model.fit(
    train_generator,
    epochs=2,
    validation_data=test_generator,
    callbacks=[model_ckp, stop],
)

print("\nTraining finished.")

# You can optionally save the training history or evaluate the model further here
# For example:
import pandas as pd

history_df = pd.DataFrame(h.history)
print("\nTraining History:")
print(history_df)

# Evaluate the model after training
loss, accuracy = model.evaluate(test_generator)
print(f"\nTest Loss: {loss:.4f}")
print(f"Test Accuracy: {accuracy:.4f}")
