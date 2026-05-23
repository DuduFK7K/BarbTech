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
        fields = ['id', 'estabelecimento', 'profissional', 'nome', 'descricao', 'duracao_min', 'preco', 'ativo']
        read_only_fields = ['id']

    def validate(self, attrs):
        # Se for uma criação e o usuário for um profissional autenticado, assume que será vinculado a ele
        request = self.context.get('request')
        is_profissional = request and request.user.is_authenticated and hasattr(request.user, 'profissional_profile')
        
        if not attrs.get('estabelecimento') and not attrs.get('profissional') and not is_profissional:
            raise serializers.ValidationError("O serviço deve estar vinculado a um estabelecimento ou a um profissional.")
        return attrs

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
        source='servicos',
        required=False
    )
    class Meta:
        model = Profissional
        fields = [
            'id', 'user', 'estabelecimento', 'servicos', 'servico_ids', 'cargo', 'is_vip', 
            'atende_domicilio', 'raio_km', 'score', 'total_avaliacoes', 
            'cnpj', 'foto_perfil', 'foto_banner'
        ]
        read_only_fields = ['id', 'score', 'total_avaliacoes']
        
class ConviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convite
        fields = '__all__'
