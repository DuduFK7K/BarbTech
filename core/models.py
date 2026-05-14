import uuid
from django.db import models
from django.conf import settings
from .base_models import BaseModel

User = settings.AUTH_USER_MODEL

class Estabelecimento(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    fotos = models.JSONField(blank=True, null=True, help_text="URLs de fotos")

    class Meta:
        db_table = 'estabelecimentos'

    def __str__(self):
        return self.nome

class Servico(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.CASCADE, related_name='servicos', null=True, blank=True)
    profissional = models.ForeignKey('Profissional', on_delete=models.CASCADE, related_name='servicos_proprios', null=True, blank=True)
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    duracao_min = models.IntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    ativo = models.BooleanField(default=True)

    class Meta:
        db_table = 'servicos'

    def __str__(self):
        owner = self.estabelecimento.nome if self.estabelecimento else (self.profissional.user.nome if self.profissional else 'Sem dono')
        return f"{self.nome} - {owner}"

class Profissional(BaseModel):
    class CargoChoices(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        FUNCIONARIO = 'FUNCIONARIO', 'Funcionário'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profissional_profile')
    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.SET_NULL, null=True, blank=True, related_name='profissionais')
    servicos = models.ManyToManyField(Servico, related_name='profissionais', blank=True)
    cargo = models.CharField(max_length=20, choices=CargoChoices.choices, default=CargoChoices.FUNCIONARIO)
    is_vip = models.BooleanField(default=False)
    atende_domicilio = models.BooleanField(default=False)
    raio_km = models.IntegerField(default=0)
    score = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_avaliacoes = models.IntegerField(default=0)
    cnpj = models.CharField(max_length=18, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='profissionais/perfil/', null=True, blank=True)
    foto_banner = models.ImageField(upload_to='profissionais/banner/', null=True, blank=True)

    class Meta:
        db_table = 'profissionais'

    def __str__(self):
        return str(self.user)

class Convite(BaseModel):
    class StatusChoices(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        ACEITO = 'ACEITO', 'Aceito'
        RECUSADO = 'RECUSADO', 'Recusado'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estabelecimento = models.ForeignKey(Estabelecimento, on_delete=models.CASCADE, related_name='convites')
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE, related_name='convites_recebidos')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDENTE)
    expira_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'convites'

    def __str__(self):
        return f"Convite para {self.profissional} em {self.estabelecimento}"
