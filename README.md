# Calendário da Copa 2026

## Sobre o projeto

O **Calendário da Copa 2026** é um aplicativo desktop desenvolvido em **Python** com **PySide6** para acompanhar os jogos da Copa do Mundo de 2026.

O projeto possui uma interface moderna, com visual esportivo em tema escuro, responsividade para telas no formato celular **9:16** e também adaptação para uso em desktop.

## Objetivo

O objetivo do projeto é facilitar o acompanhamento da Copa do Mundo 2026, permitindo ao usuário visualizar jogos, resultados, favoritos, alertas, calendário mensal, detalhes das partidas e tabela de classificação dos grupos.

Além disso, o sistema permite exportar partidas para o calendário do computador ou celular, tornando mais fácil acompanhar os jogos importantes.

## Funcionalidades principais

* Tela inicial com próximo jogo, estatísticas e atalhos;
* Lista de jogos com busca e filtros;
* Favoritar partidas;
* Ativar alertas para jogos;
* Escolher um time favorito;
* Destacar partidas do time favorito;
* Ver detalhes de cada jogo;
* Consultar partidas em um calendário mensal;
* Visualizar tabela de classificação dos grupos;
* Ver legenda explicando as colunas da tabela;
* Exportar partidas para calendário no formato `.ics`;
* Exportar dados em arquivo `.csv`;
* Ajustar tamanho da fonte;
* Alternar entre modo celular 9:16 e modo desktop;
* Salvar preferências do usuário automaticamente.

## Como o aplicativo funciona

O aplicativo utiliza arquivos locais em formato JSON para armazenar dados dos jogos, favoritos, alertas e preferências do usuário.

Ao ser executado, o sistema cria automaticamente os arquivos necessários, caso eles ainda não existam. Dessa forma, o usuário pode utilizar o aplicativo sem precisar configurar tudo manualmente.

Os jogos ficam cadastrados no arquivo `dados_copa.json`, enquanto favoritos, alertas e preferências ficam salvos em arquivos separados.

## Tecnologias utilizadas

* Python;
* PySide6;
* JSON;
* CSV;
* Arquivos `.ics` para integração com calendário.

## Estrutura do projeto

```text
calendario_copa_2026/
│
├── main.py
├── requirements.txt
├── README.md
├── abrir_app.bat
│
├── dados_copa.json
├── favoritos.json
├── preferencias.json
│
├── calendario_copa_2026.ics
└── calendario_copa_2026.csv
```

## Arquivos principais

### `main.py`

Arquivo principal do projeto. Contém a interface gráfica, as telas, a navegação, os filtros, os favoritos, os alertas, a tabela de grupos e as funções de exportação.

### `requirements.txt`

Arquivo com as dependências necessárias para executar o projeto.

### `abrir_app.bat`

Arquivo para abrir o aplicativo com mais facilidade no Windows.

### `dados_copa.json`

Arquivo responsável por armazenar os dados das partidas, como seleções, data, horário, fase, grupo, estádio, cidade, placar e status do jogo.

### `favoritos.json`

Arquivo usado para salvar os jogos favoritados e os alertas já notificados.

### `preferencias.json`

Arquivo usado para salvar preferências do usuário, como modo de abertura, tamanho da fonte, tempo de alerta e time favorito.

### `calendario_copa_2026.ics`

Arquivo gerado ao exportar partidas para calendário.

### `calendario_copa_2026.csv`

Arquivo gerado ao exportar a lista de jogos em formato CSV.

## Como instalar

Antes de executar o projeto, é necessário ter o Python instalado no computador.

Depois, abra o terminal na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

## Como executar

Após instalar as dependências, execute:

```bash
python main.py
```

No Windows, também é possível abrir o aplicativo clicando no arquivo:

```text
abrir_app.bat
```

## Como atualizar os jogos

Os jogos podem ser atualizados no arquivo:

```text
dados_copa.json
```

Cada partida possui uma estrutura parecida com esta:

```json
{
  "id": "m001",
  "data": "2026-06-11",
  "hora": "19:00",
  "time_a": "México",
  "time_b": "África do Sul",
  "grupo": "Grupo A",
  "fase": "Grupos",
  "estadio": "Estadio Azteca",
  "cidade": "Cidade do México, México",
  "status": "encerrado",
  "placar": "2-0",
  "alerta": false,
  "destaque": "Jogo de abertura da Copa 2026."
}
```

Para atualizar um resultado, basta alterar o campo `placar` e mudar o campo `status` para `encerrado`.

## Observação

A base interna do projeto é demonstrativa e pode não conter todos os 104 jogos da Copa do Mundo 2026.

O projeto foi desenvolvido com foco em estudo, prática de programação, criação de interface gráfica, organização de dados e desenvolvimento de aplicativos desktop com Python.
