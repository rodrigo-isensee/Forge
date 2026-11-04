---
tipo: revisao-devops
contrato: 1
pedido: versao-033
branch: melhoria/ci-env-argv0-v2
commit: cf90c797c03e7c9da2a094a6e833f1858323cfb7
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-04
---
# Review de devops: ci-env-argv0

## Parecer
Aprovado, sem achado bloqueante. Retomada da branch `melhoria/ci-env-argv0` (3 commits de 2026-10-27, mantida intacta no remoto) reaplicada sobre a develop (dc615c2) e depois reempilhada sobre `melhoria/ci-comentario-rapida` (que contém `melhoria/ci-ubuntu-26`, runners em `ubuntu-26.04`). A develop não resolve o problema de outra forma: a busca por `uutils`, `rust-coreutils` e `argv0` em `.github/` e `scripts/` não acha nada; o `ci.yml` da develop não instala um `env` que aceite `-a`, e `tests/apoio_volta_unica.py` (`envs_da_maquina`) segue procurando o `env` do uutils no PATH.

- Mudança: um passo "env com -a" em `bateria (python 3.14)` e outro em `bateria`, antes de "Testes do Forge". Instala `rust-coreutils` do apt do ubuntu-24.04 (sem ação de terceiros), liga `/usr/lib/cargo/bin/coreutils/env` como `env` numa pasta no começo do `PATH` (`$GITHUB_PATH`) e confere com `shutil.which("env")` que é esse, que aceita `-a x true` e que roda `env X=1 printf`. Falha fecha o job (`set -euo pipefail`, sem `continue-on-error`). Na `bateria` o passo segue o `if` da suíte (gate de commit só de parecer).
- Cobertura: o job `rapida` (push na develop) não ganha o passo, igual à branch original; segue com o `env` do runner. Recomendado, não bloqueia.
- Ferramentas: `shellcheck` limpo no corpo do passo; `actionlint` e `zizmor` ausentes do PATH (lacuna; o job `bateria` do PR roda os dois neste arquivo); patch aplicado sem conflito, `permissions:` inalteradas; `python3 -m unittest tests.test_ci_local`: 52 testes, OK.
- Segurança do pipeline: sem entrada não confiável em `run:`, sem segredo, nada escreve na `main`.
- Conflito com o PR #440 (`release-suite-paralela`): nenhum. O #440 toca `release.yml` e `tests/test_ci_local.py`; este PR toca só `ci.yml`, `changelog.d` e este parecer. `git merge-tree` entre as duas pontas: rc=0.
- recomendado: fixar `rust-coreutils=<versão>` se a mudança de versão do apt virar ruído; não vale agora (runner fixado, conferência pega regressão).

## Reempilhada sobre o ubuntu-26.04 (A1 da segurança)
- O que muda: os dois passos "env com -a" agora rodam em `ubuntu-26.04`. O comentário "o GNU env 9.4 do runner recusa `-a`" valia só para o 24.04; o README da imagem 26.04 (`Ubuntu2604-Readme.md`, 20261026.180.1) lista `coreutils 9.5-1ubuntu2+0.0.0~ubuntu25`, pacote de transição para o uutils, contra `coreutils 9.4-3ubuntu6.3` do 24.04. Comentário corrigido nas duas cópias (`ci.yml`, commit `cf90c79`); nenhuma linha executável mudou.
- Não provado: não há runner 26.04 aqui, então não sei se o `env` do sistema já aceita `-a`, nem se `rust-coreutils` e `/usr/lib/cargo/bin/coreutils/env` seguem iguais no 26.04. O passo falha fechado (`[ -x "$alvo" ]`, `env -a x true`), então um engano reprova o job, não passa em falso. O `env --version` do passo registra o que o runner tem no primeiro run.
- recomendado: depois do primeiro run em 26.04, se o `env` do sistema já aceitar `-a`, retirar a instalação (cartão novo); não mudo a lógica sem prova.
- Pareceres de review (`d8ad0ad`) e de segurança (`ea2227f`) citam o `commit` antigo `3984d0b`, que a reempilhada reescreveu: precisam de revalidação sobre o HEAD novo (a segurança pediu revisão curta do delta). `python3 -I -m unittest discover -s tests -p test_ci_local.py`: OK.

## Risco
- A versão do `rust-coreutils` do noble pode não aceitar `-a`: a conferência reprova o job (falha fechada). Sem rede ao apt do runner aqui, a primeira execução do PR é a prova.
- `apt-get update` e `install` dependem do espelho do runner; falha de rede reprova o job, sem nova tentativa.
- O `env` do PATH vale para a suíte inteira (é o objetivo); `#!/usr/bin/env` absoluto não muda.

## Custo e rollback
- 15 a 30 s por job, dois jobs em paralelo (estimativa; medir na primeira execução), dentro da franquia gratuita (`R-CUSTO`). Sem recurso novo nem serviço pago.
- Rollback: reverter o commit remove os passos; nada persiste no runner. A branch antiga continua no remoto, para o dono decidir.
