---
tipo: revisao-seguranca
contrato: 1
pedido: v0475-ci-custo
branch: melhoria/v0475-ci-custo
commit: d8e1b09b050f7455637234be5a9ccbc97c9d0ed5
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0475-ci-custo (revalidação por delta)

Escopo: delta `f59f7766..d8e1b09b` lido por `forge-check parecer delta` (pedido v0474, E3.103). No domínio: `templates/projeto/.github/workflows/ci.yml`, `ci-docs.yml` (removido) e `skills/ci-cd/SKILL.md`. Fora do domínio: `tests/test_modelo_ci.py`, `tests/mutantes/*.json`, `changelog.d/`. A rodada anterior (no head f59f7766) fica no git.

## Gatilhos
Gatilhos: CI/CD (workflow-modelo copiado para todo projeto novo).

## Achados
- A1 (recomendado) templates/projeto/.github/workflows/ci.yml:75 · Resolvido no d8e1b09b: o ci-docs.yml saiu; um workflow só e um único check `ci`, que exige `mudanca` success e a suíte success, ou skipped só com so_documento=true.
- A2 (recomendado) templates/projeto/.github/workflows/ci.yml:21 · Resolvido no d8e1b09b: grupo por `github.event.pull_request.number || github.ref`; PR de fork homônimo e push da develop não cancelam mais a rodada alheia.
- A3 (bloqueante) templates/projeto/.github/workflows/ci.yml:45 · `git diff --name-only` detecta renomeação e lista só o destino: mover código para `docs/` ou para `*.md` esconde a remoção da origem, a detecção diz "só documento", a suíte é pulada e o `ci` fica verde. Correção: `--no-renames`.

## Sondas
- S1 · repositório com `src/app.py`; commit `git mv src/app.py docs/app.py`; trecho `run:` do job `mudanca` com BASE/CABECA dos dois commits · espera: so_documento=false · obtido: so_documento=true (git 2.43.0; `git diff --name-only` lista só `docs/app.py`)
- S2 · idem com `git mv src/app.py src/app.md` · espera: so_documento=false · obtido: so_documento=true
- S3 · arquivo novo com quebra de linha no nome (`a\nb.md`) · espera: so_documento=false · obtido: so_documento=false (git cita o nome entre aspas; fecha)

## Detalhe dos achados
**A3** (média). Evidência: `ci.yml:45`, `git diff --name-only "$BASE...$CABECA"` sem `--no-renames`; o `diff.renames` padrão do git (desde 2.9) é ligado, e com `--name-only` a renomeação aparece só pelo caminho novo. Caminho: o autor de um PR (pessoa ou agente, inclusive de fork) move um módulo, um teste ou a configuração do build para `docs/` ou muda a extensão para `.md` (com até 50% de alteração ainda conta como renomeação); a origem some do diff, a suíte é pulada (`ci.yml:59`) e o agregador aceita o pulo (`ci.yml:75-94`): o check exigido fica verde com o build quebrado ou um teste de segurança removido. Também acontece sem má-fé (mover arquivo para a pasta de documentação). Correção mínima (dono: `devops-engineer`, esforço P): `git diff --no-renames --name-only "$BASE...$CABECA"`; com ela a S1 lista `docs/app.py` e `src/app.py` e dá false. Teste: em `tests/test_modelo_ci.py`, exigir `--no-renames` na linha do diff e um caso que execute o trecho contra um repositório com `git mv` de código para `docs/` (as sondas S1 e S2 servem de caso de abuso).

Conferido no delta e sem achado (foco: injeção no `run:` do job de detecção):
- **Dados do evento:** `base.sha`, `before`, `head.sha` e `sha` entram por `env:` (`ci.yml:40-42`) e são lidos entre aspas; nenhum `${{ }}` dentro do `run:`. São SHAs gerados pelo GitHub, não texto do autor (título, corpo e nome de branch não são usados). `git cat-file -e "$BASE^{commit}"` falha com o `before` zerado do primeiro push e com base ausente: a detecção fica false e a suíte roda (fecha).
- **Nomes de arquivo (controlados pelo autor do PR):** só passam por `case` contra padrão, sem `eval`, expansão ou escrita em `$GITHUB_OUTPUT`; o que vai ao `$GITHUB_OUTPUT` é só o literal `true`/`false`. Nome com caractere incomum sai entre aspas do git e não casa com `*.md` nem `docs/*` (S3): fecha.
- **Checkout do job `mudanca`:** `persist-credentials: false`, `contents: read`, ação fixada pelo mesmo SHA (`ci.yml:34`); só roda `git`, sem código do repositório; `--name-only` não aciona driver de diff nem textconv.
- **Concorrência:** `github.event.pull_request.number || github.ref` em `concurrency.group`, fora de shell.
- **Agregador:** `needs: [mudanca, suite]`, `if: always()`; `mudanca` diferente de success falha; saída vazia faz a suíte rodar.
- **Skill:** `skills/ci-cd/SKILL.md:58-60` descreve o mesmo padrão; ao corrigir A3, citar `--no-renames` no item.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Teste rodado: `python3 -m unittest tests.test_modelo_ci`, 17 testes, OK; sondas S1 a S3 rodadas localmente sobre o trecho copiado do `run:`. Sem PR aberto para a branch, sem CI a citar: a suíte inteira fica com o CI do PR na volta. Ferramentas ausentes no PATH (lacuna, nada instalado): `zizmor`, `actionlint`, `gitleaks`.
