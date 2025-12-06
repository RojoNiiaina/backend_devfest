from django.db import models
from django.conf import settings


class Prompt(models.Model):
    FUNCTIONALITY_CHOICES = [
        ('F1', 'Sécurisation des prompts'),
        ('F2', 'Analyse de code'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prompts'
    )

    type_functionality = models.CharField(
        max_length=2,
        choices=FUNCTIONALITY_CHOICES,
        default='F1',
        help_text="F1 = sécurisation des prompts, F2 = analyse de code"
    )

    # F1 : sécurisation et amélioration
    original_text = models.TextField(blank=True, null=True, help_text="Texte original fourni par l'utilisateur")
    secured_text = models.TextField(blank=True, null=True, help_text="Texte sécurisé et amélioré par l'IA")
    risk_level = models.CharField(max_length=50, blank=True, null=True, help_text="Niveau de risque détecté")

    # F2 : analyse de code
    input_text = models.TextField(blank=True, null=True, help_text="Code et/ou prompt fourni par l'utilisateur")
    output_text = models.TextField(blank=True, null=True, help_text="Résultat généré par l'IA")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt {self.id} ({self.get_type_functionality_display()})"
