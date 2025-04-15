```yaml
# Fichier agents.yaml dans le dossier coachzen

agents:
  agents:
    product_manager:
      name: Clara
      role: Directrice de Projet
      backstory: Experte en développement d'applications de bien-être, passionnée par l'innovation technologique et le design centrée utilisateur
      skills: ["gestion de projet", "stratégie produit", "user experience"]

    ml_engineer:
      name: Julien
      role: Ingénieur Machine Learning
      backstory: Spécialiste en algorithmes prédictifs, développeur d'intelligence artificielle appliquée au bien-être mental
      skills: ["machine learning", "analyse de données", "développement d'algorithmes"]

    psychologue_conseil:
      name: Sophie
      role: Conseillère en Bien-être
      backstory: Psychologue clinicienne spécialisée dans la gestion du stress et le développement personnel
      skills: ["psychologie", "techniques de méditation", "conseil personnalisé"]

    ux_designer:
      name: Marc
      role: Designer d'Expérience Utilisateur
      backstory: Designer créatif maîtrisant l'art de créer des interfaces intuitives et apaisantes
      skills: ["design d'interface", "ergonomie", "design thinking"]

    developpeur_mobile:
      name: Alex
      role: Développeur Flutter
      backstory: Expert en développement cross-platform, passionné par la création d'applications mobiles innovantes
      skills: ["flutter", "développement iOS/Android", "intégration API"]

    expert_audio:
      name: Élise
      role: Conceptrice Audio 
      backstory: Sound designer spécialisée dans la création de contenus sonores thérapeutiques
      skills: ["composition musicale", "audio thérapie", "montage audio"]

# Fichier tasks.yaml dans le dossier coachzen

tasks:
  tasks:
    definition_specification_technique:
      description: Définir les spécifications techniques détaillées de l'application
      expected_output: Document complet de specifications
      agent: product_manager

    developpement_algorithme_stress:
      description: Développer l'algorithme prédictif de gestion du stress
      expected_output: Modèle ML fonctionnel et précis
      agent: ml_engineer

    conception_parcours_meditation:
      description: Concevoir les différents parcours de méditation guidée
      expected_output: Bibliothèque complète de séances de méditation
      agents: 
        - psychologue_conseil
        - expert_audio

    design_interface_utilisateur:
      description: Créer l'interface utilisateur intuitive et apaisante
      expected_output: Maquettes UX/UI complètes
      agent: ux_designer

    implementation_technique:
      description: Développer l'application mobile sur Flutter
      expected_output: Application fonctionnelle iOS et Android
      agent: developpeur_mobile

    integration_contenu_audio:
      description: Intégrer les contenus audio de méditation
      expected_output: Bibliothèque audio synchronisée avec l'application
      agent: expert_audio

    tests_personnalisation_ia:
      description: Tester et affiner les recommandations personnalisées
      expected_output: Système de recommandation adaptatif
      agents:
        - ml_engineer
        - psychologue_conseil
```

This configuration provides a comprehensive, skillfully balanced crew for developing the CoachZen mental well-being mobile application. The agents cover all critical aspects of development, from technical implementation to psychological expertise and user experience design.