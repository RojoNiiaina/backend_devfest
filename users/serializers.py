# api/users/serializers.py
from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from google.auth.transport import requests
from google.oauth2 import id_token
import os
from dotenv import load_dotenv

load_dotenv()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Email ou mot de passe incorrect")

class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate_token(self, value):
        """Valide le token Google et retourne les infos utilisateur"""
        try:
            CLIENT_ID = os.getenv('ID_CLIENT')
            
            # Vérifier le token avec Google
            idinfo = id_token.verify_oauth2_token(value, requests.Request(), CLIENT_ID)
            
            # Vérifier que le token n'est pas expiré
            if idinfo['aud'] != CLIENT_ID:
                raise ValueError('Token audience mismatch')
            
            return idinfo
        except ValueError as e:
            raise serializers.ValidationError(f"Token Google invalide: {str(e)}")
        except Exception as e:
            raise serializers.ValidationError(f"Erreur lors de la validation du token: {str(e)}")

    def create(self, validated_data):
        """Crée ou récupère l'utilisateur depuis les infos Google"""
        idinfo = validated_data['token']
        
        email = idinfo.get('email')
        name = idinfo.get('name', email.split('@')[0])
        
        # Créer ou récupérer l'utilisateur
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': name,
                'is_active': True
            }
        )
        
        return user
