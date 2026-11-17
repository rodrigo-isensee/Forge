---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.4
branch: melhoria/v0474-release-0474
commit: f198cfbd8261eb15acee8adbb95709484f524097
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: release-0.47.4

Escopo: o que entra na `main` desde a 0.47.3 (`origin/main` = `cacbdf06`, merge do #620) até `2539b54f`: 94 commits, da leva v047 (#607 a #634) e da v0474 (#635 a #639) mais a marca `f198cfbd` e os pareceres. Base: o parecer da marca `docs/security/v0474-release-0474.md` (aprovado no `f198cfbd`); daqui ao `2539b54f` só entram `docs/reviews/` e `docs/qa/` (sem código). Os commits seguintes da branch (`77393459`, `444834f4`, `3b1f909c`) só acrescentam `docs/devops/release-0.47.4.md` e `docs/qa/release-0.47.4.md`.

O `commit:` aponta o Revisar-sha do commit da versão (`f198cfbd`); de lá a `2539b54f` só entram pareceres (AQ-5): o conteúdo revisado é o mesmo.

Gatilhos: workflow de CI (`.github/workflows/ci.yml`), hooks (`agentes`, `conformidade`, `parecer`, `pesado`, `meta`, `ambiente`, `hooks.json`), execução de comando (`bin/forge-check`, `bin/forge-mutante`, `bin/forge-fechar`, `scripts/`) e controle novo (`bin/forge_autorizacao.py`, `bin/forge_tamanho.py`).

## Achados

## Sondas

## Detalhe dos achados
Sem achados novos. Conferido:
- `.github/workflows/ci.yml` (+190/-35): gatilhos sem mudança (`pull_request` opened/synchronize/reopened, `push` nas três branches, `workflow_dispatch`); nenhum `pull_request_target`; `permissions: contents: read` no topo e repetido em cada job novo; todas as ações fixadas por SHA de 40 (checkout, setup-python, setup-node, upload-artifact v7.0.2, download-artifact v8.0.2); dado do evento (`head_ref`, `head.sha`, `head.repo.full_name`, `event.before`) só por `env:`, nunca interpolado em `run:`; o `ROTULO` interpolado vem de `matrix.parte`, valor fixo do próprio workflow; `scripts/falhas-no-resumo.py` roda com `python3 -I`. Parecer de origem `docs/security/v047-ci-falhas-no-resumo.md` (aprovado).
- Hooks e ferramentas: cada mudança tem parecer próprio aprovado (27 pareceres novos em `docs/security/`, todos `parecer: aprovado`); os controles e as recomendações abertas estão listados no parecer da marca e valem aqui sem recópia: H1, H2, G1, heredoc, conformidade (A20 de prioridade alta, sem regressão), trava de estado, MAQ-I9 e o patch do pre-push. `hooks/ambiente.py`, `hooks/hooks.json` e `scripts/preparar-estacao.sh`: parecer `docs/security/v047-ambiente-sobrevive.md` (aprovado).
- #608 (evals-ambiente-git): só `tests/` e docs, sem gatilho.
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.4, topo do `CHANGELOG.md` `[0.47.4] - 2026-11-17`; o marketplace não fixa versão.

## Riscos aceitos e ferramentas
Sem riscos aceitos e nenhum pendente de aceite (nenhum parecer da leva em `riscos-aceitos`; não há `docs/security/aceites/`). Os afrouxamentos da versão (heredoc, ADR 0011; MAQ-I9; MAX_PENDENTES 7→8; troca de invariantes da diretriz 29) são decisões do dono por `afrouxa-regra`, não risco aceito. Pendente do dono: aplicar `docs/devops/pp1-pre-push.patch`. Testes rodados: `python3 -m unittest tests.test_changelog tests.test_conferir_release` (106, OK); a suíte inteira é do CI (o run do CI no `2539b54f` estava em andamento ao escrever, Catraca verde; o merge exige o CI inteiro verde). Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint não estão no PATH; workflow conferido por leitura (pins, permissões, injeção de expressão).
