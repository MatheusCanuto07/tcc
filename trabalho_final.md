# A Implementação de um Mapa Interativo Sobre as Empresas de TI do Município de Contagem

## Introdução

O uso de dados para compreender a dinâmica econômica de um município pode contribuir para a identificação de características relacionadas à distribuição das atividades econômicas, à ocupação territorial e ao desenvolvimento de determinados setores.
Nesse contexto, dados produzidos e mantidos por órgãos públicos podem ser utilizados não apenas para fins administrativos, mas também para produzir informações que auxiliem cidadãos, empresas, pesquisadores e gestores na compreensão do ambiente econômico local.
Parte desses registros é publicada como dado aberto, em arquivos que cobrem o Brasil ou uma unidade da federação e que podem ser filtrados até o município.
Nenhuma dessas fontes, isoladamente, reúne a identificação do estabelecimento, a atividade econômica e a coordenada geográfica.
Assim, conhecer um setor em uma cidade exige cruzar dados de mais de uma instituição.

A existência de dados abertos com essas características oferece diferentes possibilidades de análise, porém a disponibilização das informações em sua forma original não necessariamente proporciona uma compreensão simples e acessível para diferentes públicos.
Os arquivos podem conter uma quantidade significativa de registros, classificações e atributos geográficos, dispersos em mais de uma fonte, o que dificulta sua interpretação quando analisados diretamente em tabelas ou arquivos isolados.
Segundo Ansari (2022), apesar do aumento da disponibilidade de dados governamentais, sua utilização ainda pode ser limitada, e o emprego de mecanismos de visualização pode tornar essas informações mais compreensíveis, úteis e acessíveis.
Diante desse cenário, este trabalho busca responder à seguinte questão de pesquisa: como dados abertos podem ser combinados para caracterizar e apresentar, de maneira acessível e interativa, informações sobre as empresas do setor de Tecnologia da Informação localizadas no município de Contagem?
Além da caracterização geral dessas empresas, pretende-se explorar sua distribuição territorial a partir da integração entre os endereços dos estabelecimentos e bases geográficas abertas, sem limitar a análise ao aspecto espacial.

Para responder a essa questão, o objetivo geral deste trabalho é desenvolver uma aplicação web interativa que permita caracterizar e visualizar as empresas do setor de Tecnologia da Informação do município de Contagem a partir da integração de dados abertos.
A aplicação reunirá indicadores, gráficos, mapas, tabelas e mecanismos de filtragem, ajustados à estrutura e à qualidade das fontes utilizadas.

Como objetivos específicos, pretende-se:

\begin{itemize}
    \item identificar as fontes de dados abertos pertinentes e mapear os atributos e as chaves que permitem integrá-las para o recorte municipal;
    \item caracterizar as empresas de Tecnologia da Informação localizadas em Contagem, com base na classificação CNAE e nos atributos disponíveis nas bases integradas;
    \item analisar a distribuição geográfica dessas empresas a partir das coordenadas obtidas pela integração entre endereço e bases territoriais abertas;
    \item desenvolver a aplicação web interativa que permita ao usuário consultar, filtrar e interpretar as informações por meio de visualizações e tabelas.
\end{itemize}

A relevância deste estudo justifica-se pela necessidade de aproximar dados públicos, hoje dispersos e pouco acessíveis em sua forma bruta, de públicos que podem utilizá-los na prática.
Como por exemplo:

\begin{itemize}
    \item cidadãos poderão conhecer melhor as empresas de tecnologia existentes no município;
    \item profissionais poderão identificar organizações relacionadas às suas áreas de interesse;
    \item empresários poderão utilizar as informações para conhecer empresas do mesmo setor e identificar possíveis fornecedores ou parceiros;
    \item empreendedores poderão explorar características da distribuição das atividades econômicas no município.
\end{itemize}

