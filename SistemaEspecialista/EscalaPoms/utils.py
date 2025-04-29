from .models import Treinador, Aluno
import re

def converter_para_inteiro(valor):

    return int(valor) if valor and valor.isdigit() else None

def somar_campos_post(request, prefixo, quantidade=6):
    """
    Soma os valores dos campos enviados via POST com o prefixo especificado.
    Exemplo: Para o prefixo 'tensao', soma os campos tensao_1 até tensao_6.
    """
    total = 0
    for i in range(1, quantidade + 1):
        valor_campo = request.POST.get(f'{prefixo}_{i}')
        if valor_campo is None or not valor_campo.isdigit():
            raise ValueError(f"Valor inválido para {prefixo}_{i}.")
        total += int(valor_campo)
    return total

def processar_dados_escala(request):
    """
    Processa e retorna os dados da escala em forma de dicionário para salvamento.
    """
    soma_tensao = somar_campos_post(request, 'tensao')
    soma_depressao = somar_campos_post(request, 'depressao')
    soma_hostilidade = somar_campos_post(request, 'hostilidade')
    soma_fadiga = somar_campos_post(request, 'fadiga')
    soma_confusao = somar_campos_post(request, 'confusao')
    soma_vigor = somar_campos_post(request, 'vigor')
    soma_desajuste = somar_campos_post(request, 'desajuste')

    pth = ((soma_tensao + soma_depressao + soma_hostilidade +
           soma_fadiga + soma_confusao) - soma_vigor) + 100

    sono = converter_para_inteiro(request.POST.get('sono'))
    volume_treino = converter_para_inteiro(request.POST.get('volume_treino'))
    freq_cardiaca_media = converter_para_inteiro(request.POST.get('freq_cardiaca_media'))

    return {
        'somaTensao': soma_tensao,
        'somaDepressao': soma_depressao,
        'somaHostilidade': soma_hostilidade,
        'somaFadiga': soma_fadiga,
        'somaConfusao': soma_confusao,
        'somaVigor': soma_vigor,
        'somaDesajuste': soma_desajuste,
        'pth': pth,
        'sono': sono,
        'volume_treino': volume_treino,
        'freq_cardiaca_media': freq_cardiaca_media,
    }

def obter_url_dashboard(cpf):
    """
    Retorna a URL do dashboard de acordo com o tipo de usuário (Treinador ou Aluno).
    """
    if Treinador.objects.filter(cpf=cpf).exists():
        return 'home_treinador'
    if Aluno.objects.filter(cpf=cpf).exists():
        return 'home_aluno'
    return None

def obter_usuario_por_cpf(cpf):
    """
    Retorna o usuário correspondente ao CPF, buscando primeiramente entre Treinadores e,
    se não encontrado, entre Alunos.
    """
    try:
        return Treinador.objects.get(cpf=cpf)
    except Treinador.DoesNotExist:
        return Aluno.objects.get(cpf=cpf)

def validar_cpf(cpf: str) -> bool:
    """
    Valida um CPF brasileiro.
    Remove caracteres não numéricos, verifica se o CPF tem 11 dígitos,
    se não é uma sequência repetida e se os dígitos verificadores estão corretos.
    """
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * len(cpf):
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10

    return cpf[-2:] == f'{digito1}{digito2}'

def validar_numero_telefone(telefone: str) -> bool:
    """
    Valida o número de telefone.
    Remove tudo que não seja dígito e verifica se o número possui 10 ou 11 dígitos.
    """
    telefone = re.sub(r'\D', '', telefone)
    return len(telefone) in (10, 11)