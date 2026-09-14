# Cadastro de contribuintes do ICMS — Minas Gerais

Fonte estadual. Serve só como marca extra em quem já está na lista do CNPJ. Não tem CNAE, não tem endereço útil e não tem coordenada.

## Links

- Página de download: https://portalsped.fazenda.mg.gov.br/spedmg/cteos/Consulta-Cadastro-de-Contribuintes/
- Portal de dados abertos do estado (não tem esta base): https://dados.mg.gov.br/pt_BR/

O portal estadual publica orçamento, sanções e outros conjuntos. Não publica o cadastro econômico com atividade e geolocalização. A Secretaria de Fazenda é que oferece o cadastro resumido de contribuintes do ICMS, atualizado semanalmente.

## O que é

Lista de quem tem inscrição estadual em Minas Gerais. O arquivo resumido traz inscrição estadual, CNPJ, nome do contribuinte e situação cadastral perante o ICMS.

Empresa de serviço de TI muitas vezes não é contribuinte de ICMS. Ausência nesta lista não significa que a empresa não existe. Presença significa que ela tem inscrição estadual, o que é mais comum em comércio e indústria do que em software.

## Formato

O download sai da página da SEF/MG. O arquivo semanal costuma ser texto delimitado (**TXT** ou **CSV**), não XLSX. Confira o separador e a codificação no arquivo que baixar antes de citar o formato no TCC. Não assuma Excel.

A cobertura é estadual. Filtre pelo CNPJ que já está no recorte de Contagem. Não use este arquivo para descobrir quem é de Contagem: ele não traz município de forma confiável para esse fim.

## Como juntar

Chave: CNPJ de 14 dígitos, sem pontuação, contra o CNPJ completo do estabelecimento.

O que essa junção acrescenta:

- uma coluna "tem inscrição estadual em MG" (sim ou não);
- a situação dessa inscrição, que não é a mesma situação cadastral da Receita.

Não use o nome desta lista para corrigir razão social. A Receita é a fonte do nome.

## Quando vale o esforço

Só se sobrar tempo e o painel tiver um filtro "também contribuinte de ICMS". Para o mapa e para a qualificação, esta fonte é opcional. Se o arquivo vier sem dicionário claro, deixe de fora e registre isso como fonte avaliada e não utilizada.

## Limitação

Não localiza a empresa em Contagem, não classifica TI e não cobre quem só presta serviço. Tratar esta lista como o universo de empresas do município subconta o setor e erra o problema do trabalho.
