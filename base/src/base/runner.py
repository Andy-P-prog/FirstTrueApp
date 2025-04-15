from datetime import datetime
import os
from base.crew import Base, llms

def run_crew_GUI(inputs, log_queue=None):

    def log(msg):
        if log_queue:
            log_queue.put(str(msg))
        else:
            print(str(msg))
    log(f"[DEBUG] Inputs reçus : {inputs}")
    # Callback exécuté à chaque étape de la Crew
    def live_logger(step_output):
        try:
            # ToolResult (ex: vision, traducteur...)
            if hasattr(step_output, "result"):
                log(f"[Live tool_result] {step_output.result}")
            if hasattr(step_output, "output"):
                log(f"[Live output]{step_output.output}")
            elif hasattr(step_output, "text"):
                log(f"[Live text]{step_output.text}")
            else:
                if not any(hasattr(step_output, attr) for attr in ["result", "output", "text"]):
                    log(f"[Live fallback] {str(step_output)}")
                    log(f"[Live task_output]{step_output.task_output}")
            log(f"[Live debug] type: {type(step_output)}")
            log(f"[Live debug] Attributs: {dir(step_output)}")

        except Exception as e:
            log(f"[Live error] {e}")
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = f"output/{inputs['nom_projet']}_{date_str}"
    os.makedirs(output_dir, exist_ok=True)

    """ log("\n📦 Modèles LLM utilisés par agent :")
    for nom_agent, llm in llms.items():
        log(f"🧠 {nom_agent}: {llm.model}") """
    try:
        log("[DEBUG] Construction de la crew...")
        base = Base(inputs=inputs)
        base.log_widget = log_queue  # ou tout autre widget si dispo (voir plus bas)
        crew = base.crew()

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log(f"[ERREUR] Impossible de construire la crew : {e}\n{tb}")
        raise
    log("[DEBUG] Attribution du callback live_logger...")
    crew.step_callback = live_logger
    log(">>> Lancement de la crew...")

    try:
        log("[DEBUG] Lancement de la crew...")
        result = crew.kickoff(inputs=inputs)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        log(f"[ERREUR] Échec durant kickoff : {e}\n{tb}")
        raise
    log(">>> Crew terminée.")
    log(str(result))

    with open(os.path.join(output_dir, "resultats.txt"), "w", encoding="utf-8") as f:
        f.write(str(result))



    return result
