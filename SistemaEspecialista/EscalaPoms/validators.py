import re

def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf or ''))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10

    return cpf[-2:] == f'{digito1}{digito2}'


def validar_numero_telefone(telefone: str) -> bool:
    telefone = re.sub(r'\D', '', telefone or '')
    return len(telefone) in (10, 11)


def normalizar_cpf(texto: str) -> str:
    return re.sub(r'\D', '', texto or '')

def converter_para_inteiro(valor):
    return int(valor) if valor and valor.isdigit() else None
