## 🔑 Guide pour résoudre l'erreur "App en cours de test"

### 🎯 **Problème :**
Google affiche : _"Cette app est en cours de test et seuls les testeurs approuvés y ont accès"_

### ✅ **Solution 1 : Continuer malgré l'avertissement (Rapide)**

1. **Dans le navigateur**, quand l'erreur apparaît :
   - Cliquez sur **"Paramètres avancés"** (en bas à gauche)
   - Cliquez sur **"Accéder à get-drive (non sécurisé)"**
   - ⚠️ C'est normal et sécurisé pour votre propre app !

### 🔧 **Solution 2 : Ajouter votre email comme testeur (Recommandé)**

1. **Allez sur [Google Cloud Console](https://console.cloud.google.com/)**
2. **Sélectionnez votre projet**
3. **Menu ☰ → APIs & Services → OAuth consent screen**
4. **Section "Test users"** :
   - Cliquez **"+ ADD USERS"**
   - Ajoutez votre adresse email
   - Cliquez **"SAVE"**

### 🚀 **Solution 3 : Publier l'app (Pour usage intensif)**

Si vous voulez éviter complètement cette étape :

1. **Dans OAuth consent screen**
2. **Cliquez "PUBLISH APP"**
3. **Soumettez pour vérification** (peut prendre quelques jours)

### 📋 **Configuration complète étape par étape :**

#### **Étape 1 : Créer le projet Google Cloud**
```
1. Allez sur https://console.cloud.google.com/
2. Cliquez "Select a project" → "NEW PROJECT"
3. Nom : "Mon Drive Downloader"
4. Cliquez "CREATE"
```

#### **Étape 2 : Activer l'API Google Drive**
```
1. Menu ☰ → APIs & Services → Library
2. Recherchez "Google Drive API"
3. Cliquez dessus → "ENABLE"
```

#### **Étape 3 : Configurer OAuth Consent Screen**
```
1. Menu ☰ → APIs & Services → OAuth consent screen
2. Choisissez "External" → "CREATE"
3. Remplissez :
   - App name: "Mon Drive Downloader"
   - User support email: votre email
   - Developer contact: votre email
4. Cliquez "SAVE AND CONTINUE"
5. Scopes → "SAVE AND CONTINUE"
6. Test users → "ADD USERS" → votre email → "SAVE AND CONTINUE"
7. Summary → "BACK TO DASHBOARD"
```

#### **Étape 4 : Créer les credentials**
```
1. Menu ☰ → APIs & Services → Credentials
2. "CREATE CREDENTIALS" → "OAuth 2.0 Client IDs"
3. Application type: "Desktop application"
4. Name: "Drive Downloader Client"
5. "CREATE"
6. Téléchargez le JSON
7. Renommez-le "credentials.json"
8. Placez-le dans le dossier d:\dl\
```

### 🔄 **Test rapide :**

```python
# Dans d:\dl\, lancez :
python get_drive_file.py
```

### 💡 **Conseils :**

- ✅ **L'avertissement est normal** pour les apps en développement
- ✅ **Votre app est sécurisée** - c'est juste Google qui vérifie
- ✅ **"Non sécurisé" = non vérifié**, pas dangereux
- ✅ **Une fois configuré**, plus besoin de refaire ces étapes

### 🆘 **Si ça ne marche toujours pas :**

1. **Vérifiez que votre email est dans "Test users"**
2. **Essayez en navigation privée**
3. **Attendez 5-10 minutes** après avoir ajouté l'email
4. **Supprimez le fichier `token.pickle`** et réessayez

---

🎉 **Une fois configuré, vous pourrez télécharger vos fichiers Google Drive directement en Python !**
