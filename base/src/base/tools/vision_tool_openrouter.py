import base64
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class VisionToolInput(BaseModel):
    image_path_url: str = Field(..., description="URL ou chemin local vers une image (jpg/png)")

class OpenRouterVisionTool(BaseTool):
    name: str = "OpenRouter Vision Tool"
    description: str = "Analyse une image à l'aide de GPT-4-Vision via OpenRouter"
    args_schema: Type[BaseModel] = VisionToolInput

    def _run(self, image_path_url: str) -> str:
        from dotenv import load_dotenv
        import os
        load_dotenv()

        api_key = os.getenv("VISION_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        if not api_key:
            raise ValueError("VISION_API_KEY manquant dans le fichier .env")

        # 🔁 Si Dropbox, conversion vers lien image direct
        if "dropbox.com" in image_path_url:
            image_path_url = image_path_url.replace("www.dropbox.com", "dl.dropboxusercontent.com")
            image_path_url = image_path_url.replace("?dl=0", "?raw=1")
            image_path_url = image_path_url.replace("?rlkey=", "&rlkey=")  # parfois présent dans les liens partagés

        # ✅ Vérifie si c'est un format d'image accepté
        valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
        if not any(image_path_url.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError("Le fichier doit être une image (.jpg, .jpeg, .png, .webp)")

        # Vérifier si c’est une URL ou un fichier local
        if image_path_url.startswith("http"):
            image_data = {"url": image_path_url}
        else:
            with open(image_path_url, "rb") as image_file:
                b64 = base64.b64encode(image_file.read()).decode("utf-8")
                image_data = {"image": f"data:image/jpeg;base64,{b64}"}

        payload = {
            "model": "openrouter/meta-llama/llama-3.2-90b-vision-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Décris le contenu de cette image :"},
                        {"type": "image_url", "image_url": image_data}
                    ]
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
