from django.db import models
from users.models import User
from prompt.models import Prompt

class CodeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_analyses')
    prompt = models.OneToOneField(Prompt, on_delete=models.CASCADE, related_name='code_analysis')
    created_at = models.DateTimeField(auto_now_add=True)

class Resultat(models.Model):
    code_analysis = models.OneToOneField(CodeAnalysis, on_delete=models.CASCADE, related_name='resultat')
    changes_explained = models.TextField()
    best_practices = models.TextField(blank=True)
    errors_corrected = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Note(models.Model):
    resultat = models.ForeignKey(Resultat, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    language = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='note_images/', blank=True, null=True)

class QCM(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='qcms')
    question_text = models.TextField()

class Choice(models.Model):
    qcm = models.ForeignKey(QCM, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

class ResultatQCM(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resultats_qcm')
    qcm = models.ForeignKey(QCM, on_delete=models.CASCADE, related_name='resultats')
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
