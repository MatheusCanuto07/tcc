# Barreto Junior et al. (2021)

Barreto Junior, E. S.; Cavassin, W.; Kozievitch, N. P.; Gutierrez, M. B. Buskaki Empresas: ferramenta para busca de dados abertos de empresas curitibanas. In: **Anais da XVI Escola Regional de Banco de Dados**. Porto Alegre: SBC, 2021. p. 1-10.

No texto do TCC, a citação aparece como Barreto Junior et al. (2021). Chave no `.bib`: `barretojunior2021`.

## Link para ler

DOI: https://doi.org/10.5753/erbd.2021.17233

TCC que originou o artigo (UTFPR): http://repositorio.utfpr.edu.br/jspui/handle/1/28908

## Resumo

Aplicação web para consultar empresas de Curitiba por nome (razão social e nome fantasia), e não só pelo CNPJ. A motivação foi uma ONG que buscava CNPJs manualmente em planilhas para o programa Nota Paraná.

Usa os dados abertos da Receita Federal e informações da prefeitura. Foi feita com Ruby on Rails, PostgreSQL e PostGIS, hospedada no Heroku, com geocodificação pela gem Geocoder. Os autores compararam Levenshtein, Soundex e Metaphone adaptados ao português e escolheram Levenshtein. Relatam que o Nominatim errou até 2 km em alguns endereços.

A ferramenta busca por nome ou CNPJ, lista empresas por bairro e por rua e mostra os detalhes em um mapa dinâmico. Exige cadastro e login. Testes com usuários finais e análise de requisitos aparecem como trabalhos futuros.

No trabalho, é o correlato mais próximo: dados da Receita, recorte municipal e mapa. A diferença é que o foco dele é achar uma empresa, e não caracterizar um setor.
