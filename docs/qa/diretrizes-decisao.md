---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/diretrizes-decisao
commit: 3a86bd3853ad610cbbfa72593b9d29a79d853aca
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: diretrizes 1, 8 e 9 na regra de decisão (E26.15)

Branch `melhoria/diretrizes-decisao`, head `3a86bd38`, base `c340c322`. Diff: `docs/regras/R-DECISAO.md`, `skills/falar-com-o-dono/SKILL.md`, `changelog.d/diretrizes-decisao.md`. Sem PR aberto: rodei só o teste afetado (`R-QA`, carga alta).

## Achados
- A1 (bloqueante) docs/regras/R-DECISAO.md:15 · cortes para caber no orçamento apagaram 5 trechos de `invariantes` em R-DECISAO.md (`a próxima espera a resposta`, `na entrega, `pendente:``, `um comando, um efeito`, `evidência no motivo`, formato `origem: <coluna>; ação: <o que o usuário faz>; comando:`) e `tests/config.json` não foi tocado; RegrasInviolaveis cai (6 subtestes).
- A2 (bloqueante) skills/falar-com-o-dono/SKILL.md:13 · o corte removeu `Sem resposta, fica pendente.` da skill, invariante de `tests/config.json`; o texto continua em R-DECISAO, mas o teste exige o trecho neste arquivo. Restaure o trecho ou afrouxe o invariante com destaque no título do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Diretriz 1: custo em tokens e ganho de velocidade por opção | leitura do diff (R-DECISAO.md:15; SKILL.md:13 "Custo e origem") | n/a | passou |
| Diretriz 8: origem do item em toda decisão | leitura do diff (R-DECISAO.md:15; SKILL.md:13) | n/a | passou |
| Diretriz 9: conferir decisão ruim, também a do dono, antes de cumprir | leitura do diff (R-DECISAO.md:16) | n/a | passou |
| Nenhuma regra com ID ou invariante some nos cortes | `test_forge.RegrasInviolaveis.test_trechos_obrigatorios` | trecho obrigatório presente | FALHOU (6 subtestes) |

IDs de regra citados antes e depois no diff (`R-DECISAO`, `R-CONFORMIDADE`, `R-CUSTO`) seguem presentes; o que sumiu são só invariantes de trecho.

## Cenários e resultado real
Comando (em `tests/`, 2 tentativas não necessárias, falha determinística):
`python3 -m unittest test_forge.RegrasInviolaveis.test_trechos_obrigatorios`
Saída: `Ran 1 test in 0.055s` / `FAILED (failures=6)`, subtestes:
- `skills/falar-com-o-dono/SKILL.md` · `Sem resposta, fica pendente\.`
- `docs/regras/R-DECISAO.md` · `na entrega, `pendente:``
- `docs/regras/R-DECISAO.md` · `origem: <coluna>; ação: <o que o usuário faz>; comando:`
- `docs/regras/R-DECISAO.md` · `um comando, um efeito`
- `docs/regras/R-DECISAO.md` · `evidência no motivo`
- `docs/regras/R-DECISAO.md` · `a próxima espera a resposta`

Mesma checagem sobre a base `c340c322` não falha (os trechos existiam); a regressão é do head. Vermelho antes do verde e mutação: n/a (não há teste novo nem código).

## Recomendados
Nenhum.
