# api/users/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, GoogleLoginSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            # Extraire le premier message d'erreur pour un affichage plus clair
            errors = serializer.errors
            
            # Déterminer le message principal
            if 'email' in errors:
                message = errors['email'][0] if isinstance(errors['email'], list) else errors['email']
            elif 'password' in errors:
                message = errors['password'][0] if isinstance(errors['password'], list) else errors['password']
            elif 'non_field_errors' in errors:
                message = errors['non_field_errors'][0] if isinstance(errors['non_field_errors'], list) else errors['non_field_errors']
            else:
                message = "Erreur de validation"
            
            return Response({
                'error': message,
                'details': errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

class GoogleLoginView(generics.GenericAPIView):
    serializer_class = GoogleLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer/récupérer l'utilisateur
        user = serializer.save()
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'message': 'Login Google réussi'
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveAPIView):
    """Récupère les infos de l'utilisateur authentifié"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class GetUsers(generics.ListAPIView):
    """Récupère la liste de tous les utilisateurs"""
    queryset = None
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        from .models import User
        return User.objects.all()
