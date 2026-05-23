import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from core.base_models import BaseModel

class Endereco(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rua = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    cliente = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True, related_name='enderecos')
    estabelecimento = models.ForeignKey('core.Estabelecimento', on_delete=models.CASCADE, null=True, blank=True, related_name='enderecos')
    profissional = models.ForeignKey('core.Profissional', on_delete=models.CASCADE, null=True, blank=True, related_name='enderecos')

    class Meta:
        db_table = 'enderecos'

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.cidade}"

class User(AbstractUser):
    class TipoChoices(models.TextChoices):
        CLIENTE = 'CLIENTE', 'Cliente'
        PROFISSIONAL = 'PROFISSIONAL', 'Profissional'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    tipo = models.CharField(max_length=20, choices=TipoChoices.choices, default=TipoChoices.CLIENTE)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    rg = models.CharField(max_length=20, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email

class Cliente(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente_profile')
    condicoes_especiais = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return str(self.user)
