import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import SGD
from libs.chrono import chrono
import pickle

model_name = "fashion_mnist"
# Forcer l'utilisation de tous les threads (Donc aussi le GPU)
# tf.config.threading.set_intra_op_parallelism_threads(0)  # 0 = tous les cœurs
# tf.config.threading.set_inter_op_parallelism_threads(0)  # 0 = optimal automatique


def train_model():

    # Démarrer le chronomètre
    chrono.start()

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
            # Couche d'entrée explicite (recommandé)
            tf.keras.layers.Input(shape=(28, 28, 1)),
            # Extraction de caractéristiques
            tf.keras.layers.Conv2D(
                filters=64,
                kernel_size=(3, 3),
                padding="same",
                activation="relu",
            ),
            tf.keras.layers.MaxPooling2D(2, 2),
            tf.keras.layers.Conv2D(
                filters=64,
                kernel_size=(3, 3),
                activation="relu",
            ),
            tf.keras.layers.MaxPooling2D(2, 2),
            # applatir
            tf.keras.layers.Flatten(),
            # Dense
            tf.keras.layers.Dense(units=128, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(units=10, activation="softmax"),
        ]
    )

    model_ckp = tf.keras.callbacks.ModelCheckpoint(
        filepath=f"{model_name}/best_model_{model_name}.keras",
        monitor="val_accuracy",
        mode="max",
        save_best_only=True,
    )
    stop = tf.keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=7)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.001
        ),  # Optionnel: LR explicite !
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    h = model.fit(
        training_images,
        training_labels,
        epochs=999,
        validation_data=(test_images, test_labels),
        callbacks=[model_ckp, stop],
    )

    # Obtenir le temps d'exécution
    execution_time = chrono.elapsed()

    # Nouveau format avec métadonnées
    training_data = {
        "history": h.history,
        "execution_time": execution_time,
        "training_config": {
            "epochs_planned": 999,
            "epochs_executed": len(h.history["accuracy"]),
            "patience": 7,
            "model_name": model_name,
        },
    }

    with open(f"{model_name}/training_history_{model_name}.pkl", "wb") as f:
        pickle.dump(training_data, f)

    print("✅ Entraînement terminé et sauvegardé !")

    import pandas as pd

    history_df = pd.DataFrame(h.history)
    print("\nTraining History:")
    print(history_df)

    # Evaluate the model after training
    print("Résultat final:")
    val_loss, val_accuracy = model.evaluate(test_images, test_labels)
    print(f"\nTest Loss: {val_loss:.4f}")
    print(f"Test Accuracy: {val_accuracy:.4f}")

    return training_images, training_labels, training_data


def diapos(training_images, training_labels):
    import matplotlib.pyplot as plt

    labels = [
        "t-shirt/haut",
        "pantalon",
        "pull",
        "robe",
        "manteau",
        "sandales",
        "chemise",
        "baskets",
        "sac",
        "bottines",
    ]

    # Choisir training ou test images en activant LA ligne ad'hoc
    img_ids = training_images

    # Récupérer les labels originaux (avant to_categorical)
    data = tf.keras.datasets.fashion_mnist
    (_, original_training_labels), (_, original_test_labels) = data.load_data()

    # Utiliser les labels originaux (entiers, pas one-hot)
    img_labels = original_training_labels

    # Si vous voulez les images de test, décommentez cette ligne :
    # img_labels = original_test_labels

    # Calculate the number of rows and columns for the subplot grid
    n_images = 20
    n_cols = 10  # You can adjust the number of columns
    n_rows = (n_images + n_cols - 1) // n_cols

    plt.figure(
        figsize=(n_cols * 1.5, n_rows * 1.5)
    )  # Adjust figure size as needed to accommodate xlabel

    print("Images " + ("d'entrainement" if len(img_labels) == 60000 else "de test"))

    for i in range(n_images):
        plt.subplot(n_rows, n_cols, i + 1)  # Create a subplot for each image
        plt.imshow(img_ids[i], cmap="gray")

        # Maintenant img_labels[i] est un entier simple
        plt.xlabel(
            str(i) + " - " + labels[img_labels[i]].capitalize()
        )  # Use xlabel for title below the image
        plt.xticks([])  # Remove x ticks
        plt.yticks([])  # Remove y ticks
        plt.axis("on")  # Turn axis on to show xlabel

    plt.tight_layout()  # Adjust layout to prevent labels overlapping
    plt.show()


