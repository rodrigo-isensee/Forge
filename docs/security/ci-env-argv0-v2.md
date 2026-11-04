---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/ci-env-argv0-v2
commit: 91055e7f82bb19884565ddc004d02c910bd3e80a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: ci-env-argv0-v2

## Gatilhos
R-SEGURANCA: CI (.github/workflows/ci.yml, dois passos novos com sudo e instalação de pacote); controles do Forge não tocados.

## Achados
- A1 (recomendado) .github/workflows/ci.yml:64 · apt sem versão fixa e o PATH do job inteiro passa a usar o env do uutils; sem caminho realista de ataque, só deriva de ambiente

## Detalhe dos achados
A1: o pacote rust-coreutils vem do universe do runner, sem versão fixa (cadeia de suprimentos: um pacote comprometido executaria no job). O job tem permissions contents: read, persist-credentials false e gatilho pull_request, sem segredo. Impacto baixo; mitigação opcional é fixar a versão com apt. Esforço P, dono devops-engineer. O passo falha fechado (set -euo pipefail, confere o caminho do env e o `-a`). Os dois passos são idênticos; o segundo só roda com a bateria pesada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Análise estática do diff; zizmor, actionlint e gitleaks não rodados aqui (o CI os roda).

## Revalidação
Head 91055e7 (branch reempilhada sobre melhoria/ci-comentario-rapida, CI em ubuntu-26.04). O `forge-check delta` não calcula (3984d0b não é ancestral de 91055e7, por causa do rebase); a releitura foi feita assim:
- Rebase: `git range-diff` dá 3984d0b = ad9e262 (patch idêntico). As linhas executáveis do diff de ci.yml (sem comentários) entre a base e 91055e7 são iguais às entre a base antiga e 4815498.
- cf90c79 muda só linhas de comentário (.github/workflows/ci.yml:58-61 e :261-264); resolve o A1 da revisão sec-ci-034 (o comentário não afirma mais GNU env 9.4 no 26.04).
- Falha fechado no 26.04 (.github/workflows/ci.yml:62-76 e :265-279): com `set -euo pipefail`, pacote rust-coreutils ausente faz o `apt-get install` reprovar o passo; caminho /usr/lib/cargo/bin/coreutils/env mudado ou ausente cai no `[ -x "$alvo" ] || exit 1`; env do PATH que não seja o do link cai na conferência do `shutil.which`; env sem `-a` cai no `env -a x true || exit 1`. Se o coreutils de transição do 26.04 já trouxer o uutils, o passo segue verde pelas mesmas conferências; não há caminho que passe com um env sem `-a`.
- Ações: nenhum `uses:` novo nem alterado; todos seguem fixados por SHA. Sem mudança de `permissions`, gatilho ou segredo.
- Teste: `python3 -I -m unittest discover -s tests -p test_ci_local.py`, 54 testes OK.
- A1 (recomendado) continua como estava, só com a linha atualizada. Parecer mantido: aprovado.
