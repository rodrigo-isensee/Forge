---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/ci-env-argv0-v2
commit: 91055e7f82bb19884565ddc004d02c910bd3e80a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033 (ci-env-argv0-v2)

## Achados
- A1 (recomendado) .github/workflows/ci.yml:23 · O job rapida (push na develop) roda a suíte sem o passo env com -a e segue com o env do runner; a prova viva de 20 formas cai ali. Duplicar o passo ou extrair ação local.
- A2 (recomendado) .github/workflows/ci.yml:55 · O corpo do passo está copiado nos dois jobs da bateria (19 linhas); mudar um e esquecer o outro diverge. Extrair para scripts/ ou ação composta.
- A3 (recomendado) .github/workflows/ci.yml:60 · O comentário diz que o passo "confere o `env --version`", mas o passo só imprime a versão (`env --version | head -1`, :76). Quem confere é o `shutil.which` e o `env -a x true`. Trocar por "imprime o `env --version` e confere o `-a`".

## Parecer
Aprovado. Lido o diff inteiro (39 linhas em ci.yml, abaixo do teto M14, uma classe de comportamento). Passo seguro: pacote do apt do runner (assinado pelo apt, sem download avulso nem checksum a verificar, sem ação de terceiros), sem entrada não confiável em run:, permissions inalteradas. Fica no lugar certo, antes da suíte e sob o mesmo if do gate na bateria. Falha fechado (set -euo pipefail, conferência de which, -a e env X=1). Pinagem de versão do rust-coreutils não é necessária com runner fixado em ubuntu-24.04 (parecer de devops). Não quebra o job rapida, que não foi alterado. Teste: test_ci_local, rc=0. Segurança: CI é gatilho de R-SEGURANCA, mas o parecer de devops não cobre segurança; peça ao security-engineer parecer curto (instalação de pacote com sudo no runner, sem segredo).

## Revalidação (91055e7, volta por delta)
- Rebase: `bin/forge-check delta --parecer` sai com rc 2 ("3984d0b não é ancestral de 91055e7"), então conferi à mão. `git range-diff 3984d0b^! ad9e262^!` marca o commit como `=`, idêntico. O `diff` dos dois `git show`, sem as linhas `index`, só muda os cabeçalhos de hunk (`@@ -52` vira `@@ -53`, `@@ -233` vira `@@ -234`), por causa da linha que a ci-comentario-rapida acrescentou acima. Nenhuma linha executável mudou.
- cf90c79: muda só linhas de comentário, nas duas cópias do passo (`.github/workflows/ci.yml:58-61` e `:261-264`). Confere com a fonte: o `Ubuntu2604-Readme.md` de actions/runner-images (imagem 20261026.180.1) lista `coreutils 9.5-1ubuntu2+0.0.0~ubuntu25`, como diz o comentário. O texto não afirma mais que o env do 26.04 recusa `-a` ("pode recusar"). A conferência do passo falha fechado qualquer que seja o env da imagem. Fica um ajuste de texto, o A3 (recomendado).
- 91055e7 em diante: só pareceres (`docs/devops/`, e o `docs/security/` em 7ddee26, depois do head revisado).
- `python3 -I -m unittest discover -s tests -p test_ci_local.py` em 91055e7: 54 testes, OK, rc 0.
- M14: `git diff --numstat --no-renames 169c885 91055e7` (base: o topo da ci-comentario-rapida) só conta `.github/workflows/ci.yml` 43+0, abaixo de 150. Uma classe de comportamento.
- Segurança e devops revalidados nos pareceres próprios (`docs/security/ci-env-argv0-v2.md`, `docs/devops/`). Não refiz essas revisões.
- Parecer mantido: aprovado. A1 e A2 seguem como recomendação.
