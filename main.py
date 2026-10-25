#1 Leitura dos Dados
import pandas as pd

df = pd.read_csv("halloween_vendas.csv", encoding="utf-8")
print(df.shape)
print(df.head(5))

import re

#2 substitui valores nulos por "sem categoria"
total_vazios = df['categoria'].isna().sum()
# trata nulos 
df['categoria'] = df['categoria'].fillna("sem categoria")
# passa para minúsculas e remover espaços
df['categoria'] = df['categoria'].str.lower().str.strip()
# aplica regex para manter apenas letras sem acento e espaços
df['categoria'] = df['categoria'].str.replace(r'[^a-z\s]', '', regex=True)
# caso o regex tenha limpado tudo de uma string problemática, preenche novamente
df['categoria'] = df['categoria'].replace('', 'sem categoria')
total_preenchidos = df['categoria'].isna().sum()
print("total de categorias vazias preenchidas: ", total_vazios)
print("total de categorias vazias preenchidas: ", total_preenchidos)
print(df['categoria'].head())

# conversão para numéricos
df['quantidade_num'] = pd.to_numeric(df['quantidade'], errors='coerce')
df['preco_unitario_num'] = pd.to_numeric(df['preco_unitario'], errors='coerce')

# criar máscaras booleanas para identificar as inconsistências
mascara_qtd_invalida = (
    df['quantidade_num'].isna() |
    (df['quantidade_num'] <= 0) |
    (df['quantidade_num'] % 1 != 0) 
)

mascara_preco_invalido = (
    df['preco_unitario_num'].isna() |
    (df['preco_unitario_num'] < 0)
)

# máscara combinada: registro tem pelo menos um problema numérico
mascara_problema_numerico = mascara_qtd_invalida | mascara_preco_invalido

# adiciona as colunas booleanas no DataFrame
df['qtd_invalida'] = mascara_qtd_invalida
df['preco_invalido'] = mascara_preco_invalido
df['tem_inconsistencia_numerica'] = mascara_problema_numerico

# contagens individuais por campo
total_qtd_invalida = mascara_qtd_invalida.sum()
total_preco_invalido = mascara_preco_invalido.sum()

# total de pedidos únicos afetados
total_pedidos_afetados = mascara_problema_numerico.sum()

print("Pedidos com quantidade inválida (<=0 ou nulo): ", total_qtd_invalida)
print("Pedidos com quantidade inválida (<0 ou nulo): ", total_preco_invalido)
print("Total de pedidos afetados por problemas numéricos: ", total_pedidos_afetados)


registros_com_problema = df[mascara_problema_numerico]
print("\nExemplo de registro inconsistentes:")
print(registros_com_problema[['quantidade', 'preco_unitario', 'qtd_invalida', 'preco_invalido']].head())

# padronizar canal
canais_validos = {"mercado": "Mercado",
                  "loja física": "Loja física",
                  "web": "Web",
                  "site": "Web"}

canal_limpo = df['canal_venda'].astype(str).str.strip().str.lower()

df['canal_venda'] = canal_limpo.map(canais_validos).fillna(df['canal_venda'])

print("\nPadronizar Canal")
print(df['canal_venda'].value_counts(dropna=False))

# trata caso a data_entrega venha como NaN ou string vazia/com espaço
sem_entrega = df['data_entrega'].isna() | (df['data_entrega'].astype(str).str.strip() == '')

# criando 2 grupos de investigação
grupo_1 = sem_entrega & (df['status_pedido'].astype(str).str.strip().str.lower() == 'cancelado')

grupo_2 = sem_entrega & (df['status_pedido'].astype(str).str.strip().str.lower() != 'cancelado')

# filtra os DataFrames e realizar as contagens
df_grupo_1 = df[grupo_1]
df_grupo_2 = df[grupo_2]

total_sem_entrega = sem_entrega.sum()
qtd_grupo_1 = len(df_grupo_1)
qtd_grupo_2 = len(df_grupo_2)

print("\nTotal de pedidos sem data de entrega: ", total_sem_entrega)
print("Grupo 1 (Sem entrega + Status Cancelado): ", qtd_grupo_1)
print("Grupo 2 (Sem entrega + Status Diferente de Cancelado): ", qtd_grupo_2)

print("\n hipótese ")
if qtd_grupo_2 == 0:
    print("hipótese é verdadeira. Todos os pedidos sem data de entrega estão cancelados.")
else:
    print("hipótese é falsa! Existem pedidos sem data de entrega com outros status.")
    print("\nExemplo de até 3 registros de Grupo 2 (contraexemplos):")
    print(df_grupo_2[['status_pedido', 'data_venda', 'data_entrega', 'canal_venda']].head(5))