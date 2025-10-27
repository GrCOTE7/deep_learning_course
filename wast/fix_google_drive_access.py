"""
Script pour configurer automatiquement l'accès Google Drive
et résoudre l'erreur 403: access_denied
"""

import webbrowser
import os


def ouvrir_configuration_google():
    """Ouvre les pages nécessaires pour configurer l'accès"""

    print("🔧 RÉSOLUTION DE L'ERREUR 403: access_denied")
    print("=" * 50)
    print()

    print("📋 ÉTAPES À SUIVRE :")
    print()

    print("1️⃣  AJOUTER VOTRE EMAIL COMME TESTEUR")
    print("   → Je vais ouvrir Google Cloud Console")
    print("   → Allez dans 'OAuth consent screen'")
    print("   → Section 'Test users' → 'ADD USERS'")
    print("   → Ajoutez votre adresse email")
    print("   → Cliquez 'SAVE'")
    print()

    input("⏵ Appuyez sur Entrée pour ouvrir Google Cloud Console...")
    webbrowser.open("https://console.cloud.google.com/apis/credentials/consent")

    print()
    print("2️⃣  ALTERNATIVE : CONTOURNER L'AVERTISSEMENT")
    print("   → Lors de l'authentification, si vous voyez l'erreur :")
    print("   → Cliquez 'Paramètres avancés' (en bas)")
    print("   → Cliquez 'Accéder à [app] (non sécurisé)'")
    print("   → ✅ C'est sécurisé car c'est VOTRE app !")
    print()

    print("3️⃣  VÉRIFIER LA CONFIGURATION")
    print("   → Assurez-vous d'avoir le bon projet sélectionné")
    print("   → Vérifiez que l'API Google Drive est activée")
    print()

    response = input("💾 Avez-vous ajouté votre email comme testeur ? (o/n): ")

    if response.lower() == "o":
        print(
            "✅ Parfait ! Maintenant supprimons le token pour forcer une nouvelle authentification..."
        )

        if os.path.exists("token.pickle"):
            os.remove("token.pickle")
            print("🗑️  Token supprimé - nouvelle authentification requise")

        print()
        print("🚀 PROCHAINES ÉTAPES :")
        print("   1. Relancez votre script Python")
        print("   2. Lors de l'authentification, vous devriez pouvoir continuer")
        print("   3. Si l'erreur persiste, utilisez l'option 'Paramètres avancés'")

    else:
        print()
        print("📝 GUIDE DÉTAILLÉ :")
        print("   1. Dans Google Cloud Console (qui vient de s'ouvrir)")
        print("   2. Sélectionnez votre projet en haut")
        print("   3. Menu ☰ → APIs & Services → OAuth consent screen")
        print("   4. Scrollez jusqu'à 'Test users'")
        print("   5. Cliquez '+ ADD USERS'")
        print("   6. Entrez votre adresse email")
        print("   7. Cliquez 'SAVE'")
        print()
        print("   Puis relancez ce script !")


def verifier_configuration():
    """Vérifie si les fichiers nécessaires sont présents"""

    print("🔍 VÉRIFICATION DE LA CONFIGURATION")
    print("=" * 40)

    # Vérifier credentials.json
    if os.path.exists("credentials.json"):
        print("✅ credentials.json trouvé")
    else:
        print("❌ credentials.json manquant")
        print("   → Téléchargez-le depuis Google Cloud Console")
        print("   → APIs & Services → Credentials → CREATE CREDENTIALS")
        return False

    # Vérifier token.pickle
    if os.path.exists("token.pickle"):
        print("⚠️  token.pickle existe (peut être corrompu)")
        response = input("🗑️  Supprimer pour forcer nouvelle authentification ? (o/n): ")
        if response.lower() == "o":
            os.remove("token.pickle")
            print("✅ Token supprimé")
    else:
        print("✅ Pas de token existant (normal pour première utilisation)")

    return True


def main():
    """Fonction principale"""
    print("🛠️  ASSISTANT DE CONFIGURATION GOOGLE DRIVE")
    print("=" * 50)
    print()

    print("Vous avez l'erreur : 'access_denied' ?")
    print("Ce script va vous aider à la résoudre !")
    print()

    if not verifier_configuration():
        print("❌ Configuration incomplète - résolvez d'abord les fichiers manquants")
        return

    print()
    ouvrir_configuration_google()

    print()
    print("🎉 CONFIGURATION TERMINÉE !")
    print("   Relancez maintenant votre script de téléchargement")


if __name__ == "__main__":
    main()
