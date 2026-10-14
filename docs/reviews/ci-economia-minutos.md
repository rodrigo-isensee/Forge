---
tipo: review
contrato: 1
pedido: ci-economia-minutos
branch: melhoria/ci-economia-minutos
commit: 9b002b0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: economia de minutos do GitHub Actions

- **Mudança:** `ci.yml` com os ~10 jobs juntos no job `bateria` (passos nomeados, `if: always()` para reportar todas as falhas; mesmos passos e cobertura) mais o job `rapida` (só no push da `develop`); `pr-texto` vira passo do job `catraca`; `timeout-minutes` em todo job (inclui `release.yml`). Gate por passo: commit de PR que só muda `docs/reviews/` ou `docs/qa/` pula os passos pesados se a `bateria` do commit anterior estava verde (consulta de leitura à API de checks); qualquer dúvida roda tudo. Sem `paths-ignore`. `versão`, `fluxo`, `segredos` e `pareceres` rodam sempre.
- **Push na `develop`:** só testes estruturais; a bateria completa fica no PR e na `homolog` (decisão do dono, opção A). `R-FLUXO`, `.claude/CLAUDE.md`, README e `docs/hooks.md` atualizados; os invariantes de `tests/config.json` não mudaram.
- **Nomes de checks:** os checks `testes estruturais`, `shellcheck`, `workflows`, `validação do plugin`, `instalação de ponta a ponta`, `versão e changelog`, `fluxo de promoção`, `segredos`, `pareceres` e `pr-texto` deixam de existir como jobs; passam a ser `bateria` (CI) e `catraca`. Não há ruleset versionado em `.github/rulesets/`; se a proteção de branch no GitHub exige os nomes antigos, o dono precisa trocá-los por `bateria` e `catraca`.
- **Testes:** ajustei `test_job_versao_cobre_develop_e_main` e o teste dos workflows (catraca com passo `pr-texto`) e acrescentei um teste da estrutura (um job de bateria, timeout em todo job, sem `paths-ignore`). 311 testes OK; `scripts/validar-plugin.sh` passa.
- **Não verificado:** `actionlint` e `zizmor` não existem neste ambiente (o CI roda os dois, no passo `workflows`); o gate só se exercita no GitHub. Risco: o nome do check-run `bateria` no gate; se mudar, o gate cai no caminho seguro (roda tudo).
- **Catraca:** o PR altera `.github/workflows/`, então exige o rótulo `afrouxa-regra` do dono depois do último push (`R-CONFORMIDADE`). Nenhuma regra foi afrouxada de fato; o texto de `R-FLUXO` muda só a bateria do push na `develop`.
