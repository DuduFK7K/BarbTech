from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Agendamento, Disponibilidade, Bloqueio
from .serializers import AgendamentoSerializer, DisponibilidadeSerializer, BloqueioSerializer
from .services import AppointmentService
from core.permissions import IsOwnerOrAdmin

class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            agendamento = AppointmentService.agendar(
                cliente=serializer.validated_data['cliente'],
                profissional=serializer.validated_data['profissional'],
                servico=serializer.validated_data['servico'],
                data_hora=serializer.validated_data['data_hora'],
                tipo_atendimento=serializer.validated_data['tipo_atendimento'],
                endereco=serializer.validated_data.get('endereco')
            )
            return Response(AgendamentoSerializer(agendamento).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DisponibilidadeViewSet(viewsets.ModelViewSet):
    queryset = Disponibilidade.objects.all()
    serializer_class = DisponibilidadeSerializer
    permission_classes = [IsAuthenticated]

class BloqueioViewSet(viewsets.ModelViewSet):
    queryset = Bloqueio.objects.all()
    serializer_class = BloqueioSerializer
    permission_classes = [IsAuthenticated]
