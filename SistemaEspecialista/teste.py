import re
from typing import Dict, List, Tuple

# Função para carregar e interpretar regras POMS de um arquivo de texto

def carregar_regras_poms(caminho_arquivo: str) -> Dict[str, List[Tuple[float, float, str]]]:
    """
    Lê o arquivo de regras POMS e retorna um mapa:
      chave: nome da variável de soma (ex: 'soma_tensao')
      valor: lista de tuplas (min_inclusivo, max_inclusivo, rotulo)
    """
    mapa_intervalos: Dict[str, List[Tuple[float, float, str]]] = {}
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        texto_regras = arquivo.read()

    # Regex para capturar cada bloco de 'REGRA', sua condição e conclusão
    regex_bloco = re.compile(
        r"REGRA:\s*(?P<nome_regra>\w+)"           # nome da regra
        r"[\s\S]*?SE\s*(?P<condicao>[^\n]+)"     # parte da condição
        r"[\s\S]*?ENTAO\s*(?P<conclusao>[^\n]+)",# parte da conclusão
        re.MULTILINE
    )

    for bloco in regex_bloco.finditer(texto_regras):
        condicao_texto = bloco.group('condicao').strip()
        conclusao_texto = bloco.group('conclusao').strip()

        # Extrair variável de saída e rótulo: 'nivel_tensao = Baixo'
        variavel_saida, rotulo_saida = [item.strip() for item in conclusao_texto.split('=')]

        # Extrair comparações na condição: ex 'soma_tensao > 5 E soma_tensao <= 10'
        comparacoes = re.findall(r"(\w+)\s*(<=|>=|<|>)\s*(\d+(?:\.\d+)?)", condicao_texto)
        if not comparacoes:
            continue

        nome_variavel_soma = comparacoes[0][0]
        limites_temp: Dict[str, float] = {}
        for _, operador, valor_str in comparacoes:
            valor = float(valor_str)
            if operador in ('>=', '>'):
                limites_temp['min'] = valor if operador == '>=' else valor + 1e-9
            else:
                limites_temp['max'] = valor

        min_inclusivo = limites_temp.get('min', float('-inf'))
        max_inclusivo = limites_temp.get('max', float('inf'))

        mapa_intervalos.setdefault(nome_variavel_soma, []).append(
            (min_inclusivo, max_inclusivo, rotulo_saida)
        )

    # Ordenar os intervalos de cada variável de soma pelo limite mínimo
    for variavel_soma, lista_intervalos in mapa_intervalos.items():
        lista_intervalos.sort(key=lambda intervalo: intervalo[0])

    return mapa_intervalos


# Função para classificar níveis emocionais usando arquivo de regras POMS

def classificar_niveis_emocoes(caminho_arquivo_regras: str,
                                somas_emocoes: Dict[str, float]) -> Dict[str, str]:
    """
    Carrega regras de um arquivo POMS e recebe dicionário:
      'soma_tensao': float, 'soma_depressao': float, ...
    Retorna dicionário:
      'nivel_tensao': rotulo, 'nivel_depressao': rotulo, ...
    """
    mapa_intervalos = carregar_regras_poms(caminho_arquivo_regras)
    niveis_resultantes: Dict[str, str] = {}

    for nome_soma, intervalos in mapa_intervalos.items():
        valor_soma = somas_emocoes.get(nome_soma)
        if valor_soma is None:
            continue

        # Encontrar intervalo cuja faixa contenha o valor_soma
        for limite_min, limite_max, rotulo in intervalos:
            if limite_min <= valor_soma <= limite_max:
                nome_nivel = nome_soma.replace('soma_', 'nivel_')
                niveis_resultantes[nome_nivel] = rotulo
                break

    return niveis_resultantes


# Exemplo de utilização
if __name__ == '__main__':
    # Definir caminho para o arquivo de regras POMS
    arquivo_regras_poms = 'regras.txt'

    # Dicionário com as somas de cada domínio emocional
    somas_por_dominio = {
        'soma_tensao': 22.0,
        'soma_depressao': 23.0,
        'soma_hostilidade': 18.0,
        'soma_fadiga': 22.0,
        'soma_confusao': 17.0,
        'soma_vigor': 22.0,
        'soma_desajuste': 24.0
    }

    niveis_emocionais = classificar_niveis_emocoes(arquivo_regras_poms, somas_por_dominio)
    for nivel, rotulo in niveis_emocionais.items():
        print(f"{nivel}: {rotulo}")
