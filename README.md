# Calendário da Copa 2026 - versão melhorada

App desktop em Python/PySide6 com visual esportivo moderno, responsivo para celular 9:16 e desktop.

## Como rodar

```bash
pip install -r requirements.txt
python main.py
```

## O que foi melhorado

- Responsividade real para phone/tablet/desktop.
- Tela inicial com próximo jogo, estatísticas e atalhos.
- Tela de jogos com busca, filtros, favoritos, alertas e detalhes.
- Calendário mensal navegável com dias marcados por quantidade de jogos.
- Favoritos persistentes em `favoritos.json`.
- Exportação de partidas para `.ics`, compatível com Google Calendar, Outlook, Windows e celulares.
- Exportação CSV.
- Notificações via bandeja do sistema quando disponível.
- Preferências salvas em `preferencias.json`.
- Dados editáveis em `dados_copa.json`.
- Base demonstrativa corrigida para sedes da Copa 2026, removendo dados antigos do Catar usados nas versões anteriores.

### Novidades adicionadas nesta atualização

- **Tabela de grupos**: novo item na navegação inferior (ícone 📊) que mostra a classificação por grupos com base nos resultados das partidas encerradas. A tabela calcula jogos, vitórias, empates, derrotas, gols pró/contra, saldo de gols e pontos, ordenando as seleções de forma automática.
- **Tempo de alerta configurável**: na página **Mais → Dados e calendário** é possível definir quantos minutos antes de cada partida o alerta deve ser disparado, através de um seletor numérico. O valor é salvo em `preferencias.json` e utilizado nas notificações.

## Arquivos criados pelo app

- `dados_copa.json`: base de partidas e jogadores.
- `favoritos.json`: favoritos e alertas já notificados.
- `preferencias.json`: tamanho de fonte e modo de abertura.
- `calendario_copa_2026.ics`: gerado quando exportar calendário.
- `calendario_copa_2026.csv`: gerado quando exportar CSV.

## Observação

A base interna é demonstrativa e não contém todos os 104 jogos. Para usar a tabela completa, substitua o conteúdo de `dados_copa.json` mantendo a estrutura JSON.
