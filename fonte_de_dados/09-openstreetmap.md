# OpenStreetMap

Mapa de fundo. Não é cadastro de empresas e não substitui o CNEFE na geocodificação em lote.

## Links

- Mapa: https://www.openstreetmap.org/
- Nominatim (busca de endereço, um a um): https://nominatim.openstreetmap.org/
- Política de uso do Nominatim: https://operations.osmfoundation.org/policies/nominatim/
- Overpass Turbo (consulta da base, uso pontual): https://overpass-turbo.eu/
- Tiles, com atribuição obrigatória: https://tile.openstreetmap.org/{z}/{x}/{y}.png
- Copyright e atribuição: https://www.openstreetmap.org/copyright

## O que é

Mapa colaborativo mundial. Ruas, bairros e o contorno de Contagem existem lá, editados por voluntários. A geometria oficial para contar empresa por bairro continua sendo a malha do IBGE. O OpenStreetMap entra para a pessoa ver a rua debaixo do ponto.

## Formato

Não é CSV, XLSX nem Excel.

- Tiles de imagem, para o fundo do Leaflet, MapLibre ou biblioteca parecida.
- Dados vetoriais sob consulta (Overpass), em JSON ou GeoJSON, se um dia precisar de uma camada extra (rio, via, distrito industrial desenhado por voluntário).
- Nominatim devolve JSON com latitude e longitude de um endereço.

Para o TCC, use os tiles. Não monte o trabalho em cima de extrair "todas as empresas de TI" do OpenStreetMap. Essa tag é incompleta e não tem CNAE.

## Como combinar

O ponto vem do cruzamento CNPJ + CNEFE. O polígono do bairro vem do IBGE. O OpenStreetMap só desenha o fundo. Os três usam latitude e longitude em graus. Dá para sobrepor.

Atribuição visível no mapa: "© colaboradores do OpenStreetMap". Sem isso, o uso dos tiles foge da licença.

## Não faça geocodificação em lote aqui

A política do Nominatim pede no máximo uma consulta por segundo e proíbe uso massivo. Geocodificar centenas ou milhares de CNPJs por essa API quebra a regra e ainda perde para o CNEFE, que já tem coordenada oficial do endereço censitário.

Nominatim serve para testar meia dúzia de endereços que falharam no CNEFE e entender o erro. O resultado desse teste manual não entra como método geral.

## Limitação

Nome de bairro e desenho de via no OpenStreetMap podem divergir da malha do IBGE e do cadastro da prefeitura. Se dois contornos discordarem, o do IBGE é o que vale na contagem.
