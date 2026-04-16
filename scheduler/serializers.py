from rest_framework import serializers
from .models import Agendamento, Disponibilidade, Bloqueio

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = '__all__'
        read_only_fields = ['valor', 'status']

class DisponibilidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disponibilidade
        fields = '__all__'

class BloqueioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bloqueio
        fields = '__all__'
