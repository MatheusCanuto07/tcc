# RAIS e Novo CAGED

Fonte de emprego formal. Serve para dizer se o setor de TI em Contagem ocupa gente, não para colocar a empresa no mapa.

## Links

- Microdados RAIS e CAGED: https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/acoes-e-programas/programas-projetos-acoes-obras-e-atividades/estatisticas-trabalho/microdados-rais-e-caged
- Página de estatísticas do trabalho: https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho
- Painel do Novo CAGED: https://bi.mte.gov.br/bgcaged/
- FTP dos microdados: ftp://ftp.mtps.gov.br/pdet/microdados/

O FTP não abre em todo navegador. No Windows, cole o endereço na barra do Explorador de Arquivos. No FTP, a RAIS fica na pasta da RAIS e o fluxo mensal na pasta do Novo CAGED, por ano e mês.

Se o FTP travar, use a [Base dos Dados](07-base-dos-dados.md), que já publica essas tabelas para consulta. O painel do Ministério permite recortar município e atividade sem baixar o microdado.

## O que é

A RAIS é a declaração anual de vínculos formais. O Novo CAGED é o fluxo mensal de admissões e desligamentos. Os microdados públicos são não identificados: não vêm com CNPJ nem com nome da empresa. Vêm município, CNAE, ocupação (CBO), escolaridade, sexo, idade e faixa de remuneração, conforme o arquivo.

## Formato

Não é XLSX.

- Texto delimitado, em geral `.txt` compactado em `.7z`.
- Separador: ponto e vírgula (`;`).
- Novo CAGED: UTF-8.
- RAIS mais antiga: frequentemente Latin-1.
- Há um arquivo de layout na mesma pasta do FTP. Sem ele, a coluna não tem nome.

Um ano de vínculos da RAIS, no Brasil, tem vários gigabytes. Não abra no Excel. Se for usar microdado, leia só Minas Gerais ou só o município 311860 e só os CNAEs do recorte, e grave um CSV pequeno.

Para o artigo, o painel agregado pode bastar. Microdado só vale se o resultado for, por exemplo, escolaridade ou sexo dos vínculos formais de TI em Contagem. Isso cabe em uma tabela. Não cabe processar o arquivo nacional inteiro dentro do prazo do TCC.

## O que dá para usar

- Estoque de vínculos formais em Contagem nas classes 62 (e 63, se entrar no recorte), último ano da RAIS disponível.
- Admissões e desligamentos recentes no Novo CAGED, como sinal de movimento do setor. Um mês sozinho não diz tendência.
- CBO, se quiser um parágrafo sobre ocupações (desenvolvedor, suporte, analista) sem identificar empresa.

Código do município na RAIS: confirme no layout se o arquivo usa 6 ou 7 dígitos. Contagem é **311860** ou **3118601**.

## Ligação

Não dá para juntar vínculo com CNPJ nesta divulgação. A ligação é só município + CNAE, no nível da classe. O número de vínculos não é o número de empresas. Uma empresa grande segura os dois. Diga isso no texto.

## Limitação

MEI e sócio sem vínculo CLT quase não aparecem aqui, e aparecem no CNPJ. Por isso RAIS e mapa de estabelecimentos não podem ser apresentados como a mesma contagem.
