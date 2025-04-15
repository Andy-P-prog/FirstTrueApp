import requests,re,yaml,os
from crewai import Agent, Crew, Process, Task,LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
from dotenv import load_dotenv
from base.tools.vision_tool_openrouter import OpenRouterVisionTool
from base.tools.deepl_tool import DeepLTool
from crewai_tools import SerperDevTool
from crewai.agent import Agent as CrewAgent
from jinja2 import Template
from datetime import datetime
load_dotenv()
filedate = datetime.now().strftime("%Y-%m-%d")
llms = {
    "redacteur": LLM(
        model="openrouter/anthropic/claude-3.5-haiku",
        api_key=os.getenv("CLAUDE_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL")
    ),
    "chercheur": LLM(
        model="openrouter/anthropic/claude-3.5-haiku",
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL")
    ),
    "analyseur": LLM(
        model="openrouter/anthropic/claude-3.5-haiku",
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL")
    ),
    "developpeur": LLM(
        model="openrouter/x-ai/grok-3-mini-beta",
        api_key=os.getenv("GROK_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL")
    ),
    "extracteur": LLM(
        model="openrouter/mistralai/anthropic/claude-3.5-haiku",
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL")
    ),
    "raisonneur": LLM(
        model="openrouter/anthropic/claude-3.5-haiku",
        api_key=os.getenv("MIXTRAL_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL")
    ),
    "reporter": LLM(
        model="openrouter/anthropic/claude-3.5-haiku",
        api_key=os.getenv("MIXTRAL_API_KEY"),
        base_url=os.getenv("OPENROUTER_BASE_URL")
    )
}

if not hasattr(CrewAgent, "__original_execute_task__"):
    CrewAgent.__original_execute_task__ = CrewAgent.execute_task
def safe_execute_task(self, task, context=None, tools=None):
    try:
        return self.__original_execute_task__(task, context, tools)
    except ValueError as e:
        print(f"[ERROR] Agent '{self.role}' a échoué : {e}")
        return f"Erreur de l'agent {self.role}: {e}"


CrewAgent.execute_task = safe_execute_task

def interpolate_yaml(path, variables):
    base_dir = os.path.dirname(__file__)  # src/base
    full_path = os.path.join(base_dir, "config", path)
    with open(full_path, 'r', encoding='utf-8') as f:
        template = Template(f.read())
        rendered = template.render(**variables)

    print(f"\n[DEBUG] Contenu YAML interpolé pour {path}:\n{'-'*60}\n{rendered}\n{'-'*60}")

    try:
        return yaml.safe_load(rendered)
    except yaml.YAMLError as e:
        print(f"[ERREUR YAML dans {path}]:\n{e}")
        raise

def get_llm_infos():
        def extraire_nom(model_str):
            # Garde uniquement le dernier segment après le dernier /
            return str(model_str.split("/")[-1])
        return {
            key: {
                "model": extraire_nom(llm.model)
            }
            for key, llm in llms.items()
        }

