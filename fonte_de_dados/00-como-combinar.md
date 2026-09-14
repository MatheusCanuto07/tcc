# Como combinar as fontes

Estas bases cobrem o Brasil ou Minas Gerais. Nenhuma delas, sozinha, entrega o mapa pronto de empresas de TI de Contagem. O recorte do município é um filtro, não uma base separada.

Código de Contagem no IBGE: **3118601**. UF: **MG**. Na RAIS, alguns arquivos usam o código de 6 dígitos **311860**. O código de município da Receita Federal não é o do IBGE: ele está no arquivo `Municipios.zip` da própria base de CNPJ, na linha cujo nome é CONTAGEM.

## O que usar de verdade

| Papel no trabalho | Fonte | Arquivo |
| --- | --- | --- |
| Lista de empresas, CNAE e endereço | [CNPJ da Receita Federal](01-cnpj-receita-federal.md) | CSV dentro de ZIP |
| Definir o que conta como TI | [CNAE do IBGE](02-cnae-ibge.md) | XLSX |
| Latitude e longitude do endereço | [CNEFE do IBGE](03-cnefe-ibge.md) | CSV ou GeoJSON |
| Contorno do município e dos bairros | [Malhas territoriais](04-malhas-territoriais-ibge.md) | Shapefile (ZIP) |
| Consulta mais fácil, sem baixar o Brasil inteiro | [Base dos Dados](07-base-dos-dados.md) | SQL; exporta CSV |
| Conferir se a contagem faz sentido | [CEMPRE / SIDRA](05-cempre-sidra.md) | XLSX, CSV ou ODS |
| Emprego do setor, sem plotar empresa | [RAIS e CAGED](06-rais-caged.md) | TXT |
| Contexto do município | [Censo e PIB](08-censo-e-pib-municipal.md) | XLSX, CSV ou API |
| Mapa de fundo | [OpenStreetMap](09-openstreetmap.md) | Tiles; não é planilha |
| Conferência secundária em MG | [Cadastro de contribuintes do ICMS](10-cadastro-icms-minas-gerais.md) | TXT ou CSV |

O [portal de dados abertos de Minas Gerais](https://dados.mg.gov.br/pt_BR/) não publica o cadastro de empresas com CNAE e endereço. Não gaste tempo procurando essa base lá. A fonte estadual útil é o cadastro de contribuintes do ICMS, e mesmo assim só como conferência.

## Chaves de junção

- **CNPJ básico** (8 primeiros dígitos): liga `Estabelecimentos` com `Empresas` e com `Simples`.
- **CNPJ completo** (14 dígitos): identifica o estabelecimento no mapa. Matriz e filial são registros diferentes.
- **CNAE** (7 dígitos, sem pontuação): liga o estabelecimento à descrição oficial. No arquivo da Receita vem `6201501`; na planilha do IBGE aparece `6201-5/01`.
- **Código de município da Receita**: liga o estabelecimento a `Municipios.zip`. Só depois disso se filtra Contagem.
- **Código IBGE 3118601**: liga o resultado já filtrado às malhas, ao CNEFE, ao Censo, ao PIB, ao CEMPRE e à RAIS.
- **CEP** (8 dígitos): melhor chave prática para achar latitude e longitude no CNEFE. Não é perfeita: um CEP pode cobrir uma quadra inteira.
- **Logradouro + número**: segunda tentativa, quando o CEP existir dos dois lados e o número estiver preenchido. Espere falha: a Receita usa `S/N`, abreviações e complemento solto.

## Ordem de trabalho

1. Baixe a estrutura da CNAE em XLSX e feche a lista de subclasses de TI. Comece pela divisão 62. A divisão 63 entra só se o recorte for ampliado de propósito.
2. Da base de CNPJ, fique com estabelecimentos de Contagem, situação ativa e CNAE dessa lista. Não carregue o Brasil inteiro na aplicação.
3. Junte razão social, porte e capital social pelo CNPJ básico.
4. Junte latitude e longitude pelo CEP no CNEFE de Contagem. Guarde um campo dizendo se o ponto veio do endereço, do CEP ou se não foi localizado.
5. Recorte a malha de bairros de MG para Contagem e conte quantos pontos caem em cada bairro. Isso alimenta o mapa e a tabela.
6. Use CEMPRE e RAIS só para comparar totais. Eles não substituem o ponto no mapa.
7. O mapa de fundo vem do OpenStreetMap. Não use o Nominatim para geocodificar milhares de endereços: a política de uso não permite isso em lote. O CNEFE existe para essa etapa.

## O que não esperar dessas fontes

Nenhuma base aberta nacional traz, de forma confiável e junta, faturamento, número de funcionários por CNPJ e coordenada oficial do estabelecimento. Porte e capital social vêm do CNPJ. Pessoal ocupado, na prática, vem agregado por CNAE e município no CEMPRE ou na RAIS. A coordenada é estimada pelo endereço.

Se a Secretaria de Contagem entregar a base geolocalizada, ela entra como conferência, não como dependência. O trabalho precisa fechar com as fontes desta pasta.
