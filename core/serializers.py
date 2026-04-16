from rest_framework import serializers
from .models import Estabelecimento, Profissional, Convite, Servico
from accounts.models import User, Endereco

class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nome', 'email', 'cpf', 'rg', 'tipo', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = '__all__'

class EstabelecimentoSerializer(serializers.ModelSerializer):
    servicos = ServicoSerializer(many=True, read_only=True)
    class Meta:
        model = Estabelecimento
        fields = '__all__'

class ProfissionalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    servicos = ServicoSerializer(many=True, read_only=True)
    servico_ids = serializers.PrimaryKeyRelatedField(
        queryset=Servico.objects.all(),
        many=True,
        write_only=True,
        source='servicos'
    )
    class Meta:
        model = Profissional
        fields = '__all__'
        
class ConviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convite
        fields = '__all__'
