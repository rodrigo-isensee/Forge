---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/diretrizes-decisao
commit: 39c163cc5d2fdfd69982e1eb3e80815aea0202e6
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: diretrizes 1, 8 e 9 na regra de decisão (E26.15)

Branch `melhoria/diretrizes-decisao`, head `39c163cc` (antes `3a86bd38`), base `c340c322`. Diff: `docs/regras/R-DECISAO.md`, `skills/falar-com-o-dono/SKILL.md`, `changelog.d/diretrizes-decisao.md`. Sem PR aberto: rodei só o teste afetado (`R-QA`, carga alta).

## Achados

## Revalidação por delta (head `39c163cc`)
A1 e A2 da rodada anterior (head `3a86bd38`) foram resolvidos: a volta E26.19 restaurou os trechos protegidos.
`forge-check parecer delta` lista no domínio do QA só `docs/regras/R-DECISAO.md` e `skills/falar-com-o-dono/SKILL.md` (intervalo `3a86bd38..39c163cc`). Reteste: `python3 -m unittest test_forge.RegrasInviolaveis` em `tests/`: `Ran 3 tests ... OK` (os 6 subtestes de A1/A2 passam). Os seis trechos voltaram, formato `origem: <coluna>; ação: <o que o usuário faz>; comando:` e `(não amplia autorização)` incluídos. Custo declarado conferido: R-DECISAO perdeu `nem a do dono` e `origem` no item "Decisão ruim"; a origem segue em "Uma por vez" (`cada decisão, a origem`) e a skill mantém `decisão ruim do dono volta a ele`, então as diretrizes 8 e 9 seguem cobertas no texto. Suíte inteira não rodada local (carga alta); vale o check `bateria` do CI quando houver PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Diretriz 1: custo em tokens e ganho de velocidade por opção | leitura do diff (R-DECISAO.md:15; SKILL.md:13 "Custo e origem") | n/a | passou |
| Diretriz 8: origem do item em toda decisão | leitura do diff (R-DECISAO.md:15; SKILL.md:13) | n/a | passou |
| Diretriz 9: conferir decisão ruim, também a do dono, antes de cumprir | leitura do diff (R-DECISAO.md:16; skill: "decisão ruim do dono volta a ele") | n/a | passou |
| Nenhuma regra com ID ou invariante some nos cortes | `test_forge.RegrasInviolaveis.test_trechos_obrigatorios` | trecho obrigatório presente | passou no head `39c163cc` (falhava em `3a86bd38`) |

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
