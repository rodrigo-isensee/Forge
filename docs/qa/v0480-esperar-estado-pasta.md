---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-esperar-estado-pasta
commit: be805bc832dbce125ef69637d62fc35229bf08ee
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0480-esperar-estado-pasta

Diff do código (be805bc8): uma frase em `skills/esperar-estado/SKILL.md:19` ("e rode na pasta do repositório") e o fragmento de changelog. Sem código e sem regra de decisão: sem teste novo, vermelho ou mutação aplicáveis.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E120.1 (frase devolvida ao laço do PR) | `tests/test_esperar_estado.py` (15 testes) | texto da skill e laço intactos | passou |
| E120.1 (sem regressão de métrica de texto) | `tests/test_metricas_texto.py` (2 testes) | tamanho e forma do texto | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_esperar_estado.py` com TMPDIR: Ran 15 tests, OK.
- `python3 -I -m unittest discover -s tests -p test_metricas_texto.py` com TMPDIR: Ran 2 tests, OK.
- Suíte inteira: não rodada local; vale o check-run `bateria` do CI do PR.
