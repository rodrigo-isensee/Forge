---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-merge-checks
commit: cc4934ded283fd19b3d614f7981431db61713739
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0474 E3.194 (revalidação por delta, E3.185 sobre o E3.45 e o E3.80)

Delta lido (`forge-check parecer delta`, `27c4c567..cc4934de`, sem o que veio da develop). No domínio: `bin/forge-check` (`GH_SEM_PR` em `:1444-1445`; `modelo_atras_do_plugin` e `branch_do_modelo_sem_pr` em `:9541-9575`; aviso no `executar` em `:10250`), `bin/forge-testes` (`RODAM_OS_HOOKS` e os mapas do `test_sempre_atual`) e `tests/test_forge_check_pr.py:137`. Já lido antes: o resto do E3.45 e do E3.80 (pareceres no `9f497b0f` e no `27c4c567`, no git).

Conclusão: aprovado. Ponto pedido, a nova marca `"set the GH_TOKEN environment variable"` em `GH_SEM_PR`:
- O `gh` só escreve esse texto quando a checagem de login falha com `GITHUB_ACTIONS=true`. Fora do Actions, o mesmo ramo escreve `gh auth login`, marca que já existia. Com token no ambiente ou login no `GH_CONFIG_DIR`, o `gh` não chega a esse texto. As sondas S1 e S2 (gh 2.104.0) mostram que o texto só aparece com `GITHUB_ACTIONS=true` e config vazia. Fora do Actions, a mensagem traz `populate the GH_TOKEN ...`, que não casa com a marca nova (casa pela `gh auth login`, já existente).
- O casamento é por substring do stderr do `gh pr view` (`bin/forge-check:1493`). O único dado do agente nesse stderr é o nome da branch, e nome de branch não tem espaço, então não forja a frase. Falha de rede, teto ou saída ilegível continua indo a `CHECKS_NAO_CONFERIDOS` e é gravada como reprovado (`:10286`).
- Mexer no ambiente de propósito (`GITHUB_ACTIONS=true` e config vazia na linha do `forge-check pr`) não abre caminho novo: a mesma manobra sem `GITHUB_ACTIONS` já caía em `gh auth login`. O hook `parecer` não confere checks por conta própria, só usa o resultado gravado (`hooks/parecer.py:20-21`). Então esse aprovado vale o mesmo que não rodar o `pr`, como já dizia o parecer do `27c4c567`. No Forge, o ruleset do GitHub exige os três pares de `CHECKS_EXIGIDOS_DO_FORGE`.
- Resto do delta. `branch_do_modelo_sem_pr` só lê refs locais com `git rev-parse --verify -q` (sem rede nem `gh`) e só avisa no stderr; o nome é montado com os inteiros da versão e não injeta nada. O `forge-testes` só amplia os planos dirigidos e não tira módulo nenhum: o `hooks/.*` mantém a mesma tupla, agora em `RODAM_OS_HOOKS`.

Gatilhos: controle do Forge (portão de merge e hook `parecer`), integração com o GitHub, `bin/` do fluxo de branches (`R-MAIN`).

## Achados
- A2 (recomendado) bin/forge-check:1509 · projeto sem ruleset nem proteção legível, logo depois do push (lista vazia), o pr aprova; aberto da rodada anterior, sem mudança.
- A3 (recomendado) bin/forge-check:1493 · até 4 chamadas ao gh de 10 s no caminho do pr contra o prazo de 8 s do hook do merge; aberto da rodada anterior, falha fechada.
- A4 (recomendado) bin/forge-fechar:1297 · com --armar num projeto sem checks obrigatórios no destino, nem o passo 1 nem o 4 os conferem e o auto-merge pode mesclar com o CI rodando; aberto da rodada anterior, sem mudança.
- A5 (recomendado) bin/forge-check:10288 · com o PR não lido, o pr sai 0 e imprime aprovado no stdout enquanto grava reprovado para o hook; aberto da rodada anterior, sem mudança.

## Sondas
- S1 · `GH_TOKEN= GITHUB_TOKEN= GH_CONFIG_DIR=<vazio> GITHUB_ACTIONS=true gh pr view x --json number` · espera: texto da marca nova só sem login no Actions · obtido: `gh: To use GitHub CLI in a GitHub Actions workflow, set the GH_TOKEN environment variable.`
- S2 · a mesma linha sem `GITHUB_ACTIONS` · espera: só a marca antiga casa · obtido: `To get started with GitHub CLI, please run:  gh auth login` e `populate the GH_TOKEN environment variable`, que não casa com a marca nova

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes rodados aqui no `cc4934de`: `tests.test_forge_check_pr`, `tests.test_testes_tocados` e `tests.test_ambiente_git` (210 testes, OK). O `tests/catraca.py --base origin/develop` só recusa por `R-CONFORMIDADE`: a mudança em `bin/forge-check` pede o rótulo `afrouxa-regra`, que o PR #653 já tem e que é decisão do dono. CI: o PR #653 ainda não reporta checks no head atual. A suíte inteira fica para esse CI, que o passo 4 do forge-fechar exige verde. Lacuna: faltam no PATH gitleaks, zizmor, actionlint, semgrep e shellcheck. Nenhum workflow mudou.
