import requests
from django.conf import settings


OLLAMA_URL = getattr(settings, "OLLAMA_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = getattr(settings, "OLLAMA_MODEL", "llama3.2")


def ask_ollama(prompt: str) -> str:
    """
    Envoie un prompt à Ollama en local et retourne la réponse.
    Sécurisé, timeout, sans streaming.
    """
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        response.raise_for_status()

        data = response.json()
        return data.get("response", "⚠️ Aucun contenu retourné par l'IA")

    except requests.exceptions.Timeout:
        return "⏳ Temps d'attente dépassé avec l'IA."

    except requests.exceptions.ConnectionError:
        return "❌ Impossible de se connecter à Ollama."

    except Exception as e:
        return f"⚠️ Erreur IA : {str(e)}"
