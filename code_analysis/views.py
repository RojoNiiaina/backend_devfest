from rest_framework import viewsets, permissions
from .models import CodeAnalysis, Resultat
from .serializers import CodeAnalysisSerializer, ResultatSerializer

class CodeAnalysisViewSet(viewsets.ModelViewSet):
    queryset = CodeAnalysis.objects.all()
    serializer_class = CodeAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

class ResultatViewSet(viewsets.ModelViewSet):
    queryset = Resultat.objects.all()
    serializer_class = ResultatSerializer
    permission_classes = [permissions.IsAuthenticated]
