from rest_framework import serializers
from accounts.models import User, Cliente
from core.models import Profissional

class ClienteRegistrationSerializer(serializers.Serializer):
    user = serializers.JSONField()
    cpf = serializers.CharField(max_length=14, required=False, allow_blank=True)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    condicoes_especiais = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        # Create User
        user = User.objects.create_user(
            username=user_data.get('email'), # using email as username
            email=user_data.get('email'),
            password=user_data.get('password'),
            nome=user_data.get('first_name', ''),
            cpf=validated_data.get('cpf'),
            telefone=validated_data.get('telefone'),
            tipo=User.TipoChoices.CLIENTE
        )
        
        # Create Cliente Profile
        Cliente.objects.create(
            user=user, 
            condicoes_especiais=validated_data.get('condicoes_especiais')
        )
        
        return user

class ProfissionalRegistrationSerializer(serializers.Serializer):
    user = serializers.JSONField()
    cpf = serializers.CharField(max_length=14, required=False, allow_blank=True)
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    cnpj = serializers.CharField(max_length=18, required=False, allow_blank=True, allow_null=True)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        # Create User
        user = User.objects.create_user(
            username=user_data.get('email'),
            email=user_data.get('email'),
            password=user_data.get('password'),
            nome=user_data.get('first_name', ''),
            cpf=validated_data.get('cpf'),
            telefone=validated_data.get('telefone'),
            tipo=User.TipoChoices.PROFISSIONAL
        )
        
        # Create Profissional Profile
        Profissional.objects.create(
            user=user,
            cnpj=validated_data.get('cnpj')
        )
        
        return user
