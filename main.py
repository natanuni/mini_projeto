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

print("\nhipótese ")
if qtd_grupo_2 == 0:
    print("hipótese é verdadeira. Todos os pedidos sem data de entrega estão cancelados.")
else:
    print("hipótese é falsa! Existem pedidos sem data de entrega com outros status.")
    print("\nExemplo de até 5 registros de Grupo 2 (contraexemplos):")
    print(df_grupo_2[['status_pedido', 'data_venda', 'data_entrega', 'canal_venda']].head(5))

# conversão da data de venda e indentificação de inválidas
df['data_venda_dt'] = pd.to_datetime(df['data_venda'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

data_invalida = df['data_venda_dt'].isna()
total_data_invalidas = data_invalida.sum()

print(f"Total de registros com data de venda inválida/vazia: {total_data_invalidas}\n")

# formatação brasileiro (DD/MM/AAAA)
df['data_venda_br'] = df['data_venda_dt'].dt.strftime('%d/%m/%Y')

# Criando a coluna do período (Ano-Mês) em formato YYYY-MM para agrupamento
df['ano_mes'] = df['data_venda_dt'].dt.to_period('M')

# Considerando apenas os canais de venda reconhecidos/padronizados
canais_validos = ['Mercado', 'Loja física', 'Web']
df_canais_validos = df[df['canal_venda'].isin(canais_validos)]

contagem_canal = df_canais_validos['canal_venda'].value_counts()
excluidos_canal = len(df) - len(df_canais_validos)

print(contagem_canal)
print(f"Registros excluídos (canais não reconhecidos/nulos): {excluidos_canal}\n")

# Contagem de Pedidos por Ano-Mês
# datas de venda válidas
df_datas_validas = df[~data_invalida]

# Agrupamento por Ano-Mês
contagem_ano_mes = df_datas_validas.groupby('ano_mes').size()

print(contagem_ano_mes)
print(f"Registros excluídos (datas inválidas): {total_data_invalidas}\n")

print("==================================================")
print("       RELATÓRIO DE STATUS E QUALIDADE DOS DADOS  ")
print("==================================================")
print(f"Total de linhas lidas no CSV:                   {len(df)}")
print(f"Categorias vazias preenchidas ('sem categoria'): {total_vazios}")
print(f"Pedidos com problemas numéricos (Qtd / Preço):  {total_pedidos_afetados}")
print(f"Registros com data de venda inválida/vazia:     {total_data_invalidas}")
print(f"Total de pedidos com status 'Cancelado':         {(df['status_pedido'].str.lower() == 'cancelado').sum()}")
print("--------------------------------------------------")
print("  INVESTIGAÇÃO DA HIPÓTESE (PEDIDOS SEM DATA DE ENTREGA)")
print(f"  - Grupo 1 (Sem entrega + Cancelados):            {qtd_grupo_1}")
print(f"  - Grupo 2 (Sem entrega + Outros Status):         {qtd_grupo_2}")
print("==================================================\n")

print("--- CONTAGEM DE PEDIDOS POR CANAL DE VENDA ---")
print(contagem_canal)
print(f"(Excluídos da contagem por canal inválido/nulo: {excluidos_canal})\n")

print("--- CONTAGEM DE PEDIDOS POR ANO-MÊS ---")
print(contagem_ano_mes)
print(f"(Excluídos da contagem por data de venda inválida: {total_data_invalidas})\n")