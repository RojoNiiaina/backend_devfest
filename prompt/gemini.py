import os
import logging
from django.conf import settings
from google import genai

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash")

# Créer le client Gemini
client = None
if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(prompt: str) -> str:
    """
    Envoie un prompt à Gemini API et retourne la réponse.
    Sécurisé, avec gestion des erreurs.
    """
    try:
        if not client or not GEMINI_API_KEY:
            return "❌ Clé API Gemini non configurée."
        
        from .ai_identity import add_system_context, clean_response
        
        # Ajouter le contexte système
        enhanced_prompt = add_system_context(prompt)
        
        # Générer la réponse via l'API Gemini
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=enhanced_prompt,
        )
        
        # Nettoyer la réponse
        raw_response = response.text if response.text else "⚠️ Aucun contenu retourné par l'IA"
        cleaned = clean_response(raw_response)
        
        return cleaned

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Erreur Gemini API: {error_msg}", exc_info=True)
        
        if "API key" in error_msg or "authentication" in error_msg.lower() or "401" in error_msg:
            return "❌ Erreur d'authentification API Gemini."
        elif "timeout" in error_msg.lower():
            return "⏳ Temps d'attente dépassé avec l'IA."
        elif "connection" in error_msg.lower():
            return "❌ Impossible de se connecter à l'IA."
        else:
            return f"⚠️ Erreur IA : {error_msg}"

