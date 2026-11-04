---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/pr-parecer-por-branch
commit: 72be218e2198631c3716a68225b078a90020e0e3
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: PARECER-POR-BRANCH (E11, forma mínima)

Aprovado. Testado o head 495be5c (só pareceres depois de 72be218; o código testado é o do `commit:`). Diff `f54d9b7...72be218`: `bin/forge-check` (+14/-1), 27 linhas de teste, fragmento de changelog; sem `hooks/`, `.githooks/` nem `tests/catraca.py`, logo sem lista de mutantes declarada. Sem bug aberto.

## Achados

## Critério → teste → resultado
O pedido não tem `CA-n` em EARS; as obrigações vêm do brief 52 (Entregar do E11).

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Vale o parecer da branch da ref sobre o de outra branch (mesma data, caminho depois na ordem, desatualizado) | `test_pr_parecer_da_branch_da_ref_vale_sobre_o_de_outra_branch` + CT-01, CT-02 | empate de data e ordem por caminho | passou |
| Reprovado ou desatualizado da própria branch reprova | `test_pr_parecer_reprovado_da_propria_branch_reprova` + CT-05, CT-06 | filtro não esconde o veredito | passou |
| Sha, HEAD solto e ref sem branch valem como na base | CT-03, CT-04, CT-07 | ref sem nome de branch | passou |
| Sem parecer da branch cai no mais recente do pedido | `test_pr_sem_parecer_da_branch_cai_no_mais_recente_do_pedido` + CT-07 | lista da branch vazia | passou |

## Cenários e resultado real
Repositório descartável em `$TMPDIR/qa-engineer-pr-parecer-por-branch/repo`, pedido `ped`, review e qa nas duas branches: `feat-b` (parecer `zz-b.md`, desatualizado: código mudou depois) e `feat-a` (parecer `aa-a.md`, aprovado, com o de `feat-b` também na árvore). Mesma data; `zz-b` vem depois na ordem.

| ID | Comando | Esperado | Obtido |
|---|---|---|---|
| CT-01 | `forge-check pr ped --ref feat-a` | aprova pelo parecer da branch | rc 0 |
| CT-02 | `--ref origin/feat-a` (ref remota criada) | aprova | rc 0; antes da ref remota existir, rc 1 "sem parecer" (esperado: a árvore da ref não existe) |
| CT-03 | `--ref <sha de feat-a>` | comportamento da base: pega `zz-b`, reprova | rc 1 |
| CT-04 | HEAD solto, com e sem `--ref HEAD` | idem base | rc 1 nos dois |
| CT-05 | `--ref feat-rep` (review reprovado da própria branch) | reprova | rc 1, "o último parecer não é aprovado" |
| CT-06 | `--ref feat-des` (código mudou após o parecer da própria branch) | reprova | rc 1, "desatualizado" |
| CT-07 | `--ref feat-r` (nenhum parecer com essa branch) | cai no mais recente, como a base | rc 1 (`zz-b`); a base f54d9b7 dá o mesmo |
| CT-08 | sem `--ref`, HEAD em `feat-a` | branch do HEAD | rc 0 |
| CT-09 | base f54d9b7 sobre `feat-a` (contraste) | reprova pelo caso do #437 | rc 1 (confirma a correção) |

## Execução
- Suíte inteira (`.githooks/pre-push --suite`, esperou a vez na fila): `Ran 2519 tests in 827.108s (4 processos)`, `OK (skipped=28)`, rc=0. Os 28 skips são da base, nenhum do diff.
- `scripts/validar-plugin.sh`: `Validation passed`, rc=0. `bin/forge-check docs`: rc=0.
- Vermelho antes do verde: `bin/forge-testes --vermelho f54d9b7` estourou meu prazo de 580 s (rc 124, sem veredito, não vale como vermelho). Recuo: cópia do head com `bin/forge-check` da base, `python3 -m unittest tests.test_forge -k pr_parecer -k pr_sem_parecer_da_branch`: `FAILED (failures=1)`, cai `test_pr_parecer_da_branch_da_ref_vale_sobre_o_de_outra_branch` ("desatualizado: src/app.txt mudou depois do parecer"); os outros dois testes guardam o comportamento preservado e passam nos dois lados, como esperado.
- Review A1 e segurança A1 já registrados; não repetidos.
