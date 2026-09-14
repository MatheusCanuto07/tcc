# CNEFE — Cadastro Nacional de Endereços para Fins Estatísticos

É a fonte para transformar o endereço do CNPJ em ponto no mapa. Cobre o Brasil. O arquivo de Contagem é um recorte municipal.

## Links

- Página oficial: https://www.ibge.gov.br/estatisticas/sociais/populacao/38734-cadastro-nacional-de-enderecos-para-fins-estatisticos.html
- Resultados e dicionários: https://www.ibge.gov.br/estatisticas/sociais/populacao/38734-cadastro-nacional-de-enderecos-para-fins-estatisticos.html?edicao=40122&t=resultados
- CSV por município (entre em `31_MG`): https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE/CSV/Municipio/
- GeoJSON por UF: https://ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE/GeoJSON/UF_20240910/

O arquivo de Contagem segue o padrão `3118601_CONTAGEM.zip` dentro da pasta `31_MG`. Confira o nome exato na pasta, porque o IBGE pode usar underscore ou variação do nome.

Não baixe o GeoJSON de Minas Gerais inteiro se o objetivo é só Contagem. O arquivo da UF 31 passa de 600 MB. O CSV do município é o arquivo certo.

## O que é

Cadastro de endereços do Censo Demográfico 2022, com coordenadas coletadas pelo IBGE. Inclui domicílio e estabelecimento. Não é um cadastro de empresas e não tem CNPJ nem CNAE.

A foto é a do Censo, divulgada em 2024. Endereço novo, aberto depois da coleta, pode não estar lá.

## Formato

- Microdados por município: **CSV** dentro de ZIP.
- Também existe **GeoJSON**.
- Dicionário de variáveis: **XLS**.
- Agregados por CEP: **CSV**, com dicionário XLS.
- Coordenadas no sistema SIRGAS 2000 (EPSG:4674). Latitude e longitude em graus. O Leaflet e o OpenStreetMap aceitam esse sistema.

Não é XLSX na origem. O CSV do município de Contagem abre em Python sem problema. No Excel, só se o arquivo do município não estourar o limite de linhas.

## Campos úteis

Código do município, distrito, setor censitário, tipo e nome do logradouro, número, complemento, localidade, CEP, latitude, longitude e espécie do endereço.

Para o cruzamento, use CEP, nome do logradouro e número. Guarde o setor censitário se for agregar o mapa em unidade oficial do IBGE, em vez de bairro.

## Como juntar com o CNPJ

1. Normalize o CEP dos dois lados para 8 dígitos, sem hífen.
2. Primeiro case CEP + número, quando o número do CNPJ não for vazio nem `S/N`.
3. Se falhar, use só o CEP e marque o ponto como aproximado. Várias empresas no mesmo CEP vão cair no mesmo lugar ou muito perto. Isso distorce mapa de calor se não for dito.
4. Se o CEP do CNPJ não existir no CNEFE, o registro entra na tabela e nos gráficos, mas fica de fora do mapa de pontos. Conte essa perda. Ela é um resultado do trabalho, não um defeito a esconder.

Não use o nome do bairro do CNPJ para ligar ao CNEFE. A grafia não bate (`ELDORADO` e `JARDIM ELDORADO`, abreviação, acento).

## Limitações

- Não há chave CNPJ. A junção é por endereço e sempre incompleta.
- A coordenada é a do endereço censitário, não a fachada auditada da empresa.
- A base não atualiza todo mês, ao contrário do CNPJ. Empresa aberta depois de 2022 pode ter CEP novo sem correspondente.
