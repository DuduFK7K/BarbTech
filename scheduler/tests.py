from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
import datetime

from accounts.models import User
from core.models import Estabelecimento, Servico, Profissional
from scheduler.models import Agendamento, Disponibilidade
from scheduler.services import AppointmentService

class AppointmentServiceTest(TestCase):
    def setUp(self):
        # Criação dos usuários mockados
        self.cliente = User.objects.create_user(
            username='cliente1', email='cliente@teste.com', 
            password='senha', nome='Cliente 1', tipo=User.TipoChoices.CLIENTE
        )
        self.user_pro = User.objects.create_user(
            username='pro1', email='pro@teste.com', 
            password='senha', nome='Profissional 1', tipo=User.TipoChoices.PROFISSIONAL
        )

        # setup das instâncias principais dependentes
        self.estabelecimento = Estabelecimento.objects.create(nome="Barbearia Teste")
        self.servico = Servico.objects.create(
            estabelecimento=self.estabelecimento,
            nome="Corte",
            duracao_min=30,
            preco=50.00
        )
        self.profissional = Profissional.objects.create(
            user=self.user_pro,
            estabelecimento=self.estabelecimento
        )
        self.profissional.servicos.add(self.servico)

        # Resgatar data futura para evitar falhas de timestamp
        agora = timezone.localtime()
        dia_amanha = agora + datetime.timedelta(days=1)
        self.data_hora_teste = dia_amanha.replace(
            hour=10, minute=0, second=0, microsecond=0
        )

        # Recuperar dia da semana mapeado para a disponibilidade (0=Domingo..6=Sábado)
        dia_semana_model = int(self.data_hora_teste.strftime('%w'))

        self.disponibilidade = Disponibilidade.objects.create(
            profissional=self.profissional,
            dia_semana=dia_semana_model,
            hora_inicio=datetime.time(9, 0),
            hora_fim=datetime.time(18, 0)
        )

    def test_agendamento_com_sucesso(self):
        agendamento = AppointmentService.agendar(
            cliente=self.cliente,
            profissional=self.profissional,
            servico=self.servico,
            data_hora=self.data_hora_teste,
            tipo_atendimento=Agendamento.TipoAtendimentoChoices.LOCAL
        )
        
        self.assertEqual(agendamento.cliente, self.cliente)
        self.assertEqual(agendamento.servico, self.servico)
        self.assertEqual(agendamento.valor, self.servico.preco)
        self.assertEqual(agendamento.status, Agendamento.StatusChoices.PENDENTE)
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_agendamento_sem_disponibilidade(self):
        # Tenta agendar num horário sem disponibilidade ativa (ex: 8h da manhã que está fora do range 9h-18h)
        data_hora_fora = self.data_hora_teste.replace(hour=8, minute=0)
        
        with self.assertRaisesMessage(ValidationError, "não atende neste horário"):
            AppointmentService.agendar(
                cliente=self.cliente,
                profissional=self.profissional,
                servico=self.servico,
                data_hora=data_hora_fora,
                tipo_atendimento=Agendamento.TipoAtendimentoChoices.LOCAL
            )

    def test_agendamento_conflito(self):
        # Insere o primeiro agendamento na base (sucesso)
        AppointmentService.agendar(
            cliente=self.cliente,
            profissional=self.profissional,
            servico=self.servico,
            data_hora=self.data_hora_teste,
            tipo_atendimento=Agendamento.TipoAtendimentoChoices.LOCAL
        )

        # Tenta marcar exatamente no mesmo espaço para provar o bloqueio de sobreposição (Race condition handler test)
        with self.assertRaisesMessage(ValidationError, "já possui um agendamento"):
            AppointmentService.agendar(
                cliente=self.cliente,
                profissional=self.profissional,
                servico=self.servico,
                data_hora=self.data_hora_teste,
                tipo_atendimento=Agendamento.TipoAtendimentoChoices.LOCAL
            )
