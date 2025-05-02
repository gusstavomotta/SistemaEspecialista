from .models import Treinador, Aluno
import re

def converter_para_inteiro(valor):

    return int(valor) if valor and valor.isdigit() else None

def somar_campos_post(request, prefixo, quantidade=6):

    total = 0
    for i in range(1, quantidade + 1):
        valor_campo = request.POST.get(f'{prefixo}_{i}')
        if valor_campo is None or not valor_campo.isdigit():
            raise ValueError(f"Valor inválido para {prefixo}_{i}.")
        total += int(valor_campo)
    return total

def processar_dados_escala(request):

    soma_tensao = somar_campos_post(request, 'tensao')
    soma_depressao = somar_campos_post(request, 'depressao')
    soma_hostilidade = somar_campos_post(request, 'hostilidade')
    soma_fadiga = somar_campos_post(request, 'fadiga')
    soma_confusao = somar_campos_post(request, 'confusao')
    soma_vigor = somar_campos_post(request, 'vigor')
    soma_desajuste = somar_campos_post(request, 'desajuste')

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

def obter_usuario_por_cpf(cpf):

    try:
        return Treinador.objects.get(cpf=cpf)
    except Treinador.DoesNotExist:
        return Aluno.objects.get(cpf=cpf)

def validar_cpf(cpf: str) -> bool:

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

    telefone = re.sub(r'\D', '', telefone)
    return len(telefone) in (10, 11)

def normalizar_cpf(texto: str) -> str:
    return re.sub(r'\D', '', texto or '')