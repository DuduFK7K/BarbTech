import uuid
from django.db import models
from django.conf import settings
from core.models import Profissional, Servico
from accounts.models import Endereco
from core.base_models import BaseModel
import datetime

User = settings.AUTH_USER_MODEL

class Disponibilidade(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='disponibilidades')
    dia_semana = models.IntegerField(help_text="0=Domingo, 6=Sábado")
    hora_inicio = models.TimeField()
    hora_fim = models.TimeField()

    class Meta:
        db_table = 'disponibilidades'

class Bloqueio(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='bloqueios')
    data_hora_inicio = models.DateTimeField()
    data_hora_fim = models.DateTimeField()

    class Meta:
        db_table = 'bloqueios'

class Agendamento(BaseModel):
    class StatusChoices(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        ACEITO = 'ACEITO', 'Aceito'
        RECUSADO = 'RECUSADO', 'Recusado'
        CANCELADO = 'CANCELADO', 'Cancelado'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'

    class TipoAtendimentoChoices(models.TextChoices):
        LOCAL = 'LOCAL', 'Local'
        DOMICILIO = 'DOMICILIO', 'Domicílio'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agendamentos_cliente')
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='agendamentos_profissional')
    servico = models.ForeignKey(Servico, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDENTE)
    tipo_atendimento = models.CharField(max_length=20, choices=TipoAtendimentoChoices.choices, default=TipoAtendimentoChoices.LOCAL)
    endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True, blank=True)
    data_hora = models.DateTimeField()
    data_hora_fim = models.DateTimeField(null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'agendamentos'
        unique_together = ('profissional', 'data_hora')

    def save(self, *args, **kwargs):
        if self.data_hora and hasattr(self, 'servico') and self.servico:
            self.data_hora_fim = self.data_hora + datetime.timedelta(minutes=self.servico.duracao_min)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Agendamento {self.id} - {self.status}"
