# Censo Demográfico e PIB dos Municípios

Contexto. Não localiza empresa. Serve para não descrever Contagem só pela lista de CNPJ.

## Links

- Censo 2022: https://www.ibge.gov.br/estatisticas/sociais/populacao/22827-censo-demografico-2022.html
- Panorama e resultados: https://censo2022.ibge.gov.br/
- API de localidades (Contagem): https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3118601
- PIB dos municípios: https://www.ibge.gov.br/estatisticas/economicas/contas-nacionais/9088-produto-interno-bruto-dos-municipios.html
- SIDRA, para exportar a tabela pronta: https://sidra.ibge.gov.br/

A API acima devolve nome, UF e a posição de Contagem na hierarquia do IBGE (microrregião, região geográfica, região metropolitana de Belo Horizonte). É JSON, não planilha. Útil para fixar o código 3118601 no texto e no programa.

## O que é

O Censo 2022 traz população e características dos domicílios. O PIB municipal traz o valor adicionado por grandes setores. Nenhum dos dois lista empresa de TI.

Contagem entra como município da Região Metropolitana de Belo Horizonte. Essa frase, com a fonte da API de localidades, evita tratar a cidade como se fosse um polo isolado.

## Formato

- Tabelas do SIDRA e da página do IBGE: **XLSX**, **CSV** e **ODS**.
- API de localidades: **JSON**.
- Agregados do Censo também saem em planilha pelo SIDRA.

São arquivos pequenos. Aqui o Excel resolve.

## O que vale a pena puxar

- População de Contagem no Censo 2022. Com o número de estabelecimentos de TI, dá para calcular estabelecimentos por 10 mil habitantes. Sem a população, "há N empresas" não diz se isso é muito ou pouco.
- Se a tabela do Censo ou do SIDRA tiver população por bairro ou por setor para Contagem, use só como denominador do mapa. Não invente taxa por bairro se a população do bairro não existir na mesma malha em que os pontos foram contados.
- PIB municipal e, se a tabela separar, o valor adicionado de serviços. O PIB não isola "setor de TI". Não escreva que o PIB de serviços é o PIB de tecnologia.

## Ligação

Chave única: **3118601**. Não há CNAE no Censo nem CNPJ no PIB.

Ano diferente é esperado. Censo é 2022, PIB municipal costuma ter um ou dois anos de atraso, CNPJ é o mês que você baixar. Cada número no artigo leva o ano da sua fonte.

## Limitação

Estas duas fontes não mudam o mapa. Se o prazo apertar, elas são as primeiras a virar uma frase de contexto, não um capítulo.
