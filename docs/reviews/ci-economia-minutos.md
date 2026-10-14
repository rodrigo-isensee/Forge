---
tipo: review
contrato: 1
pedido: ci-economia-minutos
branch: melhoria/ci-economia-minutos
commit: 060aab3
parecer: reprovado
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

## Review independente (head `060aab3`)

Conferido: `git diff origin/develop HEAD`, a proposta (diagnóstico de minutos) e o parecer de autor. `python3 -m unittest discover -s tests`: 311 testes, OK. `scripts/validar-plugin.sh`: passa. `actionlint` 1.7.12 e `zizmor` 1.30.1 (baixados com o mesmo checksum do CI): sem achados (`zizmor --offline --min-severity medium`).

### Cobertura (passo a passo contra a `origin/develop`)
Nenhum passo se perdeu: testes estruturais, shellcheck (mesma lista de arquivos), download com checksum, `actionlint`, `zizmor`, `claude plugin validate --strict`, instalação de ponta a ponta, os dois passos de versão (com os mesmos `if` do antigo job `versao`), "Nada pula degrau", segredos e pareceres estão no job `bateria`, e `pr-texto` virou passo do `catraca` com o mesmo `if`. Versão, fluxo, segredos e pareceres ficam fora do gate e rodam com `always()` em todo PR. Push na `homolog`, na `main` e `workflow_dispatch` sempre rodam tudo (`pesada=true` fora de `synchronize`). O push na `develop` roda só os testes estruturais, como decidido pelo dono. O texto de `R-FLUXO`, do `.claude/CLAUDE.md`, do README e de `docs/hooks.md` corresponde ao workflow, com a ressalva do item R3.

### Segurança dos workflows
- **`permissions`:** o padrão é `contents: read`. A `bateria` acrescenta só `checks: read`, e o `catraca` não mudou.
- **Gatilhos e interpolação:** não há `pull_request_target`. Todo dado do PR entra por `env:`, e o `${{ }}` só aparece em `env`, `if` e `concurrency`.
- **Token:** o `github.token` vai só no passo do gate (`GH_TOKEN`), e o checkout continua com `persist-credentials: false`.
- **Falha fechada:** o gate roda tudo quando a API falha (`|| echo 0`), quando o `before` some depois de um force push (`cat-file`), quando o diff falha (`?`), quando o diff vem vazio e em qualquer evento que não seja `synchronize`. Se o próprio passo do gate falhar, o job falha.
- **Concorrência:** um commit de parecer enviado com a bateria anterior ainda em curso cancela essa bateria, que conclui como `cancelled`, e por isso roda tudo. Um commit de parecer depois de bateria vermelha também roda tudo.

### Bloqueia o merge
1. **Renomear para `docs/reviews/` ou `docs/qa/` esconde código mudado do gate** (`.github/workflows/ci.yml`, passo "Gate", linha do `git diff --name-only "$ANTES" "$HEAD_SHA"`). Com a detecção de renomeação (padrão do git), `--name-only` lista só o destino. Um commit que move `agents/x.md`, `scripts/*.sh` ou `tests/test_*.py` para `docs/reviews/` aparece como só de parecer e pula testes, shellcheck, validação do plugin e instalação. Reproduzido com git 2.43: o diff de `git mv scripts/a.sh docs/reviews/a.md` lista só `docs/reviews/a.md`. Com `--no-renames`, lista os dois caminhos. Isso quebra a garantia "commit que mistura parecer e código nunca pula a bateria".
   **Correção:** `git diff --name-only --no-renames "$ANTES" "$HEAD_SHA"`, mais um teste em `tests/test_catraca.py::Workflows` que exija `--no-renames` na linha do gate.
2. **O commit só de parecer pula os testes que leem `docs/reviews/` e `docs/qa/`.** `arquivos_texto()` (`tests/test_forge.py:54`) inclui `docs`, e por isso `Neutralidade.test_sem_termos_de_projeto` (`termos_proibidos_hash`, `R-NEUTRO`), `Referencias` e `AntiDuplicacao` (pastas com `docs`, sem ignorar pareceres) varrem os pareceres. `neutralidade_nucleo.ignorar` só vale para os termos de stack. Um parecer com termo de projeto deixa o PR verde. A falha só aparece depois do merge, no push da `develop`, que fica vermelha. O `verificar-contribuicao.sh`, que roda sempre, não confere o hash. É exatamente um commit de parecer deixando verde algo que os testes reprovariam.
   **Correção:** no caminho `pesada=false`, rodar ao menos `python3 -m unittest tests.test_forge.Neutralidade tests.test_forge.Referencias tests.test_forge.AntiDuplicacao`, que levam poucos segundos e cabem no mesmo minuto faturado. Outra opção é tirar "Testes do Forge" do gate. Também precisa de um teste que trave isso no `ci.yml`.

### Recomendado (não bloqueia)
- **R1, nome do check-run:** o gate aceita qualquer check `bateria` com `success` no commit anterior. Dois caminhos permitem forjar esse check.
  - Um GitHub App com `checks: write` cria um check com esse nome.
  - Um PR que acrescenta um workflow com um job `name: bateria` produz o check verde ao lado do vermelho verdadeiro. O commit de parecer seguinte, então, pula os passos pesados.

  O segundo caminho exige mudar `.github/workflows/`, o que a catraca já prende ao rótulo do dono. Ainda assim, vale endurecer.
  **Sugestão:** filtrar por `.app.slug == "github-actions"` e exigir que o check `bateria` mais recente (`max_by(.completed_at)`) seja `success`, sem aceitar um verde ao lado de um vermelho do mesmo commit.
- **R2, `always()` roda até em execução cancelada:** com `cancel-in-progress`, o run cancelado continua executando todos os passos pesados que têm `always()` e gasta os minutos que o PR quer poupar.
  **Sugestão:** `!cancelled() && steps.gate.outputs.pesada == 'true'` (e `!cancelled()` nos passos de regra e no `pr-texto` da catraca).
- **R3, PR de promoção para a `homolog`:** o gate vale para qualquer PR, então um avanço só de parecer na `develop` pula os pesados no PR `develop` → `homolog`. Isso contradiz a `R-FLUXO` ("bateria completa no PR de promoção e no push"). O push na `homolog` roda tudo, então o risco é baixo.
  **Sugestão:** limitar o gate a `github.base_ref == 'develop'`, passando o valor por `env`, ou ajustar o texto da regra.

### Riscos aceitos e pendências
- **Base que avançou:** se a `develop` avança e o PR recebe só um parecer, a combinação nova não é retestada no PR. Como o push na `develop` agora roda só os testes, a bateria completa dessa combinação fica para a `homolog`. É o risco que o dono aceitou na opção A, registrado na proposta.
- **Checks exigidos:** a proteção de branch no GitHub precisa trocar os nomes antigos de checks exigidos por `bateria` e `catraca` antes do merge, senão os PRs ficam pendentes para sempre. Essa troca é do dono.

**Parecer: reprovado.** Os bloqueantes 1 e 2 voltam ao autor. Re-review depois da correção.
