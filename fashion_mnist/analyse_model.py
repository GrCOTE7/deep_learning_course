import tensorflow as tf
import matplotlib.pyplot as plt
import pickle
import pandas as pd


def display_best_scores(history):
    """Affiche les meilleurs scores d'accuracy et de validation accuracy avec les époques"""

    best_accuracy = max(history["accuracy"])
    best_val_accuracy = max(history["val_accuracy"])

    best_accuracy_epoch = history["accuracy"].index(best_accuracy) + 1
    best_val_accuracy_epoch = history["val_accuracy"].index(best_val_accuracy) + 1

    print("=" * 60)
    print("🏆 MEILLEURS SCORES D'ENTRAÎNEMENT")
    print("=" * 60)
    print(
        f"📈 Meilleure Accuracy:     {best_accuracy:.4f} (Époque {best_accuracy_epoch})"
    )
    print(
        f"✅ Meilleure Val_Accuracy: {best_val_accuracy:.4f} (Époque {best_val_accuracy_epoch})"
    )

    # Analyse du surapprentissage
    gap = (best_accuracy - best_val_accuracy) * 100
    print("-" * 60)
    print(f"🔍 ÉCART (Overfitting): {gap:.2f}%")

    if gap < 3:
        print("✅ Excellent! Pas de surapprentissage significatif")
    elif gap < 7:
        print("⚠️  Surapprentissage modéré - acceptable")
    else:
        print("❌ Surapprentissage important - besoin de régularisation")

    print(f"🎯 Score de production attendu: ~{best_val_accuracy:.2%}")
    print("=" * 60)
    print()


def plot_learning_curves(history):
    """Affiche les courbes d'apprentissage (accuracy et loss)"""

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # Graphique 1: Accuracy
    epochs = range(1, len(history["accuracy"]) + 1)

    ax1.plot(epochs, history["accuracy"], "bo-", label="Training Accuracy", linewidth=2)
    ax1.plot(
        epochs, history["val_accuracy"], "ro-", label="Validation Accuracy", linewidth=2
    )
    ax1.set_title("Courbes d'Accuracy", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Époques")
    ax1.set_ylabel("Accuracy")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Graphique 2: Loss
    ax2.plot(epochs, history["loss"], "bo-", label="Training Loss", linewidth=2)
    ax2.plot(epochs, history["val_loss"], "ro-", label="Validation Loss", linewidth=2)
    ax2.set_title("Courbes de Loss", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Époques")
    ax2.set_ylabel("Loss")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def bilan_model(model_name):

    print("🔄 Chargement du modèle et de l'historique...")
    print()

    # Charger le modèle
    model = tf.keras.models.load_model(f"{model_name}/best_model_{model_name}.keras")

    # Charger l'historique d'entraînement
    with open(f"{model_name}/training_history_{model_name}.pkl", "rb") as f:
        training_data = pickle.load(f)

    # Gérer l'ancien et le nouveau format
    if isinstance(training_data, dict) and "history" in training_data:
        # Nouveau format avec métadonnées
        history = training_data["history"]
        execution_time = training_data.get("execution_time", None)
        config = training_data.get("training_config", {})
    else:
        # Ancien format (juste l'historique)
        history = training_data
        execution_time = None
        config = {}

    # Afficher les infos d'entraînement si disponibles
    if execution_time or config:
        print("⏱️  INFORMATIONS D'ENTRAÎNEMENT")
        print("=" * 60)
        if execution_time:
            hours = int(execution_time // 3600)
            minutes = int((execution_time % 3600) // 60)
            seconds = execution_time % 60
            print(f"🕒 Temps d'exécution: {hours:02d}:{minutes:02d}:{seconds:05.2f}")

        if config:
            if "epochs_planned" in config:
                print(f"📈 Époques planifiées: {config['epochs_planned']}")
            if "epochs_executed" in config:
                print(f"✅ Époques exécutées: {config['epochs_executed']}")
            if "patience" in config:
                print(f"⏳ Patience Early Stopping: {config['patience']}")
        print()

    # Afficher le bilan détaillé avec pandas
    print("📊 BILAN DÉTAILLÉ DE L'ENTRAÎNEMENT")
    print("=" * 60)
    history_df = pd.DataFrame(history)
    print(history_df.round(4))  # Arrondir à 4 décimales pour une meilleure lisibilité
    print()

    # Afficher le résumé du modèle
    print("📋 RÉSUMÉ DU MODÈLE")
    print("=" * 60)
    model.summary()
    print()

    # Afficher les meilleurs scores
    display_best_scores(history)

    # Afficher les courbes d'apprentissage
    print("📊 Affichage des courbes d'apprentissage...")
    plot_learning_curves(history)


if __name__ == "__main__":
    model_name = "fashion_mnist"
    bilan_model(model_name)
