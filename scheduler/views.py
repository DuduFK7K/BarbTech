from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from .models import Agendamento, Disponibilidade, Bloqueio
from .serializers import AgendamentoSerializer, DisponibilidadeSerializer, BloqueioSerializer
from .services import AppointmentService
from core.permissions import IsOwnerOrAdmin

class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.none()
        
        if self.request.user.is_superuser:
            profissional_id = self.request.query_params.get('profissional')
            if profissional_id:
                queryset = queryset.filter(profissional_id=profissional_id)
            return queryset
            
        if self.request.user.tipo == 'PROFISSIONAL':
            try:
                profile = self.request.user.profissional_profile
                queryset = queryset.filter(profissional=profile)
            except Exception:
                return queryset.none()
        else: # CLIENTE
            queryset = queryset.filter(cliente=self.request.user)
            
        return queryset

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
    filterset_fields = ['profissional']

    @action(detail=False, methods=['post'], url_path='bulk-update')
    def bulk_update(self, request):
        """
        Recebe um array de dias da semana e horários para atualizar a agenda do profissional.
        """
        try:
            profissional = request.user.profissional_profile
        except Exception:
            return Response({"detail": "Apenas profissionais podem editar sua agenda."}, status=status.HTTP_403_FORBIDDEN)
        
        # O frontend envia algo como: [{nome: 'Segunda', inicio: '09:00', fim: '18:00', fechado: false}, ...]
        agenda_data = request.data
        if not isinstance(agenda_data, list):
            return Response({"detail": "Dados devem ser uma lista."}, status=status.HTTP_400_BAD_REQUEST)

        # Mapeamento de nome do dia para o índice do banco (opcional, ou podemos usar o dia_semana direto)
        dias_map = {
            'Segunda': 1, 'Terça': 2, 'Quarta': 3, 'Quinta': 4, 'Sexta': 5, 'Sábado': 6, 'Domingo': 0
        }

        # Limpa agenda anterior
        Disponibilidade.objects.filter(profissional=profissional).delete()

        novas_disponibilidades = []
        for item in agenda_data:
            if item.get('fechado'):
                continue
            
            dia_nome = item.get('nome')
            dia_idx = dias_map.get(dia_nome, item.get('dia_semana'))
            
            if dia_idx is None:
                continue

            novas_disponibilidades.append(Disponibilidade(
                profissional=profissional,
                dia_semana=dia_idx,
                hora_inicio=item.get('inicio'),
                hora_fim=item.get('fim')
            ))
        
        Disponibilidade.objects.bulk_create(novas_disponibilidades)
        return Response({"detail": "Agenda atualizada com sucesso."}, status=status.HTTP_200_OK)

class BloqueioViewSet(viewsets.ModelViewSet):
    queryset = Bloqueio.objects.all()
    serializer_class = BloqueioSerializer
    permission_classes = [IsAuthenticated]
