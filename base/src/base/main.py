#!/usr/bin/env python
import sys
import warnings

from datetime import datetime
import os
from base.crew import Base,llms
# GUI imports
from src.base.runner import run_crew_GUI
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
warnings.filterwarnings("ignore", category=UserWarning)

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
os.makedirs("output", exist_ok=True)
def run_create_specialized_crew():
    nom_projet = input("Nom du projet à générer : ")
    resume = input("Résumé de l'objectif : ")
    cible = input("Cible principale : ")
    app_type = input("Type d'application : ")
    langue = input("Langue : ")
    annee = str(datetime.now().year)

    inputs = {
        "nom_projet": nom_projet,
        "resume": resume,
        "cible": cible,
        "app_type": app_type,
        "langue": langue,
        "current_year": annee
    }

    from base.crew import Base
    base = Base(inputs)
    crew = base.crew()
    print("📦 Création du Crew spécialisé en cours...\n")
    result = crew.kickoff()
    print("\n✅ Résultat :")
    print(result)
    print(f"\n📝 Blueprint YAML généré dans : output/{nom_projet}_{str(datetime.now())}/crew_config/")



def run_cli(inputs = {}):
    """
    Run the crew.
    """
        
    print("Bienvenue dans le générateur d'app Cyberpunk 🌐")
    
    # Paramètres personnalisés avec choix multiples
    print("\nTypes d'application disponibles :")
    app_types = ["Application mobile", "Web app", "Jeu interactif", "Bot IA"]
    for i, option in enumerate(app_types, 1):
        print(f"{i}. {option}")
    app_type_index = input("Choisissez le type d'application (numéro ou nom) : ")
    app_type = app_types[int(app_type_index)-1] if app_type_index.isdigit() else app_type_index

    print("\nCibles disponibles :")
    cibles = ["Grand public", "Développeurs", "Entreprises", "Éducation"]
    for i, option in enumerate(cibles, 1):
        print(f"{i}. {option}")
    cible_index = input("Choisissez la cible (numéro ou nom) : ")
    cible = cibles[int(cible_index)-1] if cible_index.isdigit() else cible_index

    print("\nLangues disponibles :")
    langues = ["FR", "EN", "DE", "ES"]
    for i, option in enumerate(langues, 1):
        print(f"{i}. {option}")
    langue_index = input("Choisissez la langue (numéro ou code) : ")
    langue = langues[int(langue_index)-1] if langue_index.isdigit() else langue_index.upper()

    # Champs personnalisés
    nom_projet = input("\nNom du projet : ")
    resume = input("Résumé rapide de l'idée de l'application : ")

    inputs = {
        "current_year": str(datetime.now().year),
        "app_type": app_type,
        "cible": cible,
        "langue": langue,
        "nom_projet": nom_projet,
        "resume": resume
    }

    
    try:
        run_crew_GUI(inputs) 
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
def run():
    
        choix_gui = input("Souhaitez-vous utiliser l'interface graphique ? (o/n) : ").strip().lower()
        if choix_gui in ["o", "oui", "y", "yes"]:
            from gui.interface import launch_gui
            launch_gui()
        else:
            print("1. Lancer un projet classique")
            print("2. Générer un nouveau Crew spécialisé")

            choix = input("Choix : ").strip()

            if choix == "1":
                    run_cli(inputs={})

            elif choix == "2":
                run_create_specialized_crew()
