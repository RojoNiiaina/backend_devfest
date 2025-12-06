import os
from django.conf import settings
import google.generativeai as genai


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = getattr(settings, "GEMINI_MODEL", "gemini-3-pro-preview")

# Configurer l'API Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def ask_gemini(prompt: str) -> str:
    """
    Envoie un prompt à Gemini API et retourne la réponse.
    Sécurisé, avec gestion des erreurs.
    """
    try:
        if not GEMINI_API_KEY:
            return "❌ Clé API Gemini non configurée."
        
        from .ai_identity import add_system_context, clean_response
        
        # Ajouter le contexte système
        enhanced_prompt = add_system_context(prompt)
        
        # Créer le modèle et générer la réponse
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(enhanced_prompt)
        
        # Nettoyer la réponse
        raw_response = response.text if response.text else "⚠️ Aucun contenu retourné par l'IA"
        cleaned = clean_response(raw_response)
        
        return cleaned

    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg or "authentication" in error_msg.lower():
            return "❌ Erreur d'authentification API Gemini."
        elif "timeout" in error_msg.lower():
            return "⏳ Temps d'attente dépassé avec l'IA."
        elif "connection" in error_msg.lower():
            return "❌ Impossible de se connecter à l'IA."
        else:
            return f"⚠️ Erreur IA : {error_msg}"