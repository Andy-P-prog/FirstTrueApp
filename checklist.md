## ✅ Checklist - Projet CrewAI Manager avec GUI

### 🧠 Général / Fonctionnel
- [ ] Créer un Crew Manager avec 10 agents spécialisés (chacun avec un LLM adapté)
- [ ] Générer automatiquement les fichiers `agents.yaml` et `tasks.yaml`
- [ ] S’assurer que `conception_crew_specialise` remplit correctement les YAML depuis les résultats des autres agents

---

### 🧩 Ajout d’un Crew Personnalisé
- [ ] Copier `agents.yaml` et `tasks.yaml` dans `config/nom_du_crew` lors de l’ajout
- [ ] Vérifier la validité des fichiers YAML automatiquement
- [ ] Ajouter dynamiquement les agents manquants dans `crew.py` si besoin
- [ ] Ajouter dynamiquement les tâches manquantes dans `crew.py` si besoin
- [ ] Permettre de trier les crews personnalisés dans des sous-dossiers (`config/projets/...`)

---

### 🖥️ Interface Graphique (GUI)
- [x] Ajouter un bouton "Coller" à côté des champs "Nom du projet" et "Description"
- [x] Assurer la visibilité du bouton "Lancer le Crew" même en mode fenêtré
- [x] Réinitialiser automatiquement le bouton après l’arrêt du crew
- [x] Ajouter un menu déroulant "Démarrer" avec les crews standards et personnalisés
- [x] Ajouter un bouton "Mode développeur" qui affiche/masque l’onglet Debug
- [x] Ajouter un bouton "Ajouter Crew personnalisé" (depuis un dossier `output`)
- [ ] Permettre d’assigner un LLM à chaque agent depuis l’interface
- [ ] Afficher dynamiquement les agents et les LLM utilisés dans l’onglet Debug

