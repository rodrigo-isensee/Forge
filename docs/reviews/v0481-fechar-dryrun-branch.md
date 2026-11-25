---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-dryrun-branch
commit: 1bf95225578a79532bae4ee99f3875af3a8bc007
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.40, code review do #898)

Escopo: `bin/forge-fechar` (o `--dry-run` sem a branch local e o `--limpar --dry-run`), `docs/fechamento-integrador.md`, `tests/test_fechar.py`, `tests/mutantes/v0481-fechar-dryrun-branch.json` e o fragmento do changelog, de `b224ee09e` a `1bf95225`. Clone de review pelo `bin/forge-copia` em `/root/.forge-contrib/wt/v0481-fechar-dryrun-branch-rev`, no head do remoto (`git ls-remote` = `1bf95225`).

## Achados
- A1 (bloqueante) bin/forge-fechar:1674 · o --dry-run cria a branch local na origin/<b> do clone e a deixa; o passo real seguinte usa essa branch, não o servidor, e com o remoto adiante para no passo 2 (envie a branch); sem o dry-run passa (S1, S2). Apague-a na saída (branch_criada) ou leia a origin/<b> sem criar ref.
- A2 (bloqueante) tests/mutantes/mp1311-fechar-cartao.json:29 · CI vermelho (suíte parte 4/5, py 3.12 e 3.14): test_toda_spec_do_forge_confere_com_a_fonte acusa o `de` fora da fonte em mp1311 M3 e M5 e v0478-fechar-lote-2 FL-M11 e FL-M12 (linhas do ref_dry removidas); retire ou alinhe as quatro no mesmo commit.
- A3 (recomendado) bin/forge-fechar:1667 · o cabeçalho ainda diz que nada será executado além do 1c, que só lê; o dry-run agora pode criar a branch local (se ela ficar, depois do A1).

## Sondas
- S1 · sonda /root/.forge-contrib/wt/_tl146-v0481-sonda.py, sem branch local e remoto adiante, só o passo real · espera: rc 0 · obtido: rc 0
- S2 · a mesma, --dry-run e depois o passo real · espera: rc 0 (como S1) · obtido: dry-run conferiu 7015db1d (velho, não 0cc0c1b2) e o real saiu com 1: parou no passo 2: o head local (7015db1d) difere do remoto (0cc0c1b2); envie a branch

## Parecer
Reprovado.

O que o brief pede conferir:
- **Teste removido** (`test_dry_run_sem_branch_local_marca_o_sha_como_nao_lido`): fixava o marcador "sha não lido", que deixou de existir; o caminho que ele cobria (sem a branch local e sem a `origin/<b>`) agora para com 1 e tem teste próprio (`..._nem_a_origin_para_com_1_e_diz_como_destravar`). Não tira guarda. O ajuste de `test_dry_run_avisa_quando_nao_consegue_ler_o_diff` (sem a base local) preserva o ramo do aviso.
- **Remoto e outras branches:** `git branch --no-track` só cria `refs/heads/<b>` local, sem rastreio e sem busca; nada vai ao servidor nem toca outra branch. Mas a ref local persiste e muda o passo real seguinte (A1): o modo só remota (FECHAR-BRANCH-LOCAL) lê o servidor e apaga a branch que criou se parar antes do passo 3; a branch deixada pelo dry-run desliga esse modo e o 1c do dry-run confere a árvore da `origin/<b>` velha. Com o remoto igual (S3 da sonda) o real passa e a limpeza apaga a branch.
- **Nada que barra deixa de barrar:** o dry-run só ficou mais estrito (o 1c que não roda passou de 0 a 1); o `--limpar --dry-run` continua sem executar nada (`chamadas()` vazia). A regressão é no outro sentido: um passo real que passava passa a parar (A1).
- **Mutantes:** `bin/forge-mutante` na spec do item, 1 processo: M1 a M4 morreram (linhas 1660, 1671, 1673, 1674); um por linha de guarda mudada, e cada um tem teste do ramo de falha.
- **Módulo tocado:** `tests/test_fechar.py` local, 114 testes, OK (skipped=1).
- **CI do head `1bf95225`:** vermelho na suíte parte 4/5 nas duas versões (A2, lido nas anotações do check run); `bateria (pareceres)` e `catraca` vermelhos esperam os pareceres. Sem `- ci:` neste parecer.

Sugestão para A1: no ramo que cria a branch, `branch_criada="$sha_dry"` faz o `fim()` apagá-la (como no FECHAR-CRIA-BRANCH do passo real), com um teste que roda o dry-run, avança o remoto e confere que a branch local não ficou; o texto da doc e o A3 acompanham.
