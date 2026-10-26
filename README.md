Análise de Dados - Festa em Cena

Este projeto foi desenvolvido para a rede Festa em Cena, especializada em vendas de fantasias e acessórios para o Halloween através dos canais, Mercado, Loja Física e Web.

O objetivo principal é realizar o tratamento, saneamento e exploração inicial da base de dados de vendas "halloween_vendas.csv, identificando inconsistências em textos, valores numéricos e registros temporais antes de submeter os dados a análise.

Execução: Utilizei a bibliotece Pandas

Limpeza e tratamento

Os registros nulos ou vazios foram substituidos por "sem categoria", foi padronizado as letras de maiúsculas e minúsculas, remoção de espaços e pontuação via Regex

A coluna data_vendas foi convertida utilizando datetime

Total de linhas lidas: 1.500

Categorias vazias preenchidas ('sem categoria'): 18

Pedidos afetados por problemas numéricos: 19

Registros com data de venda inválida/vazia: 4

Total de pedidos com status 'cancelado': 109