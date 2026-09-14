# CNAE — Classificação Nacional de Atividades Econômicas

Dicionário oficial para decidir quais códigos entram no recorte de Tecnologia da Informação. Não é uma lista de empresas.

## Links

- Busca da estrutura: https://cnae.ibge.gov.br/?view=estrutura
- Página da classificação: https://www.ibge.gov.br/estatisticas/metodos-e-classificacoes/classificacoes-e-listas-estatisticas/9078-classificacao-nacional-de-atividades-economicas.html
- Downloads da CONCLA (planilhas): https://concla.ibge.gov.br/classificacoes/download-concla.html
- Estrutura detalhada da CNAE-Subclasses 2.3 (XLSX): https://concla.ibge.gov.br/images/concla/documentacao/CNAE_Subclasses_2_3_Estrutura_Detalhada.xlsx
- Tabela de correspondência entre versões (XLSX): https://concla.ibge.gov.br/images/concla/documentacao/CNAE_Subclasses_2_3_Tabelas_de_correspond%C3%AAncia.xlsx

Se o link direto do XLSX falhar, use a página de downloads e baixe a linha "CNAE 2.3 Subclasses".

## O que é

Hierarquia usada pela Receita, pelo IBGE e pelo Ministério do Trabalho para classificar a atividade econômica. A versão de uso cadastral é a CNAE-Subclasses 2.3. A seção J é "Informação e comunicação" (divisões 58 a 63). Dentro dela, a divisão 62 é a de serviços de tecnologia da informação.

## Formato

**XLSX** (Excel). Também há páginas HTML para consulta código a código. Não é CSV na origem, mas a planilha pode ser salva como CSV depois.

A tabela de correspondência, também XLSX, serve se uma fonte antiga citar CNAE 2.0, 2.1 ou 2.2 e for preciso alinhar com o código de 7 dígitos do CNPJ.

## Como usar no trabalho

O CNPJ guarda o código sem máscara (`6201501`). A planilha mostra seção, divisão, grupo, classe, subclasse e a denominação (`6201-5/01`). Na junção, tire ponto, barra e hífen dos dois lados.

Recorte recomendado para começar, divisão 62:

| Código | Atividade |
| --- | --- |
| 6201-5/01 | Desenvolvimento de programas de computador sob encomenda |
| 6201-5/02 | Web design |
| 6202-3/00 | Desenvolvimento e licenciamento de programas customizáveis |
| 6203-1/00 | Desenvolvimento e licenciamento de programas não customizáveis |
| 6204-0/00 | Consultoria em tecnologia da informação |
| 6209-1/00 | Suporte técnico, manutenção e outros serviços em TI |

Ampliação possível, e que precisa ser justificada, não assumida:

| Código | Por que não entra sozinho |
| --- | --- |
| 6311-9/00 | Hospedagem e tratamento de dados. É próximo de TI, mas não é desenvolvimento |
| 6319-4/00 | Portais e conteúdo na internet. Mistura mídia e serviço de informação |
| 4751-2/01 e 4651-6/01 | Comércio de equipamento, não serviço de TI |
| 2621-3/00 e 2622-1/00 | Fabricação de equipamento |
| 9511-8/00 | Conserto de computador |
| 8599-6/03 | Curso de informática |

Confira os nomes na planilha oficial antes de fechar a lista. A versão citada no texto do TCC deve ser a CNAE-Subclasses 2.3.

## Ligação com as outras fontes

- Com o CNPJ: campo `cnae_fiscal_principal` e a lista de secundários.
- Com o CEMPRE e a RAIS: ambos usam CNAE, mas às vezes só até a classe (5 dígitos), não a subclasse. Ao comparar totais, agregue o seu recorte no mesmo nível. Senão a conta não fecha e o erro é de granularidade, não de dado.
