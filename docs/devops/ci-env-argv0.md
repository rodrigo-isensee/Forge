---
tipo: revisao-devops
contrato: 1
pedido: ci-env-argv0
branch: melhoria/ci-env-argv0-v2
commit: 3984d0b2721058d8d1d525c12466da2102ecfead
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-04
---
# Review de devops: ci-env-argv0

## Parecer
Aprovado, sem achado bloqueante. Retomada da branch `melhoria/ci-env-argv0` (3 commits de 2026-10-27, mantida intacta no remoto) reaplicada sobre a develop atual (dc615c2). A develop não resolve o problema de outra forma: a busca por `uutils`, `rust-coreutils` e `argv0` em `.github/` e `scripts/` não acha nada; o `ci.yml` da develop não instala um `env` que aceite `-a`, e `tests/apoio_volta_unica.py` (`envs_da_maquina`) segue procurando o `env` do uutils no PATH.

- Mudança: um passo "env com -a" em `bateria (python 3.14)` e outro em `bateria`, antes de "Testes do Forge". Instala `rust-coreutils` do apt do ubuntu-24.04 (sem ação de terceiros), liga `/usr/lib/cargo/bin/coreutils/env` como `env` numa pasta no começo do `PATH` (`$GITHUB_PATH`) e confere com `shutil.which("env")` que é esse, que aceita `-a x true` e que roda `env X=1 printf`. Falha fecha o job (`set -euo pipefail`, sem `continue-on-error`). Na `bateria` o passo segue o `if` da suíte (gate de commit só de parecer).
- Cobertura: o job `rapida` (push na develop) não ganha o passo, igual à branch original; segue com o `env` do runner. Recomendado, não bloqueia.
- Ferramentas: `shellcheck` limpo no corpo do passo; `actionlint` e `zizmor` ausentes do PATH (lacuna; o job `bateria` do PR roda os dois neste arquivo); patch aplicado sem conflito, `permissions:` inalteradas; `python3 -m unittest tests.test_ci_local`: 52 testes, OK.
- Segurança do pipeline: sem entrada não confiável em `run:`, sem segredo, nada escreve na `main`.
- Conflito com o PR #440 (`release-suite-paralela`): nenhum. O #440 toca `release.yml` e `tests/test_ci_local.py`; este PR toca só `ci.yml`, `changelog.d` e este parecer. `git merge-tree` entre as duas pontas: rc=0.
- recomendado: fixar `rust-coreutils=<versão>` se a mudança de versão do apt virar ruído; não vale agora (runner fixado, conferência pega regressão).

## Risco
- A versão do `rust-coreutils` do noble pode não aceitar `-a`: a conferência reprova o job (falha fechada). Sem rede ao apt do runner aqui, a primeira execução do PR é a prova.
- `apt-get update` e `install` dependem do espelho do runner; falha de rede reprova o job, sem nova tentativa.
- O `env` do PATH vale para a suíte inteira (é o objetivo); `#!/usr/bin/env` absoluto não muda.

## Custo e rollback
- 15 a 30 s por job, dois jobs em paralelo (estimativa; medir na primeira execução), dentro da franquia gratuita (`R-CUSTO`). Sem recurso novo nem serviço pago.
- Rollback: reverter o commit remove os passos; nada persiste no runner. A branch antiga continua no remoto, para o dono decidir.
