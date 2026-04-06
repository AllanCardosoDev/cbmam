# data_processing.py

import pandas as pd
from datetime import datetime
from scoring_rules import calcular_nota_exercicio, MAP_EXERCICIOS

def load_and_process_data(militares_path: str, avaliacoes_path: str) -> pd.DataFrame:
    """
    Carrega os dados dos militares e avaliações, calcula a idade,
    e aplica as regras de pontuação do TAF.
    """
    # Carregar dados dos militares
    df_militares = pd.read_csv(militares_path, sep=';', encoding='utf-8', decimal=',')

    # Padronizar nomes de colunas para merge
    df_militares.rename(columns={'MATRICULA': 'MATRICULA_MILITAR'}, inplace=True)

    # Limpar e converter 'DATA DE NASCIMENTO' para datetime
    # Assumindo que a coluna 'DATA DE NASCIMENTO' está no formato DD/MM/YYYY
    df_militares['DATA DE NASCIMENTO'] = pd.to_datetime(df_militares['DATA DE NASCIMENTO'], format='%d/%m/%Y', errors='coerce')

    # Calcular idade
    current_date = datetime.now()
    df_militares['IDADE'] = df_militares['DATA DE NASCIMENTO'].apply(
        lambda dob: current_date.year - dob.year - ((current_date.month, current_date.day) < (dob.month, dob.day)) if pd.notna(dob) else np.nan
    )
    df_militares['IDADE'] = df_militares['IDADE'].astype('Int64') # Para permitir NaN em inteiros

    # Carregar dados das avaliações
    df_avaliacoes = pd.read_csv(avaliacoes_path, sep=';', encoding='utf-8', decimal=',')

    # Renomear 'MATRICULA' para 'MATRICULA_MILITAR' para o merge
    df_avaliacoes.rename(columns={'MATRICULA': 'MATRICULA_MILITAR'}, inplace=True)

    # Converter colunas de desempenho para numérico, tratando vírgulas como decimais
    colunas_desempenho = [col for col in df_avaliacoes.columns if col not in ['MATRICULA_MILITAR', 'SEXO']]
    for col in colunas_desempenho:
        df_avaliacoes[col] = df_avaliacoes[col].astype(str).str.replace(',', '.', regex=False)
        df_avaliacoes[col] = pd.to_numeric(df_avaliacoes[col], errors='coerce')

    # Unir os DataFrames
    df_all = pd.merge(df_avaliacoes, df_militares[['MATRICULA_MILITAR', 'SEXO', 'IDADE', 'NOME COMPLETO']], on='MATRICULA_MILITAR', how='left')

    # Preencher SEXO e IDADE caso venham nulos do merge (se df_avaliacoes tiver mais militares)
    # Isso é uma redundância, pois df_militares já deveria ter todos os dados.
    # No entanto, se df_avaliacoes tiver militares que não estão em df_militares,
    # esses campos ficarão NaN. Para este exemplo, assumimos que df_militares é a fonte primária.

    # Padronizar a coluna SEXO para 'Masculino' e 'Feminino'
    df_all['SEXO'] = df_all['SEXO'].replace({'M': 'Masculino', 'F': 'Feminino'})

    # Aplicar as regras de pontuação
    for col_desempenho, nome_exercicio in MAP_EXERCICIOS.items():
        df_all[f'NOTA_{nome_exercicio}'] = df_all.apply(
            lambda row: calcular_nota_exercicio(
                row['SEXO'],
                row['IDADE'],
                nome_exercicio,
                row[col_desempenho]
            ) if pd.notna(row['IDADE']) and pd.notna(row[col_desempenho]) else 0.0,
            axis=1
        )

    # Calcular a nota total (média das notas dos exercícios)
    colunas_notas = [col for col in df_all.columns if col.startswith('NOTA_')]
    df_all['NOTA_TOTAL'] = df_all[colunas_notas].mean(axis=1)

    return df_all
