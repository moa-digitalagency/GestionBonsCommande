# BTP Commande - Guide Utilisateur

Bienvenue sur **BTP Commande**, votre outil de gestion des achats pour le BTP. Ce guide vous explique comment utiliser efficacement la plateforme.

---

## 1. Tableau de Bord (Dashboard)

Dès votre connexion, vous accédez à une vue d'ensemble de votre activité.

*   **Commandes en cours :** Liste des bons de commande (BC) créés mais non encore validés.
*   **À valider :** (Pour les validateurs) Liste des BC nécessitant votre approbation.
*   **Statistiques rapides :** Nombre total de commandes, montant engagé sur le mois.
*   **Accès Rapide :** Boutons pour créer un nouveau BC ou consulter le dictionnaire.

---

## 2. Gestion des Commandes

Le cœur de l'application est la création et le suivi des bons de commande.

### 2.1 Créer une Commande
1.  Allez dans le menu **"Bons de Commande"** > **"Nouveau"**.
2.  **Sélectionnez le Chantier :** Obligatoire.
3.  **Date Souhaitée :** Indiquez quand la livraison est attendue.
4.  **Fournisseur :** (Optionnel à cette étape) Nom et contact.
5.  **Notes :** Ajoutez des instructions spécifiques (interne ou pour le fournisseur).
6.  Cliquez sur **"Créer le Brouillon"**.

### 2.2 Ajouter des Articles
Une fois le brouillon créé :
1.  Dans la section "Lignes de commande", cliquez sur **"Ajouter une ligne"**.
2.  **Description :** Tapez le nom de l'article (ex: "Ciment CPJ 45").
    *   *Astuce :* Le système traduira automatiquement la description pour le fournisseur si nécessaire.
3.  **Quantité & Unité :** Précisez le volume (m³, kg, unite, etc.).
4.  **Prix Unitaire :** (Optionnel) Pour estimation.
5.  Validez. Répétez pour chaque article.

### 2.3 Soumettre pour Validation
Lorsque votre commande est complète :
1.  Vérifiez le récapitulatif.
2.  Cliquez sur le bouton **"Soumettre"**.
3.  Le statut passe à `SOUMIS`. Vous ne pouvez plus la modifier, sauf si elle est rejetée.

### 2.4 Valider une Commande (Profil Valideur/Admin)
1.  Ouvrez une commande au statut `SOUMIS`.
2.  Vérifiez les lignes et les montants.
3.  Cliquez sur **"Valider"** pour approuver ou **"Rejeter"** (avec un motif) pour retourner au demandeur.
4.  Une fois validée, le statut passe à `VALIDE`.

### 2.5 Générer et Partager le PDF
Une fois la commande `VALIDE` :
1.  Le bouton **"Générer PDF"** apparaît. Cliquez dessus.
2.  Le document officiel est créé avec le logo de l'entreprise et la signature numérique.
3.  Utilisez les boutons de partage :
    *   **WhatsApp :** Ouvre l'application avec un message pré-rédigé et le lien.
    *   **Email :** Prépare un courriel avec le PDF en pièce jointe (ou lien).

---

## 3. Utiliser le Dictionnaire Technique

Le module **Lexique** vous aide à trouver les bons termes techniques et leurs traductions (Français ↔ Arabe/Darija).

### 3.1 Recherche
1.  Allez dans le menu **"Dictionnaire"**.
2.  Tapez un mot dans la barre de recherche (ex: "Béton").
3.  Le système affiche :
    *   Le terme standard.
    *   La traduction en Arabe et Darija.
    *   La catégorie (ex: Gros Œuvre).

### 3.2 Suggérer une Traduction
Si vous ne trouvez pas un terme :
1.  Cliquez sur **"Suggérer un terme"**.
2.  Remplissez le formulaire avec le mot français et votre proposition de traduction.
3.  Un administrateur validera votre suggestion pour l'ajouter à la base commune.

---

## 4. Mon Compte & Paramètres

*   **Langue :** Cliquez sur le drapeau en haut à droite pour changer la langue de l'interface (Français, Arabe, Anglais).
    *   *Note :* En Arabe, l'interface s'inverse (RTL) pour une lecture naturelle.
*   **Déconnexion :** Pour quitter l'application en sécurité.
