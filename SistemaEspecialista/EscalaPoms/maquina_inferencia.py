import re
from typing import Dict, List, Tuple

def carregar_regras_classificacao_poms(caminho_arquivo: str) -> Dict[str, List[Tuple[float, float, str]]]:
    """
    Lê o arquivo de regras POMS e constrói intervalos de classificação para cada soma emocional.

    Retorna:
        Um dicionário que mapeia cada 'soma_<dominio>' para uma lista de tuplas:
        (min_inclusivo, max_inclusivo, rotulo_nivel)
    """
    mapa_intervalos: Dict[str, List[Tuple[float, float, str]]] = {}
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        texto_regras = arquivo.read()

    # Padrão para blocos de regra: nome, condição e conclusão
    padrao_bloco = re.compile(
        r"REGRA:\s*(?P<nome_regra>\w+)[\s\S]*?"
        r"SE\s*(?P<condicao>[^\n]+)[\s\S]*?"
        r"ENTAO\s*(?P<conclusao>[^\n]+)",
        re.MULTILINE
    )

    for bloco in padrao_bloco.finditer(texto_regras):
        texto_condicao = bloco.group('condicao').strip()
        texto_conclusao = bloco.group('conclusao').strip()

        # Processa apenas regras de classificação (conclusão começa com 'nivel_')
        if not texto_conclusao.startswith("nivel_"):
            continue

        # Extrai variável de nível e rótulo: 'nivel_tensao = Baixo'
        var_saida, rotulo_nivel = [parte.strip() for parte in texto_conclusao.split('=')]

        # Captura comparações, ex: ('soma_tensao','>','5')
        comparacoes = re.findall(r"(\w+)\s*(<=|>=|<|>)\s*(\d+(?:\.\d+)?)", texto_condicao)
        if not comparacoes:
            continue

        nome_variavel_soma = comparacoes[0][0]
        limites: Dict[str, float] = {}

        # Constrói limites mínimo e máximo conforme operadores
        for _, operador, valor_str in comparacoes:
            valor = float(valor_str)
            if operador in ('>=', '>'):
                limites['min'] = valor if operador == '>=' else valor + 1e-9
            else:
                limites['max'] = valor

        limite_min = limites.get('min', float('-inf'))
        limite_max = limites.get('max', float('inf'))

        mapa_intervalos.setdefault(nome_variavel_soma, []).append(
            (limite_min, limite_max, rotulo_nivel)
        )

    # Ordena intervalos de cada soma pelo limite mínimo
    for soma, lista_intervalos in mapa_intervalos.items():
        lista_intervalos.sort(key=lambda intervalo: intervalo[0])

    return mapa_intervalos


def carregar_sugestoes_treino_poms(caminho_arquivo: str) -> Dict[str, Dict[str, str]]:
    """
    Lê o arquivo de regras POMS e constrói o mapa de sugestões de treino.

    Retorna:
        Um dicionário onde cada chave é 'nivel_<dominio>' e o valor é outro dicionário
        mapeando rótulo de nível ('Baixo', 'Medio', etc.) para a string de sugestão de treino.
    """
    mapa_sugestoes: Dict[str, Dict[str, str]] = {}
    with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
        texto_regras = arquivo.read()

    padrao_bloco = re.compile(
        r"REGRA:\s*(?P<nome_regra>\w+)[\s\S]*?"
        r"SE\s*(?P<condicao>[^\n]+)[\s\S]*?"
        r"ENTAO\s*(?P<conclusao>.+)",
        re.MULTILINE
    )

    for bloco in padrao_bloco.finditer(texto_regras):
        texto_conclusao = bloco.group('conclusao').strip()

        # Processa apenas regras de sugestão (conclusão começa com 'sugestao_treino_')
        if not texto_conclusao.startswith("sugestao_treino_"):
            continue

        # Extrai variável de sugestão e texto: 'sugestao_treino_tensao = "..."'
        var_sugestao, texto_sugestao = texto_conclusao.split('=', 1)
        var_sugestao = var_sugestao.strip()
        texto_sugestao = texto_sugestao.strip().strip('"')

        # Extrai condição do nível: 'SE nivel_tensao = Baixo'
        texto_condicao = bloco.group('condicao').strip()
        match_nivel = re.match(r"(nivel_\w+)\s*=\s*(\w+)", texto_condicao)
        if not match_nivel:
            continue
        nome_variavel_nivel, rotulo_nivel = match_nivel.groups()

        mapa_sugestoes.setdefault(nome_variavel_nivel, {})[rotulo_nivel] = texto_sugestao

    return mapa_sugestoes


def classificar_e_recomendar_poms(caminho_arquivo_regras: str,
                                  somas_emocoes: Dict[str, float]) -> Dict[str, str]:
    """
    Realiza toda a inferência POMS:
      1. Classifica cada domínio em um nível ('nivel_*').
      2. A partir desses níveis, busca a sugestão de treino correspondente.

    Retorna:
        Um dicionário contendo:
        - Chaves 'nivel_<dominio>' com seus respectivos rótulos.
        - Chaves 'sugestao_treino_<dominio>' com a recomendação de treino.
    """
    # 1) Carrega e aplica classificação de níveis
    intervalos_classificacao = carregar_regras_classificacao_poms(caminho_arquivo_regras)
    niveis_resultantes: Dict[str, str] = {}

    for soma_nome, lista_intervalos in intervalos_classificacao.items():
        valor_soma = somas_emocoes.get(soma_nome)
        if valor_soma is None:
            continue
        for min_val, max_val, label in lista_intervalos:
            if min_val <= valor_soma <= max_val:
                nome_nivel = soma_nome.replace('soma_', 'nivel_')
                niveis_resultantes[nome_nivel] = label
                break

    # 2) Carrega mapa de sugestões e aplica
    mapa_sugestoes = carregar_sugestoes_treino_poms(caminho_arquivo_regras)
    recomendacoes_finais: Dict[str, str] = {}
    recomendacoes_finais.update(niveis_resultantes)

    for nome_nivel, label_nivel in niveis_resultantes.items():
        sugestoes_por_nivel = mapa_sugestoes.get(nome_nivel, {})
        texto_sugestao = sugestoes_por_nivel.get(label_nivel)
        if texto_sugestao:
            nome_sugestao = nome_nivel.replace('nivel_', 'sugestao_treino_')
            recomendacoes_finais[nome_sugestao] = texto_sugestao

    return recomendacoes_finais
