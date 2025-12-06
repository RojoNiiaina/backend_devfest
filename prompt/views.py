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



def get_prompts_list(request):
    """Récupère l'historique des conversations groupées par utilisateur"""
    if request.method != "GET":
        return JsonResponse({"error": "Méthode non autorisée"}, status=405)
    
    try:
        # Récupérer les conversations groupées par utilisateur
        # Limiter aux 30 derniers jours
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        conversations = Prompt.objects.filter(
            created_at__gte=thirty_days_ago
        ).values('user').annotate(
            count=Count('id'),
            last_interaction=Max('created_at')
        ).order_by('-last_interaction')
        
        conversations_data = []
        
        for conv in conversations:
            user_id = conv['user']
            if user_id is None:
                continue
                
            # Récupérer les prompts de cet utilisateur
            user_prompts = Prompt.objects.filter(
                user_id=user_id,
                created_at__gte=thirty_days_ago
            ).order_by('-created_at')
            
            # Récupérer l'utilisateur
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                username = user.username or user.email
            except:
                username = f"User {user_id}"
            
            # Construire les détails de la conversation
            prompts_details = []
            for prompt in user_prompts[:5]:  # Limiter à 5 derniers prompts par utilisateur
                label = (prompt.original_text or prompt.input_text or "Sans titre")[:60]
                prompts_details.append({
                    'id': prompt.id,
                    'label': label,
                    'type': prompt.get_type_functionality_display(),
                    'created_at': prompt.created_at.isoformat()
                })
            
            conversations_data.append({
                'user_id': user_id,
                'username': username,
                'total_interactions': conv['count'],
                'last_interaction': conv['last_interaction'].isoformat(),
                'prompts': prompts_details
            })
        
        return JsonResponse({
            'success': True,
            'total_conversations': len(conversations_data),
            'conversations': conversations_data
        })
    
    except Exception as e:
        logger.error(f"Erreur get_prompts_list: {str(e)}", exc_info=True)
        return JsonResponse({"error": f"Erreur serveur: {str(e)}"}, status=500)
