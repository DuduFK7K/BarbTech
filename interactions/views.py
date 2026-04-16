from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Avaliacao, Notificacao
from .serializers import AvaliacaoSerializer, NotificacaoSerializer
from .services import ReviewService

class AvaliacaoViewSet(viewsets.ModelViewSet):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            avaliacao = ReviewService.avaliar_agendamento(
                cliente=serializer.validated_data['cliente'],
                profissional=serializer.validated_data['profissional'],
                agendamento=serializer.validated_data['agendamento'],
                nota=serializer.validated_data['nota'],
                comentario=serializer.validated_data.get('comentario')
            )
            return Response(AvaliacaoSerializer(avaliacao).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class NotificacaoViewSet(viewsets.ModelViewSet):
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
