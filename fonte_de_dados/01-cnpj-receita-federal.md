# CNPJ — Dados abertos da Receita Federal

Fonte principal. É o cadastro nacional de pessoas jurídicas. Cobre o Brasil inteiro e dá para filtrar Contagem.

## Links

- Página de cadastros abertos: https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos/cadastros
- Catálogo no Portal de Dados Abertos: https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-da-pessoa-juridica---cnpj
- Repositório dos arquivos (pastas mensais): https://arquivos.receitafederal.gov.br/index.php/s/YggdBLfdninEJX9
- Layout oficial dos campos (PDF): https://www.gov.br/receitafederal/dados/cnpj-metadados.pdf

A Receita publica uma pasta por mês. Entre na mais recente. O catálogo do dados.gov.br aponta para esse conjunto, mas o download em massa sai do repositório da Receita.

## O que é

Fotografia mensal de todos os CNPJs do país: matrizes, filiais, situação cadastral, atividade econômica e endereço declarado. Não é uma base já filtrada por cidade nem por setor.

## Formato

Não é XLSX e não abre bem no Excel.

- Arquivos `.zip`.
- Dentro deles, CSV **sem cabeçalho**.
- Separador: ponto e vírgula (`;`).
- Codificação: Latin-1 / ISO-8859-1, não UTF-8.
- Os nomes de coluna estão no PDF de layout, na ordem das posições.

Tamanho aproximado da foto nacional: vários gigabytes compactados. `Estabelecimentos0.zip` a `Estabelecimentos9.zip` são os maiores (centenas de MB cada). Não importe isso numa planilha. Leia com Python, DuckDB ou similar, filtre Contagem e grave só o recorte em CSV. Esse recorte, aí sim, pode ir para XLSX.

## Arquivos que importam

| Arquivo | Para que serve |
| --- | --- |
| `Estabelecimentos*.zip` | Onde a empresa funciona: CNPJ completo, nome fantasia, situação, CNAE, endereço, CEP, bairro, UF, município, telefone, e-mail, data de início |
| `Empresas*.zip` | Razão social, natureza jurídica, capital social, porte |
| `Simples.zip` | Se é optante do Simples Nacional ou MEI |
| `Cnaes.zip` | Código e descrição da atividade |
| `Municipios.zip` | Traduz o código interno da Receita para o nome do município |
| `Motivos.zip` | Motivo da situação cadastral |
| `Naturezas.zip` | Natureza jurídica |
| `Socios*.zip` | Quadro de sócios. Não é necessário para o mapa. CPF de pessoa física vem mascarado |

A chave entre `Empresas`, `Estabelecimentos` e `Simples` é o **CNPJ básico** (8 primeiros dígitos).

## Campos úteis em Estabelecimentos

- CNPJ básico, ordem e dígito. Ordem `0001` é matriz; as demais são filiais.
- Identificador matriz/filial: `1` matriz, `2` filial.
- Nome fantasia.
- Situação cadastral: `02` ativa. As outras (nula, suspensa, inapta, baixada) devem sair do mapa, salvo se o trabalho quiser histórico.
- Data da situação cadastral e data de início da atividade.
- CNAE fiscal principal (7 dígitos) e CNAEs secundários, estes separados por vírgula.
- Tipo de logradouro, logradouro, número, complemento, bairro, CEP, UF e município.

Não há latitude nem longitude.

## Campos úteis em Empresas

- Razão social.
- Natureza jurídica.
- Capital social.
- Porte: `00` não informado, `01` microempresa, `03` empresa de pequeno porte, `05` demais.

Porte e capital social não estão no arquivo de estabelecimentos. Sem essa junção, o painel fica só com endereço e CNAE.

## Como filtrar Contagem

1. Abra `Municipios.zip` e ache a linha CONTAGEM. Anote o código de 4 dígitos da Receita.
2. Nos estabelecimentos, fique com `uf = MG` e esse código de município.
3. Fique com situação `02`.
4. Fique com o CNAE principal (e, se a regra do trabalho permitir, o secundário) na lista definida na fonte da CNAE.

O bairro neste arquivo é texto digitado no cadastro. Não confie nele para agregar o mapa. A regionalização espacial deve sair da coordenada cruzada com a malha de bairros do IBGE.

## Limitações

- Endereço pode estar vazio, desatualizado ou como `S/N`.
- O CNAE é o declarado, não uma auditoria do que a empresa faz.
- Usar só o CNAE principal subconta o setor. Usar qualquer secundário infla a base. Essa regra precisa estar escrita na metodologia.
- Atualização mensal. Para o TCC, fixe a pasta do mês usada e cite essa data.