Sob a perspectiva acadêmica, o trabalho contribui para a área de Sistemas de Informação ao integrar dados abertos, análise descritiva e visualização interativa em um recorte municipal concreto, alinhado a estudos que relacionam localização e setor de tecnologia em contextos urbanos, como o de Zenka (2021).
A escolha do tema pauta-se na formação em Sistemas de Informação e no interesse por soluções que transformem bases públicas em instrumentos de consulta e interpretação para usuários não especializados.

Este trabalho está estruturado em sete capítulos.
Após esta introdução, o Capítulo 2 apresenta o referencial teórico, e o Capítulo 3 os trabalhos relacionados.
O Capítulo 4 descreve a metodologia empregada, incluindo a obtenção e a integração das bases de dados abertos e os critérios de identificação do setor.
O Capítulo 5 detalha o desenvolvimento da aplicação web.
O Capítulo 6 apresenta e discute os resultados obtidos, bem como a aplicação desenvolvida.
Por fim, o Capítulo 7 apresenta as conclusões do trabalho, suas limitações e as possibilidades de continuidade da pesquisa.

## Referencial Teórico

Este capítulo apresenta os conceitos que fundamentam o trabalho.
São tratados, em sequência, dados abertos, classificação de atividades econômicas (CNAE), distribuição geográfica das empresas e aplicações web interativas.

### Dados abertos governamentais

Dados abertos governamentais são informações produzidas ou mantidas pelo poder público e disponibilizadas para que outras pessoas possam usá-las de novo. O objetivo costuma ser aumentar a transparência, a participação e a inovação. Attard et al. (2015), em revisão de iniciativas nessa área, descrevem um ciclo que inclui publicar e usar os dados. Os autores mostram que só abrir a base não basta: o valor depende dos processos, dos formatos e das regras de uso. Em linha parecida, Janssen, Charalabidis e Zuiderwijk (2012) dizem que os benefícios esperados convivem com barreiras de instituição, lei, técnica e qualidade dos dados, além da dificuldade das tarefas pedidas ao usuário. Assim, ter arquivos públicos disponíveis não garante que eles sejam fáceis de entender ou de reutilizar. Para o uso funcionar na prática, é preciso tratar, combinar e apresentar os dados de forma adequada ao público. Esse raciocínio apoia a ideia deste trabalho: caracterizar as empresas de Tecnologia da Informação em Contagem a partir de bases abertas nacionais e estaduais, e não a partir de um único arquivo municipal já pronto.

### Visualização de dados e usabilidade

A visualização de dados é apresentada na literatura como estratégia para reduzir a distância entre a publicação do dado e o seu uso por pessoas sem domínio técnico avançado.
Graves e Hendler (2013) sustentam que parcela relevante da população poderia se beneficiar de dados abertos, mas não consegue coletar, processar, combinar e interpretar esses registros sem ferramentas que simplifiquem essas operações.
Os autores defendem visualizações e mecanismos exploratórios sobre dados e metadados como meio de comunicação e de apoio à criação de sentido.
Janssen, Charalabidis e Zuiderwijk (2012) convergem nesse ponto ao indicar que recursos de visualização podem diminuir barreiras de uso para usuários pouco experientes, desde que as iniciativas considerem a perspectiva de quem consome a informação.
Ansari (2022) aprofunda essa discussão ao revisar pesquisas sobre visualização de dados governamentais abertos e observar que, apesar do crescimento de casos e ferramentas, ainda há lacunas na avaliação de usabilidade para públicos distintos.
Para o autor, plataformas que embutem gráficos, mapas e recursos analíticos tendem a ampliar a utilidade do dado em relação à entrega isolada de arquivos.
Esse conjunto de contribuições fundamenta a opção por uma aplicação que reúna indicadores, tabelas, filtros e representações geográficas, em vez de limitar a contribuição do trabalho à disponibilização de planilhas tratadas.

### Classificação de atividades econômicas e integração de bases

