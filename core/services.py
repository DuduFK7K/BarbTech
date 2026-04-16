from django.core.exceptions import ValidationError
from django.db.models import Avg, Count
from .models import Convite, Profissional

# Nota: Importações lazy para interactions se necessário ou tratar diretamente
class ProfissionalService:
    pass


class InviteService:
    @staticmethod
    def convidar_profissional(estabelecimento, profissional_convidado):
        if Convite.objects.filter(estabelecimento=estabelecimento, profissional=profissional_convidado, status=Convite.StatusChoices.PENDENTE).exists():
            raise ValidationError("Já existe um convite pendente para este profissional.")

        return Convite.objects.create(
            estabelecimento=estabelecimento,
            profissional=profissional_convidado,
            status=Convite.StatusChoices.PENDENTE
        )

    @staticmethod
    def responder_convite(convite, aceito=True):
        if convite.status != Convite.StatusChoices.PENDENTE:
            raise ValidationError("Convite não está pendente.")

        if aceito:
            convite.status = Convite.StatusChoices.ACEITO
            profissional = convite.profissional
            profissional.estabelecimento = convite.estabelecimento
            profissional.cargo = Profissional.CargoChoices.FUNCIONARIO
            profissional.save()
        else:
            convite.status = Convite.StatusChoices.RECUSADO
        
        convite.save()
        return convite
