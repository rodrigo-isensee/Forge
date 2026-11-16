---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-reverte-576
commit: 988ca87aa95f0b9dea54bdb442f0ee5b5b7f0e0f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (revert do #576, CI-RAPIDO)

Intervalo revisado: `befbb464..988ca87a` (E2.440), um commit, `git revert` de `22f1eaa8` (#576), 28 arquivos. Parecer completo (não havia parecer anterior desta branch).

## Gatilhos
Gatilhos: CI e pipeline (`.github/workflows/ci.yml`), controles de teste da fábrica (`R-SEGURANCA`, `R-CONFORMIDADE`).

## Achados

## Sondas

## Detalhe dos achados
Sem achado. O que foi conferido:

- **Revert puro do #576.** Os 28 arquivos do diff `befbb464..988ca87a` são os mesmos 28 do `22f1eaa8^..22f1eaa8`, e as linhas `+`/`-` do revert são idênticas às do inverso do #576 (comparação linha a linha, sem diferença). `22f1eaa8` é ancestral de `befbb464`. Nenhum outro arquivo foi tocado.
- **Estado restaurado.** `.github/workflows/ci.yml` e `scripts/suite-partes.py` ficam byte a byte iguais a `22f1eaa8^` (o último estado aprovado antes do #576). Dos 28 arquivos, só `docs/engineering/achados-recorrentes.md` difere de `22f1eaa8^`, e a diferença é de commits posteriores (#590, #586: AR-1 e AR-4), preservada pelo revert: nada de terceiro foi desfeito.
- **Workflow (lado da segurança).** Topo `permissions: contents: read` (`.github/workflows/ci.yml:24-25`), jobs com `contents: read`; todas as ações fixadas por SHA; sem `pull_request_target`; dados do evento só via `env:` (`ci.yml:173-174`, `:446`). Os jobs removidos (matrizes de 5 partes, tetos e agregadores do #576) levavam só `contents: read`; a remoção não abre permissão nem ação nova. Os timeouts voltam a 30 min (falha fechada, sem pular prova).
- **Prova da promoção.** `JOBS_DE_PROVA` (`scripts/arvore-testada.py:31`) não muda e os dois nomes existem no `ci.yml` restaurado (`:33`, `:75`, jobs `rapida` e `rapida-quatorze`); a promoção continua lendo um job com o nome exato.
- **Remoção de controles do #576.** Saem `scripts/pesos-do-ci.py` (o único script que lia a API com token, A2 do parecer do #576) e o emissor de anotação de `suite-partes.py`, com os testes deles (`tests/test_pesos_do_ci.py`, `tests/test_ci_rapido_guardas.py`, mutantes `v047-ci-rapido-*`). Os requisitos A1 a A6 do parecer do #576 protegiam só o que sai junto; sem o código, não há superfície órfã. Nenhuma referência pendurada a `pesos-do-ci` fora de docs históricos.
- **Catraca de workflows.** `tests/test_catraca.py` volta ao par com o `ci.yml` de antes do #576; sem teste de controle alterado (o revert não toca `tests/test_catraca.py`). `python3 -m unittest tests.test_catraca.Workflows`: 6 testes, OK; `tests.test_suite_partes tests.test_ci_local`: 99, OK; `tests.test_orcamento_instrucao` OK. Em `tests.test_metricas_texto` resta só o teto de `agents/jarvis.md`, que vem do #584 (`e2e32879`), fora deste revert (consertado na junção E2.438).
- **Segredos no diff:** só remoções; o valor fictício de token sai com `tests/test_pesos_do_ci.py`.

Recomendação (não bloqueante, dono `devops-engineer`): ao reapresentar o CI-RAPIDO, o mesmo PR atualiza `tests/test_catraca.py` com revisão (`R-CONFORMIDADE`), e o parecer do #576 (`docs/security/v047-ci-rapido.md`, removido aqui) é recuperado do histórico como base do novo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `git diff`/`git show` e os testes de unidade do item. `gitleaks`, `actionlint` e `zizmor` não estão no PATH deste ambiente (lacuna; rodam no CI).
