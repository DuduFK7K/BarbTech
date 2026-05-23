from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.views import (
    UserViewSet, EstabelecimentoViewSet, 
    ProfissionalViewSet, ServicoViewSet, ConviteViewSet
)
from scheduler.views import (
    AgendamentoViewSet, DisponibilidadeViewSet, BloqueioViewSet
)
from interactions.views import AvaliacaoViewSet, NotificacaoViewSet
from accounts.views import ClienteRegistrationView, ProfissionalRegistrationView

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'estabelecimentos', EstabelecimentoViewSet)
router.register(r'profissionais', ProfissionalViewSet)
router.register(r'servicos', ServicoViewSet)
router.register(r'convites', ConviteViewSet)
router.register(r'agendamentos', AgendamentoViewSet)
router.register(r'disponibilidades', DisponibilidadeViewSet)
router.register(r'bloqueios', BloqueioViewSet)
router.register(r'avaliacoes', AvaliacaoViewSet)
router.register(r'notificacoes', NotificacaoViewSet)

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/cliente/', ClienteRegistrationView.as_view(), name='register_cliente'),
    path('api/register/profissional/', ProfissionalRegistrationView.as_view(), name='register_profissional'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