def lr_graph(h):
    """Graph du Learning Curve"""

    import matplotlib.pyplot as plt
    import pandas as pd  # Make sure pandas is imported

    # Assuming results_df is already created and populated in a previous cell

    if "h" in locals() and not h.empty:
        print("\n--- Visualisation des Résultats ---")

        # Plotting Best Validation Accuracy
        plt.figure(figsize=(10, 5))
        plt.plot(
            h.index,
            h["val_accuracy"],
            marker="o",
            linestyle="-",
            color="b",
        )
        plt.title("Learning Curve")
        plt.xlabel("Epochs")
        plt.ylabel("Val Accuracy")
        plt.xticks(h.index)  # Set x-ticks to patience values
        plt.grid(True)
        plt.tight_layout()
        plt.show()


def afficher_meilleur_resultat(training_data):
    """Affiche le meilleur val_accuracy et l'époque correspondante"""

    import pandas as pd

    h = training_data["history"]
    config = training_data["training_config"]
    execution_time = training_data["execution_time"]

    # Convertir en DataFrame pour faciliter l'analyse
    df = pd.DataFrame(h)

    # Trouver le meilleur val_accuracy
    best_val_acc = df["val_accuracy"].max()
    best_epoch = df["val_accuracy"].idxmax() + 1  # +1 car les époques commencent à 1

    # Obtenir les autres métriques de cette époque
    best_epoch_data = df.iloc[df["val_accuracy"].idxmax()]

    print("\n" + "=" * 60)
    print("🏆 MEILLEUR RÉSULTAT D'ENTRAÎNEMENT")
    print("=" * 60)
    print(f"📈 Meilleur Val Accuracy: {best_val_acc:.4f} ({best_val_acc*100:.2f}%)")
    print(f"🎯 Époque correspondante: {best_epoch}/{config['epochs_executed']}")
    print(f"📉 Val Loss à cette époque: {best_epoch_data['val_loss']:.4f}")
    print(
        f"📊 Train Accuracy à cette époque: {best_epoch_data['accuracy']:.4f} ({best_epoch_data['accuracy']*100:.2f}%)"
    )
    print(f"📉 Train Loss à cette époque: {best_epoch_data['loss']:.4f}")

    # Utiliser la fonction de formatage de chrono
    formatted_time = chrono.format_time(execution_time)

    print(f"⏱️  Temps d'exécution total: {formatted_time}")
    print(f"📝 Modèle: {config['model_name']}")  # Vérifier s'il y a eu overfitting
    train_acc = best_epoch_data["accuracy"]
    val_acc = best_val_acc
    overfit_diff = train_acc - val_acc

    print(f"\n🔍 ANALYSE:")
    if overfit_diff > 0.05:  # Plus de 5% de différence
        print(
            f"⚠️  Possible overfitting: différence train-val = {overfit_diff:.4f} ({overfit_diff*100:.2f}%)"
        )
    elif overfit_diff < -0.02:  # Val meilleur que train (rare mais possible)
        print(
            f"✨ Excellent! Val accuracy > Train accuracy (différence: {abs(overfit_diff):.4f})"
        )
    else:
        print(f"✅ Bon équilibre train-val (différence: {overfit_diff:.4f})")

    # Progression
    if config["epochs_executed"] > 1:
        improvement = df["val_accuracy"].iloc[-1] - df["val_accuracy"].iloc[0]
        print(f"📈 Amélioration totale: {improvement:.4f} ({improvement*100:.2f}%)")

    print("=" * 60)

    return {
        "best_val_accuracy": best_val_acc,
        "best_epoch": best_epoch,
        "total_epochs": config["epochs_executed"],
        "execution_time": execution_time,
    }


if __name__ == "__main__":

    import pandas as pd

    training_images, training_labels, training_data = train_model()
    diapos(training_images, training_labels)

    # Utiliser l'historique depuis training_data
    h = training_data["history"]

    # Charger l'historique sauvegardé (alternative)
    # with open(f"{model_name}/training_history_{model_name}.pkl", "rb") as f:
    #     loaded_data = pickle.load(f)
    #     h = loaded_data["history"]

    lr_graph(pd.DataFrame(h))

    # Afficher le meilleur résultat
    best_results = afficher_meilleur_resultat(training_data)
