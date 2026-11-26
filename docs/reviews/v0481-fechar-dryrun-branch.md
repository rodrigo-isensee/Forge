---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-dryrun-branch
commit: 432ac20dda60577b3ff69c649deb5d44a89931fc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.53, code review por delta do #898)

Escopo: revalidação por delta, de `1bf95225` a `432ac20d` (volta única E14.45), lido em `forge-check parecer delta docs/reviews/v0481-fechar-dryrun-branch.md`: `bin/forge-fechar`, `docs/fechamento-integrador.md`, `tests/test_fechar.py`, as specs `tests/mutantes/mp1311-fechar-cartao.json`, `tests/mutantes/v0478-fechar-lote-2.json` e `tests/mutantes/v0481-fechar-dryrun-branch.json` e o fragmento do changelog. Clone de review em `/root/.forge-contrib/wt/v0481-fechar-dryrun-branch-rev`, avançado com `--ff-only` até o head do remoto (`432ac20d`).

## Rodada anterior (E14.40)
Sem achado novo no delta. Os achados de `1bf95225` estão resolvidos:
- A1 (bloqueante, resolvido) bin/forge-fechar:1676 · `branch_criada="$sha_dry"` faz o `fim()` (linha 447) apagar a ref criada pelo `--dry-run`, só se ainda está no sha criado (`git update-ref -d <ref> <sha>`), também na recusa do 1c e em qualquer `die` depois da criação. A sonda S2 da rodada anterior, rerrodada no head: dry-run com rc 0, branch local ausente depois, passo real seguinte com rc 0 (antes, parava no passo 2).
- A2 (bloqueante, resolvido) tests/mutantes/mp1311-fechar-cartao.json:39 · `bin/forge-mutante --conferir --todas` não acusa nenhuma spec de fechar; cada `de` realinhado aparece uma vez na fonte (M5 na 1679, FL-M11 na 1683, M5 do item na 1676). Classe AR-12 (spec desatualizada pelo commit que muda a linha); a contagem fica para quem grava o AR, porque o brief limita este commit ao parecer.
- A3 (recomendado, resolvido) bin/forge-fechar:1667 · o cabeçalho do `--dry-run` diz que a branch nasce só para o 1c e sai no fim.

## Parecer
Aprovado.

O que o brief pede conferir:
- **Mutantes realinhados mantêm a guarda:** mp1311 M5 passou do `ref_dry="refs/heads/$ref"` (removido) ao `passo 1 ... --ref refs/heads/$ref`, a mesma guarda (FECHAR-REF-POR-NOME: o dry-run mostra a ref completa, não o nome curto), com o mesmo teste; FL-M11 passou do `if` sobre `ref_dry` ao `conferir_1c "$sha_dry"`, a mesma guarda (o `--dry-run` roda o 1c de verdade), com os mesmos dois testes. Saem mp1311 M3 (o marcador "sha não lido" deixou de existir em E14.32) e FL-M12 (a guarda "sem a branch local não roda o 1c" foi invertida de propósito por E14.32; o caminho sem a branch e sem a `origin/<b>` para com 1 e tem teste e mutante próprios na spec do item). `bin/forge-mutante --processos 1`: mp1311 M5 morreu (1679), FL-M11 morreu (1683), M5 do item morreu (1676).
- **Nada que barra deixa de barrar:** o delta de código é só a atribuição `branch_criada` e dois textos; nenhuma linha de guarda (`if`, `||`, `die`) mudou. A remoção da ref passa pelo `fim()` existente (FECHAR-CRIA-BRANCH), com o valor antigo no `update-ref -d`: uma branch que outro processo moveu não é apagada. O dry-run continua sem chamar o servidor nem o `gh`.
- **Testes:** `test_dry_run_sem_a_branch_local_nao_prende_o_passo_real_na_origin_velha` reproduz o A1 (servidor adiante, `origin/<b>` velha) e confere que o passo real usa o sha do servidor; a recusa do 1c confere que a ref sai. `tests/test_fechar.py` local no head: 115 testes, OK (skipped=1).
- **CI do head `432ac20d`:** as 10 partes da suíte (3.12 e 3.14), `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, os tetos de pulados, a instalação e a árvore provada estão verdes. `bateria (pareceres)` vermelha só pelos pareceres reprovados de review, QA e segurança; `bateria` só agrega essa (`pareceres: failure`, o resto `success`). A `catraca` vermelha tem duas causas: os pareceres e a remoção de dois testes que já estava em `1bf95225` (`test_1c_no_dry_run_sem_a_branch_local_nao_roda` e `test_dry_run_sem_branch_local_marca_o_sha_como_nao_lido`, R-CONFORMIDADE), que pede o rótulo `afrouxa-regra` do dono e o destaque no título do PR; não é falha do código do item, e o review não a decide. Nenhuma falha nova contra a `develop`.
- ci: 432ac20dda60577b3ff69c649deb5d44a89931fc verde
- suíte: 432ac20dda60577b3ff69c649deb5d44a89931fc rc=0 módulos=test_fechar

## Pendências para o merge
- Rótulo `afrouxa-regra` do dono e destaque no título do #898 para os dois testes removidos (motivo: comportamento invertido por E14.32, coberto pelos testes e mutantes da spec do item); sem ele a `catraca` segue vermelha.
- Pareceres de QA e segurança no head `432ac20d`.
