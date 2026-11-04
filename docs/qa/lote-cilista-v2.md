---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-cilista-v2
commit: 6f7a9d1a5d629c350ee2411712a9b5c26a25f0bd
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: lote-cilista-v2 (trava de ordem do lint, env por recuo)

## Achados
- A1 (bloqueante) tests/test_ci_local.py:75 · comentário no recuo do env zera a leitura e PATH passa; ver docs/qa/bugs/cilista-v2-comentario-no-env.md

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Lista positiva de env por passo e job | test_ci_local (53 testes) | chave fora da lista | passou |
| Env em fluxo, âncora, merge key, aspas simples | tentativa manual | forma do env | reprovadas |
| Comentário no meio do env | tentativa manual | recuo relativo | escapou (A1) |

## Cenários e resultado real
`python3 -I -m unittest discover -s tests -p test_ci_local.py`: 53 testes, OK. Fluxo, âncora, `<<:`, aspas simples: reprovam. Tab escapa, mas o YAML o rejeita. Comentário em coluna 0 falha fechado. Comentário no recuo do env escapa (A1).
