# Buscador de links
Este projeto foi desenvolvido para obter links de postagens do Facebook e Instagram.

O projeto é dividido em duas partes:
## Formatter
Este programa elimina posts repetitivos e formata os dados para o padrão utilizado no projeto alvo.

## Searcher
Programa principal, responsável por buscar os links de postagens do Facebook e Instagram. O programa lê os arquivos fragmentados e busca os links de postagens a partir do texto da postagem e do outro dela. 
O script utiliza a API Custom Search do Google para buscar os links, a biblioteca google-searcher e a biblioteca requests para fazer as requisições. A biblioteca request é utilizada para fazer requisições no Bing e no DuckDuckGo, tentando encontrar links que não foram encontrados no Google.

## Instalação
Para instalar as dependências do projeto, execute o comando abaixo:
```bash
poetry install
```

## Utilização
Para utilizar o programa fragmentador, execute o comando abaixo:
```bash
poetry run formatter
```

Para utilizar o programa de busca de links, execute o comando abaixo:
```bash
poetry run searcher
```

## Configuração	
Para configurar o programa, crie um arquivo .env na raiz do projeto e adicione as seguintes variáveis:
```bash
CSE_API_KEY_0=
CSE_ID=
NUM_KEYS=
```

Para obter a chave de API e o ID do mecanismo de pesquisa personalizado, acesse o site do [Google Custom Search](https://developers.google.com/custom-search/v1/overview) e siga as instruções para obter a chave de API e o ID do mecanismo de pesquisa personalizado.

O número de chaves é o número de chaves que você deseja usar para fazer as solicitações. Por exemplo, se você tiver 3 chaves, deverá adicionar as chaves no arquivo .env da seguinte maneira:
```bash
CSE_API_KEY_0=chave1
CSE_API_KEY_1=chave2
CSE_API_KEY_2=chave3
```
