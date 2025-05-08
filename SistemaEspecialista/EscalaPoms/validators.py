import re
from django.forms import ValidationError

def normalizar_cpf(cpf: str) -> str:
    return re.sub(r'\D', '', cpf or '')

def validar_cpf(cpf: str) -> str:
    cpf = normalizar_cpf(cpf)

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError("CPF inválido.")

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10

    if cpf[-2:] != f'{digito1}{digito2}':
        raise ValidationError("CPF inválido.")

    return cpf

def validar_numero_telefone(telefone: str) -> str:
    telefone_normalizado = re.sub(r'\D', '', telefone or '')
    if len(telefone_normalizado) in (10, 11):
        return telefone_normalizado
    return ''  

def converter_para_inteiro(valor):
    return int(valor) if valor and valor.isdigit() else None

