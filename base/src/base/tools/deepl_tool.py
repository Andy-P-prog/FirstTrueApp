from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
import requests

# Définition du schéma d’entrée
class DeepLToolInput(BaseModel):
    text: str = Field(..., description="Texte à traduire")
    target_lang: str = Field("FR", description="Langue cible du texte (ex: EN, FR, DE)")

# Définition de l’outil DeepL
class DeepLTool(BaseTool):
    name: str = "DeepL Translator"
    description: str = "Utilise l’API DeepL pour traduire du texte dans une langue cible donnée."
    args_schema: Type[BaseModel] = DeepLToolInput

    def _run(self, text: str, target_lang: str = "EN") -> str:
        api_key = os.getenv("DEEPL_API_KEY")
        if not api_key:
            raise ValueError("DEEPL_API_KEY est manquant dans le fichier .env")

        url = "https://api-free.deepl.com/v2/translate"
        params = {
            "auth_key": api_key,
            "text": text,
            "target_lang": target_lang.upper(),
        }

        response = requests.post(url, data=params)
        response.raise_for_status()
        return response.json()["translations"][0]["text"]
