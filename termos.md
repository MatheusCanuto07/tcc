# Termos

## CNAE

Classificação Nacional de Atividades Econômicas. É o código oficial que diz qual é a atividade principal de uma empresa. A Receita Federal grava esse código no CNPJ. A versão usada no cadastro é a CNAE-Subclasses 2.3, mantida pelo IBGE.

No trabalho, a CNAE é o critério para separar as empresas de Tecnologia da Informação das demais. O recorte inicial é a divisão 62. O código no arquivo da Receita vem sem pontuação (`6201501`); na planilha do IBGE aparece com máscara (`6201-5/01`).

Detalhe da fonte: [fontes de dados/02-cnae-ibge.md](fontes%20de%20dados/02-cnae-ibge.md).

## CNEFE

Cadastro Nacional de Endereços para Fins Estatísticos. É a base de endereços do Censo Demográfico 2022, do IBGE, com latitude e longitude. Não é um cadastro de empresas e não traz CNPJ.

No trabalho, serve para transformar o endereço e o CEP do CNPJ em ponto no mapa. A junção não é perfeita: o CNPJ não tem o identificador do CNEFE, e endereço incompleto fica sem coordenada.

Detalhe da fonte: [fontes de dados/03-cnefe-ibge.md](fontes%20de%20dados/03-cnefe-ibge.md).

## CEMPRE-SIDRA

O CEMPRE é o Cadastro Central de Empresas, do IBGE. Publica totais de unidades locais, pessoal ocupado e salários por atividade econômica e por município. Não publica a lista de CNPJs nem a localização de cada empresa.

O SIDRA é o sistema do IBGE em que essas tabelas são consultadas e baixadas em XLSX, CSV ou ODS.

No trabalho, serve para conferir se a contagem feita a partir do CNPJ está na mesma ordem de grandeza do dado oficial. A comparação tem de usar o mesmo nível de CNAE e aceitar que o ano do CEMPRE não é o mês do CNPJ.

Detalhe da fonte: [fontes de dados/05-cempre-sidra.md](fontes%20de%20dados/05-cempre-sidra.md).

## RAIS-CAGED

A RAIS é a Relação Anual de Informações Sociais. É a declaração anual de vínculos de emprego formal. O CAGED, na versão atual chamado Novo CAGED, é o registro mensal de admissões e desligamentos. Os dois são do Ministério do Trabalho e Emprego.

Os microdados públicos não trazem CNPJ nem nome da empresa. Trazem município, CNAE e características do vínculo.

No trabalho, servem para descrever o emprego do setor em Contagem. Não servem para colocar a empresa no mapa. Número de vínculos não é número de empresas.

Detalhe da fonte: [fontes de dados/06-rais-caged.md](fontes%20de%20dados/06-rais-caged.md).
