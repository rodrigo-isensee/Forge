---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/ci-ubuntu-26
commit: c481b780e7d368f426043e49451ae7297f5281f3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: ci-ubuntu-26 (runners em ubuntu-26.04, FILA-30 16c)

Este arquivo substitui o parecer de 2026-10-15 do pedido `ci-ubuntu-26` (fixação em `ubuntu-24.04`), que segue no histórico (74d5c27).

## Achados
- A1 (recomendado) tests/test_ci_local.py:124 · o laço sobre `.github/workflows/*.yml` não afirma um mínimo de arquivos; com a pasta vazia ou RAIZ errada o teste passa sem conferir nada; afirmar ao menos 3 workflows (checklist 11)

## Parecer
Aprovado. Diff `b45e40a...c481b78`: os 5 `runs-on` (`ci.yml` 3, `catraca.yml` 1, `release.yml` 1) passam de `ubuntu-24.04` para `ubuntu-26.04`; nenhuma outra linha de workflow muda. Faz o que o cartão pede, nem mais nem menos.

- M14: `git diff --numstat --no-renames b45e40a...c481b78` em `.github/` e `tests/*.py`: 1+1, 3+3, 1+1, 9+0 = 19 linhas, abaixo de 150. Um comportamento (troca do runner). Mexe em `.github/`, então o PR leva o rótulo `afrouxa-regra` do dono e o push com escopo `workflow` é dele.
- Teste reprova sem a mudança: com o teste da branch sobre os workflows da develop (b45e40a), `test_todo_job_roda_no_ubuntu_26_04` falha nos três workflows (subTest catraca.yml, ci.yml, release.yml).
- `python3 -I -m unittest discover -s tests -p test_ci_local.py`: 54 testes, OK (HEAD 4135cde, que contém esta branch).
- Fragmento `changelog.d/ci-ubuntu-26.md` presente. Commits em Conventional Commits.
- Ferramenta: `actionlint` e `zizmor` não rodaram aqui (fora do PATH, lacuna já registrada pelo devops); rodam no job `bateria` do PR, que é a prova de que o actionlint 1.7.12 conhece o rótulo `ubuntu-26.04`.
- Devops: `docs/devops/ci-ubuntu-26-migracao.md` aprovado (citado, não refeito). Segurança: parecer em andamento na worktree `sec-ci-034`.
- Pendência para o fechamento (não é do código): o parecer de devops declara `pedido: ci-ubuntu-26-migracao`, não `versao-033`; o `forge-check pr versao-033` casa pelo campo `pedido` e não o acharia. Alinhar com o devops antes do `forge-fechar`.
