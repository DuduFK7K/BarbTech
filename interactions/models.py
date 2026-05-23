import uuid
from django.db import models
from django.conf import settings
from core.models import Profissional
from scheduler.models import Agendamento
from core.base_models import BaseModel

User = settings.AUTH_USER_MODEL

class Avaliacao(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avaliacoes_feitas')
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='avaliacoes_recebidas')
    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE, related_name='avaliacao')
    nota = models.IntegerField(help_text="1 a 5")
    comentario = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'avaliacoes'

class Notificacao(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    agendamento = models.ForeignKey(Agendamento, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=100)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)

    class Meta:
        db_table = 'notificacoes'
