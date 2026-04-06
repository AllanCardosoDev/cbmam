"""
═══════════════════════════════════════════════════════════════════════════════
DASHBOARD TAF - Sistema Interativo de Análise de Teste de Aptidão Física
Corpo de Bombeiros Militar do Amazonas | 2026
═══════════════════════════════════════════════════════════════════════════════
Adaptado da estrutura robusta do projeto CBMAM com integração das regras
de pontuação por faixa etária e sexo.
═══════════════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys

# ══════════════════════════════════════════════════════════════════════════════
# IMAGEM CBMAM (agora buscando direto da internet)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def _get_cbmam_image_url() -> str:
    """Retorna a URL de uma imagem CBMAM diretamente da internet."""
    # Exemplo de URL de uma imagem CBMAM (substitua por uma URL real se tiver uma preferência)
    return (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/"
        "Bras%C3%A3o_do_Corpo_de_Bombeiros_Militar_do_Amazonas.svg/"
        "200px-Bras%C3%A3o_do_Corpo_de_Bombeiros_Militar_do_Amazonas.svg.png"
    )

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES DE TEMA PARA PLOTLY
# ══════════════════════════════════════════════════════════════════════════════
DARK = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": "#e7eefc",
}
GRID = {
    "showgrid": True,
    "gridwidth": 1,
    "gridcolor": "#334155",
    "zeroline": True,
    "zerolinewidth": 1,
    "zerolinecolor": "#334155",
}

# ══════════════════════════════════════════════════════════════════════════════
# REGRAS DE PONTUAÇÃO DO TAF (Baseadas nas tabelas fornecidas)
# ══════════════════════════════════════════════════════════════════════════════

# Dicionários com as regras de pontuação para cada exercício, sexo e faixa etária
# A estrutura é: {sexo: {exercicio: {faixa_idade: {valor_minimo: nota}}}}

# Masculino
REGRAS_MASCULINO = {
    'CORRIDA': {
        '18-24': {3200: 10, 3000: 9, 2800: 8, 2600: 7, 2400: 6, 2200: 5, 2000: 4, 1800: 3, 1600: 2, 1400: 1, 0: 0},
        '25-29': {3000: 10, 2800: 9, 2600: 8, 2400: 7, 2200: 6, 2000: 5, 1800: 4, 1600: 3, 1400: 2, 1200: 1, 0: 0},
        '30-34': {2800: 10, 2600: 9, 2400: 8, 2200: 7, 2000: 6, 1800: 5, 1600: 4, 1400: 3, 1200: 2, 1000: 1, 0: 0},
        '35-39': {2600: 10, 2400: 9, 2200: 8, 2000: 7, 1800: 6, 1600: 5, 1400: 4, 1200: 3, 1000: 2, 800: 1, 0: 0},
        '40-44': {2400: 10, 2200: 9, 2000: 8, 1800: 7, 1600: 6, 1400: 5, 1200: 4, 1000: 3, 800: 2, 600: 1, 0: 0},
        '45-49': {2200: 10, 2000: 9, 1800: 8, 1600: 7, 1400: 6, 1200: 5, 1000: 4, 800: 3, 600: 2, 400: 1, 0: 0},
        '50-54': {2000: 10, 1800: 9, 1600: 8, 1400: 7, 1200: 6, 1000: 5, 800: 4, 600: 3, 400: 2, 200: 1, 0: 0},
        '55+':   {1800: 10, 1600: 9, 1400: 8, 1200: 7, 1000: 6, 800: 5, 600: 4, 400: 3, 200: 2, 100: 1, 0: 0}
    },
    'FLEXAO': {
        '18-24': {40: 10, 36: 9, 32: 8, 28: 7, 24: 6, 20: 5, 16: 4, 12: 3, 8: 2, 4: 1, 0: 0},
        '25-29': {38: 10, 34: 9, 30: 8, 26: 7, 22: 6, 18: 5, 14: 4, 10: 3, 6: 2, 2: 1, 0: 0},
        '30-34': {36: 10, 32: 9, 28: 8, 24: 7, 20: 6, 16: 5, 12: 4, 8: 3, 4: 2, 1: 1, 0: 0},
        '35-39': {34: 10, 30: 9, 26: 8, 22: 7, 18: 6, 14: 5, 10: 4, 6: 3, 2: 2, 1: 1, 0: 0},
        '40-44': {32: 10, 28: 9, 24: 8, 20: 7, 16: 6, 12: 5, 8: 4, 4: 3, 1: 2, 0: 1, 0: 0}, # Ajuste para 0:1 se 0 for o mínimo para 1 ponto
        '45-49': {30: 10, 26: 9, 22: 8, 18: 7, 14: 6, 10: 5, 6: 4, 2: 3, 1: 2, 0: 1, 0: 0},
        '50-54': {28: 10, 24: 9, 20: 8, 16: 7, 12: 6, 8: 5, 4: 4, 1: 3, 0: 2, 0: 1, 0: 0},
        '55+':   {26: 10, 22: 9, 18: 8, 14: 7, 10: 6, 6: 5, 2: 4, 1: 3, 0: 2, 0: 1, 0: 0}
    },
    'ABDOMINAL': {
        '18-24': {45: 10, 40: 9, 35: 8, 30: 7, 25: 6, 20: 5, 15: 4, 10: 3, 5: 2, 1: 1, 0: 0},
        '25-29': {42: 10, 37: 9, 32: 8, 27: 7, 22: 6, 17: 5, 12: 4, 7: 3, 2: 2, 1: 1, 0: 0},
        '30-34': {39: 10, 34: 9, 29: 8, 24: 7, 19: 6, 14: 5, 9: 4, 4: 3, 1: 2, 0: 1, 0: 0},
        '35-39': {36: 10, 31: 9, 26: 8, 21: 7, 16: 6, 11: 5, 6: 4, 1: 3, 0: 2, 0: 1, 0: 0},
        '40-44': {33: 10, 28: 9, 23: 8, 18: 7, 13: 6, 8: 5, 3: 4, 1: 3, 0: 2, 0: 1, 0: 0},
        '45-49': {30: 10, 25: 9, 20: 8, 15: 7, 10: 6, 5: 5, 1: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '50-54': {27: 10, 22: 9, 17: 8, 12: 7, 7: 6, 2: 5, 1: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '55+':   {24: 10, 19: 9, 14: 8, 9: 7, 4: 6, 1: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0}
    },
    'BARRA': { # Adaptei para repetições, se for tempo, precisa ajustar
        '18-24': {10: 10, 9: 9, 8: 8, 7: 7, 6: 6, 5: 5, 4: 4, 3: 3, 2: 2, 1: 1, 0: 0},
        '25-29': {9: 10, 8: 9, 7: 8, 6: 7, 5: 6, 4: 5, 3: 4, 2: 3, 1: 2, 0: 1, 0: 0},
        '30-34': {8: 10, 7: 9, 6: 8, 5: 7, 4: 6, 3: 5, 2: 4, 1: 3, 0: 2, 0: 1, 0: 0},
        '35-39': {7: 10, 6: 9, 5: 8, 4: 7, 3: 6, 2: 5, 1: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '40-44': {6: 10, 5: 9, 4: 8, 3: 7, 2: 6, 1: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '45-49': {5: 10, 4: 9, 3: 8, 2: 7, 1: 6, 0: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '50-54': {4: 10, 3: 9, 2: 8, 1: 7, 0: 6, 0: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '55+':   {3: 10, 2: 9, 1: 8, 0: 7, 0: 6, 0: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0}
    },
    'NATACAO': { # Adaptei para segundos (tempo), se for distância, precisa ajustar
        '18-24': {40: 10, 45: 9, 50: 8, 55: 7, 60: 6, 65: 5, 70: 4, 75: 3, 80: 2, 85: 1, 999: 0}, # Menor tempo = maior nota
        '25-29': {42: 10, 47: 9, 52: 8, 57: 7, 62: 6, 67: 5, 72: 4, 77: 3, 82: 2, 87: 1, 999: 0},
        '30-34': {44: 10, 49: 9, 54: 8, 59: 7, 64: 6, 69: 5, 74: 4, 79: 3, 84: 2, 89: 1, 999: 0},
        '35-39': {46: 10, 51: 9, 56: 8, 61: 7, 66: 6, 71: 5, 76: 4, 81: 3, 86: 2, 91: 1, 999: 0},
        '40-44': {48: 10, 53: 9, 58: 8, 63: 7, 68: 6, 73: 5, 78: 4, 83: 3, 88: 2, 93: 1, 999: 0},
        '45-49': {50: 10, 55: 9, 60: 8, 65: 7, 70: 6, 75: 5, 80: 4, 85: 3, 90: 2, 95: 1, 999: 0},
        '50-54': {52: 10, 57: 9, 62: 8, 67: 7, 72: 6, 77: 5, 82: 4, 87: 3, 92: 2, 97: 1, 999: 0},
        '55+':   {54: 10, 59: 9, 64: 8, 69: 7, 74: 6, 79: 5, 84: 4, 89: 3, 94: 2, 99: 1, 999: 0}
    }
}

# Feminino
REGRAS_FEMININO = {
    'CORRIDA': {
        '18-24': {2800: 10, 2600: 9, 2400: 8, 2200: 7, 2000: 6, 1800: 5, 1600: 4, 1400: 3, 1200: 2, 1000: 1, 0: 0},
        '25-29': {2600: 10, 2400: 9, 2200: 8, 2000: 7, 1800: 6, 1600: 5, 1400: 4, 1200: 3, 1000: 2, 800: 1, 0: 0},
        '30-34': {2400: 10, 2200: 9, 2000: 8, 1800: 7, 1600: 5, 1400: 4, 1200: 3, 1000: 2, 800: 1, 600: 0, 0: 0},
        '35-39': {2200: 10, 2000: 9, 1800: 8, 1600: 7, 1400: 6, 1200: 5, 1000: 4, 800: 3, 600: 2, 400: 1, 0: 0},
        '40-44': {2000: 10, 1800: 9, 1600: 8, 1400: 7, 1200: 6, 1000: 5, 800: 4, 600: 3, 400: 2, 200: 1, 0: 0},
        '45-49': {1800: 10, 1600: 9, 1400: 8, 1200: 7, 1000: 6, 800: 5, 600: 4, 400: 3, 200: 2, 100: 1, 0: 0},
        '50-54': {1600: 10, 1400: 9, 1200: 8, 1000: 7, 800: 6, 600: 5, 400: 4, 200: 3, 100: 2, 50: 1, 0: 0},
        '55+':   {1400: 10, 1200: 9, 1000: 8, 800: 7, 600: 6, 400: 5, 200: 4, 100: 3, 50: 2, 25: 1, 0: 0}
    },
    'FLEXAO': { # Adaptei para repetições, se for tempo, precisa ajustar
        '18-24': {30: 10, 27: 9, 24: 8, 21: 7, 18: 6, 15: 5, 12: 4, 9: 3, 6: 2, 3: 1, 0: 0},
        '25-29': {28: 10, 25: 9, 22: 8, 19: 7, 16: 6, 13: 5, 10: 4, 7: 3, 4: 2, 1: 1, 0: 0},
        '30-34': {26: 10, 23: 9, 20: 8, 17: 7, 14: 6, 11: 5, 8: 4, 5: 3, 2: 2, 1: 1, 0: 0},
        '35-39': {24: 10, 21: 9, 18: 8, 15: 7, 12: 6, 9: 5, 6: 4, 3: 3, 1: 2, 0: 1, 0: 0},
        '40-44': {22: 10, 19: 9, 16: 8, 13: 7, 10: 6, 7: 5, 4: 4, 1: 3, 0: 2, 0: 1, 0: 0},
        '45-49': {20: 10, 17: 9, 14: 8, 11: 7, 8: 6, 5: 5, 2: 4, 1: 3, 0: 2, 0: 1, 0: 0},
        '50-54': {18: 10, 15: 9, 12: 8, 9: 7, 6: 6, 3: 5, 1: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '55+':   {16: 10, 13: 9, 10: 8, 7: 7, 4: 6, 1: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0}
    },
    'ABDOMINAL': {
        '18-24': {40: 10, 35: 9, 30: 8, 25: 7, 20: 6, 15: 5, 10: 4, 5: 3, 1: 2, 0: 1, 0: 0},
        '25-29': {37: 10, 32: 9, 27: 8, 22: 7, 17: 6, 12: 5, 7: 4, 2: 3, 1: 2, 0: 1, 0: 0},
        '30-34': {34: 10, 29: 9, 24: 8, 19: 7, 14: 6, 9: 5, 4: 4, 1: 3, 0: 2, 0: 1, 0: 0},
        '35-39': {31: 10, 26: 9, 21: 8, 16: 7, 11: 6, 6: 5, 1: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '40-44': {28: 10, 23: 9, 18: 8, 13: 7, 8: 6, 3: 5, 1: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '45-49': {25: 10, 20: 9, 15: 8, 10: 7, 5: 6, 1: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '50-54': {22: 10, 17: 9, 12: 8, 7: 7, 2: 6, 1: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '55+':   {19: 10, 14: 9, 9: 8, 4: 7, 1: 6, 0: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0}
    },
    'BARRA': { # Adaptei para repetições, se for tempo, precisa ajustar
        '18-24': {8: 10, 7: 9, 6: 8, 5: 7, 4: 6, 3: 5, 2: 4, 1: 3, 0: 2, 0: 1, 0: 0},
        '25-29': {7: 10, 6: 9, 5: 8, 4: 7, 3: 6, 2: 5, 1: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '30-34': {6: 10, 5: 9, 4: 8, 3: 7, 2: 6, 1: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '35-39': {5: 10, 4: 9, 3: 8, 2: 7, 1: 6, 0: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '40-44': {4: 10, 3: 9, 2: 8, 1: 7, 0: 6, 0: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '45-49': {3: 10, 2: 9, 1: 8, 0: 7, 0: 6, 0: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '50-54': {2: 10, 1: 9, 0: 8, 0: 7, 0: 6, 0: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0},
        '55+':   {1: 10, 0: 9, 0: 8, 0: 7, 0: 6, 0: 5, 0: 4, 0: 3, 0: 2, 0: 1, 0: 0}
    },
    'NATACAO': { # Adaptei para segundos (tempo), se for distância, precisa ajustar
        '18-24': {45: 10, 50: 9, 55: 8, 60: 7, 65: 6, 70: 5, 75: 4, 80: 3, 85: 2, 90: 1, 999: 0},
        '25-29': {47: 10, 52: 9, 57: 8, 62: 7, 67: 6, 72: 5, 77: 4, 82: 3, 87: 2, 92: 1, 999: 0},
        '30-34': {49: 10, 54: 9, 59: 8, 64: 7, 69: 6, 74: 5, 79: 4, 84: 3, 89: 2, 94: 1, 999: 0},
        '35-39': {51: 10, 56: 9, 61: 8, 66: 7, 71: 6, 76: 5, 81: 4, 86: 3, 91: 2, 96: 1, 999: 0},
        '40-44': {53: 10, 58: 9, 63: 8, 68: 7, 73: 6, 78: 5, 83: 4, 88: 3, 93: 2, 98: 1, 999: 0},
        '45-49': {55: 10, 60: 9, 65: 8, 70: 7, 75: 6, 80: 5, 85: 4, 90: 3, 95: 2, 100: 1, 999: 0},
        '50-54': {57: 10, 62: 9, 67: 8, 72: 7, 77: 6, 82: 5, 87: 4, 92: 3, 97: 2, 102: 1, 999: 0},
        '55+':   {59: 10, 64: 9, 69: 8, 74: 7, 79: 6, 84: 5, 89: 4, 94: 3, 99: 2, 104: 1, 999: 0}
    }
}

# Mapeamento de faixas etárias
FAIXAS_ETARIAS = {
    (18, 24): '18-24',
    (25, 29): '25-29',
    (30, 34): '30-34',
    (35, 39): '35-39',
    (40, 44): '40-44',
    (45, 49): '45-49',
    (50, 54): '50-54',
    (55, 150): '55+' # Idade máxima razoável
}

def get_faixa_etaria(idade):
    for (min_idade, max_idade), faixa in FAIXAS_ETARIAS.items():
        if min_idade <= idade <= max_idade:
            return faixa
    return None # Caso a idade não se encaixe em nenhuma faixa

def calcular_nota(exercicio, valor, idade, sexo):
    faixa_etaria = get_faixa_etaria(idade)
    if not faixa_etaria:
        return 0 # Idade fora das faixas definidas

    regras = REGRAS_MASCULINO if sexo == 'Masculino' else REGRAS_FEMININO
    regras_exercicio = regras.get(exercicio)

    if not regras_exercicio or faixa_etaria not in regras_exercicio:
        return 0 # Regras não encontradas para o exercício/faixa etária

    pontuacoes = regras_exercicio[faixa_etaria]

    # Para corrida, flexão, abdominal e barra (maior valor = maior nota)
    if exercicio in ['CORRIDA', 'FLEXAO', 'ABDOMINAL', 'BARRA']:
        for limite, nota in sorted(pontuacoes.items(), reverse=True):
            if valor >= limite:
                return nota
    # Para natação (menor tempo = maior nota)
    elif exercicio == 'NATACAO':
        for limite, nota in sorted(pontuacoes.items(), key=lambda item: item[0]): # Ordena por limite crescente
            if valor <= limite:
                return nota
    return 0 # Valor não atingiu nenhuma pontuação mínima

# ══════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO E PRÉ-PROCESSAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    # Carrega os dados dos militares
    df_militares = pd.read_csv('militaresALL.csv', encoding='utf-8')
    # Renomear colunas para facilitar o merge e padronizar
    df_militares = df_militares.rename(columns={
        'MATRICULA': 'matricula',
        'SEXO': 'sexo',
        'DATA_NASCIMENTO': 'data_nascimento'
    })
    # Converte 'data_nascimento' para datetime e calcula a idade
    df_militares['data_nascimento'] = pd.to_datetime(df_militares['data_nascimento'], format='%d/%m/%Y', errors='coerce')
    df_militares['idade'] = (datetime.now().year - df_militares['data_nascimento'].dt.year).astype(int)

    # Carrega os dados das avaliações do TAF
    df_avaliacoes = pd.read_csv('taf_avaliacoes.csv', encoding='utf-8')

    # Merge dos DataFrames para adicionar informações de sexo e idade às avaliações
    df_all = pd.merge(df_avaliacoes, df_militares[['matricula', 'sexo', 'idade']], on='matricula', how='left')

    # Preencher sexo e idade para dados que não encontraram correspondência (ex: TAF Adaptado ou dados fictícios)
    # Para o propósito deste exemplo, vamos gerar sexo e idade aleatórios para os que faltam
    # Em um cenário real, você buscaria essas informações ou as marcaria como ausentes.
    df_all['sexo'] = df_all['sexo'].fillna(np.random.choice(['Masculino', 'Feminino'], size=df_all['sexo'].isnull().sum()))
    df_all['idade'] = df_all['idade'].fillna(np.random.randint(20, 50, size=df_all['idade'].isnull().sum())).astype(int)

    # Limpeza e padronização de colunas
    df_all['atividade'] = df_all['atividade'].str.upper().str.strip()
    df_all['sexo'] = df_all['sexo'].replace({'M': 'Masculino', 'F': 'Feminino'})

    # Identifica os exercícios de TAF padrão
    exercicios_padrao = ['CORRIDA', 'FLEXAO', 'ABDOMINAL', 'BARRA', 'NATACAO']

    # Inicializa colunas de notas e valores brutos
    for ex in exercicios_padrao:
        df_all[f'NOTA_{ex}'] = 0
        df_all[f'{ex}_RAW'] = np.nan

    # Processa cada linha para aplicar as regras de pontuação
    for index, row in df_all.iterrows():
        atividade = row['atividade']
        valor = row['valor']
        idade = row['idade']
        sexo = row['sexo']

        if atividade in exercicios_padrao:
            df_all.loc[index, f'{atividade}_RAW'] = valor
            df_all.loc[index, f'NOTA_{atividade}'] = calcular_nota(atividade, valor, idade, sexo)
        else:
            # Para TAF Adaptado, ou outras atividades, a pontuação pode ser diferente
            # Por simplicidade, vamos considerar 10 para 'resultado_ok' e 0 caso contrário
            # ou um valor específico se 'atividade' for um exercício adaptado com pontuação direta
            if row['resultado_ok'] == 'sim':
                df_all.loc[index, f'NOTA_{atividade}'] = 10
            else:
                df_all.loc[index, f'NOTA_{atividade}'] = 0

    # Calcula a média final apenas para os exercícios padrão
    df_all['MEDIA_FINAL'] = df_all[[f'NOTA_{ex}' for ex in exercicios_padrao]].mean(axis=1).round(2)

    # Classificação
    df_all['CLASSIFICACAO'] = df_all['MEDIA_FINAL'].apply(
        lambda x: 'APTO' if x >= 5 else 'INAPTO'
    )

    return df_all, exercicios_padrao

df_all, exercicios_padrao = load_data()

# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT APP
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Dashboard TAF CBMAM",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS para estilo
st.markdown(
    """
    <style>
    .st-emotion-cache-1dp5vir .dataframe {
        background-color: #1e293b;
        color: #e7eefc;
        border: 1px solid #334155;
    }
    .st-emotion-cache-1dp5vir .dataframe th {
        background-color: #1e293b;
        color: #e7eefc;
        border-bottom: 1px solid #334155;
    }
    .st-emotion-cache-1dp5vir .dataframe td {
        border-bottom: 1px solid #334155;
    }
    .st-emotion-cache-1dp5vir .dataframe tr:hover {
        background-color: #334155;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.image(_get_cbmam_image_url(), use_column_width=True)
    st.title("Filtros do Dashboard")

    # Filtro por Sexo
    sexo_options = ['Todos'] + list(df_all['sexo'].unique())
    selected_sexo = st.selectbox("Filtrar por Sexo", sexo_options)

    # Filtro por Idade
    min_idade, max_idade = int(df_all['idade'].min()), int(df_all['idade'].max())
    selected_idade_range = st.slider(
        "Filtrar por Idade",
        min_value=min_idade,
        max_value=max_idade,
        value=(min_idade, max_idade)
    )

    # Filtro por Posto
    posto_options = ['Todos'] + list(df_all['posto'].unique())
    selected_posto = st.selectbox("Filtrar por Posto", posto_options)

    # Filtro por OBM
    obm_options = ['Todos'] + list(df_all['obm'].unique())
    selected_obm = st.selectbox("Filtrar por OBM", obm_options)

    # Filtro por Classificação
    classificacao_options = ['Todos'] + list(df_all['CLASSIFICACAO'].unique())
    selected_classificacao = st.selectbox("Filtrar por Classificação", classificacao_options)

# Aplicar filtros
filtered_df = df_all.copy()
if selected_sexo != 'Todos':
    filtered_df = filtered_df[filtered_df['sexo'] == selected_sexo]
filtered_df = filtered_df[
    (filtered_df['idade'] >= selected_idade_range[0]) &
    (filtered_df['idade'] <= selected_idade_range[1])
]
if selected_posto != 'Todos':
    filtered_df = filtered_df[filtered_df['posto'] == selected_posto]
if selected_obm != 'Todos':
    filtered_df = filtered_df[filtered_df['obm'] == selected_obm]
if selected_classificacao != 'Todos':
    filtered_df = filtered_df[filtered_df['CLASSIFICACAO'] == selected_classificacao]

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT PRINCIPAL DO DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
st.title("📊 Dashboard de Avaliação TAF CBMAM")
st.markdown("Este dashboard apresenta uma análise detalhada do Teste de Aptidão Física (TAF) dos militares do CBMAM, incluindo pontuações baseadas em idade e sexo.")

st.subheader("Visão Geral dos Militares Avaliados")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Militares Avaliados", filtered_df['matricula'].nunique())
with col2:
    st.metric("Média Geral de Pontuação", f"{filtered_df['MEDIA_FINAL'].mean():.2f}")
with col3:
    st.metric("Militares Aptos", filtered_df[filtered_df['CLASSIFICACAO'] == 'APTO']['matricula'].nunique())
with col4:
    st.metric("Militares Inaptos", filtered_df[filtered_df['CLASSIFICACAO'] == 'INAPTO']['matricula'].nunique())

st.markdown("---")

# Gráfico de Distribuição de Classificação
st.subheader("Distribuição de Classificação (Apto/Inapto)")
classificacao_counts = filtered_df['CLASSIFICACAO'].value_counts().reset_index()
classificacao_counts.columns = ['Classificacao', 'Quantidade']
fig_class = px.pie(
    classificacao_counts,
    values='Quantidade',
    names='Classificacao',
    title='Proporção de Militares Aptos e Inaptos',
    color='Classificacao',
    color_discrete_map={'APTO': '#22c55e', 'INAPTO': '#ef4444'}
)
fig_class.update_layout(**DARK)
st.plotly_chart(fig_class, use_container_width=True)

st.markdown("---")

# Desempenho por Exercício (Notas)
st.subheader("Desempenho Médio por Exercício (Notas)")
# Calcular a média das notas para cada exercício padrão
avg_notas_exercicios = {
    ex: filtered_df[f'NOTA_{ex}'].mean() for ex in exercicios_padrao if f'NOTA_{ex}' in filtered_df.columns
}
df_avg_notas = pd.DataFrame(list(avg_notas_exercicios.items()), columns=['Exercício', 'Nota Média'])

fig_notas = px.bar(
    df_avg_notas,
    x='Exercício',
    y='Nota Média',
    title='Nota Média por Exercício',
    color='Nota Média',
    color_continuous_scale=px.colors.sequential.Plasma
)
fig_notas.update_layout(**DARK, yaxis=dict(**GRID))
st.plotly_chart(fig_notas, use_container_width=True)

st.markdown("---")

# Desempenho por Posto e Sexo
st.subheader("Desempenho Médio por Posto e Sexo")
if not filtered_df.empty:
    desempenho_posto_sexo = filtered_df.groupby(['posto', 'sexo'])['MEDIA_FINAL'].mean().reset_index()
    fig_posto_sexo = px.bar(
        desempenho_posto_sexo,
        x='posto',
        y='MEDIA_FINAL',
        color='sexo',
        barmode='group',
        title='Média Final por Posto e Sexo',
        labels={'MEDIA_FINAL': 'Média Final', 'posto': 'Posto', 'sexo': 'Sexo'},
        color_discrete_map={'Masculino': '#3b82f6', 'Feminino': '#ec4899'}
    )
    fig_posto_sexo.update_layout(**DARK, xaxis=dict(**GRID, tickangle=-45), yaxis=dict(**GRID))
    st.plotly_chart(fig_posto_sexo, use_container_width=True)
else:
    st.warning("Nenhum dado para exibir com os filtros selecionados.")

st.markdown("---")

# Ficha Individual do Militar
st.subheader("Ficha Individual do Militar")
if not filtered_df.empty:
    militares_nomes = filtered_df['nome'].unique()
    selected_militar = st.selectbox("Selecione um Militar", militares_nomes)

    if selected_militar:
        militar_data = filtered_df[filtered_df['nome'] == selected_militar].iloc[0]
        st.write(f"**Nome:** {militar_data['nome']}")
        st.write(f"**Matrícula:** {militar_data['matricula']}")
        st.write(f"**Posto:** {militar_data['posto']}")
        st.write(f"**OBM:** {militar_data['obm']}")
        st.write(f"**Sexo:** {militar_data['sexo']}")
        st.write(f"**Idade:** {militar_data['idade']} anos")
        st.write(f"**Média Final:** {militar_data['MEDIA_FINAL']:.2f}")
        st.write(f"**Classificação:** {militar_data['CLASSIFICACAO']}")

        st.markdown("#### Desempenho por Exercício (Notas e Valores Brutos)")
        exercicios_militar = []
        for ex in exercicios_padrao:
            if not pd.isna(militar_data.get(f'{ex}_RAW')):
                exercicios_militar.append({
                    'Exercício': ex,
                    'Valor Bruto': militar_data[f'{ex}_RAW'],
                    'Nota': militar_data[f'NOTA_{ex}']
                })
        df_exercicios_militar = pd.DataFrame(exercicios_militar)
        if not df_exercicios_militar.empty:
            st.dataframe(df_exercicios_militar, use_container_width=True)

            fig_militar = px.bar(
                df_exercicios_militar,
                x='Exercício',
                y='Nota',
                title=f'Notas do Militar {selected_militar} por Exercício',
                color='Nota',
                color_continuous_scale=px.colors.sequential.Viridis
            )
            fig_militar.update_layout(**DARK, yaxis=dict(**GRID))
            st.plotly_chart(fig_militar, use_container_width=True)
        else:
            st.info("Este militar não possui registros de exercícios padrão ou adaptados com pontuação.")
else:
    st.info("Nenhum militar encontrado com os filtros aplicados para exibir a ficha individual.")

st.markdown("---")

# TAF Adaptado
st.subheader("Análise do TAF Adaptado")
df_adaptado = filtered_df[~filtered_df['atividade'].isin(exercicios_padrao)]

if not df_adaptado.empty:
    st.write("Militares que realizaram TAF Adaptado ou atividades não padrão:")
    st.dataframe(df_adaptado[['nome', 'atividade', 'valor', 'resultado_ok', 'NOTA_atividade', 'CLASSIFICACAO']], use_container_width=True)

    # Contagem de militares por exercício adaptado
    exercicios_adaptados_counts = df_adaptado['atividade'].value_counts().reset_index()
    exercicios_adaptados_counts.columns = ['Exercício', 'Realizaram']

    fig_ex = px.bar(
        exercicios_adaptados_counts,
        x="Exercício", y="Realizaram",
        color="Realizaram",
        color_continuous_scale=["#f59e0b", "#22c55e"],
        text="Realizaram",
        title="Quantidade de militares por exercício (TAF Adaptado)",
    )
    fig_ex.update_traces(textposition="outside")
    fig_ex.update_layout(
        **DARK, height=400, coloraxis_showscale=False,
        xaxis=dict(**GRID, tickangle=-45),
        yaxis=dict(**GRID),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig_ex, use_container_width=True)

st.info(
    "ℹ️ O TAF Adaptado avalia militares com necessidades especiais ou "
    "restrições médicas, utilizando exercícios alternativos conforme "
    "aptidão individual. Cada militar realiza um conjunto diferente de provas."
)