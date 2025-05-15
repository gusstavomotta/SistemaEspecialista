import re
from django.forms import ValidationError


def normalizar_cpf(cpf: str) -> str:
    """
    Remove todos os caracteres não numéricos de um CPF.

    Args:
        cpf: string contendo CPF com ou sem pontuação.

    Returns:
        String apenas com os 11 dígitos numéricos.
    """
    return re.sub(r"\D", "", cpf or "")


def validar_cpf(cpf: str) -> str:
    """
    Valida a estrutura de um CPF, incluindo os dígitos verificadores.

    Args:
        cpf: string contendo CPF (com ou sem formatação).

    Returns:
        CPF normalizado (somente números) se válido.

    Raises:
        ValidationError: se o CPF for inválido.
    """
    cpf = normalizar_cpf(cpf)

    # Verificação de tamanho e repetição
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        raise ValidationError("CPF inválido.")

    # Validação do primeiro dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10

    # Validação do segundo dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10

    if cpf[-2:] != f"{digito1}{digito2}":
        raise ValidationError("CPF inválido.")

    return cpf


def validar_numero_telefone(telefone: str) -> str:
    """
    Valida e normaliza número de telefone brasileiro (10 ou 11 dígitos).

    Args:
        telefone: string com número de telefone.

    Returns:
        Número contendo apenas dígitos se válido, ou string vazia se inválido.
    """
    telefone_normalizado = re.sub(r"\D", "", telefone or "")
    if len(telefone_normalizado) in (10, 11):
        return telefone_normalizado
    return ""


def converter_para_inteiro(valor):
    """
    Converte uma string numérica para inteiro, se possível.

    Args:
        valor: string contendo dígitos.

    Returns:
        Inteiro convertido ou None se o valor for nulo ou inválido.
    """
    return int(valor) if valor and valor.isdigit() else None
