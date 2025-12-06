from .gemini import ask_gemini
from .security import sanitize_prompt
from .models import Prompt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def ai_prompt(request):
    if request.method != "POST":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)

    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()
        ftype = data.get("type_functionality", "F1")

        if not text:
            return JsonResponse({"error": "Le texte du prompt est vide"}, status=400)

        # Nettoyage du prompt pour sécurité
        clean_text = sanitize_prompt(text)

        # Création du prompt dans la base de données
        prompt = Prompt.objects.create(
            user=request.user if request.user.is_authenticated else None,
            type_functionality=ftype,
            original_text=clean_text if ftype == "F1" else None,
            input_text=clean_text if ftype == "F2" else None
        )

        # Envoi à Gemini
        result = ask_gemini(clean_text)

        # Mise à jour du prompt avec le résultat
        if ftype == "F1":
            prompt.secured_text = result
        else:
            prompt.output_text = result

        prompt.save()

        return JsonResponse({
            "success": True,
            "result": result
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalide"}, status=400)
    except Exception as e:
        logger.error(f"Erreur ai_prompt: {str(e)}", exc_info=True)
        return JsonResponse({"error": f"Erreur serveur: {str(e)}"}, status=500)