A identificação de um setor econômico em cadastros administrativos e estatísticos depende de uma classificação padronizada das atividades.
No Brasil, a Classificação Nacional de Atividades Econômicas (CNAE), mantida pelo IBGE no âmbito da CONCLA, é o instrumento oficial adotado pelo sistema estatístico nacional e pelos órgãos gestores de registros administrativos (IBGE, 2020).
A CNAE organiza as atividades em hierarquia e, na versão de subclasses para uso da Administração Pública, detalha categorias empregadas em cadastros de pessoa jurídica.
Essa padronização permite filtrar estabelecimentos do setor de Tecnologia da Informação por códigos de atividade, em especial na divisão associada a serviços de TI, e comparar resultados com estatísticas oficiais agregadas.
Contudo, a classificação resolve apenas parte do problema.
Attard et al. (2015) enfatizam que o consumo de dados abertos envolve etapas de obtenção, transformação e combinação de fontes.
Graves e Hendler (2013) reforçam que mesclar conjuntos distintos é uma das operações que afastam usuários leigos do aproveitamento direto dos portais.
No caso deste trabalho, a caracterização municipal exige integrar cadastros de estabelecimentos, tabelas de referência de atividade e município, bases de endereço com coordenadas e malhas territoriais.
A integração, portanto, não é detalhe operacional: é condição para que a CNAE, o endereço e a localização espacial passem a compor um mesmo conjunto analisável.

### Distribuição espacial de empresas e geovisualização

A localização das empresas no território é um atributo analítico, e não apenas um campo cadastral.
Estudos sobre a distribuição intramunicipal de firmas de Tecnologia da Informação e Comunicação mostram que padrões de concentração podem ser identificados quando há informação geográfica adequada.
Zenka (2021), ao investigar Ostrava, evidencia agrupamentos relevantes no centro e na cidade interior, com associação a tipologias urbanas específicas, e demonstra o valor de analisar a posição das empresas além da contagem agregada por município.
Embora o contexto daquele estudo diferencie-se de Contagem, a contribuição conceitual permanece: a geografia intramunicipal ajuda a interpretar como o setor se organiza no espaço urbano.
Para tornar essa geografia legível, a literatura de cartografia interativa e geovisualização discute o papel da exploração visual.
Roth (2013) propõe uma taxonomia de primitivas de interação em cartografia e geovisualização, destacando operações como filtrar, ampliar, consultar e reordenar a representação como parte do raciocínio espacial mediado por mapas.
Em diálogo com a agenda de dados abertos, Ansari (2022) inclui mapas entre os mecanismos capazes de ampliar a compreensão de conjuntos governamentais.
A síntese dessas linhas orienta o presente estudo: a coordenada estimada a partir do endereço e das bases territoriais abertas não substitui, por si só, a análise; ela alimenta representações — pontos, mapas de calor e agregações por recortes do município — que permitem observar concentração, vazios e diferenças internas.

### Aplicações web interativas para exploração de dados

A materialização prática dos conceitos anteriores, no escopo de Sistemas de Informação, ocorre por meio de aplicações que integrem consulta, filtragem e visualização em uma interface acessível.
Graves e Hendler (2013) defendem ferramentas que reduzam a necessidade de expertise técnica para explorar dados abertos e que apoiem a navegação por metadados e a construção de visualizações.
Ansari (2022) recomenda plataformas avançadas com visualizações e recursos analíticos embutidos, associadas a avaliação do uso por diferentes stakeholders.
Roth (2013), no domínio cartográfico, mostra que a interatividade não é adorno: ela estrutura a forma como o usuário formula e responde perguntas espaciais sobre o mapa.
Combinadas, essas contribuições sustentam o quarto objetivo específico deste trabalho: desenvolver uma aplicação web interativa na qual indicadores, gráficos, mapas e tabelas operem sobre a base integrada, permitindo que o usuário explore as empresas de Tecnologia da Informação de Contagem de acordo com os atributos disponíveis.
Assim, o referencial teórico conecta a abertura dos dados, a classificação da atividade, a leitura espacial e a interface de exploração em um mesmo encadeamento conceitual.

## Trabalhos Relacionados

## Metodologia

## Desenvolvimento

## Resultados

## Considerações Finais
