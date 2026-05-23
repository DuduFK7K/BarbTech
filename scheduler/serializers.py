from rest_framework import serializers
from .models import Agendamento, Disponibilidade, Bloqueio
from core.serializers import UserSerializer, ServicoSerializer

class AgendamentoSerializer(serializers.ModelSerializer):
    cliente_detalhes = UserSerializer(source='cliente', read_only=True)
    servico_detalhes = ServicoSerializer(source='servico', read_only=True)

    class Meta:
        model = Agendamento
        fields = ['id', 'cliente', 'profissional', 'servico', 'status', 'tipo_atendimento', 'endereco', 'data_hora', 'data_hora_fim', 'valor', 'cliente_detalhes', 'servico_detalhes']
        read_only_fields = ['valor', 'status']

class DisponibilidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disponibilidade
        fields = '__all__'

class BloqueioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bloqueio
        fields = '__all__'
