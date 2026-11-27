---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-f6-ci-uma-vez
commit: e85793a8317bf410d3b98cc7f45ad46ffed285e8
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E32.10, #929, F6 no CI), volta 1 por delta

Delta lido (H3): `forge-check parecer delta` de `e8368a4c..e85793a8`, sem o que veio da develop (o merge `2b68d805` fica fora). São 12 arquivos no domínio: `ci.yml`, `diario.yml`, o changelog, `scripts/arvore-testada.py`, 4 specs de mutantes e 4 arquivos de teste. Nada fora do delta foi relido.

## Achados
- A11 (recomendado) tests/test_catraca.py:4267 · O CI do head reprova: a develop ficou com um agregador `always()` só (o `rapida-quatorze` saiu na 1ª rodada), e o teste ainda espera (2, 2) e 4 jobs com always(). Ajuste para (2, 1) e 3, com o comentário. Sem isso o CI não fica verde e o G3 barra.
- A12 (bloqueante) .github/workflows/ci.yml:35 · O CI do head reprova em tests/test_catraca.py:4253: a lista de `timeout-minutes` ainda tem o job `arvore-envio`, que o delta tirou, e as pernas do 3.14. O head tem 13 valores. Alinhe a lista e o comentário de cima dela ao ci.yml novo.
- A13 (recomendado) .github/workflows/diario.yml:82 · O CI do head reprova em tests/test_forge.py:511 (NeutralidadeDoNucleo): `npm` no diario.yml. Registre a exceção de `\bnpm\b` para o diario.yml em tests/config.json, como a do ci.yml (tests/config.json:78). Sem isso o CI não fica verde e o G3 barra.
- A14 (bloqueante) .github/workflows/diario.yml:111 · V2: as 5 linhas de guarda novas da fatia (111, 116, 119, 120 e 121) não têm mutante declarado. A spec do F6 só tem CI-M1 a CI-M3. Declare um mutante por linha; o teste test_suite_partes.py:754 já mata os de 116, 120 e 121.
- A15 (bloqueante) .github/workflows/ci.yml:35 · `pendente:` o corte A5 entrou no código, mas o corpo do #929 ainda descreve o `arvore-envio` e o `--do-pr` e não traz a linha `teto: excedido, <n> linhas, <motivo>` (H1). Atualize o corpo do PR, sem push.
- A16 (recomendado) tests/test_suite_partes.py:758 · O teste lê `date.today()` e o subprocesso lê de novo. Na virada da meia-noite os dois discordam e o teste falha. Passe o dia ao programa (variável de ambiente) ou compare só a forma da saída.
- A7 (recomendado) scripts/arvore-testada.py:31 · A entrada "3.14" de JOBS_DE_PROVA continua morta. Isto já estava na 1ª rodada; vira cartão.
- A10 (recomendado) .github/workflows/diario.yml:91 · Com uma spec por chamada, a fatia passa a ter cerca de 39 chamadas por dia (1164 specs / 30), cada uma com o seu preparo, sob teto de 60 min. Meça o primeiro `workflow_dispatch`.

## Parecer
**Reprovado.** Os bloqueantes da 1ª rodada saíram. Ficam os três defeitos que o CI do head provou (A11 a A13), os mutantes das guardas novas (A14) e o corpo do PR (A15). O A11 e o A13 vêm de linhas da 1ª rodada, fora do delta, e por isso ficam como recomendados (G1.2). Mesmo assim, entram na volta 2: sem eles o CI fica vermelho, e sem CI verde não há aprovação (G3).

**CI (G3):** não há linha `ci:`. `gh pr checks 929` no head `e85793a8` (run 45930295535):
- Em vermelho: `suíte (python 3.12, parte 2/5)` (A11 e A12), `suíte (python 3.12, parte 3/5)` (A13) e o agregador `bateria`.
- Em verde: as partes 1, 4 e 5, `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)` e `bateria (python 3.14)`.

A `catraca` (run 45930295435) espera o rótulo `afrouxa-regra` depois do último push, porque o diff mexe no ci.yml e no diario.yml. Isso fica com o dono. Os seis "confira no parecer" de valor esperado trocado (test_ci_local, test_falhas_no_resumo e test_suite_partes) foram lidos. Todos acompanham a saída das pernas do 3.14 e do `arvore-envio`: conferem com o pedido.

**Situação dos achados da 1ª rodada (o delta):**
- **A1:** resolvido. O `name:` está entre aspas e o GitHub criou o CI. O teste novo varre os `name:` de todos os workflows atrás de `: ` sem aspas.
- **A2:** resolvido. As specs v047-ci-binario-cli, v047-ci-rapido-3 e v047-ci-falhas-no-resumo estão alinhadas. O `bin/forge-mutante --conferir --todas` no head só acusa as pendentes conhecidas, e ConferirTodas passa local.
- **A3:** resolvido. A fatia vai uma spec por chamada, e o teste roda o próprio programa do diario.yml numa árvore descartável. Os ids da spec do F6 viraram CI-M1 a CI-M3, com teste contra repetição no pedido.
- **A4:** resolvido. Os pendentes saem por `--ids`, e a spec toda pendente não roda.
- **A5:** o código foi cortado: `arvore-envio`, `--do-pr`, `ProvaDoPr` e os mutantes M1 a M7 saíram. Falta o corpo do PR (A15).
- **A6:** resolvido.
- **A8:** resolvido, porque o teste saiu com o `ProvaDoPr`.
- **A9:** resolvido, com 3 mutantes.
- **A7 e A10:** seguem como recomendados.

**Verificado local** (com o flock da trava a):
- `tests.test_suite_partes.FiacaoDoCI`, `tests.test_forge_mutante.ConferirTodas`, `tests.test_arvore_testada` e `tests.test_ci_local.InstalacaoDoCliTest`: 41 testes, OK.
- `bin/forge-mutante tests/mutantes/v0481-f6-ci-uma-vez.json --processos 1`: CI-M1, CI-M2 e CI-M3 morreram.

**Volta 2:** A11 a A14 num commit só, com a mutação `--base e85793a8` e o teste do A13 rodados antes do push. Depois, o corpo do PR (A15). A próxima rodada lê o delta e exige o CI verde no head novo.
