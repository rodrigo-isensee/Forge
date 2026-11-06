---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/lote-cilista-v2
commit: 0ad1ad79e463bd2afd6dcc163f40ca6d4e692ae5
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: lote-cilista-v2 (trava de ordem do lint, env por recuo)

## Achados
- A1 (recomendado) docs/qa/bugs/cilista-v2-comentario-no-env.md:1 · fechado em 0ad1ad7; a sonda não escapa mais

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Lista positiva de env por passo e job | test_ci_local (53 testes) | chave fora da lista | passou |
| Env em fluxo, âncora, merge key, aspas simples, tab | sonda esc.py | forma do env | reprovadas |
| Comentário no meio do env | sonda esc.py | recuo relativo | reprovado, A1 fechado |

## Cenários e resultado real
`python3 -I -m unittest discover -s tests -p test_ci_local.py`: 53 testes, OK. Sonda esc.py no head: todas as variantes reprovam, inclusive comentário no recuo 8 do passo e no recuo 4 do job.
