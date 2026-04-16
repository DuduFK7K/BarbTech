from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Estabelecimento, Profissional, Convite, Servico
from accounts.models import User
from .serializers import (
    EstabelecimentoSerializer, ProfissionalSerializer,
    ConviteSerializer, ServicoSerializer, UserSerializer
)
from .permissions import IsAdminEstabelecimento
from .services import InviteService

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]

class EstabelecimentoViewSet(viewsets.ModelViewSet):
    queryset = Estabelecimento.objects.all()
    serializer_class = EstabelecimentoSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], permission_classes=[IsAdminEstabelecimento])
    def convidar(self, request, pk=None):
        estabelecimento = self.get_object()
        profissional_id = request.data.get('profissional_id')
        try:
            profissional = Profissional.objects.get(id=profissional_id)
            convite = InviteService.convidar_profissional(estabelecimento, profissional)
            return Response(ConviteSerializer(convite).data, status=status.HTTP_201_CREATED)
        except Profissional.DoesNotExist:
            return Response({"detail": "Profissional não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer
    filterset_fields = ['is_vip', 'atende_domicilio', 'estabelecimento']
    search_fields = ['user__nome']
    ordering_fields = ['score']

class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer
    permission_classes = [IsAuthenticated]

class ConviteViewSet(viewsets.ModelViewSet):
    queryset = Convite.objects.all()
    serializer_class = ConviteSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def responder(self, request, pk=None):
        convite = self.get_object()
        aceito = request.data.get('aceito', True)
        
        try:
            convite = InviteService.responder_convite(convite, aceito=aceito)
            return Response(ConviteSerializer(convite).data)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
