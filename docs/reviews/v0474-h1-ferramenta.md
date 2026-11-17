---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0474-h1-ferramenta
commit: db0b1f987bccc0cf549d47cd2cd7073a01404ac0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E2.25, H1-ferramenta; revalidado no E2.34 e no E2.48)

## Revalidação (E2.48, head db0b1f98)
Delta lido: `forge-check parecer delta docs/reviews/v0474-h1-ferramenta.md`, escopo sem o que veio da develop, no domínio `bin/forge-testes` e `tests/test_testes_tocados.py` (o aviso sobre 69e4d864 é a junção da própria branch remota, só `docs/security/`). `git show --remerge-diff db0b1f98`: o único conflito foi a contagem em `tests/test_testes_tocados.py:77`, resolvida em 92 (91 da develop com `test_conformidade_verde` mais `test_forge_tamanho` desta branch), com os dois comentários preservados; `bin/forge-testes:112` junta os dois módulos no `FORGE_CHECK` sem conflito. Nada do código do item (`bin/forge-check`, `bin/forge_tamanho.py`, testes e specs) mudou no delta. `python3 -m unittest tests.test_testes_tocados`: `Ran 162 tests in 254.019s`, `OK (skipped=1)`. Suíte inteira no CI do PR. Sem achado novo.

## Revalidação (E2.34, head 7924b25b)
Delta lido: `forge-check parecer delta docs/reviews/v0474-h1-ferramenta.md`, intervalo `4ddaa68b..7924b25b`, no domínio `bin/forge-check`, `bin/forge_tamanho.py`, `tests/test_forge_tamanho.py` e as três specs de mutantes.
- A1 resolvido: `bin/forge-check:1428` só confere o corpo com `state == "OPEN"` (o `{}` sem PR cai no mesmo ramo); `test_pr_fechado_ou_mesclado_nao_reprova` cobre CLOSED e MERGED e o OPEN que reprova; M13 (`if not pr:`) e M21 (`if False:`) na guarda. A S1 agora dá `[]` com só o aviso.
- A2 resolvido: `tem_motivo(corpo, total)` exige `<n> >= total` em alguma linha (`bin/forge_tamanho.py:39`), com `test_numero_do_motivo_cobre_o_total` (9 e 151 contra 160 e 400 reprovam; linha velha mais a nova passa) e M22.
- Novo: `tamanho_do_pr` recebe a `ref` no teste (`test_ref_diferente_do_head_mede_a_ref`, M20); carga do módulo sob demanda (`tam()`), sem mudar o que se afirma.
- Mutação no delta: `bin/forge-mutante --processos 1 --base 4ddaa68b` nas três specs: 22 de 22 mortos (M1 a M22); `--cobertura --base 4ddaa68b`: as guardas mudadas (`forge-check:1428`, `forge_tamanho.py:39` e `:44`) cobertas. Testes novos rodados: `Ran 10 tests`, `OK`. Suíte inteira no CI do PR. Código do item: 118 linhas em `bin/`, dentro do teto (M14).

## Review anterior (head 4ddaa68b)

Diff `681d4b33...4ddaa68b`: `bin/forge_tamanho.py` novo, `tamanho_do_pr` e os avisos do `brief gerar` em `bin/forge-check`, `test_forge_tamanho` no `FORGE_CHECK` (91), 19 mutantes em `tests/mutantes/v0474-h1-ferramenta*.json`, M29 e M30 de `lote-l08-e7.json` realinhados.

Conferido: classificação pelo `e_codigo` do T1 (testes, docs e `changelog.d/` fora), como na decisão do dono de 17/11 11:15; o item soma 114 linhas de código (bin/), dentro do teto. Uma guarda por mutante declarado (M1 a M19). `python3 -m unittest tests.test_forge_tamanho tests.test_t1_codigo_sem_teste tests.test_testes_tocados`: `Ran 189 tests in 241.043s`, `OK (skipped=1)`. A suíte inteira fica no CI do PR.

## Achados
- A1 (bloqueante) bin/forge-check:1427 · o pr reprova também com PR CLOSED ou MERGED da branch (gh pr view <branch> devolve o último); o pedido e a docstring dizem só PR aberto. Gatilho: branch com PR antigo fechado. Ajuste: só confere com state OPEN, com teste e mutante (S1, R-REVIEW)
- A2 (recomendado) bin/forge_tamanho.py:13 · LINHA_DE_MOTIVO aceita qualquer <n>: uma linha com 151 deixa passar o item que cresceu para 400; conferir n >= total, ou dizer no texto que o número é livre

## Sondas
- S1 · tamanho_do_pr com item de 151 linhas e gh falso {"state": "CLOSED"} e depois "MERGED", corpo sem a linha do teto · espera: [] e só o aviso · obtido: ['pr: tamanho: 151 linhas de código acima do teto de 150 sem a linha ... no corpo do PR #7'] nos dois

## Parecer
Aprovado no head db0b1f98 (E2.48): a junção da develop só somou a contagem dos módulos, sem tocar o código do item.

Aprovado no head 7924b25b: A1 e A2 corrigidos, com teste do ramo de falha e mutante morto para cada guarda mudada.

Parecer anterior (4ddaa68b): reprovado por A1: a reprovação do corpo vale só com o PR aberto (requisito do E2.13), e hoje vale com qualquer PR que o gh devolva para a branch. Sugestão: em `tamanho_do_pr`, `if not pr or pr.get("state") != "OPEN": return []` antes do `falta_de_motivo`, com um teste do ramo CLOSED/MERGED e o mutante da guarda nova na spec `-2` ou numa `-4`. A2 não devolve.
