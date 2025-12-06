from rest_framework import serializers
from .models import CodeAnalysis, Resultat

class ResultatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resultat
        fields = ['id', 'code_analysis', 'changes_explained', 'best_practices', 'errors_corrected', 'created_at']
        read_only_fields = ['id', 'created_at']

class CodeAnalysisSerializer(serializers.ModelSerializer):
    resultat = ResultatSerializer(read_only=True)

    class Meta:
        model = CodeAnalysis
        fields = ['id', 'user', 'prompt', 'created_at', 'resultat']
        read_only_fields = ['id', 'created_at', 'resultat']
