---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: ac8202d0e2644d015f1c13be3fd7f040101db06f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E32.16, #929, F6 no CI), voltas 2 e 3 por delta

Delta lido (H3): `forge-check parecer delta` de `e85793a8..ac8202d0`. No domínio há 5 arquivos: `tests/config.json`, `tests/mutantes/v0481-f6-ci-uma-vez.json`, `tests/test_arvore_testada.py`, `tests/test_catraca.py` e `tests/test_suite_partes.py`. De `5f26b0f9` a `ac8202d0` só mudou `docs/devops/`. Nada fora do delta foi relido.

- ci: ac8202d0e2644d015f1c13be3fd7f040101db06f verde

## Parecer
**Aprovado.** Todos os bloqueantes da volta 1 foram resolvidos.

**CI (G3):** o sha revisado é o `ac8202d0`, com código igual ao `5f26b0f9`. `gh pr checks 929` lido no run 45935698348 (pull_request, head `ac8202d0`). Estão verdes as 5 partes da suíte 3.12, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, `teto de pulados (python 3.12)` e `árvore já provada na develop`. Ficam fora da conta `bateria`, `bateria (pareceres)` e `catraca`, que esperam o parecer e o rótulo `afrouxa-regra` do dono.

O run do `5f26b0f9` (45933270128) reprovou só na parte 3/5. A causa foi `NeutralidadeDoNucleo` em `docs/devops/v0481-f6-ci-uma-vez.md` (`npm`), um parecer e não código. O `ac8202d0` corrige isso e o diff dele toca só `docs/devops/`, por isso o CI vale lido no próprio `ac8202d0`.

**Situação dos achados da volta 1 (o delta):**
- **A11:** resolvido. O teste agora espera `(2, 1)` e 3 jobs com `always()`, e o comentário foi alinhado.
- **A12:** resolvido. A lista tem os 13 `timeout-minutes` na ordem do ci.yml, sem o `arvore-envio` e sem as pernas do 3.14. O ci.yml tem 13 ocorrências.
- **A13:** resolvido. Há exceção de `\bnpm\b` só para o `diario.yml` em `tests/config.json`, e o título e a seção "Regras afrouxadas" do PR a destacam.
- **A14:** resolvido. CI-M4 a CI-M8 cobrem as linhas 111, 116, 119, 120 e 121 do diario.yml, uma por linha, e os cinco morreram.
- **A15:** resolvido. O corpo do #929 não cita mais o `arvore-envio` nem o `--do-pr` e traz a linha `teto: excedido` com o motivo. O número estava errado (176), e o `forge-check pr --previo` conta 432, adições mais remoções do código (`tamanho-por-item.md`). Como o texto do PR é do tech-lead, troquei o número no corpo, sem push e sem mexer no código.
- **A16:** resolvido. O dia vai fixo ao programa (`dia = 331`, 2026-11-27), e o teste confere que o `date.today()` que ele troca existe.
- **Sonda S1 como teste:** `test_check_bateria_do_pr_nao_e_prova_e_o_script_nao_le_check_runs` mostra pelo comportamento que o check `bateria` do PR não serve de prova e que não há leitura de check-runs.
- **A7 e A10:** seguem como recomendados da volta 1 e viram cartão depois do merge, sem bloquear.

**Verificado local** (com o flock da trava a):
- `tests.test_suite_partes.FiacaoDoCI`, `tests.test_arvore_testada`, `tests.test_catraca.Workflows` e `tests.test_forge.NeutralidadeDoNucleo`: 45 testes, OK.
- `bin/forge-mutante tests/mutantes/v0481-f6-ci-uma-vez.json --processos 1` em `ac8202d0`: CI-M1 a CI-M8 morreram.
