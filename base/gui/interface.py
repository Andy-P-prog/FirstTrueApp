import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import re
from src.base.runner import run_crew_GUI
import threading
import multiprocessing
from tkinter import simpledialog
from tkinter import filedialog
import yaml
import shutil
import os
import json
CREWS_SAVE_FILE = "custom_crews.json"
from src.base.crew import get_llm_infos,Base


def crew_target(inputs, log_queue, on_done=None):
        try:
            run_crew_GUI(inputs, log_queue=log_queue)
        except Exception as e:
            import traceback
            print("[GUI ERROR]", e)
            print(traceback.print_exc())
            messagebox.showerror("Erreur", f"{e}\n\nInputs : {inputs}")
        finally:
            if on_done:
                on_done()

def charger_crews(menu, callback):
    if not os.path.exists(CREWS_SAVE_FILE):
        return
    try:
        with open(CREWS_SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for crew in data:
            menu.add_command(label=crew["label"], command=lambda c=crew: callback(c))
    except Exception as e:
        print("[ERREUR] Chargement des crews personnalisés :", e)
def extraire_infos_agents(path_yaml):
    try:
        with open(path_yaml, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        llm_data = get_llm_infos()
        resultats = []
        for agent_key in data:
            nom_affiche = data[agent_key].get("name", agent_key)
            model = llm_data.get(agent_key, "Inconnu")
            resultats.append(f"- {nom_affiche} (modèle : {model})")
        
        return "\n".join(resultats)
    except Exception as e:
        return f"[ERREUR] Lecture des agents et LLMs : {e}"
def afficher_infos_llm_debug(chemin_agents, log_widget, inputs=None):
    try:
        if chemin_agents and os.path.exists(chemin_agents):
            details = extraire_infos_agents_et_llm_direct(chemin_agents, inputs or {},log_areas=log_widget)
            timestamp = datetime.now().strftime("%H:%M:%S")
            if not hasattr(log_widget, "insert"):
                print("[ERREUR] log_widget ne supporte pas .insert")
                return

            log_widget.insert(tk.END, f"[{timestamp}] Agents et LLM utilisés :\n{details}\n\n")
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_widget.insert(tk.END, f"[{timestamp}] Aucun fichier agents.yaml trouvé à{chemin_agents}\n")
        log_widget.see(tk.END)
    except Exception as e:
        log_widget.insert(tk.END, f"[ERREUR] Chargement LLM: {e}\n")

def extraire_infos_agents_et_llm_direct(path_yaml, inputs, log_areas=None):
    try:
        with open(path_yaml, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
        

        base = Base(inputs)
        print(f"[DEBUG] log_areas ={log_areas}")
        base.log_widget = log_areas
        print(f"[DEBUG] log_widget = {type(base.log_widget)}")
        lignes = []

        for agent_key in yaml_data:
            nom_affiche = yaml_data[agent_key].get("name", agent_key)
            modele = base.get_llm_for_agent(agent_key)
            lignes.append(f"- {nom_affiche} (modèle : {modele})")

        return "\n".join(lignes)
    except Exception as e:
        return f"[ERREUR] Lecture agents/LLM depuis crew.py : {e}"


def launch_gui():
    start_menu_action_index = None
    def make_paste_button(entry,row):
        return ttk.Button(row, text="Coller", width=6, style="Dark.TButton", command=lambda e=entry: e.insert(0, root.clipboard_get()))
    def poll_queue():
            try:
                while not log_queue.empty():
                    msg = log_queue.get_nowait()
                    target = "autres"
                    match = re.match(r"\[live (\w+)\]", msg.lower())
                    if match:
                        key = match.group(1)
                        if key in log_areas:
                            target = key
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    log_areas[target].insert(tk.END, f"[{timestamp}] {msg}\n")
                    log_areas[target].see(tk.END)
            except Exception as e:
                print("[Queue Error]", e)
            nonlocal crew_process
            if crew_process and not crew_process.is_alive():
                print("[DEBUG] Arrêt du crew demandé.")
                
                launch_button.config(
                    text="Lancer le Crew",
                    style="Black.TButton",
                    state="normal"
                )
                crew_process = None
                
            else:
                root.after(100, poll_queue)
    def run_crew_gen_wrapper(inputs, log_queue):
        from src.base.crew import Base
        base = Base(inputs,log_widget=log_areas["task_output"])
        crew = base.crew()
        try:
            result = crew.kickoff()
            log_queue.put(f"[live output] Génération terminée : {result}")
        except Exception as e:
            log_queue.put(f"[live output] Erreur : {e}")
    def run_or_stop():
        global log_queue
        nonlocal crew_process
        from multiprocessing import Process, Queue
        print("[DEBUG] run_or_stop lancé")

        if crew_process and crew_process.is_alive():
            print("[DEBUG] Arrêt manuel du crew.")
            crew_process.terminate()
            crew_process.join()
            crew_process = None
            launch_button.config(
                text="Lancer le Crew",
                style="Black.TButton",
                state="normal"
            )
            start_menu.entryconfig(start_menu_action_index, label="Lancer le Crew")
          
        else:
            #Choisir les inputs selon le mode actif
            if current_mode.get() == "crew_personnalise" and selected_custom_crew:
                inputs = selected_custom_crew["inputs"]
            else:
                inputs = {key: widget.get() for key, widget in entries.items()}
                inputs["current_year"] = str(datetime.now().year)
            # === Si mode Générateur de Crew ===    
            if current_mode.get() == "crew_gen":
                log_queue = Queue()
                crew_process = multiprocessing.Process(target=run_crew_gen_wrapper, args=(inputs, log_queue))
                crew_process.start()
                return

               
            # === LOG DES AGENTS & LLM ===
            chemin_agents = None
            if current_mode.get() == "crew_personnalise" and selected_custom_crew:
                crew_path = selected_custom_crew.get("path")
                if crew_path:
                    chemin_agents = os.path.join(crew_path, "crew_config", "agents.yaml")
            else:
                # Cas classique : utilise le dossier par défaut
                chemin_agents = os.path.join("src", "base","config", "agents.yaml")

            if chemin_agents and os.path.exists(chemin_agents):
                details = extraire_infos_agents(chemin_agents)
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_areas["debug"].insert(tk.END, f"[{timestamp}] Agents et LLM utilisés :\n{details}\n\n")
                log_areas["debug"].see(tk.END)
            else:
                timestamp = datetime.now().strftime("%H:%M:%S")
                log_areas["debug"].insert(tk.END, f"[{timestamp}] Aucun fichier agents.yaml trouvé à {chemin_agents} \n") 

            
            log_queue = Queue()
            print(f"[GUI DEBUG] Inputs envoyés au Process: {inputs}")

            crew_process = Process(target=crew_target, args=(inputs, log_queue))
            #print("[DEBUG] Process lancé avec inputs:", inputs)
            crew_process.start()

            launch_button.config(
                text="Arrêter le Crew",
                style="Red.TButton",
                state="normal"
            )
            start_menu.entryconfig(start_menu_action_index, label="Arrêter le Crew")


            root.after(100, poll_queue)
            
      
    # def supprimer_crew():
    #     if not os.path.exists(CREWS_SAVE_FILE):
    #         messagebox.showinfo("Info", "Aucun crew personnalisé enregistré.")
    #         return

    #     with open(CREWS_SAVE_FILE, "r", encoding="utf-8") as f:
    #         data = json.load(f)

    #     if not data:
    #         messagebox.showinfo("Info", "Aucun crew à supprimer.")
    #         return

    #     noms = [entry["label"] for entry in data]
    #     selection = simpledialog.askstring("Supprimer Crew", "Nom du Crew à supprimer :\n" + "\n".join(noms))
    #     if not selection:
    #         return

    #     new_data = [entry for entry in data if entry["label"] != selection]
    #     if len(new_data) == len(data):
    #         messagebox.showwarning("Non trouvé", f"Aucun crew nommé “{selection}” trouvé.")
    #         return

    #     with open(CREWS_SAVE_FILE, "w", encoding="utf-8") as f:
    #         json.dump(new_data, f, ensure_ascii=False, indent=2)

    #     messagebox.showinfo("Succès", f"Crew “{selection}” supprimé avec succès.\nRedémarre l'interface pour mettre à jour le menu.")
    def ajouter_crew():
        folder = filedialog.askdirectory(title="Sélectionnez un dossier de Crew généré")
        if not folder:
            return

        agents_path = os.path.join(folder, "crew_config", "agents.yaml")
        tasks_path = os.path.join(folder, "crew_config", "tasks.yaml")

        if not os.path.exists(agents_path) or not os.path.exists(tasks_path):
            messagebox.showerror("Erreur", "Le dossier ne contient pas un Crew valide (agents.yaml et tasks.yaml manquants)")
            return

        # Nom du projet = nom du dossier sans la date
        nom_projet = os.path.basename(folder).split("_")[0]
        current_year = str(datetime.now().year)

        # Valeurs par défaut
        app_type = "Web app"
        langue = "FR"
        cible = "Grand public"
        resume = "Projet personnalisé"

        # Essayons de lire le report.md s’il existe
        report_path = os.path.join(folder, "report.md")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
                match_langue = re.search(r"Langue\s*:\s*(FR|EN|DE|ES)", content, re.IGNORECASE)
                match_type = re.search(r"Type\s*:\s*(.+)", content)
                match_cible = re.search(r"Public Cible\s*:\s*(.+)", content)
                match_resume = re.search(r"### Mission\n(.+)", content)
                titre_match = re.search(r"#\s*(.+)", content)

                if match_langue: langue = match_langue.group(1).upper()
                if match_type: app_type = match_type.group(1).strip()
                if match_cible: cible = match_cible.group(1).strip()
                if match_resume: resume = match_resume.group(1).strip()
                nom_projet_affiche = titre_match.group(1).strip() if titre_match else nom_projet

        def lancer_crew_personnalise():
            inputs = {
                "nom_projet": nom_projet,
                "resume": resume,
                "cible": cible,
                "app_type": app_type,
                "langue": langue,
                "current_year": current_year
            }

            from multiprocessing import Process, Queue
            global log_queue
            log_queue = Queue()

            nonlocal crew_process
            if crew_process and crew_process.is_alive():
                crew_process.terminate()
                crew_process.join()

            crew_process = multiprocessing.Process(target=crew_target, args=(inputs, log_queue))
            crew_process.start()

            launch_button.config(
                text="Arrêter le Crew",
                style="Red.TButton",
                state="normal"
            )

            root.after(100, poll_queue)

        #crew_menu.add_command(label=nom_projet_affiche, command=lancer_crew_personnalise)
        

        charger_crews(custom_crew_menu, lambda c: relancer_crew(c)())

        # Sauvegarder dans custom_crews.json
        entry = {
            "label": nom_projet_affiche,
            "path": folder,
            "inputs": {
                "nom_projet": nom_projet,
                "resume": resume,
                "cible": cible,
                "app_type": app_type,
                "langue": langue,
                "current_year": current_year
            }
        }
        existing = []
        if os.path.exists(CREWS_SAVE_FILE):
            with open(CREWS_SAVE_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.append(entry)
        with open(CREWS_SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("Succès", f"Crew “{nom_projet}” ajouté au menu avec détection automatique !")

        

        # Chargement initial des crews dans le sous-menu
        rafraichir_menu_crew_personnalise()
    def supprimer_crew_selectionne(nom_crew):
            confirmation = messagebox.askyesno("Confirmation", f"Supprimer le crew « {nom_crew} » ?")
            if not confirmation:
                return

            with open(CREWS_SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            new_data = [entry for entry in data if entry["label"] != nom_crew]

            with open(CREWS_SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Succès", f"Crew « {nom_crew} » supprimé.")
            rafraichir_menu_crew_personnalise()

    def rafraichir_menu_crew_personnalise():
        menu_supprimer_crew.delete(0, "end")
        custom_crew_menu.delete(0, "end")
        if not os.path.exists(CREWS_SAVE_FILE):
            return

        with open(CREWS_SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for crew in data:
            nom = crew.get("label", "Sans nom")
            menu_supprimer_crew.add_command(
                label=nom,
                command=lambda nom=nom: supprimer_crew_selectionne(nom)
            )
            custom_crew_menu.add_command(
            label=nom,
            command=lambda crew=crew: relancer_crew(crew)()
        )

    BG_COLOR = "#1e1e1e"       # fond général
    FG_COLOR = "#ffffff"       # texte blanc
    ACCENT_COLOR = "#00ffff"   # pour hover ou bordures
    HOVER_BG = "#333333"
    DISABLED_COLOR = "#777777"
    selected_custom_crew = None  # mémorise le crew personnalisé sélectionné
    crew_process = None
    root = tk.Tk()
    root.title("NeonWake - Interface de lancement")
    root.configure(background=BG_COLOR)
    root.geometry("800x700")  # Fenêtre agrandie
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    start_menu = tk.Menu(menu_bar, tearoff=0)
    custom_crew_menu = tk.Menu(start_menu, tearoff=0)
    #menu_bar.add_cascade(label="Démarrer", menu=start_menu)
    # Bouton Lancer le Crew dans le menu Démarrer
    start_menu_action_label = "Lancer le Crew"
    
    start_menu.add_command(label=start_menu_action_label, command=run_or_stop)
    start_menu_action_index = start_menu.index("end")
    menu_bar.configure(background=BG_COLOR, foreground=FG_COLOR, activebackground=HOVER_BG, activeforeground=ACCENT_COLOR)
    menu_bar.add_cascade(label="Démarrer", menu=start_menu)
    
    dev_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Outils", menu=dev_menu)
    dev_mode = tk.BooleanVar(value=False)
    def toggle_debug_tab():
        if dev_mode.get():
            log_tabs.hide(log_tabs.tabs_dict["debug"])
            dev_mode.set(False)
        else:
            log_tabs.add(log_tabs.tabs_dict["debug"])
            dev_mode.set(True)   
    
    dev_menu.add_command(label="Mode développeur", command=toggle_debug_tab)
    dev_menu.add_separator()
    def relancer_crew(crew):
        def select():
            nonlocal selected_custom_crew
            selected_custom_crew = crew
            current_mode.set("crew_personnalise")
            root.title(f"NeonWake - {crew['label']}")
            # désactiver les champs modifiables
            for key, widget in entries.items():
                if key in crew["inputs"]:
                    widget.delete(0, tk.END)
                    widget.insert(0, crew["inputs"][key])
                    widget.config(state="disabled")
            launch_button.config(text="Lancer le Crew", style="Black.TButton")
            chemin_agents = os.path.join("src", "base", "config", "agents.yaml")
            afficher_infos_llm_debug(chemin_agents, log_areas["debug"])

        return select

    


    # --- Sous-menu dans le menu "Outils" ---
    menu_crew_tools = tk.Menu(dev_menu, tearoff=0)
    dev_menu.add_cascade(label="Crew personnalisé", menu=menu_crew_tools)

    # Bouton : Ajouter un Crew
    menu_crew_tools.add_command(label="Ajouter un Crew personnalisé", command=ajouter_crew)

    # Sous-menu : Supprimer un Crew
    menu_supprimer_crew = tk.Menu(menu_crew_tools, tearoff=0)
    menu_crew_tools.add_cascade(label="Supprimer un Crew personnalisé", menu=menu_supprimer_crew)
    rafraichir_menu_crew_personnalise()

    # Conteneur principal
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill="both", expand=True)
    main_frame.configure(style="Dark.TFrame")
    
    
    #print("[DEBUG] setting entry")
    # Champs de saisie
    entries = {}
     # Dropdowns pour choix multiples
    app_types = ["Application mobile", "Web app", "Jeu interactif", "Bot IA"]
    cibles = ["Grand public", "Développeurs", "Entreprises", "Éducation"]
    langues = ["FR", "EN", "DE", "ES"]
    fields = [
        ("Nom du projet", "nom_projet", "entry"),
        ("Résumé de l'application", "resume", "entry"),
        ("Type d'application", "app_type", app_types),
        ("Cible", "cible", cibles),
        ("Langue (FR, EN...)", "langue", langues),
    ]
    

    #menu_crew_tools.add_command(label="Supprimer un Crew personnalisé", command=supprimer_crew)
    current_mode = tk.StringVar(value="classique")
    def set_entry_state(key, state):
        if key in entries:
            entries[key].config(state=state)
    def switch_mode(mode):
        current_mode.set(mode)
        print(f"[DEBUG] switch_mode appelé avec mode = {mode}")
        if mode == "classique":
            root.title("NeonWake - Projet Classique")
            set_entry_state("nom_projet","normal")
            set_entry_state("resume","normal")
            entries["app_type"].config(state="readonly")
            entries["cible"].config(state="readonly")
            launch_button.config(text="Lancer le Crew", style="Black.TButton")
            chemin_agents = os.path.join("src", "base", "config", "agents.yaml")
            afficher_infos_llm_debug(chemin_agents, log_areas["debug"])


            log_areas["output"].pack(fill=tk.BOTH, expand=True)
            log_areas["output"].pack_forget()
        elif mode == "crew_personnalise":
            root.title("NeonWake - Crew personnalisé")
            for key in entries:
                entries[key].config(state="disabled")
            launch_button.config(text="Lancer le Crew", style="Black.TButton")
        else:
            root.title("NeonWake - Générateur de Crew")
            set_entry_state("nom_projet","normal")
            set_entry_state("resume","normal")
            entries["app_type"].config(state="disabled")
            entries["cible"].config(state="disabled")
            launch_button.config(text="Générer le Crew", style="Black.TButton")
            chemin_agents = os.path.join("src", "base", "config", "agents.yaml")
            afficher_infos_llm_debug(chemin_agents, log_areas["debug"])


            log_areas["output"].pack(fill=tk.BOTH, expand=True)
            log_areas["output"].pack_forget()


    
    
    
        
    for label_text, key, widget_type in fields:
        row = ttk.Frame(main_frame, style="Dark.TFrame")
        row.pack(fill="x", pady=5)
        label = ttk.Label(row, text=label_text, style="Dark.TLabel")
        label.pack()

        if isinstance(widget_type, list):
            combo = ttk.Combobox(row, values=widget_type, style="Dark.TCombobox", state="readonly", width=30)
            combo.current(0)
            combo.pack(padx=5)
            entries[key] = combo
        else:
            entry_width = 80 if key == "resume" else 30
            entry = ttk.Entry(row, width=entry_width, style="Dark.TEntry")
            entry.pack( padx=5)
            entries[key] = entry
            if key in ["nom_projet", "resume"]:
                paste_btn = make_paste_button(entry,row)
                paste_btn.pack()

    
    crew_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Crew", menu=crew_menu)
    crew_menu.add_command(label="Mode : Projet Classique", command=lambda: switch_mode("classique"))
    crew_menu.add_command(label="Mode : Générateur de Crew", command=lambda: switch_mode("crew_gen"))
    crew_menu.add_cascade(label="Crew personnalisé", menu=custom_crew_menu)
    # Zone de logs
    log_label = ttk.Label(main_frame, text="Logs d'exécution :")
    log_label.pack(anchor="w", pady=(15, 0))

    log_tabs = ttk.Notebook(main_frame)
    log_tabs.pack(fill="both", expand=True, pady=(5, 40))

    log_areas = {}
    log_tabs.tabs_dict = {}   
    for key in ["Output", "Text", "task_output", "tool_result", "Debug","Autres"]:
        
        frame = ttk.Frame(log_tabs,style='Dark.TFrame')
        text_area = scrolledtext.ScrolledText(frame, height=20, wrap=tk.WORD,background=BG_COLOR,foreground=FG_COLOR )
        text_area.pack(fill="both", expand=True)
        log_tabs.add(frame, text=key)
        log_areas[key.lower()] = text_area
        log_tabs.tabs_dict[key.lower()] = frame  # stocke la tab
    log_tabs.hide(log_tabs.tabs_dict["debug"])
     
    
    #print("[DEBUG] Apres redirect")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Red.TButton", background="#820c1d",relief="flat", foreground="white")
    style.configure("Black.TButton", background="#1a2387",relief="flat", foreground="black")
    style.configure("Dark.TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=FG_COLOR)
    style.configure("TEntry", fieldbackground=BG_COLOR, foreground=FG_COLOR,bordercolor="#007fff",
     lightcolor="#007fff",
     darkcolor="#007fff",)

    style.configure("Dark.TCombobox",
    foreground=FG_COLOR,
    fieldbackground=BG_COLOR,
    background=BG_COLOR,
    borderwidth=0,
    bordercolor="#007fff",
    lightcolor="#007fff",
    darkcolor="#007fff",
    relief="flat",arrowcolor=FG_COLOR,
    selectforeground=FG_COLOR,
    selectbackground=BG_COLOR)
    style.map("Dark.TCombobox", fieldbackground=[("readonly", BG_COLOR)],foreground=[("readonly", FG_COLOR)],background=[("readonly", BG_COLOR)])
    style.configure("TCombobox", bordercolor=BG_COLOR)
    style.configure("Dark.TEntry",
        foreground=FG_COLOR,
        fieldbackground=BG_COLOR,
        background=BG_COLOR,
        bordercolor="#007fff",
        lightcolor="#007fff",
        darkcolor="#007fff",borderwidth=0,relief="flat",insertcolor=FG_COLOR  # <- curseur blanc
        )
    style.configure("TNotebook",background=BG_COLOR,bordercolor="#007fff",
        lightcolor="#007fff",
        darkcolor="#007fff",borderwidth=0)
    style.configure("TNotebook.Tab",background=BG_COLOR,foreground=FG_COLOR,padding=5,bordercolor="#007fff",
        lightcolor="#007fff",
        darkcolor="#007fff",borderwidth=0,focusthickness=0,)
    style.map("TNotebook.Tab",background=[("selected", "#2e2e2e")],foreground=[("selected", FG_COLOR)],)
    style.configure("Dark.TLabel", background=BG_COLOR, foreground=FG_COLOR)
    style.configure("Dark.TButton", background=BG_COLOR, foreground=FG_COLOR,relief="flat")
    style.map("Dark.TButton", background=[("active", HOVER_BG)])
    

        


    button_frame = ttk.Frame(root)
    button_frame.pack(side=tk.BOTTOM, fill="x", pady=10)

    # === LANCER LE CREW ===
    launch_button = ttk.Button(button_frame, text="Lancer le Crew", style="Black.TButton", command=run_or_stop)
    launch_button.pack(side=tk.LEFT, padx=10, pady=15)

    


    root.mainloop()