@CrewBase
class Base():
    
    def build_agent(self, key, tools=None, llm_override=None) -> Agent:
        config = self.get_agents_config()[key]
        # Forcer l'attribution du champ 'name'
        #agent_name = config.get("name", key.capitalize())
        return Agent(
            name=key,
            config=config,
            verbose=True,
            tools=tools or [],
            llm=llm_override or llms.get(key)
        )
    def get_llm_for_agent(self, agent_key):
        if not hasattr(self, agent_key):
            return "Agent inconnu"
        try:
            agent_instance = getattr(self, agent_key)()
            if hasattr(agent_instance, "llm") and agent_instance.llm:
                return agent_instance.llm.model.split("/")[-1]
            else:
                return "Aucun modèle"
        except Exception as e:
            return f"Erreur : {e}"
    
    @before_kickoff
    def before_kickoff_function(self, inputs):
        #print(f"Before kickoff function with inputs: {inputs}")
        return inputs # You can return the inputs or modify them as needed

    @after_kickoff
    def after_kickoff_function(self, result):
        import yaml, re, os
        log_widget = getattr(self, "log_widget", None)  # widget Tkinter transmis par l'interface si dispo
        print(f"[DEBUG] log_widget reçu : {log_widget} (type: {type(log_widget)})")

        def is_log_queue(widget):
            return hasattr(widget, "put") and hasattr(widget, "get") and callable(widget.put)


        def log_debug(msg):
            print(f"[DEBUG] log_debug : {msg}")
            timestamp = datetime.now().strftime("%H:%M:%S")
            try:
                if is_log_queue(log_widget):
                    log_widget.put(f"[{timestamp}] {msg}")
                elif hasattr(log_widget, "insert"):
                    log_widget.insert("end", f"[{timestamp}] {msg}\n")
                    log_widget.see("end")
                else:
                    print(msg)
            except Exception as e:
                print(f"[LOG_WIDGET ERROR] {e}")


        
        
        blueprint_path = f"output/{self.inputs['nom_projet']}_{filedate}/crew_blueprint.md"
        if not os.path.exists(blueprint_path):
            log_debug(f"[ERREUR] Le fichier blueprint est introuvable : {blueprint_path}")
            return result

        with open(blueprint_path, "r", encoding="utf-8") as f:
            content = f.read()
            print("[DEBUG] CONTENU DU BLUEPRINT :\n", content)

        # Extraction de TOUS les blocs ```yaml ... ```
        blocks = re.findall(r"```yaml(.*?)```", content, re.DOTALL)

        agents_data, tasks_data = None, None
        for block in blocks:
            try:
                parsed = yaml.safe_load(block)
                print(f"[DEBUG] Parsed YAML type: {type(parsed)}")
                #print(f"[DEBUG] Parsed YAML content: {parsed}")
                if isinstance(parsed, dict) and "agents" in parsed:
                    agents_data = parsed
                elif isinstance(parsed, dict) and "tasks" in parsed:
                    tasks_data = parsed
                else:
                    log_debug(f"[DEBUG] Bloc YAML ignoré (pas d'agents ni de tasks) :\n{parsed}")
 
            except yaml.YAMLError as e:
                log_debug(f"[ERREUR] Bloc YAML invalide : {e}")
                continue

        if not agents_data or not tasks_data:
            log_debug("[ERREUR] agents.yaml ou tasks.yaml manquants ou invalides.")
            return result
        # Vérifie la structure exacte de agents_data
        if not isinstance(agents_data, dict) or "agents" not in agents_data:
            log_debug(f"[ERREUR] Format inattendu pour agents_data : {type(agents_data)} → {agents_data}")
            return result
        agents = agents_data["agents"]
        # Si agents est une liste de dicts, la convertir en un dict plat
        if isinstance(agents, list):
            try:
                agents = {k: v for d in agents for k, v in d.items()}
                log_debug("[INFO] Liste d'agents convertie en dictionnaire.")
            except Exception as e:
                log_debug(f"[ERREUR] Impossible de convertir la liste d'agents : {e}")
                return result

        # Sécurise l'ajout du champ name
        if isinstance(agents, dict):
            log_debug(f"[DEBUG] Contenu brut des agents : {agents}")
            for k, agent in agents.items():
                if isinstance(agent, dict):  
                    if "name" not in agent:
                        agent["name"] = k
                else:
                    # Essai de conversion d’un bloc agent plat
                    if isinstance(agent, str) and k in ["id", "name", "role", "backstory"]:
                        log_debug("[INFO] Conversion automatique d'un bloc plat détecté.")
                        agents = {
                            agents.get("id", "undefined"): {
                                "name": agents.get("name"),
                                "role": agents.get("role"),
                                "backstory": agents.get("backstory"),
                                "skills": agents.get("skills", [])
                            }
                        }
                        break  # on sort de la boucle, le format est maintenant bon
                    log_debug(f"[ERREUR] Agent {k} n'est pas un dictionnaire : {type(agent)} -> {agent}")    
            agents_data["agents"] = agents
        else:
            log_debug(f"[ERREUR] Format d'agents non pris en charge : {type(agents)}")
            return result
        # Remplace agents_data["agents"] par la version corrigée
        agents_data["agents"] = agents
        
       
        config_dir = f"output/{self.inputs['nom_projet']}_{filedate}/crew_config"
        os.makedirs(config_dir, exist_ok=True)

        try:
            with open(os.path.join(config_dir, "agents.yaml"), "w", encoding="utf-8") as f:
                yaml.dump(agents_data, f, allow_unicode=True, sort_keys=False)
            log_debug("[OK] agents.yaml généré")
        except Exception as e:
            
            log_debug(f"[ERREUR] Écriture agents.yaml : {e}")

        try:
            with open(os.path.join(config_dir, "tasks.yaml"), "w", encoding="utf-8") as f:
                yaml.dump(tasks_data, f, allow_unicode=True, sort_keys=False)
            log_debug("[OK] tasks.yaml généré")
        except Exception as e:
            log_debug(f"[ERREUR] Écriture tasks.yaml : {e}")

        return result





    def __init__(self, inputs=None):
        self.inputs = inputs or {}
        if "current_year" in self.inputs:
            self.inputs["current_year"] = str(self.inputs["current_year"])[:4]
        self.custom_config_path = self.inputs.get("custom_config_path", None)
        #log_debug(f"[DEBUG] Inputs reçus pour interpolation YAML : {self.inputs}")
    
    def get_agents_config(self):
        if not hasattr(self, '_agents_config'):
            self._agents_config = interpolate_yaml("agents.yaml", self.inputs)
        return self._agents_config

    def get_tasks_config(self):
        if not hasattr(self, '_tasks_config'):
            self._tasks_config = interpolate_yaml("tasks.yaml", self.inputs)
        return self._tasks_config
    
    

    """Base crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    vision_tool = OpenRouterVisionTool()
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def redacteur(self) -> Agent:
        config = self.get_agents_config()['redacteur']
        
        return Agent(
            config=config,
            verbose=True,
            llm=llms["redacteur"],
            tools=[SerperDevTool()]
        )

    @agent
    def chercheur(self) -> Agent:
        return Agent(
            config=self.get_agents_config()['chercheur'],
            verbose=True,
            llm=llms["chercheur"]
        )

    @agent
    def analyseur(self) -> Agent:
        

        return Agent(
            config=self.get_agents_config()['analyseur'],
            verbose=True,
            llm=llms["analyseur"]
        )

    @agent
    def developpeur(self) -> Agent:
        return Agent(
            config=self.get_agents_config()['developpeur'],
            verbose=True,
            llm=llms["developpeur"]
        )

    @agent
    def traducteur(self) -> Agent:
        config = self.get_agents_config()['redacteur']
        
        return Agent(
            config=self.get_agents_config()['redacteur'],
            verbose=True,
            tools=[DeepLTool()],
            llm=None
        )

    @agent
    def extracteur(self) -> Agent:
        config = self.get_agents_config()['extracteur']
       
        # 🔍 Ajout d'une vérification sur l'image à analyser
        image_path = self.inputs.get("image_path", "")
        if not image_path or not os.path.exists(image_path):
            print(f"[DEBUG] Aucune image trouvée ou chemin invalide : {image_path}")
        return Agent(
            config=self.get_agents_config()['extracteur'],
            tools=[self.vision_tool],
            verbose=True,
            llm=llms["raisonneur"]
        )

    @agent
    def raisonneur(self) -> Agent:
        return Agent(
            config=self.get_agents_config()['raisonneur'],
            verbose=True,
            llm=llms["raisonneur"]
        )
    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.get_agents_config()['raisonneur'],
            verbose=True,
            llm=llms["raisonneur"]
        )
    @agent
    def architecte_de_crew(self) -> Agent:
        config = self.get_agents_config()['architecte_de_crew']
        return Agent(
            config=config,
            verbose=True,
            llm=llms["raisonneur"]  # Ou claude/perplexity si besoin
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def analyse_besoins(self) -> Task:
        config=self.get_tasks_config()['analyse_besoins']
        return Task(
            description=config["description"],
        expected_output=config["expected_output"],
        agent=self.chercheur(),
            output_file=f"output/{self.inputs["nom_projet"]}_{filedate}/needs.md"
        )

    @task
    def collecte_donnees(self) -> Task:
        config=self.get_tasks_config()['collecte_donnees']
        return Task(
            description=config["description"],
        expected_output=config["expected_output"],
        agent=self.extracteur(),
            output_file=f"output/{self.inputs["nom_projet"]}_{filedate}/data.md"
        )

    @task
    def analyse_donnees(self) -> Task:
        config=self.get_tasks_config()['analyse_donnees']
        return Task(
            description=config["description"],
        expected_output=config["expected_output"],
        agent=self.analyseur(),
            output_file=f"output/{self.inputs["nom_projet"]}_{filedate}/analytic.md"
        )

    @task
    def redaction_contenu(self) -> Task:
        config=self.get_tasks_config()['redaction_contenu']
        return Task(
            description=config["description"],
        expected_output=config["expected_output"],
        agent=self.redacteur(),
            output_file=f"output/{self.inputs["nom_projet"]}_{filedate}/redac.md"
        )

    @task
    def developpement_app(self) -> Task:
        config=self.get_tasks_config()['developpement_app']
        return Task(
            description=config["description"],
        expected_output=config["expected_output"],
        agent=self.developpeur(),
            output_file=f"output/{self.inputs["nom_projet"]}_{filedate}/code.md"
        )

    @task
    def traduction(self) -> Task:
        config=self.get_tasks_config()['traduction']
        return Task(
            description=config["description"],
        expected_output=config["expected_output"],
        agent=self.traducteur(),
            output_file=f"output/{self.inputs["nom_projet"]}_{filedate}/clean_up_and_translate.md"
        )

    @task
    def verification_logique(self) -> Task:
        config=self.get_tasks_config()['verification_logique']
        
        
        return Task(
            description=config["description"],
                expected_output=config["expected_output"],
                agent=self.raisonneur(),
                output_file=f"output/{self.inputs["nom_projet"]}_{filedate}/logic.md"
                )
    @task
    def reporting_task(self) -> Task:
        return Task(
            description="Récapitule l'ensemble du projet et produit un rapport clair et structuré.",
            expected_output="Un rapport synthétique au format markdown.",
            agent=self.raisonneur(),
            output_file=f"output/{self.inputs["nom_projet"]}_{filedate}/report.md"
        )
    @task
    def conception_crew_specialise(self) -> Task:
        config = self.get_tasks_config()['conception_crew_specialise']
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=self.architecte_de_crew(),
            output_file=f"output/{self.inputs['nom_projet']}_{filedate}/crew_blueprint.md"
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Base crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        print("[DEBUG] Agents list :")
        for ag in self.agents:
            print(f"[DEBUG]  - {ag.role} ({type(ag)})")

        print("[DEBUG] Tasks list :")
        for t in self.tasks:
            print(f"  - {t.description[:50]}... -> {t.agent.role}")
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
