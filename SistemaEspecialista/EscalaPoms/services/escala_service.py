import os
import datetime

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

from ..validators import converter_para_inteiro
from ..models import EscalaPoms, ClassificacaoRecomendacao, Treinador
from ..maquina_inferencia import *

def somar_campos_post(request, prefixo: str, quantidade: int = 6) -> int:
    """
    Soma valores inteiros em campos POST sequenciais de um prefixo.

    Exemplo para prefixo='tensao' e quantidade=6 soma os campos:
      'tensao_1', 'tensao_2', ..., 'tensao_6'.

    Args:
        request: objeto HttpRequest com dados POST.
        prefixo: string base dos nomes dos campos.
        quantidade: número de campos a somar (padrão 6).

    Returns:
        Soma total dos valores inteiros encontrados.

    Raises:
        ValueError: se algum campo estiver faltando ou não for número.
    """
    total = 0
    for i in range(1, quantidade + 1):
        campo = f'{prefixo}_{i}'
        valor = request.POST.get(campo)
        if valor is None or not valor.isdigit():
            raise ValueError(f"Valor inválido para {campo}.")
        total += int(valor)
    return total


def processar_dados_escala(request) -> dict:
    """
    Extrai do request as somas dos domínios emocionais e dados adicionais.

    Calcula:
      - soma_tensao, soma_depressao, soma_hostilidade, soma_fadiga,
        soma_confusao, soma_vigor, soma_desajuste
      - pth conforme fórmula POMS
      - sono, volume_treino, freq_cardiaca_media convertidos para inteiro

    Args:
        request: objeto HttpRequest com POST e possivelmente FILES.

    Returns:
        Dicionário com todas as somas e métricas calculadas:
        {
            'soma_tensao': int,
            'soma_depressao': int,
            ...
            'pth': float,
            'sono': int,
            'volume_treino': int,
            'freq_cardiaca_media': int,
        }
    """
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


def salvar_e_classificar_escala(aluno, request):
    """
    Recebe dados do form de escala POMS, persiste no banco, classifica e grava recomendações.

    Fluxo:
      1. Processa dados brutos da escala via processar_dados_escala.
      2. Cria instância de EscalaPoms com esses dados.
      3. Prepara o dicionário de somas para inferência.
      4. Chama classificar_e_recomendar_poms para obter níveis e sugestões.
      5. Persiste ClassificacaoRecomendacao com todos os campos.

    Args:
        aluno: instância do modelo Aluno para associar a escala.
        request: HttpRequest contendo dados do formulário.

    Returns:
        HttpResponseRedirect para 'home' em caso de sucesso,
        ou para 'escala' em caso de erro, com mensagem apropriada.
    """
    campos_soma = ['tensao', 'depressao', 'hostilidade',
                   'fadiga', 'confusao', 'vigor', 'desajuste']
    try:
        dados = processar_dados_escala(request)
        observacoes = request.POST.get('observacoes', '').strip() or None

        # 1) Persiste Escala bruta
        escala = EscalaPoms.objects.create(
            aluno=aluno,
            data=datetime.datetime.now(),
            observacoes=observacoes,
            **dados
        )

        # 2) Extrai somas para a inferência
        somas = {
            f'soma_{campo}': getattr(escala, f'soma_{campo}')
            for campo in campos_soma
        }

        # 3) Aplica máquinas de regras POMS
        regras_path = os.path.join(settings.BASE_DIR, 'EscalaPoms', 'regras.txt')
        resultados = classificar_e_recomendar_poms(regras_path, somas)

        # 4) Persiste níveis e sugestões
        ClassificacaoRecomendacao.objects.create(
            escala=escala,
            nivel_tensao      = resultados.get('nivel_tensao'),
            nivel_depressao   = resultados.get('nivel_depressao'),
            nivel_hostilidade = resultados.get('nivel_hostilidade'),
            nivel_fadiga      = resultados.get('nivel_fadiga'),
            nivel_confusao    = resultados.get('nivel_confusao'),
            nivel_vigor       = resultados.get('nivel_vigor'),
            nivel_desajuste   = resultados.get('nivel_desajuste'),
            sugestao_treino_tensao      = resultados.get('sugestao_treino_tensao'),
            sugestao_treino_depressao   = resultados.get('sugestao_treino_depressao'),
            sugestao_treino_hostilidade = resultados.get('sugestao_treino_hostilidade'),
            sugestao_treino_fadiga      = resultados.get('sugestao_treino_fadiga'),
            sugestao_treino_confusao    = resultados.get('sugestao_treino_confusao'),
            sugestao_treino_vigor       = resultados.get('sugestao_treino_vigor'),
        )

        messages.success(request, "Dados salvos, classificados e recomendados com sucesso!")
        return redirect('home')

    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao salvar e classificar a escala: {e}")
        return redirect('escala')


def confirmar_treinador(aluno, request):
    """
    Valida e atualiza o treinador de um aluno.

    Args:
        aluno: instância do modelo Aluno a ter o treinador alterado.
        request: HttpRequest contendo o CPF do treinador no POST.

    Returns:
        HttpResponseRedirect para 'escala' com mensagem de sucesso ou erro.
    """
    cpf_selecionado = request.POST.get('treinador')
    try:
        treinador = Treinador.objects.get(cpf=cpf_selecionado)
        aluno.treinador = treinador
        aluno.save()
        messages.success(request, "Treinador confirmado com sucesso!")
    except Treinador.DoesNotExist:
        messages.error(request, "Treinador inválido.")
    return redirect('escala')
