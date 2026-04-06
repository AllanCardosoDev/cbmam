"""
═══════════════════════════════════════════════════════════════════════════════
DASHBOARD TAF - Sistema Interativo de Análise de Teste de Aptidão Física
Corpo de Bombeiros Militar do Amazonas | 2026
═══════════════════════════════════════════════════════════════════════════════
Adaptado da estrutura robusta do projeto CBMAM com integração das regras
de pontuação por faixa etária e sexo - VERSÃO CORRIGIDA
═══════════════════════════════════════════════════════════════════════════════
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
import re

warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════════════════════
# STREAMLIT CONFIG (DEVE SER PRIMEIRA!)
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Dashboard TAF CBMAM",
    page_icon="🚒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# IMAGEM CBMAM
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data
def _get_cbmam_image_url() -> str:
    return (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/"
        "Bras%C3%A3o_do_Corpo_de_Bombeiros_Militar_do_Amazonas.svg/"
        "200px-Bras%C3%A3o_do_Corpo_de_Bombeiros_Militar_do_Amazonas.svg.png"
    )

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES PLOTLY
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
# REGRAS DE PONTUAÇÃO (Corretas conforme scoring_rules.py)
# ══════════════════════════════════════════════════════════════════════════════

REGRAS_MASCULINO = {
    '18-21': {
        'Corrida': {3200: 10, 3100: 9.5, 3000: 9.0, 2900: 8.5, 2800: 8.0, 2700: 7.5, 2600: 7.0, 2500: 6.5, 2400: 6.0, 2300: 5.5, 2200: 5.0, 2100: 4.5, 2000: 4.0, 1900: 3.5, 1800: 3.0, 1700: 2.5, 1600: 2.0, 1500: 1.5, 0: 0},
        'Flexão': {38: 10, 37: 9.5, 36: 9.0, 35: 8.5, 34: 8.0, 33: 7.5, 32: 7.0, 31: 6.5, 30: 6.0, 29: 5.5, 28: 5.0, 27: 4.5, 26: 4.0, 25: 3.5, 24: 3.0, 23: 2.5, 22: 2.0, 21: 1.5, 0: 0},
        'Abdominal': {48: 10, 47: 9.5, 46: 9.0, 45: 8.5, 44: 8.0, 43: 7.5, 42: 7.0, 41: 6.5, 40: 6.0, 39: 5.5, 38: 5.0, 37: 4.5, 36: 4.0, 35: 3.5, 34: 3.0, 33: 2.5, 32: 2.0, 31: 1.5, 0: 0},
        'Barra Dinâmica': {13: 10, 12: 9.5, 11: 9.0, 10: 8.5, 9: 8.0, 8: 7.5, 7: 7.0, 6: 6.5, 5: 6.0, 4: 5.5, 3: 5.0, 2: 4.5, 1: 4.0, 0: 0},
        'Barra Estática': {60: 10, 57: 9.5, 55: 9.0, 53: 8.5, 51: 8.0, 49: 7.5, 47: 7.0, 45: 6.5, 43: 6.0, 41: 5.5, 39: 5.0, 37: 4.5, 35: 4.0, 33: 3.5, 31: 3.0, 29: 2.5, 27: 2.0, 25: 1.5, 0: 0},
        'Natação': {40: 10, 44: 9.5, 48: 9.0, 52: 8.5, 56: 8.0, 60: 7.5, 64: 7.0, 68: 6.5, 72: 6.0, 76: 5.5, 80: 5.0, 84: 4.5, 88: 4.0, 92: 3.5, 96: 3.0, 100: 2.5, 104: 2.0, 108: 1.5, 999: 0}
    },
    '22-25': {
        'Corrida': {3200: 10, 3100: 9.5, 3000: 9.0, 2900: 8.5, 2800: 8.0, 2700: 7.5, 2600: 7.0, 2500: 6.5, 2400: 6.0, 2300: 5.5, 2200: 5.0, 2100: 4.5, 2000: 4.0, 1900: 3.5, 1800: 3.0, 1700: 2.5, 1600: 2.0, 1500: 1.5, 0: 0},
        'Flexão': {37: 10, 36: 9.5, 35: 9.0, 34: 8.5, 33: 8.0, 32: 7.5, 31: 7.0, 30: 6.5, 29: 6.0, 28: 5.5, 27: 5.0, 26: 4.5, 25: 4.0, 24: 3.5, 23: 3.0, 22: 2.5, 21: 2.0, 20: 1.5, 0: 0},
        'Abdominal': {47: 10, 46: 9.5, 45: 9.0, 44: 8.5, 43: 8.0, 42: 7.5, 41: 7.0, 40: 6.5, 39: 6.0, 38: 5.5, 37: 5.0, 36: 4.5, 35: 4.0, 34: 3.5, 33: 3.0, 32: 2.5, 31: 2.0, 30: 1.5, 0: 0},
        'Barra Dinâmica': {12: 10, 11: 9.5, 10: 9.0, 9: 8.5, 8: 8.0, 7: 7.5, 6: 7.0, 5: 6.5, 4: 6.0, 3: 5.5, 2: 5.0, 1: 4.5, 0: 0},
        'Barra Estática': {57: 10, 55: 9.5, 53: 9.0, 51: 8.5, 49: 8.0, 47: 7.5, 45: 7.0, 43: 6.5, 41: 6.0, 39: 5.5, 37: 5.0, 35: 4.5, 33: 4.0, 31: 3.5, 29: 3.0, 27: 2.5, 25: 2.0, 23: 1.5, 0: 0},
        'Natação': {44: 10, 48: 9.5, 52: 9.0, 56: 8.5, 60: 8.0, 64: 7.5, 68: 7.0, 72: 6.5, 76: 6.0, 80: 5.5, 84: 5.0, 88: 4.5, 92: 4.0, 96: 3.5, 100: 3.0, 104: 2.5, 108: 2.0, 112: 1.5, 999: 0}
    },
    '26-29': {
        'Corrida': {3000: 10, 2900: 9.5, 2800: 9.0, 2700: 8.5, 2600: 8.0, 2500: 7.5, 2400: 7.0, 2300: 6.5, 2200: 6.0, 2100: 5.5, 2000: 5.0, 1900: 4.5, 1800: 4.0, 1700: 3.5, 1600: 3.0, 1500: 2.5, 1400: 2.0, 1300: 1.5, 0: 0},
        'Flexão': {36: 10, 35: 9.5, 34: 9.0, 33: 8.5, 32: 8.0, 31: 7.5, 30: 7.0, 29: 6.5, 28: 6.0, 27: 5.5, 26: 5.0, 25: 4.5, 24: 4.0, 23: 3.5, 22: 3.0, 21: 2.5, 20: 2.0, 19: 1.5, 0: 0},
        'Abdominal': {46: 10, 45: 9.5, 44: 9.0, 43: 8.5, 42: 8.0, 41: 7.5, 40: 7.0, 39: 6.5, 38: 6.0, 37: 5.5, 36: 5.0, 35: 4.5, 34: 4.0, 33: 3.5, 32: 3.0, 31: 2.5, 30: 2.0, 29: 1.5, 0: 0},
        'Barra Dinâmica': {11: 10, 10: 9.5, 9: 9.0, 8: 8.5, 7: 8.0, 6: 7.5, 5: 7.0, 4: 6.5, 3: 6.0, 2: 5.5, 1: 5.0, 0: 0},
        'Barra Estática': {55: 10, 53: 9.5, 51: 9.0, 49: 8.5, 47: 8.0, 45: 7.5, 43: 7.0, 41: 6.5, 39: 6.0, 37: 5.5, 35: 5.0, 33: 4.5, 31: 4.0, 29: 3.5, 27: 3.0, 25: 2.5, 23: 2.0, 21: 1.5, 0: 0},
        'Natação': {48: 10, 52: 9.5, 56: 9.0, 60: 8.5, 64: 8.0, 68: 7.5, 72: 7.0, 76: 6.5, 80: 6.0, 84: 5.5, 88: 5.0, 92: 4.5, 96: 4.0, 100: 3.5, 104: 3.0, 108: 2.5, 112: 2.0, 116: 1.5, 999: 0}
    },
    '30-34': {
        'Corrida': {2800: 10, 2700: 9.5, 2600: 9.0, 2500: 8.5, 2400: 8.0, 2300: 7.5, 2200: 7.0, 2100: 6.5, 2000: 6.0, 1900: 5.5, 1800: 5.0, 1700: 4.5, 1600: 4.0, 1500: 3.5, 1400: 3.0, 1300: 2.5, 1200: 2.0, 1100: 1.5, 0: 0},
        'Flexão': {35: 10, 34: 9.5, 33: 9.0, 32: 8.5, 31: 8.0, 30: 7.5, 29: 7.0, 28: 6.5, 27: 6.0, 26: 5.5, 25: 5.0, 24: 4.5, 23: 4.0, 22: 3.5, 21: 3.0, 20: 2.5, 19: 2.0, 18: 1.5, 0: 0},
        'Abdominal': {45: 10, 44: 9.5, 43: 9.0, 42: 8.5, 41: 8.0, 40: 7.5, 39: 7.0, 38: 6.5, 37: 6.0, 36: 5.5, 35: 5.0, 34: 4.5, 33: 4.0, 32: 3.5, 31: 3.0, 30: 2.5, 29: 2.0, 28: 1.5, 0: 0},
        'Barra Dinâmica': {10: 10, 9: 9.5, 8: 9.0, 7: 8.5, 6: 8.0, 5: 7.5, 4: 7.0, 3: 6.5, 2: 6.0, 1: 5.5, 0: 0},
        'Barra Estática': {53: 10, 51: 9.5, 49: 9.0, 47: 8.5, 45: 8.0, 43: 7.5, 41: 7.0, 39: 6.5, 37: 6.0, 35: 5.5, 33: 5.0, 31: 4.5, 29: 4.0, 27: 3.5, 25: 3.0, 23: 2.5, 21: 2.0, 19: 1.5, 0: 0},
        'Natação': {52: 10, 56: 9.5, 60: 9.0, 64: 8.5, 68: 8.0, 72: 7.5, 76: 7.0, 80: 6.5, 84: 6.0, 88: 5.5, 92: 5.0, 96: 4.5, 100: 4.0, 104: 3.5, 108: 3.0, 112: 2.5, 116: 2.0, 120: 1.5, 999: 0}
    },
    '35-39': {
        'Corrida': {2600: 10, 2500: 9.5, 2400: 9.0, 2300: 8.5, 2200: 8.0, 2100: 7.5, 2000: 7.0, 1900: 6.5, 1800: 6.0, 1700: 5.5, 1600: 5.0, 1500: 4.5, 1400: 4.0, 1300: 3.5, 1200: 3.0, 1100: 2.5, 1000: 2.0, 900: 1.5, 0: 0},
        'Flexão': {34: 10, 33: 9.5, 32: 9.0, 31: 8.5, 30: 8.0, 29: 7.5, 28: 7.0, 27: 6.5, 26: 6.0, 25: 5.5, 24: 5.0, 23: 4.5, 22: 4.0, 21: 3.5, 20: 3.0, 19: 2.5, 18: 2.0, 17: 1.5, 0: 0},
        'Abdominal': {43: 10, 42: 9.5, 41: 9.0, 40: 8.5, 39: 8.0, 38: 7.5, 37: 7.0, 36: 6.5, 35: 6.0, 34: 5.5, 33: 5.0, 32: 4.5, 31: 4.0, 30: 3.5, 29: 3.0, 28: 2.5, 27: 2.0, 26: 1.5, 0: 0},
        'Barra Dinâmica': {9: 10, 8: 9.5, 7: 9.0, 6: 8.5, 5: 8.0, 4: 7.5, 3: 7.0, 2: 6.5, 1: 6.0, 0: 0},
        'Barra Estática': {51: 10, 49: 9.5, 47: 9.0, 45: 8.5, 43: 8.0, 41: 7.5, 39: 7.0, 37: 6.5, 35: 6.0, 33: 5.5, 31: 5.0, 29: 4.5, 27: 4.0, 25: 3.5, 23: 3.0, 21: 2.5, 19: 2.0, 17: 1.5, 0: 0},
        'Natação': {56: 10, 60: 9.5, 64: 9.0, 68: 8.5, 72: 8.0, 76: 7.5, 80: 7.0, 84: 6.5, 88: 6.0, 92: 5.5, 96: 5.0, 100: 4.5, 104: 4.0, 108: 3.5, 112: 3.0, 116: 2.5, 120: 2.0, 124: 1.5, 999: 0}
    },
    '40-44': {
        'Corrida': {2400: 10, 2300: 9.5, 2200: 9.0, 2100: 8.5, 2000: 8.0, 1900: 7.5, 1800: 7.0, 1700: 6.5, 1600: 6.0, 1500: 5.5, 1400: 5.0, 1300: 4.5, 1200: 4.0, 1100: 3.5, 1000: 3.0, 900: 2.5, 800: 2.0, 700: 1.5, 0: 0},
        'Flexão': {32: 10, 31: 9.5, 30: 9.0, 29: 8.5, 28: 8.0, 27: 7.5, 26: 7.0, 25: 6.5, 24: 6.0, 23: 5.5, 22: 5.0, 21: 4.5, 20: 4.0, 19: 3.5, 18: 3.0, 17: 2.5, 16: 2.0, 15: 1.5, 0: 0},
        'Abdominal': {41: 10, 40: 9.5, 39: 9.0, 38: 8.5, 37: 8.0, 36: 7.5, 35: 7.0, 34: 6.5, 33: 6.0, 32: 5.5, 31: 5.0, 30: 4.5, 29: 4.0, 28: 3.5, 27: 3.0, 26: 2.5, 25: 2.0, 24: 1.5, 0: 0},
        'Barra Dinâmica': {8: 10, 7: 9.5, 6: 9.0, 5: 8.5, 4: 8.0, 3: 7.5, 2: 7.0, 1: 6.5, 0: 0},
        'Barra Estática': {49: 10, 47: 9.5, 45: 9.0, 43: 8.5, 41: 8.0, 39: 7.5, 37: 7.0, 35: 6.5, 33: 6.0, 31: 5.5, 29: 5.0, 27: 4.5, 25: 4.0, 23: 3.5, 21: 3.0, 19: 2.5, 17: 2.0, 15: 1.5, 0: 0},
        'Natação': {60: 10, 64: 9.5, 68: 9.0, 72: 8.5, 76: 8.0, 80: 7.5, 84: 7.0, 88: 6.5, 92: 6.0, 96: 5.5, 100: 5.0, 104: 4.5, 108: 4.0, 112: 3.5, 116: 3.0, 120: 2.5, 124: 2.0, 128: 1.5, 999: 0}
    },
    '45-49': {
        'Corrida': {2200: 10, 2100: 9.5, 2000: 9.0, 1900: 8.5, 1800: 8.0, 1700: 7.5, 1600: 7.0, 1500: 6.5, 1400: 6.0, 1300: 5.5, 1200: 5.0, 1100: 4.5, 1000: 4.0, 900: 3.5, 800: 3.0, 700: 2.5, 600: 2.0, 500: 1.5, 0: 0},
        'Flexão': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0},
        'Abdominal': {39: 10, 38: 9.5, 37: 9.0, 36: 8.5, 35: 8.0, 34: 7.5, 33: 7.0, 32: 6.5, 31: 6.0, 30: 5.5, 29: 5.0, 28: 4.5, 27: 4.0, 26: 3.5, 25: 3.0, 24: 2.5, 23: 2.0, 22: 1.5, 0: 0},
        'Barra Dinâmica': {7: 10, 6: 9.5, 5: 9.0, 4: 8.5, 3: 8.0, 2: 7.5, 1: 7.0, 0: 0},
        'Barra Estática': {47: 10, 45: 9.5, 43: 9.0, 41: 8.5, 39: 8.0, 37: 7.5, 35: 7.0, 33: 6.5, 31: 6.0, 29: 5.5, 27: 5.0, 25: 4.5, 23: 4.0, 21: 3.5, 19: 3.0, 17: 2.5, 15: 2.0, 13: 1.5, 0: 0},
        'Natação': {64: 10, 68: 9.5, 72: 9.0, 76: 8.5, 80: 8.0, 84: 7.5, 88: 7.0, 92: 6.5, 96: 6.0, 100: 5.5, 104: 5.0, 108: 4.5, 112: 4.0, 116: 3.5, 120: 3.0, 124: 2.5, 128: 2.0, 132: 1.5, 999: 0}
    },
    '50-53': {
        'Corrida': {2000: 10, 1900: 9.5, 1800: 9.0, 1700: 8.5, 1600: 8.0, 1500: 7.5, 1400: 7.0, 1300: 6.5, 1200: 6.0, 1100: 5.5, 1000: 5.0, 900: 4.5, 800: 4.0, 700: 3.5, 600: 3.0, 500: 2.5, 400: 2.0, 300: 1.5, 0: 0},
        'Flexão': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0},
        'Abdominal': {37: 10, 36: 9.5, 35: 9.0, 34: 8.5, 33: 8.0, 32: 7.5, 31: 7.0, 30: 6.5, 29: 6.0, 28: 5.5, 27: 5.0, 26: 4.5, 25: 4.0, 24: 3.5, 23: 3.0, 22: 2.5, 21: 2.0, 20: 1.5, 0: 0},
        'Barra Dinâmica': {6: 10, 5: 9.5, 4: 9.0, 3: 8.5, 2: 8.0, 1: 7.5, 0: 0},
        'Barra Estática': {45: 10, 43: 9.5, 41: 9.0, 39: 8.5, 37: 8.0, 35: 7.5, 33: 7.0, 31: 6.5, 29: 6.0, 27: 5.5, 25: 5.0, 23: 4.5, 21: 4.0, 19: 3.5, 17: 3.0, 15: 2.5, 13: 2.0, 11: 1.5, 0: 0},
        'Natação': {68: 10, 72: 9.5, 76: 9.0, 80: 8.5, 84: 8.0, 88: 7.5, 92: 7.0, 96: 6.5, 100: 6.0, 104: 5.5, 108: 5.0, 112: 4.5, 116: 4.0, 120: 3.5, 124: 3.0, 128: 2.5, 132: 2.0, 136: 1.5, 999: 0}
    },
    '54-57': {
        'Corrida': {1800: 10, 1700: 9.5, 1600: 9.0, 1500: 8.5, 1400: 8.0, 1300: 7.5, 1200: 7.0, 1100: 6.5, 1000: 6.0, 900: 5.5, 800: 5.0, 700: 4.5, 600: 4.0, 500: 3.5, 400: 3.0, 300: 2.5, 200: 2.0, 100: 1.5, 0: 0},
        'Flexão': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0},
        'Abdominal': {35: 10, 34: 9.5, 33: 9.0, 32: 8.5, 31: 8.0, 30: 7.5, 29: 7.0, 28: 6.5, 27: 6.0, 26: 5.5, 25: 5.0, 24: 4.5, 23: 4.0, 22: 3.5, 21: 3.0, 20: 2.5, 19: 2.0, 18: 1.5, 0: 0},
        'Barra Dinâmica': {5: 10, 4: 9.5, 3: 9.0, 2: 8.5, 1: 8.0, 0: 0},
        'Barra Estática': {43: 10, 41: 9.5, 39: 9.0, 37: 8.5, 35: 8.0, 33: 7.5, 31: 7.0, 29: 6.5, 27: 6.0, 25: 5.5, 23: 5.0, 21: 4.5, 19: 4.0, 17: 3.5, 15: 3.0, 13: 2.5, 11: 2.0, 9: 1.5, 0: 0},
        'Natação': {72: 10, 76: 9.5, 80: 9.0, 84: 8.5, 88: 8.0, 92: 7.5, 96: 7.0, 100: 6.5, 104: 6.0, 108: 5.5, 112: 5.0, 116: 4.5, 120: 4.0, 124: 3.5, 128: 3.0, 132: 2.5, 136: 2.0, 140: 1.5, 999: 0}
    },
    '58+': {
        'Corrida': {1600: 10, 1500: 9.5, 1400: 9.0, 1300: 8.5, 1200: 8.0, 1100: 7.5, 1000: 7.0, 900: 6.5, 800: 6.0, 700: 5.5, 600: 5.0, 500: 4.5, 400: 4.0, 300: 3.5, 200: 3.0, 100: 2.5, 50: 2.0, 25: 1.5, 0: 0},
        'Flexão': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0},
        'Abdominal': {33: 10, 32: 9.5, 31: 9.0, 30: 8.5, 29: 8.0, 28: 7.5, 27: 7.0, 26: 6.5, 25: 6.0, 24: 5.5, 23: 5.0, 22: 4.5, 21: 4.0, 20: 3.5, 19: 3.0, 18: 2.5, 17: 2.0, 16: 1.5, 0: 0},
        'Barra Dinâmica': {4: 10, 3: 9.5, 2: 9.0, 1: 8.5, 0: 0},
        'Barra Estática': {41: 10, 39: 9.5, 37: 9.0, 35: 8.5, 33: 8.0, 31: 7.5, 29: 7.0, 27: 6.5, 25: 6.0, 23: 5.5, 21: 5.0, 19: 4.5, 17: 4.0, 15: 3.5, 13: 3.0, 11: 2.5, 9: 2.0, 7: 1.5, 0: 0},
        'Natação': {76: 10, 80: 9.5, 84: 9.0, 88: 8.5, 92: 8.0, 96: 7.5, 100: 7.0, 104: 6.5, 108: 6.0, 112: 5.5, 116: 5.0, 120: 4.5, 124: 4.0, 128: 3.5, 132: 3.0, 136: 2.5, 140: 2.0, 144: 1.5, 999: 0}
    }
}

REGRAS_FEMININO = {
    '18-21': {
        'Corrida': {2800: 10, 2700: 9.5, 2600: 9.0, 2500: 8.5, 2400: 8.0, 2300: 7.5, 2200: 7.0, 2100: 6.5, 2000: 6.0, 1900: 5.5, 1800: 5.0, 1700: 4.5, 1600: 4.0, 1500: 3.5, 1400: 3.0, 1300: 2.5, 1200: 2.0, 1100: 1.5, 0: 0},
        'Flexão': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0},
        'Abdominal': {40: 10, 39: 9.5, 38: 9.0, 37: 8.5, 36: 8.0, 35: 7.5, 34: 7.0, 33: 6.5, 32: 6.0, 31: 5.5, 30: 5.0, 29: 4.5, 28: 4.0, 27: 3.5, 26: 3.0, 25: 2.5, 24: 2.0, 23: 1.5, 0: 0},
        'Barra Dinâmica': {8: 10, 7: 9.5, 6: 9.0, 5: 8.5, 4: 8.0, 3: 7.5, 2: 7.0, 1: 6.5, 0: 0},
        'Barra Estática': {50: 10, 48: 9.5, 46: 9.0, 44: 8.5, 42: 8.0, 40: 7.5, 38: 7.0, 36: 6.5, 34: 6.0, 32: 5.5, 30: 5.0, 28: 4.5, 26: 4.0, 24: 3.5, 22: 3.0, 20: 2.5, 18: 2.0, 16: 1.5, 0: 0},
        'Natação': {45: 10, 50: 9.5, 55: 9.0, 60: 8.5, 65: 8.0, 70: 7.5, 75: 7.0, 80: 6.5, 85: 6.0, 90: 5.5, 95: 5.0, 100: 4.5, 105: 4.0, 110: 3.5, 115: 3.0, 120: 2.5, 125: 2.0, 130: 1.5, 999: 0}
    },
    '22-25': {
        'Corrida': {2600: 10, 2500: 9.5, 2400: 9.0, 2300: 8.5, 2200: 8.0, 2100: 7.5, 2000: 7.0, 1900: 6.5, 1800: 6.0, 1700: 5.5, 1600: 5.0, 1500: 4.5, 1400: 4.0, 1300: 3.5, 1200: 3.0, 1100: 2.5, 1000: 2.0, 900: 1.5, 0: 0},
        'Flexão': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0},
        'Abdominal': {37: 10, 36: 9.5, 35: 9.0, 34: 8.5, 33: 8.0, 32: 7.5, 31: 7.0, 30: 6.5, 29: 6.0, 28: 5.5, 27: 5.0, 26: 4.5, 25: 4.0, 24: 3.5, 23: 3.0, 22: 2.5, 21: 2.0, 20: 1.5, 0: 0},
        'Barra Dinâmica': {7: 10, 6: 9.5, 5: 9.0, 4: 8.5, 3: 8.0, 2: 7.5, 1: 7.0, 0: 0},
        'Barra Estática': {48: 10, 46: 9.5, 44: 9.0, 42: 8.5, 40: 8.0, 38: 7.5, 36: 7.0, 34: 6.5, 32: 6.0, 30: 5.5, 28: 5.0, 26: 4.5, 24: 4.0, 22: 3.5, 20: 3.0, 18: 2.5, 16: 2.0, 14: 1.5, 0: 0},
        'Natação': {47: 10, 52: 9.5, 57: 9.0, 62: 8.5, 67: 8.0, 72: 7.5, 77: 7.0, 82: 6.5, 87: 6.0, 92: 5.5, 97: 5.0, 102: 4.5, 107: 4.0, 112: 3.5, 117: 3.0, 122: 2.5, 127: 2.0, 132: 1.5, 999: 0}
    },
    '26-29': {
        'Corrida': {2400: 10, 2300: 9.5, 2200: 9.0, 2100: 8.5, 2000: 8.0, 1900: 7.5, 1800: 7.0, 1700: 6.5, 1600: 6.0, 1500: 5.5, 1400: 5.0, 1300: 4.5, 1200: 4.0, 1100: 3.5, 1000: 3.0, 900: 2.5, 800: 2.0, 700: 1.5, 0: 0},
        'Flexão': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0},
        'Abdominal': {34: 10, 33: 9.5, 32: 9.0, 31: 8.5, 30: 8.0, 29: 7.5, 28: 7.0, 27: 6.5, 26: 6.0, 25: 5.5, 24: 5.0, 23: 4.5, 22: 4.0, 21: 3.5, 20: 3.0, 19: 2.5, 18: 2.0, 17: 1.5, 0: 0},
        'Barra Dinâmica': {6: 10, 5: 9.5, 4: 9.0, 3: 8.5, 2: 8.0, 1: 7.5, 0: 0},
        'Barra Estática': {46: 10, 44: 9.5, 42: 9.0, 40: 8.5, 38: 8.0, 36: 7.5, 34: 7.0, 32: 6.5, 30: 6.0, 28: 5.5, 26: 5.0, 24: 4.5, 22: 4.0, 20: 3.5, 18: 3.0, 16: 2.5, 14: 2.0, 12: 1.5, 0: 0},
        'Natação': {49: 10, 54: 9.5, 59: 9.0, 64: 8.5, 69: 8.0, 74: 7.5, 79: 7.0, 84: 6.5, 89: 6.0, 94: 5.5, 99: 5.0, 104: 4.5, 109: 4.0, 114: 3.5, 119: 3.0, 124: 2.5, 129: 2.0, 134: 1.5, 999: 0}
    },
    '30-34': {
        'Corrida': {2200: 10, 2100: 9.5, 2000: 9.0, 1900: 8.5, 1800: 8.0, 1700: 7.5, 1600: 7.0, 1500: 6.5, 1400: 6.0, 1300: 5.5, 1200: 5.0, 1100: 4.5, 1000: 4.0, 900: 3.5, 800: 3.0, 700: 2.5, 600: 2.0, 500: 1.5, 0: 0},
        'Flexão': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0},
        'Abdominal': {32: 10, 31: 9.5, 30: 9.0, 29: 8.5, 28: 8.0, 27: 7.5, 26: 7.0, 25: 6.5, 24: 6.0, 23: 5.5, 22: 5.0, 21: 4.5, 20: 4.0, 19: 3.5, 18: 3.0, 17: 2.5, 16: 2.0, 15: 1.5, 0: 0},
        'Barra Dinâmica': {5: 10, 4: 9.5, 3: 9.0, 2: 8.5, 1: 8.0, 0: 0},
        'Barra Estática': {44: 10, 42: 9.5, 40: 9.0, 38: 8.5, 36: 8.0, 34: 7.5, 32: 7.0, 30: 6.5, 28: 6.0, 26: 5.5, 24: 5.0, 22: 4.5, 20: 4.0, 18: 3.5, 16: 3.0, 14: 2.5, 12: 2.0, 10: 1.5, 0: 0},
        'Natação': {51: 10, 56: 9.5, 61: 9.0, 66: 8.5, 71: 8.0, 76: 7.5, 81: 7.0, 86: 6.5, 91: 6.0, 96: 5.5, 101: 5.0, 106: 4.5, 111: 4.0, 116: 3.5, 121: 3.0, 126: 2.5, 131: 2.0, 136: 1.5, 999: 0}
    },
    '35-39': {
        'Corrida': {2000: 10, 1900: 9.5, 1800: 9.0, 1700: 8.5, 1600: 8.0, 1500: 7.5, 1400: 7.0, 1300: 6.5, 1200: 6.0, 1100: 5.5, 1000: 5.0, 900: 4.5, 800: 4.0, 700: 3.5, 600: 3.0, 500: 2.5, 400: 2.0, 300: 1.5, 0: 0},
        'Flexão': {22: 10, 21: 9.5, 20: 9.0, 19: 8.5, 18: 8.0, 17: 7.5, 16: 7.0, 15: 6.5, 14: 6.0, 13: 5.5, 12: 5.0, 11: 4.5, 10: 4.0, 9: 3.5, 8: 3.0, 7: 2.5, 6: 2.0, 5: 1.5, 0: 0},
        'Abdominal': {30: 10, 29: 9.5, 28: 9.0, 27: 8.5, 26: 8.0, 25: 7.5, 24: 7.0, 23: 6.5, 22: 6.0, 21: 5.5, 20: 5.0, 19: 4.5, 18: 4.0, 17: 3.5, 16: 3.0, 15: 2.5, 14: 2.0, 13: 1.5, 0: 0},
        'Barra Dinâmica': {4: 10, 3: 9.5, 2: 9.0, 1: 8.5, 0: 0},
        'Barra Estática': {42: 10, 40: 9.5, 38: 9.0, 36: 8.5, 34: 8.0, 32: 7.5, 30: 7.0, 28: 6.5, 26: 6.0, 24: 5.5, 22: 5.0, 20: 4.5, 18: 4.0, 16: 3.5, 14: 3.0, 12: 2.5, 10: 2.0, 8: 1.5, 0: 0},
        'Natação': {53: 10, 58: 9.5, 63: 9.0, 68: 8.5, 73: 8.0, 78: 7.5, 83: 7.0, 88: 6.5, 93: 6.0, 98: 5.5, 103: 5.0, 108: 4.5, 113: 4.0, 118: 3.5, 123: 3.0, 128: 2.5, 133: 2.0, 138: 1.5, 999: 0}
    },
    '40-44': {
        'Corrida': {1800: 10, 1700: 9.5, 1600: 9.0, 1500: 8.5, 1400: 8.0, 1300: 7.5, 1200: 7.0, 1100: 6.5, 1000: 6.0, 900: 5.5, 800: 5.0, 700: 4.5, 600: 4.0, 500: 3.5, 400: 3.0, 300: 2.5, 200: 2.0, 100: 1.5, 0: 0},
        'Flexão': {20: 10, 19: 9.5, 18: 9.0, 17: 8.5, 16: 8.0, 15: 7.5, 14: 7.0, 13: 6.5, 12: 6.0, 11: 5.5, 10: 5.0, 9: 4.5, 8: 4.0, 7: 3.5, 6: 3.0, 5: 2.5, 4: 2.0, 3: 1.5, 0: 0},
        'Abdominal': {28: 10, 27: 9.5, 26: 9.0, 25: 8.5, 24: 8.0, 23: 7.5, 22: 7.0, 21: 6.5, 20: 6.0, 19: 5.5, 18: 5.0, 17: 4.5, 16: 4.0, 15: 3.5, 14: 3.0, 13: 2.5, 12: 2.0, 11: 1.5, 0: 0},
        'Barra Dinâmica': {3: 10, 2: 9.5, 1: 9.0, 0: 0},
        'Barra Estática': {40: 10, 38: 9.5, 36: 9.0, 34: 8.5, 32: 8.0, 30: 7.5, 28: 7.0, 26: 6.5, 24: 6.0, 22: 5.5, 20: 5.0, 18: 4.5, 16: 4.0, 14: 3.5, 12: 3.0, 10: 2.5, 8: 2.0, 6: 1.5, 0: 0},
        'Natação': {55: 10, 60: 9.5, 65: 9.0, 70: 8.5, 75: 8.0, 80: 7.5, 85: 7.0, 90: 6.5, 95: 6.0, 100: 5.5, 105: 5.0, 110: 4.5, 115: 4.0, 120: 3.5, 125: 3.0, 130: 2.5, 135: 2.0, 140: 1.5, 999: 0}
    },
    '45-49': {
        'Corrida': {1600: 10, 1500: 9.5, 1400: 9.0, 1300: 8.5, 1200: 8.0, 1100: 7.5, 1000: 7.0, 900: 6.5, 800: 6.0, 700: 5.5, 600: 5.0, 500: 4.5, 400: 4.0, 300: 3.5, 200: 3.0, 100: 2.5, 50: 2.0, 25: 1.5, 0: 0},
        'Flexão': {18: 10, 17: 9.5, 16: 9.0, 15: 8.5, 14: 8.0, 13: 7.5, 12: 7.0, 11: 6.5, 10: 6.0, 9: 5.5, 8: 5.0, 7: 4.5, 6: 4.0, 5: 3.5, 4: 3.0, 3: 2.5, 2: 2.0, 1: 1.5, 0: 0},
        'Abdominal': {26: 10, 25: 9.5, 24: 9.0, 23: 8.5, 22: 8.0, 21: 7.5, 20: 7.0, 19: 6.5, 18: 6.0, 17: 5.5, 16: 5.0, 15: 4.5, 14: 4.0, 13: 3.5, 12: 3.0, 11: 2.5, 10: 2.0, 9: 1.5, 0: 0},
        'Barra Dinâmica': {2: 10, 1: 9.5, 0: 0},
        'Barra Estática': {38: 10, 36: 9.5, 34: 9.0, 32: 8.5, 30: 8.0, 28: 7.5, 26: 7.0, 24: 6.5, 22: 6.0, 20: 5.5, 18: 5.0, 16: 4.5, 14: 4.0, 12: 3.5, 10: 3.0, 8: 2.5, 6: 2.0, 4: 1.5, 0: 0},
        'Natação': {57: 10, 62: 9.5, 67: 9.0, 72: 8.5, 77: 8.0, 82: 7.5, 87: 7.0, 92: 6.5, 97: 6.0, 102: 5.5, 107: 5.0, 112: 4.5, 117: 4.0, 122: 3.5, 127: 3.0, 132: 2.5, 137: 2.0, 142: 1.5, 999: 0}
    },
    '50-53': {
        'Corrida': {1400: 10, 1300: 9.5, 1200: 9.0, 1100: 8.5, 1000: 8.0, 900: 7.5, 800: 7.0, 700: 6.5, 600: 6.0, 500: 5.5, 400: 5.0, 300: 4.5, 200: 4.0, 100: 3.5, 50: 3.0, 25: 2.5, 10: 2.0, 5: 1.5, 0: 0},
        'Flexão': {16: 10, 15: 9.5, 14: 9.0, 13: 8.5, 12: 8.0, 11: 7.5, 10: 7.0, 9: 6.5, 8: 6.0, 7: 5.5, 6: 5.0, 5: 4.5, 4: 4.0, 3: 3.5, 2: 3.0, 1: 2.5, 0: 0},
        'Abdominal': {24: 10, 23: 9.5, 22: 9.0, 21: 8.5, 20: 8.0, 19: 7.5, 18: 7.0, 17: 6.5, 16: 6.0, 15: 5.5, 14: 5.0, 13: 4.5, 12: 4.0, 11: 3.5, 10: 3.0, 9: 2.5, 8: 2.0, 7: 1.5, 0: 0},
        'Barra Dinâmica': {1: 10, 0: 0},
        'Barra Estática': {36: 10, 34: 9.5, 32: 9.0, 30: 8.5, 28: 8.0, 26: 7.5, 24: 7.0, 22: 6.5, 20: 6.0, 18: 5.5, 16: 5.0, 14: 4.5, 12: 4.0, 10: 3.5, 8: 3.0, 6: 2.5, 4: 2.0, 2: 1.5, 0: 0},
        'Natação': {59: 10, 64: 9.5, 69: 9.0, 74: 8.5, 79: 8.0, 84: 7.5, 89: 7.0, 94: 6.5, 99: 6.0, 104: 5.5, 109: 5.0, 114: 4.5, 119: 4.0, 124: 3.5, 129: 3.0, 134: 2.5, 139: 2.0, 144: 1.5, 999: 0}
    },
    '54-57': {
        'Corrida': {1200: 10, 1100: 9.5, 1000: 9.0, 900: 8.5, 800: 8.0, 700: 7.5, 600: 7.0, 500: 6.5, 400: 6.0, 300: 5.5, 200: 5.0, 100: 4.5, 50: 4.0, 25: 3.5, 10: 3.0, 5: 2.5, 0: 0},
        'Flexão': {14: 10, 13: 9.5, 12: 9.0, 11: 8.5, 10: 8.0, 9: 7.5, 8: 7.0, 7: 6.5, 6: 6.0, 5: 5.5, 4: 5.0, 3: 4.5, 2: 4.0, 1: 3.5, 0: 0},
        'Abdominal': {22: 10, 21: 9.5, 20: 9.0, 19: 8.5, 18: 8.0, 17: 7.5, 16: 7.0, 15: 6.5, 14: 6.0, 13: 5.5, 12: 5.0, 11: 4.5, 10: 4.0, 9: 3.5, 8: 3.0, 7: 2.5, 6: 2.0, 5: 1.5, 0: 0},
        'Barra Dinâmica': {0: 10},
        'Barra Estática': {34: 10, 32: 9.5, 30: 9.0, 28: 8.5, 26: 8.0, 24: 7.5, 22: 7.0, 20: 6.5, 18: 6.0, 16: 5.5, 14: 5.0, 12: 4.5, 10: 4.0, 8: 3.5, 6: 3.0, 4: 2.5, 2: 2.0, 0: 0},
        'Natação': {61: 10, 66: 9.5, 71: 9.0, 76: 8.5, 81: 8.0, 86: 7.5, 91: 7.0, 96: 6.5, 101: 6.0, 106: 5.5, 111: 5.0, 116: 4.5, 121: 4.0, 126: 3.5, 131: 3.0, 136: 2.5, 141: 2.0, 146: 1.5, 999: 0}
    },
    '58+': {
        'Corrida': {1000: 10, 900: 9.5, 800: 9.0, 700: 8.5, 600: 8.0, 500: 7.5, 400: 7.0, 300: 6.5, 200: 6.0, 100: 5.5, 50: 5.0, 25: 4.5, 10: 4.0, 5: 3.5, 0: 0},
        'Flexão': {12: 10, 11: 9.5, 10: 9.0, 9: 8.5, 8: 8.0, 7: 7.5, 6: 7.0, 5: 6.5, 4: 6.0, 3: 5.5, 2: 5.0, 1: 4.5, 0: 0},
        'Abdominal': {20: 10, 19: 9.5, 18: 9.0, 17: 8.5, 16: 8.0, 15: 7.5, 14: 7.0, 13: 6.5, 12: 6.0, 11: 5.5, 10: 5.0, 9: 4.5, 8: 4.0, 7: 3.5, 6: 3.0, 5: 2.5, 4: 2.0, 3: 1.5, 0: 0},
        'Barra Dinâmica': {0: 10},
        'Barra Estática': {32: 10, 30: 9.5, 28: 9.0, 26: 8.5, 24: 8.0, 22: 7.5, 20: 7.0, 18: 6.5, 16: 6.0, 14: 5.5, 12: 5.0, 10: 4.5, 8: 4.0, 6: 3.5, 4: 3.0, 2: 2.5, 0: 0},
        'Natação': {63: 10, 68: 9.5, 73: 9.0, 78: 8.5, 83: 8.0, 88: 7.5, 93: 7.0, 98: 6.5, 103: 6.0, 108: 5.5, 113: 5.0, 118: 4.5, 123: 4.0, 128: 3.5, 133: 3.0, 138: 2.5, 143: 2.0, 148: 1.5, 999: 0}
    }
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE CÁLCULO
# ══════════════════════════════════════════════════════════════════════════════

def calcular_idade(data_nascimento):
    """Calcula idade a partir de data de nascimento (formato DD/MM/YYYY)"""
    try:
        if pd.isna(data_nascimento):
            return None
        data = pd.to_datetime(data_nascimento, format='%d/%m/%Y')
        return datetime.now().year - data.year
    except:
        return None

def obter_faixa_etaria(idade):
    """Retorna a faixa etária correta conforme scoring_rules.py"""
    if pd.isna(idade):
        return None
    
    idade = int(idade)
    
    if 18 <= idade <= 21:
        return '18-21'
    elif 22 <= idade <= 25:
        return '22-25'
    elif 26 <= idade <= 29:
        return '26-29'
    elif 30 <= idade <= 34:
        return '30-34'
    elif 35 <= idade <= 39:
        return '35-39'
    elif 40 <= idade <= 44:
        return '40-44'
    elif 45 <= idade <= 49:
        return '45-49'
    elif 50 <= idade <= 53:
        return '50-53'
    elif 54 <= idade <= 57:
        return '54-57'
    elif idade >= 58:
        return '58+'
    return None

def limpar_valor_tempo(valor):
    """Converte tempo de string para segundos (ex: 01'04\" -> 64)"""
    if pd.isna(valor):
        return None
    
    valor_str = str(valor).strip()
    
    # Se for um número simples, retorna como inteiro
    if valor_str.isdigit():
        return int(valor_str)
    
    # Trata formato: 01'04" (1 minuto 4 segundos = 64)
    try:
        # Remove aspas e comas
        valor_limpo = valor_str.replace('"', '').replace("'", ":").replace(',', '')
        
        if ':' in valor_limpo:
            partes = valor_limpo.split(':')
            if len(partes) == 2:
                minutos = int(partes[0])
                segundos = int(partes[1].replace('"', '').strip())
                return minutos * 60 + segundos
        else:
            # Se é apenas segundos
            retorno = valor_limpo.replace('"', '').strip()
            if retorno.isdigit():
                return int(retorno)
    except:
        pass
    
    return None

def normalizar_nome_exercicio(exercicio):
    """Normaliza nomes de exercícios para match com regras"""
    if pd.isna(exercicio):
        return None
    
    ex = str(exercicio).strip().upper()
    
    # Mapear variações para nomes padrão
    if 'CORR' in ex:
        return 'Corrida'
    elif 'FLEX' in ex or 'PUSH' in ex:
        return 'Flexão'
    elif 'ABDO' in ex or 'ABS' in ex:
        return 'Abdominal'
    elif 'BARRA' in ex or 'CHIN' in ex:
        if 'DIN' in ex or 'DINÂM' in ex:
            return 'Barra Dinâmica'
        elif 'EST' in ex or 'ESTÁT' in ex:
            return 'Barra Estática'
        else:
            return 'Barra Dinâmica'
    elif 'NAT' in ex or 'SWIM' in ex:
        return 'Natação'
    
    return None

def obter_nota_exercicio(exercicio, valor, idade, sexo):
    """Calcula a nota de um exercício usando as regras de scoring"""
    try:
        if pd.isna(valor) or pd.isna(idade) or pd.isna(sexo) or pd.isna(exercicio):
            return np.nan
        
        idade = int(idade)
        faixa = obter_faixa_etaria(idade)
        
        if not faixa:
            return np.nan
        
        # Selecionar regras conforme sexo
        if sexo.strip().lower() in ['masculino', 'm', 'male']:
            regras = REGRAS_MASCULINO
        else:
            regras = REGRAS_FEMININO
        
        if faixa not in regras:
            return np.nan
        
        # Normalizar nome do exercício
        ex_normalizado = normalizar_nome_exercicio(exercicio)
        
        if ex_normalizado not in regras[faixa]:
            return np.nan
        
        tabela_exercicio = regras[faixa][ex_normalizado]
        
        # Se for Natação, precisa converter tempo
        if ex_normalizado == 'Natação':
            valor_float = limpar_valor_tempo(valor)
        else:
            try:
                valor_float = float(valor)
            except:
                return np.nan
        
        if valor_float is None:
            return np.nan
        
        # Para Natação: menor tempo = maior nota
        if ex_normalizado == 'Natação':
            for limite in sorted(tabela_exercicio.keys()):
                if valor_float <= limite:
                    return tabela_exercicio[limite]
            return 0
        
        # Para outros: maior valor = maior nota
        else:
            for limite in sorted(tabela_exercicio.keys(), reverse=True):
                if valor_float >= limite:
                    return tabela_exercicio[limite]
            return 0
    
    except Exception as e:
        return np.nan

def classificar_media(media):
    """Classifica a média final em categorias"""
    if pd.isna(media):
        return 'Sem Dados'
    media = float(media)
    if media >= 9.0:
        return 'Excelente'
    elif media >= 7.5:
        return 'Bom'
    elif media >= 6.0:
        return 'Regular'
    else:
        return 'Insuficiente'

# ══════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def carregar_dados():
    """Carrega e processa dados de militaresALL.csv e TAF.csv"""
    
    try:
        # 1. Carregar militares
        df_militares = pd.read_csv('data/militaresALL.csv', encoding='utf-8')
        
        # 2. Carregar TAF (do repositório GitHub)
        try:
            df_taf = pd.read_csv('TAFCBMAM-main/TAF.csv')
        except:
            df_taf = pd.read_csv('data/TAF.csv')
        
        # 3. Preparar dados de TAF
        # Detectar as colunas
        colunas_taf = df_taf.columns.tolist()
        
        # Procurar pelas colunas de exercícios
        col_nome = None
        for col in colunas_taf:
            if 'NOME' in str(col).upper() or 'NAME' in str(col).upper():
                col_nome = col
                break
        
        if col_nome is None:
            col_nome = colunas_taf[3]  # Geralmente a 4ª coluna
        
        # Colunas de exercícios
        col_corrida = None
        col_abdominal = None
        col_flexao = None
        col_natacao = None
        col_barra = None
        
        for col in colunas_taf:
            col_upper = str(col).upper()
            if 'CORR' in col_upper:
                col_corrida = col
            elif 'ABDO' in col_upper:
                col_abdominal = col
            elif 'FLEX' in col_upper:
                col_flexao = col
            elif 'NAT' in col_upper:
                col_natacao = col
            elif 'BARRA' in col_upper:
                col_barra = col
        
        # 4. Fundir dados: TAF com Militares
        df_taf['Nome_TAF'] = df_taf[col_nome].str.strip().str.upper() if col_nome else ''
        df_militares['Nome_Upper'] = df_militares['Nome Completo'].str.strip().str.upper()
        
        df_merged = df_taf.merge(df_militares[['Nome Completo', 'Nome_Upper', 'Sexo', 'Data de Nascimento', 'Posto/Graduação', 'Quadro']], 
                                 left_on='Nome_TAF', right_on='Nome_Upper', how='left')
        
        # 5. Calcular idade
        df_merged['Idade'] = df_merged['Data de Nascimento'].apply(calcular_idade)
        df_merged['Faixa_Etaria'] = df_merged['Idade'].apply(obter_faixa_etaria)
        
        # 6. Calcular notas para cada exercício
        exercicios = {
            'Corrida': col_corrida,
            'Abdominal': col_abdominal,
            'Flexão': col_flexao,
            'Natação': col_natacao,
            'Barra': col_barra
        }
        
        for ex, col in exercicios.items():
            if col:
                df_merged[f'Nota_{ex}'] = df_merged.apply(
                    lambda row: obter_nota_exercicio(ex, row[col], row.get('Idade'), row.get('Sexo')),
                    axis=1
                )
        
        # 7. Calcular média final
        cols_notas = [f'Nota_{ex}' for ex, col in exercicios.items() if col and f'Nota_{ex}' in df_merged.columns]
        
        if cols_notas:
            df_merged['Média_Final'] = df_merged[cols_notas].mean(axis=1).round(2)
        else:
            df_merged['Média_Final'] = np.nan
        
        df_merged['Classificação'] = df_merged['Média_Final'].apply(classificar_media)
        
        # 8. Limpar dados
        df_merged['Sexo'] = df_merged['Sexo'].str.strip()
        df_merged['Idade'] = df_merged['Idade'].fillna(0).astype(int)
        
        return df_merged
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# ══════════════════════════════════════════════════════════════════════════════
# CARREGAR DADOS
# ══════════════════════════════════════════════════════════════════════════════

df = carregar_dados()

if df.empty:
    st.error("Erro: Não foi possível carregar os dados. Verifique os arquivos de dados.")
    st.stop()

# Custom CSS
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR - FILTROS
# ══════════════════════════════════════════════════════════════════════════════

st.sidebar.title("⚙️ Filtros do Dashboard")

# Sexo
sexos = ['Todos'] + sorted([s for s in df['Sexo'].dropna().unique() if s])
filtro_sexo = st.sidebar.selectbox("Sexo", sexos)

# Faixa Etária
faixas = ['Todos'] + sorted([f for f in df['Faixa_Etaria'].dropna().unique() if f])
filtro_faixa = st.sidebar.selectbox("Faixa Etária", faixas)

# Posto
postos = ['Todos'] + sorted([p for p in df['Posto/Graduação'].dropna().unique() if p])
filtro_posto = st.sidebar.selectbox("Posto/Graduação", postos)

# Quadro
quadros = ['Todos'] + sorted([q for q in df['Quadro'].dropna().unique() if q])
filtro_quadro = st.sidebar.selectbox("Quadro", quadros)

# Classificação
classificacoes = ['Todos'] + sorted([c for c in df['Classificação'].dropna().unique() if c and c != 'Sem Dados'])
filtro_classificacao = st.sidebar.selectbox("Classificação", classificacoes)

# Aplicar filtros
df_filtrado = df.copy()
if filtro_sexo != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Sexo'] == filtro_sexo]
if filtro_faixa != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Faixa_Etaria'] == filtro_faixa]
if filtro_posto != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Posto/Graduação'] == filtro_posto]
if filtro_quadro != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Quadro'] == filtro_quadro]
if filtro_classificacao != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Classificação'] == filtro_classificacao]

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

st.title("📊 Dashboard TAF CBMAM")
st.markdown("Análise do Teste de Aptidão Física - Corpo de Bombeiros Militar do Amazonas")

st.sidebar.image(_get_cbmam_image_url(), use_column_width=True)

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Militares Avaliados", len(df_filtrado))
with col2:
    media_geral = df_filtrado['Média_Final'].mean()
    st.metric("Média Geral", f"{media_geral:.2f}" if not pd.isna(media_geral) else "N/A")
with col3:
    excelentes = len(df_filtrado[df_filtrado['Classificação'] == 'Excelente'])
    st.metric("Excelentes", excelentes)
with col4:
    insuficientes = len(df_filtrado[df_filtrado['Classificação'] == 'Insuficiente'])
    st.metric("Insuficientes", insuficientes)

st.markdown("---")

# Gráficos
col1, col2 = st.columns(2)

with col1:
    clf_counts = df_filtrado['Classificação'].value_counts().reset_index()
    clf_counts.columns = ['Classificação', 'Quantidade']
    
    fig_pie = px.pie(
        clf_counts,
        values='Quantidade',
        names='Classificação',
        title='Distribuição de Classificação',
        color_discrete_map={
            'Excelente': '#22c55e',
            'Bom': '#3b82f6',
            'Regular': '#f59e0b',
            'Insuficiente': '#ef4444'
        }
    )
    fig_pie.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    media_por_classf = df_filtrado.groupby('Classificação')['Média_Final'].mean().sort_values(ascending=False)
    fig_bar = px.bar(
        x=media_por_classf.index,
        y=media_por_classf.values,
        title='Média Final por Classificação',
        color=media_por_classf.index,
        color_discrete_map={
            'Excelente': '#22c55e',
            'Bom': '#3b82f6',
            'Regular': '#f59e0b',
            'Insuficiente': '#ef4444'
        }
    )
    fig_bar.update_layout(template="plotly_dark", height=400, showlegend=False)
    fig_bar.update_xaxes(tickangle=-45)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# Ranking
st.subheader("🏆 Top 20 Militares - Ranking por Média Final")
top_20 = df_filtrado.nlargest(20, 'Média_Final')[['Nome Completo', 'Posto/Graduação', 'Faixa_Etaria', 'Média_Final', 'Classificação']].reset_index(drop=True)
top_20.index = top_20.index + 1

st.dataframe(
    top_20,
    use_container_width=True
)

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard TAF CBMAM | 2026 | GitHub: TAFCBMAM")
