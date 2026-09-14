# Malhas territoriais do IBGE

Desenho do território. Sem isso o mapa não tem contorno de município nem polígono de bairro para contar concentração.

## Links

- Página das malhas: https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html
- FTP das malhas municipais: https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/
- Bairros do Censo 2022, shapefile de Minas Gerais: https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/bairros/shp/UF/MG_bairros_CD2022.zip
- Pasta dos shapefiles de bairros por UF: https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2022/bairros/shp/UF/

No FTP de malhas municipais, entre na pasta do ano mais recente e depois em `UFs`. O arquivo de Minas traz todos os municípios do estado. Filtre o código **3118601**.

## O que é

Limites oficiais em sistema de coordenadas SIRGAS 2000, projeção geográfica. Inclui município, UF, regiões geográficas e, no Censo 2022, bairros e setores censitários.

O arquivo de bairros de MG tem cerca de 2,2 MB compactado e inclui os bairros mapeados no estado, não só Contagem. Recorte pelo código do município.

## Formato

**Shapefile** dentro de ZIP. Não é CSV, XLSX nem Excel.

Um shapefile útil é um conjunto, não um arquivo só:

- `.shp` — geometria
- `.dbf` — tabela de atributos
- `.shx` — índice
- `.prj` — sistema de coordenadas

Baixe o ZIP inteiro. Abrir só o `.shp` quebra a camada.

Quem lê isso é QGIS, GeoPandas ou uma biblioteca equivalente. Para a aplicação web, converta o recorte de Contagem para **GeoJSON** e sirva só esse arquivo. GeoJSON de um município cabe no frontend. O shapefile de Minas Gerais inteiro, não.

## Atributos que importam

Na malha municipal: código do município (3118601), nome e UF. Isso desenha o limite de Contagem e impede que um ponto geocodificado errado, caindo em Betim ou Belo Horizonte, entre na contagem do município.

Na malha de bairros: código e nome do bairro, e o município a que pertence. Depois de ter latitude e longitude, faça a interseção ponto-polígono. O bairro resultante substitui o bairro digitado no CNPJ.

## Como entra na combinação

- Com o CNPJ: só depois da geocodificação. A chave não é o nome do bairro.
- Com o CNEFE: os dois usam SIRGAS 2000. A interseção funciona sem converter projeção, desde que os dois estejam em graus.
- Com Censo, CEMPRE e PIB: a malha municipal não traz população nem número de empresas. Ela só desenha. Os números vêm das outras fontes, ligados pelo código 3118601.

## Limitação

Bairro do Censo 2022 e bairro usado pela prefeitura não são a mesma malha. Se a Secretaria entregar uma regionalização própria, não misture os dois nomes na mesma tabela sem uma coluna dizendo qual malha foi usada.
