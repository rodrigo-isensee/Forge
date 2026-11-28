# V047-PA-01 - KANBAN.md ilegível por OSError derruba `cmd_abertas` com traceback
- Severidade: média
- Responsável sugerido: dev da stack (bin/forge_dono.py)
- Ambiente: melhoria/v047-perguntas-abertas, 2511f48b, Python 3

## Passos para reproduzir
1. Raiz com `docs/pedidos/` e um `KANBAN.md` regular cuja leitura levanta `OSError` (permissão negada, erro de E/S; simulado com `Path.read_text` levantando `PermissionError` para `KANBAN.md`).
2. Chamar `forge_dono.cmd_abertas(raiz)`.

## Resultado esperado
Aviso `abertas: aviso: KANBAN.md ilegível (...)`, como nos pedidos, e a lista segue.
## Resultado obtido
`PermissionError` sem tratamento (forge_dono.py:547): o comando morre e a lista dos pedidos se perde. Só os pedidos têm `try/except (OSError, UnicodeDecodeError)`.
## Evidência
`EXC PermissionError` na execução do script de reprodução (QA, E1.147). Nenhum teste dos 9 cobre.
