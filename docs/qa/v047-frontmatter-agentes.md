---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-frontmatter-agentes
commit: b33bed29d8da3b94784cdd2ab6cae6bd5cad657a
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 frontmatter dos agentes (E2.165)

Diff `bf475209..b1fa63a8`: `agents/devops-engineer.md` (description entre aspas simples), `tests/test_frontmatter_agentes.py` (novo), fragmento de changelog. Sem especificação de UX nem contrato de API; a obrigação é a correção E2.151 (FRONTMATTER-AGENTES).

## Achados
- A2 (bloqueante) agents/devops-engineer.md:3 · as 2 aspas novas levam agente_caracteres a 5054, acima do teto 5052 de docs/regras/orcamento.json; tests.test_orcamento_instrucao.test_nenhum_agente_passa_do_teto cai no head (ok na base). Encurtar a description em 2 caracteres ou mais (R-REVIEW).
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
- Vermelho antes do verde (`bin/forge-testes --vermelho bf475209`, base=bf475209bae4 head=b1fa63a82ac4): `test_todo_frontmatter_le_como_yaml` H=ok B=falha, prova (asserção); os outros 2 passam na base (não provam sozinhos, servem de guarda). Sem veredito: test_forge (prazo). Dívida pré-existente: test_doutor.test_abrir_em_menos_de_cem_ms_em_media (H=falha B=falha). REGRESSÃO: tests.test_orcamento_instrucao.Orcamento.test_nenhum_agente_passa_do_teto H=falha B=ok (A2). Confirmado direto: `devops-engineer: agente_caracteres = 5054 passa do teto 5052`.
- Mutação manual no diff: tirar as aspas do devops é acusado; aspa simples interna sem par, aspa dupla sem fechar, falta de `description`, falta de abertura `---`, ` #` e `:` final são acusados; aspa simples dobrada é aceita. Lacuna: A1.
- PyYAML ausente no ambiente (o teste não o usa, como pedido).
- CI: o check-run `bateria` do sha não pôde ser lido daqui (`gh api` sem retorno, sem PR); a suíte inteira fica para o CI do PR.
- Achados recorrentes (PA-7): AR-1 a AR-12 conferidos; nenhum se aplica (sem controle, sem mutantes exigidos, sem ambiente do CI).

## Revalidação por delta (E2.191, head b33bed29)
`forge-check parecer delta`: intervalo b1fa63a8..b33bed29, no domínio só `agents/devops-engineer.md` (description encurtada de 365 caracteres, mesmas aspas simples).
- A2 corrigido: `python3 -m unittest tests.test_orcamento_instrucao tests.test_frontmatter_agentes` roda 11 testes, OK; `test_nenhum_agente_passa_do_teto` volta a passar e a description segue YAML válido (aspas simples, aspas duplas internas).
- B-v047-1 (`docs/qa/bugs/v047-1-devops-teto-orcamento.md`): fechado.
- A1 (recomendado) segue aberto, sem bloquear; vira cartão.
- Bugs abertos: 0 críticos, 0 altos, 0 médios, 0 baixos. O check-run `bateria` do sha fica para o CI do PR.
