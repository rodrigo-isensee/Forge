---
tipo: revisao-seguranca
contrato: 1
pedido: lote-ci1-lint
branch: melhoria/lote-ci1-lint
commit: b59891dd4b621fc6f5b0bdce44a192d1c5ed33a6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-ci1-lint

Intervalo revisado: `3c66b88..b59891d` (um commit: `.github/workflows/ci.yml`, `tests/test_ci_local.py`, `changelog.d/lote-ci1-lint.md`), e o `.github/workflows/ci.yml` inteiro no HEAD. Fecha o X2 de `est-030-ameacas-l2-l3.md` (CI-ORDEM-LINT).

## Gatilhos
- Controles do Forge e CI (`R-SEGURANCA`): ordem dos passos do job `bateria` em `.github/workflows/ci.yml` e o teste que a protege em `tests/test_ci_local.py`.

## Achados

## Detalhe dos achados
Verificações feitas, sem achado bloqueante:

1. **Nenhum código da branch roda antes do lint no caminho pesado.** Antes do download (`ci.yml:127-141`), do `actionlint` (`ci.yml:142-144`) e do `zizmor` (`ci.yml:145-147`) só há: o checkout fixado por SHA (`ci.yml:86`), o gate com shell embutido no workflow que só chama `git diff --name-only`, `git cat-file` e `gh api` (`ci.yml:90-114`; nenhum desses executa hook nem driver de diff, e o `.git/config` não vem da branch), o `setup-python` e o `setup-node` fixados por SHA, com versão literal e sem `*-version-file` (`ci.yml:118-125`). Os passos que executam código da branch vêm todos depois: `bin/forge-changelog` (`:161`), `scripts/conferir-release.py` (`:169-171`), `scripts/verificar-contribuicao.sh` (`:189`), o `catraca.py` e o `reexecutar-provas.py` (`:210`, `:232`; o da branch só na introdução), a suíte (`:235`), o shellcheck (`:238`) e o e2e (`:241`). A instalação do Claude Code (`:151`), que lê um eventual `.npmrc` da raiz, também ficou depois.
2. **O `GITHUB_PATH` não pode ser adulterado antes do lint.** Nenhum passo anterior roda código ou configuração da branch, então nada da branch escreve em `$GITHUB_PATH`, `$GITHUB_ENV` ou `BASH_ENV` antes de `actionlint` e `zizmor` serem resolvidos. O download usa `curl`, `sha256sum` e `tar` do runner, confere o SHA-256 fixo no `env` do job (`ci.yml:81-84`) e extrai só o membro nomeado. A escrita posterior no `GITHUB_PATH` por código da branch não desfaz o resultado de um passo que já falhou.
3. **Falha fechada.** Se o download falhar, os dois passos seguintes rodam (`!cancelled()`) e caem em "command not found": o job reprova. Não há `continue-on-error`. Nenhuma permissão, gatilho ou credencial mudou: `permissions:` do job (`ci.yml:77-79`), `on:` sem `pull_request_target`, `persist-credentials: false` e o `GH_TOKEN` só no gate.
4. **Caminho leve (commit só de parecer).** O passo "Testes que leem pareceres" (`ci.yml:115-117`) roda código da branch antes da posição do lint, mas só com `pesada != 'true'`, quando o lint é pulado por desenho (só `docs/reviews|qa` mudou desde um commit com a bateria verde). Não há lint a subverter ali; fica fora do X2.
5. **Job `rapida` (`ci.yml:22-35`).** Não tem o mesmo risco: roda só no push da `develop`, não tem `actionlint`, `zizmor` nem script da base como portão, só a suíte do conteúdo que o PR já validou. O job `bateria-python-tres-quatorze` (`ci.yml:37-70`) também não tem lint; a suíte roda antes do e2e, mas os dois são código da mesma branch, e um não serve de controle sobre o outro.
6. **Teste.** `tests/test_ci_local.py:166` passa no HEAD (52 testes do módulo, OK). Mutação: com `bin/forge-changelog` movido para antes do lint, o teste falha.

Recomendações (não bloqueantes):

- R1. `tests/test_ci_local.py:178`: o teste confere uma lista fechada de passos conhecidos (lista de negação). Mutação: um passo novo `run: python3 scripts/qualquer.py` inserido antes do download continua passando no teste. Caminho: um PR futuro põe um passo da branch antes do lint e o teste não pega; o review do `ci.yml` continua sendo a barreira. Correção mínima: inverter a regra para lista de permissão. Todo passo antes do download é `uses:` fixado por SHA, o gate, ou um passo com `pesada != 'true'`. Esforço P. Dono: `devops-engineer`.
- R2. `ci.yml:161`: no caminho pesado, código da branch (`bin/forge-changelog`, `scripts/verificar-contribuicao.sh`) ainda roda antes do `catraca.py` e do `reexecutar-provas.py` da base (`:210`, `:232`) e pode pôr um `python3` falso no `GITHUB_PATH`, o que anula esses portões. É o A4 de `docs/security/est-030-l2.md` (ordem dos passos e `GITHUB_PATH`), já em cartão para depois do CI-ORDEM-LINT, e fica fora deste lote. Correção mínima: chamar o interpretador pelo caminho absoluto, ou rodar os portões da base antes de qualquer código da branch. Esforço P. Dono: `devops-engineer`.
- R3 (informativa). O `actionlint` e o `zizmor` leem configuração da própria branch (`.github/actionlint.yaml`, `zizmor.yml`/`.github/zizmor.yml`), que pode silenciar regras. Hoje não existe nenhuma das duas. A alteração aparece no diff, como qualquer mudança do próprio `ci.yml`. Vale cobrir na lista de caminhos protegidos da catraca, se ainda não estiver lá.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: `shellcheck` presente; `actionlint`, `zizmor` e `gitleaks` ausentes do PATH local (lacuna; o próprio job `bateria` roda `actionlint` e `zizmor` no CI). Revisão estática e sondas de mutação do teste numa cópia em `$TMPDIR`.
