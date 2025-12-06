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
        email = data.get('email')
        password = data.get('password')
        
        # Vérifier si l'utilisateur existe
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                "email": "Aucun compte n'existe avec cet email"
            })
        
        # Vérifier le mot de passe
        if not user.check_password(password):
            raise serializers.ValidationError({
                "password": "Mot de passe incorrect"
            })
        
        # Vérifier si le compte est actif
        if not user.is_active:
            raise serializers.ValidationError({
                "non_field_errors": "Ce compte a été désactivé"
            })
        
        return user

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
