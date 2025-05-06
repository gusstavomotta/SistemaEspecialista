from django.contrib import messages
from django.shortcuts import redirect
import os
import datetime
from django.conf import settings
from ..validators import converter_para_inteiro

def somar_campos_post(request, prefixo, quantidade=6):
    total = 0
    for i in range(1, quantidade + 1):
        campo = f'{prefixo}_{i}'
        valor = request.POST.get(campo)
        if valor is None or not valor.isdigit():
            raise ValueError(f"Valor inválido para {campo}.")
        total += int(valor)
    return total


def processar_dados_escala(request):
    soma_tensao      = somar_campos_post(request, 'tensao')
    soma_depressao   = somar_campos_post(request, 'depressao')
    soma_hostilidade = somar_campos_post(request, 'hostilidade')
    soma_fadiga      = somar_campos_post(request, 'fadiga')
    soma_confusao    = somar_campos_post(request, 'confusao')
    soma_vigor       = somar_campos_post(request, 'vigor')
    soma_desajuste   = somar_campos_post(request, 'desajuste')

    pth = ((soma_tensao + soma_depressao + soma_hostilidade +
            soma_fadiga + soma_confusao) - soma_vigor) + 100

    return {
        'soma_tensao': soma_tensao,
        'soma_depressao': soma_depressao,
        'soma_hostilidade': soma_hostilidade,
        'soma_fadiga': soma_fadiga,
        'soma_confusao': soma_confusao,
        'soma_vigor': soma_vigor,
        'soma_desajuste': soma_desajuste,
        'pth': pth,
        'sono': converter_para_inteiro(request.POST.get('sono')),
        'volume_treino': converter_para_inteiro(request.POST.get('volume_treino')),
        'freq_cardiaca_media': converter_para_inteiro(request.POST.get('freq_cardiaca_media')),
    }

def confirmar_treinador(aluno, request):
    from ..models import Treinador
    cpf_sel = request.POST.get('treinador')
    try:
        treinador = Treinador.objects.get(cpf=cpf_sel)
        aluno.treinador = treinador
        aluno.save()
        messages.success(request, "Treinador confirmado com sucesso!")
    except Treinador.DoesNotExist:
        messages.error(request, "Treinador inválido.")
    return redirect('escala')


def salvar_e_classificar_escala(aluno, request):
    from ..models import EscalaPoms, ClassificacaoRecomendacao
    from ..maquina_inferencia import classificar_niveis_emocoes
    try:
        dados = processar_dados_escala(request)
        observacoes = request.POST.get('observacoes', '').strip() or None

        # Cria a escala
        escala = EscalaPoms.objects.create(
            aluno=aluno,
            data=datetime.date.today(),
            observacoes=observacoes,
            **dados
        )

        # Monta dict de somas para passar ao motor de inferência
        somas = { f'soma_{k}': getattr(escala, f'soma_{k}') 
                  for k in ['tensao', 'depressao', 'hostilidade', 'fadiga', 'confusao', 'vigor', 'desajuste'] }

        # Classifica níveis
        regras = os.path.join(settings.BASE_DIR, 'EscalaPoms', 'regras.txt')
        niveis = classificar_niveis_emocoes(regras, somas)

        # Persiste classificação
        ClassificacaoRecomendacao.objects.create(
            escala=escala,
            nivel_tensao      = niveis['nivel_tensao'],
            nivel_depressao   = niveis['nivel_depressao'],
            nivel_hostilidade = niveis['nivel_hostilidade'],
            nivel_fadiga      = niveis['nivel_fadiga'],
            nivel_confusao    = niveis['nivel_confusao'],
            nivel_vigor       = niveis['nivel_vigor'],
            nivel_desajuste   = niveis['nivel_desajuste'],
        )

        messages.success(request, "Dados salvos e classificados com sucesso!")
        return redirect('home')

    except ValueError as ve:
        messages.error(request, str(ve))
        return redirect('escala')