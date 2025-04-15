# 🚀 FirstTrueApp – Générateur d'apps IA avec CrewAI

**FirstTrueApp** est une application qui vous permet de générer des projets complets à l’aide d’une équipe virtuelle d’agents intelligents (CrewAI). Elle dispose d'une interface graphique avancée pour gérer les entrées, visualiser les logs, et même créer des crews spécialisés à la volée.

---

## 🧠 Fonctionnalités principales

- 🎛️ Interface graphique intuitive (Tkinter) avec logs temps réel
- 🧩 Architecture modulaire basée sur CrewAI
- 🧠 Agents spécialisés : rédacteur, développeur, analyste, chercheur, traducteur, etc.
- 🔄 Mode classique ou génération automatique de crew personnalisé
- ✨ Ajout & suppression de Crews personnalisés via l’interface
- 🔍 Inspection des modèles LLM assignés aux agents
- 🛠️ Intégration d’outils comme DeepL et vision via OpenRouter

---

## 🖥️ Interface utilisateur (GUI)

Lancée depuis `crewai run`, l'interface se trouve dans :

```
base/gui/interface.py
```

Elle permet :
- D’entrer les infos projet
- De lancer un crew (ou d’en créer un nouveau)
- D’afficher les logs par catégorie (task, output, etc.)
- D’activer le mode développeur
- De gérer les crews personnalisés (import/export/suppression)

---

## 📁 Structure du projet

```bash
FirstTrueApp/
│
├── base/
│   ├── gui/                  # Interface graphique (Tkinter)
│   │   └── interface.py
│   ├── src/
│   │   └── base/
│   │       ├── config/       # Fichiers agents.yaml et tasks.yaml
│   │       ├── tools/        # Outils personnalisés (ex: deepl_tool.py)
│   │       ├── crew.py       # Définition de la structure de crew
│   │       └── runner.py     # Lancement avec logs & callback
│
├── main.py                  # Entrée principale CLI/GUI
└── .env                     # Clés API pour les LLMs et outils externes
```

---

## 🧪 Lancement du projet

### 📦 Installation

1. Crée ton environnement avec Conda :
```bash
conda create -n firsttrueapp python=3.12.9
conda activate firsttrueapp
```

2. Installe les dépendances :
```bash
pip install -r requirements.txt
```

3. Configure ton fichier `.env` :
```env
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
CLAUDE_API_KEY=...
PERPLEXITY_API_KEY=...
GEMINI_API_KEY=...
GROK_API_KEY=...
MIXTRAL_API_KEY=...
DEEPL_API_KEY=...
```

---

### 🧑‍💻 Lancer l’application

```bash
crewai run
```

Depuis le menu, tu peux :
- Lancer un projet classique
- Créer un crew spécialisé
- Utiliser un crew personnalisé existant

---

## 📄 Configuration des agents & tâches

Les fichiers YAML utilisés sont situés dans :

```
base/src/base/config/
├── agents.yaml
└── tasks.yaml
```

Tu peux les modifier à la main, ou générer de nouveaux fichiers automatiquement via l'interface en mode "Générateur de Crew".

---

## 🧩 Ajouter un Crew personnalisé

1. Génère un crew via l’interface ou le mode CLI
2. Va dans `output/NomDuProjet_DATE/`
3. Clique sur "Ajouter Crew personnalisé" dans l’interface
4. Il sera automatiquement détecté et réutilisable

---

## 🛠️ Technologies

- [CrewAI](https://docs.crewai.com/)
- [Tkinter](https://docs.python.org/3/library/tkinter.html)
- [Jinja2](https://jinja.palletsprojects.com/)
- [DeepL API](https://www.deepl.com/docs-api)
- LLMs via [OpenRouter](https://openrouter.ai/)

---

## 📌 TODO / Idées futures

- Support multi-projet via onglets
- Export HTML/PDF automatique
- Intégration directe à une plateforme de déploiement

---

## 🧑‍💻 Auteur

Made with ❤️ by Andy-P-prog  
[GitHub](https://github.com/Andy-P-prog)

---

## 📜 Licence

Ce projet est sous licence MIT.
