---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.17
branch: melhoria/marca-0.47.17
commit: d2a9d91914d65aa6eb2daca515c89d0907226c85
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: release 0.47.17 (versão inteira), para a promoção

Etapa E12.10 do pedido v0481. Conteúdo: `git diff v0.47.16..d2a9d919` (tag `v0.47.16` = ad55cd9c, ancestral do Revisar-sha; 261 arquivos). Cada item já entrou na develop com o próprio parecer. Aqui confiro a junção, a marca, o CHANGELOG e a versão. O parecer da marca (#882, `docs/security/marca-0.47.17.md`, commit 8d9f51d3, neutro) continua valendo para o 8d9f51d3. Esta rodada cobre também o que veio depois: o merge da develop 6676045c, que traz o #880, e o d2a9d919.

Gatilhos: hooks (`decisao` novo no `Stop`; `agentes`, `pesado`, `conformidade`, `parecer`, `ordens`, `_comum.py`, `hooks.json`), controles do Forge (`tests/catraca.py`, `tests/config.json`, `docs/adr/0008`, `docs/adr/0019`, patches do pre-push), execução de comando (`bin/forge-fechar`, `bin/forge-check`, `bin/forge-copia`, `tests/bancada/versao.py`), release usada por todos os projetos.

## Junção: cada item com o parecer próprio
São 21 PRs: 20 de primeiro pai em `v0.47.16..7e8c9c19` e o #880 (6959cec2), que entra pelo merge 6676045c. Os 18 itens com código, teste, hook, patch ou ADR de controle têm parecer de segurança `aprovado`: #855, #856, #854, #860, #857, #865, #864, #863, #859, #866, #869, #868, #871, #870, #867, #879, #881 e #880. Os três de só documento, sem gatilho, são #873 (proposta G4), #872 (ADR 0019, proposta) e #876 (modelo de ameaças do G2.0).

Para cada um dos 18, busquei a cabeça `refs/pull/<n>/head` para `FETCH_HEAD`, sem criar ref, e conferi três coisas:
- O `commit:` do parecer é ancestral da cabeça nos 18.
- `git diff <cabeça> <commit na develop>` nos arquivos de código que o squash tocou (`bin`, `hooks`, `scripts`, `.githooks`, `.github`, `tests`, `agents`, `skills`, `docs/regras`, `templates`, `patches`, `stacks`) é vazio em 17. No #880, a única diferença é `tests/pesos-d4.json` (uma linha de peso que veio da develop).
- Entre o parecer e a cabeça, o único commit próprio da branch é 15fc9f9c, no #863. Ele só acrescenta um teste em `tests/test_decisor.py` e o mutante D5M29, aperta, e passou por QA por delta (44b0764d). As outras diferenças vêm de merges da develop. Só dois desses merges resolvem conflito à mão (995807ff e c517dbe3), e nos dois a resolução é só a contagem do índice gerado `docs/hooks-fixtures.md`. Neutro.

## Marca e versão
- `git diff 6959cec2 d2a9d919`: só os dois `plugin.json`, o `CHANGELOG.md`, os 21 fragmentos apagados de `changelog.d/` e os três pareceres da marca. Nenhum código.
- CHANGELOG: cada linha não vazia dos 21 fragmentos aparece idêntica, linha inteira, na seção `## [0.47.17] - 2026-11-25` (`CHANGELOG.md:7`), na mesma seção `###` do fragmento. São 22 linhas e não 21, porque `v0480-graphql-ilegivel.md` tinha dois itens: Adicionado 12, Alterado 6, Corrigido 4. Falta 0. Em `changelog.d/` sobra só o `README.md`. `bin/forge-changelog conferir-release` dá `ok`. `tests.test_changelog`: 91 testes, OK.
- Versão: `0.47.17` em `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3`, igual a `CHANGELOG.md:7`.
- Segredos: busquei nas linhas acrescentadas do diff inteiro os padrões de token do GitHub, chave da Anthropic, chave da AWS, chave privada e token do Slack. Nada encontrado. Os nomes de variável de credencial do bench (`ANTHROPIC_API_KEY` e outros) são só a lista do que ele recusa, sem valor.

Superfície protegida em `v0.47.16..d2a9d919`: nenhum arquivo em `.github/`, `.devcontainer/`, `.githooks/`, `scripts/`, `docs/regras/`, `docs/security/aceites/`, `agents/` nem `templates/`, e nenhum manifesto de dependência. `tests/config.json` só ganha um hash em `termos_proibidos_hash` (aperta). Nenhuma invariante sai.

Hooks medidos no Revisar-sha: `bin/forge-check comparar v0.47.16 d2a9d919` dá `so-aperta: medido base=ad55cd9c head=d2a9d919 casos=239 aceites-novos=0` (famílias merge-pr, push-forcado e sem-verificar com 8 casos cada). Essa medida cobre só a decisão dos hooks.

## Só aperta ou neutro, por escrito (para o rótulo afrouxa-regra da promoção)
Nos controles que recusam (hooks, `forge-check`, `forge-fechar`, `forge-copia`, catraca), a versão só aperta ou é neutra frente à 0.47.16. A medida dá `so-aperta`, e nenhum item faz passar uma entrada que antes era recusada. A classificação vem do parecer de cada item:
- **Só aperta:** #854 (graphql ilegível recusa), #855 (todo check-run verde, recusa de cópia velha), #859 (vigia no `agentes` e no `pesado`), #860 (cópia só do agente), #863 (D5, filtro de decisão), #867 (catraca por função), #868 (D7), #869 (D4), #870 (bench, só o dono roda), #879 (`forge-copia --base`), #880 (CI do topo), #881 (`forge-check pronto`).
- **Neutros:**
  - #856: a emenda da ADR 0008 amplia a varredura antes de tornar público e não é trava nova.
  - #857: o hook `decisao` só emite `systemMessage` ao usuário no `Stop` e sai sempre 0, pelo mesmo canal do `vigia`. Não injeta contexto nem decide.
  - #865: o `--laco` usa os mesmos portões do `--lote`.
  - #866: o idioma vai na linha fixa das ordens, só por nome fixo.
- **Patch não aplicado:** #864 (D2) e #871 ficam em `patches/`. Só valem quando o dono aplicar ao `.githooks/pre-push`, que esta versão não toca. Frente ao hook em vigor, o patch aperta. O envio só de parecer "só avisa" no D2, e isso está registrado em `docs/security/v0480-d2-portao-entrega.md`.

**A versão não é só aperta na norma.** Um item afrouxa por autorização do dono, não por esta confirmação. O #871 (`[afrouxa-regra: sai o test_prepush_lote_pp1]`) apaga `tests/test_prepush_lote_pp1.py` (497 linhas) e fecha a proposta PP1 como substituída. A prova do envio local passa para `tests/test_prepush_unico.py`, e `tests/test_pre_push_patch.py` segue provando o PP1. A autorização é a DECISÃO DO DONO de 2026-11-24 17:08, pedido v0478, como risco aceito no `docs/security/v0480-prepush-ajuste-unico.md`. Esse item vai no aviso de marco como item que afrouxa. O merge homolog → main segue com o usuário (`R-MAIN`).

## Riscos aceitos e ferramentas
Nenhum risco aceito novo e nenhum pendente de aceite. O delta não toca `docs/security/aceites/`, e a medida dá `aceites-novos=0`.

A suíte inteira vale pelo CI. Situação na escrita, no PR #882, cabeça 0536f20a, que difere do d2a9d919 só por `docs/qa/release-0.47.17.md` e `docs/reviews/release-0.47.17.md`:
- verdes: bateria (passos, pareceres e verificações longas), catraca, instalação e "árvore já provada";
- em andamento: as partes da suíte em 3.12 e 3.14;
- pulados, como esperado num PR: os jobs que só rodam em push na develop.

O CI do PR de promoção continua sendo o portão. Localmente rodei só `comparar`, `conferir-release` e `tests.test_changelog`.

Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint estão fora do PATH. O delta não toca workflow nem dependência. A busca de segredos foi feita por padrões, acima.
