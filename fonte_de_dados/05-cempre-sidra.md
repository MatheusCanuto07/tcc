# CEMPRE e SIDRA

Fonte de conferência. Responde quantas unidades locais e quanto pessoal ocupado o IBGE enxerga em Contagem, por atividade. Não entrega a lista de CNPJs nem o ponto no mapa.

## Links

- Página do CEMPRE: https://www.ibge.gov.br/estatisticas/economicas/comercio/9016-estatisticas-do-cadastro-central-de-empresas.html
- Tabelas no SIDRA: https://sidra.ibge.gov.br/pesquisa/cempre/tabelas
- Sistema SIDRA: https://sidra.ibge.gov.br/

No SIDRA, escolha a tabela, o nível geográfico Município, o local Contagem (3118601) e o nível da CNAE mais próximo do seu recorte. Nem toda tabela desce até a subclasse.

## O que é

Estatísticas do Cadastro Central de Empresas. O IBGE monta isso a partir do CNPJ, da RAIS, do CAGED e do eSocial, e publica totais: unidades locais ativas, pessoal ocupado, pessoal assalariado e salários. O recorte geográfico publicado chega a município, não a bairro.

A divulgação costuma sair com um ou dois anos de defasagem em relação ao mês do CNPJ. Compare ano com ano, não a foto de hoje com a tabela do CEMPRE.

## Formato

A consulta no SIDRA exporta **XLSX**, **CSV** e **ODS**. É o formato mais confortável desta pasta para abrir direto no Excel.

Há também notas metodológicas em PDF na página do CEMPRE. Leia o suficiente para saber se MEI entra na tabela que você baixou. Parte das divulgações deixa MEI de fora porque ele não declara folha como as demais empresas. Se o seu mapa incluir MEI e o CEMPRE não, os totais vão divergir de propósito.

## O que dá para usar

- Número de unidades locais ativas em Contagem nas classes da divisão 62 (e 63, se o recorte incluir).
- Pessoal ocupado e assalariado nessas classes.
- Uma frase de resultado do tipo: o mapa lista N estabelecimentos ativos no CNPJ de tal mês; o CEMPRE de tal ano registrava N unidades locais na mesma classe.

Isso atende a banca quando ela pergunta se o resultado foi confrontado com outra fonte. Não serve para colorir o bairro.

## Ligação

Chave: código IBGE **3118601** e código CNAE no mesmo nível da tabela (em geral classe, 5 dígitos, não subclasse). Agregue o seu extrato do CNPJ até a classe antes de comparar.

## Limitação

Não há razão social, endereço nem coordenada. Não tente "distribuir" o total do CEMPRE pelos bairros. Isso inventaria um dado que a fonte não tem.
