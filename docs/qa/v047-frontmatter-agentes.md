---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-frontmatter-agentes
commit: b1fa63a82ac4d91e898ef790a248de426c61116f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047 frontmatter dos agentes (E2.165)

Diff `bf475209..b1fa63a8`: `agents/devops-engineer.md` (description entre aspas simples), `tests/test_frontmatter_agentes.py` (novo), fragmento de changelog. Sem especificação de UX nem contrato de API; a obrigação é a correção E2.151 (FRONTMATTER-AGENTES).

## Achados
- A1 (recomendado) tests/test_frontmatter_agentes.py:43 · aspas duplas com aspas internas sem escape (`"a "b" c"`) passam como válidas, embora não sejam YAML; nenhum agente de hoje tem isso. Reforçar o ramo de aspas duplas ou aceitar a lacuna por escrito.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Frontmatter de todo agente lê como YAML com name e description | `test_todo_frontmatter_le_como_yaml` (agents/ e stacks/*/agents/) | `: ` ou ` #` em escalar simples | passou |
| Guarda contra suíte vazia | `test_ha_agentes` (mínimo 12) | pasta renomeada | passou |
| O detector acusa o defeito original | `test_detecta_dois_pontos_sem_aspas` | escalar sem aspas com `: `; `'a: b'` aceito | passou |
| devops-engineer entre aspas | leitura do diff e teste acima | aspas fecham; aspas duplas internas dentro de aspas simples | passou |

## Cenários e resultado real
- Teste direto (`python3 -I tests/test_frontmatter_agentes.py`): 3 testes, OK.
- Vermelho antes do verde: `bin/forge-testes --vermelho bf475209` não rodou no sandbox (saída `fatal library error, lookup self`, sem veredito). Feito à mão: cópia do head em `$TMPDIR` com o `devops-engineer.md` da base; o teste falhou (`- ["linha 3: 'description' tem ': ' ou ' #' sem aspas (não lê como YAML)"]`, `FAILED (failures=1)`). No head, passa.
- Mutação manual no diff: tirar as aspas do devops é acusado; aspa simples interna sem par, aspa dupla sem fechar, falta de `description`, falta de abertura `---`, ` #` e `:` final são acusados; aspa simples dobrada é aceita. Lacuna: A1.
- PyYAML ausente no ambiente (o teste não o usa, como pedido).
- CI: o check-run `bateria` do sha não pôde ser lido daqui (`gh api` sem retorno, sem PR); a suíte inteira fica para o CI do PR.
- Achados recorrentes (PA-7): AR-1 a AR-12 conferidos; nenhum se aplica (sem controle, sem mutantes exigidos, sem ambiente do CI).
