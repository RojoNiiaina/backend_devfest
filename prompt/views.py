from .gemini import ask_gemini
from .security import sanitize_prompt
from .models import Prompt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required


@csrf_exempt
def ai_prompt(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text")
        ftype = data.get("type_functionality", "F1")

        clean_text = sanitize_prompt(text)

        prompt = Prompt.objects.create(
            user=request.user if request.user.is_authenticated else None,
            type_functionality=ftype,
            original_text=clean_text if ftype == "F1" else None,
            input_text=clean_text if ftype == "F2" else None
        )

        result = ask_gemini(clean_text)

        if ftype == "F1":
            prompt.secured_text = result
        else:
            prompt.output_text = result

        prompt.save()

        return JsonResponse({
            "success": True,
            "result": result
        })

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)
