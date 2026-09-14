# Base dos Dados

Não é uma fonte nova. É a mesma Receita, a mesma RAIS e o mesmo IBGE, já tabulados para consulta. Use isto para não baixar o CNPJ do Brasil inteiro só para achar Contagem.

## Links

- Site: https://basedosdados.org/
- Como consultar no BigQuery: https://basedosdados.org/docs/access_data_bq
- Diretório de municípios (códigos IBGE, Receita, TSE): busque `br_bd_diretorios_brasil.municipio` no site
- Conjunto de CNPJ já tratado (quadros e estabelecimentos): https://basedosdados.org/dataset/e43f0d5b-43cf-4bfb-8d90-c38a4e0d7c4f

Tabelas úteis no BigQuery, no projeto `basedosdados`:

| Tabela | Conteúdo |
| --- | --- |
| `br_rf_cnpj.estabelecimentos` | Estabelecimentos do CNPJ |
| `br_rf_cnpj.socios` | Sócios. Dispensável para o mapa |
| `br_bd_diretorios_brasil.municipio` | De-para entre código IBGE e código da Receita |
| `br_me_rais.microdados_vinculos` | RAIS |
| `br_me_caged.microdados_movimentacoes` | CAGED |
| `br_ibge_pib.municipio` | PIB municipal |

Confira no site o nome exato da tabela antes de citar no TCC. A organização renomeia dataset quando a fonte original muda de ministério.

## O que é

Organização que copia dados abertos oficiais para um datalake e documenta a coluna. A cobertura do CNPJ é nacional, em "fotografias" por data. Cada data repete o universo de CNPJs daquele dia. Se selecionar duas datas, a mesma empresa aparece duas vezes.

## Formato

A consulta é SQL no BigQuery, que exige conta Google. O resultado da consulta, já filtrado, exporta em **CSV**.

Não há um XLSX pronto de "empresas de TI de Contagem". Você escreve o filtro e baixa só as linhas que interessam. Para o volume de um município e um punhado de CNAEs, o CSV resultante cabe no Excel.

A cota gratuita do BigQuery aguenta esse filtro. Não rode `SELECT *` na tabela nacional.

## Como filtrar

`id_municipio = '3118601'` é o filtro de Contagem quando a tabela já está no código IBGE. Se a coluna for o código da Receita, ligue antes com `br_bd_diretorios_brasil.municipio`, no campo `id_municipio_rf`.

Filtre também situação cadastral ativa e a lista de CNAE. Exporte esse resultado e siga o cruzamento com o CNEFE localmente. A Base dos Dados não substitui o CNEFE nem a malha de bairros.

## Por que combinar, e não escolher um ou outro

A Base dos Dados acelera o recorte e documenta o campo. A Receita continua sendo a fonte citada, porque é ela que produz o dado. No texto, escreva que os microdados vêm da Receita Federal e que a extração do município foi feita a partir da cópia tratada, informando a data da fotografia.

Se a consulta falhar ou a tabela estiver defasada, volte ao ZIP oficial descrito em [CNPJ da Receita](01-cnpj-receita-federal.md). Os dois caminhos têm de chegar na mesma lista.

## Limitação

Serviço de terceiro em cima de dado público. Para a banca, a referência bibliográfica é a Receita, o IBGE ou o Ministério do Trabalho, não a plataforma. A plataforma entra na metodologia, como ferramenta de extração.
