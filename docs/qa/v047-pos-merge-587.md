---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-pos-merge-587
commit: 58dfa2ab016fbc10c730b369995b0f1e75b000d6
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047, depois do merge do #587 (frontmatter-agentes)

Revisão depois do merge, sobre a develop em 58dfa2ab. Entrou no #587 (3b1b9e3f): `agents/devops-engineer.md`, `bin/forge-testes`, `tests/test_frontmatter_agentes.py`, `docs/qa/bugs/v047-1-devops-teto-orcamento.md`.

## Achados
- A1 (bloqueante) agents/jarvis.md:3 · o teste do #587 cai na develop: a description tem ': ' sem aspas ("sessão: entende"), YAML inválido, campos descartados (R-QA). Entrou no #584, depois do #587. Pôr aspas na linha.
- A2 (recomendado) tests/test_frontmatter_agentes.py:41 · aspas duplas só conferem início e fim: "a "b" c" passa como válido e não é YAML. Conferir aspa dupla interna sem barra, como já se faz com a simples.
- A3 (recomendado) bin/forge-testes:125 · nenhum teste guarda a entrada de test_frontmatter_agentes em LEITORES_DE_TEXTO; o mapa funciona (agents/ e stacks/ listam o módulo), mas sem teste. Um caso em test_testes_tocados.
- A4 (recomendado) agents/devops-engineer.md:3 · test_orcamento_instrucao segue vermelho na develop (total 22669 > 21991; marcadores 44 > 42). Já tratado no E2.412 (PR develop-verde-576); só citado, não corrigido.

## Critério → teste → resultado
O #587 não tem CA-n de UX; a obrigação é o E2.151 (frontmatter lê como YAML) e o teto do orçamento.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2.151 devops com aspas | test_todo_frontmatter_le_como_yaml (devops-engineer) | ': ' no escalar simples | passou |
| E2.151 todos os agentes | test_todo_frontmatter_le_como_yaml (12 arquivos) | ': ' e ' #' | falhou só em jarvis (A1) |
| guarda contra suíte vazia | test_ha_agentes (>= 12) | pasta vazia | passou (12) |
| detector | test_detecta_dois_pontos_sem_aspas | aspa simples interna | passou |
| mapa do forge-testes | `forge-testes --listar agents/jarvis.md` e `stacks/python/agents/x.md` | agents/ e stacks/ | passou (módulo listado, sem teste próprio, A3) |
| teto do orçamento | test_nenhum_agente_passa_do_teto | teto | falhou (A4, E2.412) |

## Cenários e resultado real
- `python3 tests/test_frontmatter_agentes.py`: 3 testes, 1 falha (jarvis.md, A1).
- `python3 tests/test_orcamento_instrucao.py`: 8 testes, 1 falha (devops-engineer, A4).
- Bordas do detector rodadas à mão: "a "b" c" sem erro (A2); "a: b", 'a''b', aspa sem fechar, 'x' y, ' #' e CRLF se comportam como o esperado.
- Vermelho antes do verde e mutação não rodados: a revisão pedida é do que já está na develop. Bateria completa não rerrodada; vale o CI do PR.
