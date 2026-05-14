from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db import transaction
import datetime
from .models import Agendamento, Bloqueio, Disponibilidade

class AppointmentService:
    @staticmethod
    def validar_disponibilidade(profissional, data_hora, duracao_min):
        """Verifica se o profissional está disponível no horário solicitado."""
        
        # 1. Verificar horário de expediente
        data_hora_local = timezone.localtime(data_hora)
        dia_semana_model = int(data_hora_local.strftime('%w'))

        hora_inicio_solicitada = data_hora_local.time()
        hora_fim_solicitada = (data_hora_local + datetime.timedelta(minutes=duracao_min)).time()

        # Checa se existe disponibilidade registrada
        disponibilidade = Disponibilidade.objects.filter(
            profissional=profissional,
            dia_semana=dia_semana_model,
            hora_inicio__lte=hora_inicio_solicitada,
            hora_fim__gte=hora_fim_solicitada
        ).exists()

        if not disponibilidade:
            raise ValidationError("O profissional não atende neste horário ou não tem disponibilidade cadastrada.")

        return True

    @staticmethod
    def validar_conflitos(profissional, data_hora, duracao_min):
        """Impede marcação no mesmo horário de bloqueios ou agendamentos já confirmados/pendentes."""
        data_hora_fim = data_hora + datetime.timedelta(minutes=duracao_min)

        # 1. Checar bloqueios manuais
        conflito_bloqueios = Bloqueio.objects.filter(
            profissional=profissional,
            data_hora_inicio__lt=data_hora_fim,
            data_hora_fim__gt=data_hora
        ).exists()

        if conflito_bloqueios:
            raise ValidationError("Existe um bloqueio de agenda neste horário.")

        # 2. Checar outros agendamentos (pendentes e aceitos)
        conflito_agendamentos = Agendamento.objects.filter(
            profissional=profissional,
            status__in=[Agendamento.StatusChoices.PENDENTE, Agendamento.StatusChoices.ACEITO],
            data_hora__lt=data_hora_fim,
            data_hora_fim__gt=data_hora
        ).exists()

        if conflito_agendamentos:
            raise ValidationError("O profissional já possui um agendamento neste horário.")

        return True

    @classmethod
    def agendar(cls, cliente, profissional, servico, data_hora, tipo_atendimento, endereco=None):
        with transaction.atomic():
            # Bloqueio pessimista para evitar double booking
            profissional_locked = profissional.__class__.objects.select_for_update().get(id=profissional.id)

            cls.validar_disponibilidade(profissional_locked, data_hora, servico.duracao_min)
            cls.validar_conflitos(profissional_locked, data_hora, servico.duracao_min)

            # O valor é salvo snapshot
            agendamento = Agendamento.objects.create(
                cliente=cliente,
                profissional=profissional_locked,
                servico=servico,
                data_hora=data_hora,
                tipo_atendimento=tipo_atendimento,
                endereco=endereco,
                valor=servico.preco,
                status=Agendamento.StatusChoices.PENDENTE
            )
            return agendamento
