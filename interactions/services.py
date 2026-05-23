from django.core.exceptions import ValidationError
from django.db.models import Avg, Count
from .models import Avaliacao
from scheduler.models import Agendamento

class ReviewService:
    @staticmethod
    def avaliar_agendamento(cliente, profissional, agendamento, nota, comentario=None):
        if agendamento.status != Agendamento.StatusChoices.CONCLUIDO:
            raise ValidationError("Apenas agendamentos concluídos podem ser avaliados.")
        
        if hasattr(agendamento, 'avaliacao'):
            raise ValidationError("Este agendamento já possui avaliação.")

        avaliacao = Avaliacao.objects.create(
            cliente=cliente,
            profissional=profissional,
            agendamento=agendamento,
            nota=nota,
            comentario=comentario
        )

        ReviewService.atualizar_score(profissional)
        return avaliacao

    @staticmethod
    def atualizar_score(profissional):
        aggs = Avaliacao.objects.filter(profissional=profissional).aggregate(
            media=Avg('nota'),
            total=Count('id')
        )
        profissional.score = aggs['media'] or 0.00
        profissional.total_avaliacoes = aggs['total'] or 0
        profissional.save()
