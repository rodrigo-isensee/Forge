---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0475-merge-checks
commit: d8f33e1b54ef2c19e51a43bd3140c813211819e0
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0475-merge-checks (E3.45, parecer E3.72)

## Achados

## Critério → teste → resultado
O item E3.45 não tem `CA-n`; os critérios saem do texto do item e do fragmento do changelog.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1: PR aberto, fora do rascunho, no head: check pendente, vermelho ou cancelado reprova com a lista | `tests/test_forge_check_pr.py` (23 testes) | bucket fora de pass/skipping; rascunho; outro head; `--previo` | passou |
| C2: exigido ausente ou fora de pass reprova (ruleset, proteção, pares do Forge só no Forge) | `test_forge_check_pr.py` | ausente; resposta de forma inesperada ou 404 não acrescenta | passou |
| C3: `forge-fechar` soma os exigidos do destino sem tirar os pares | `tests/test_forge_fechar.py` (5), mutantes M14 a M17 | ruleset ilegível; curinga `*` | passou |
| C4: mapa do `forge-testes` e tamanho | `test_testes_tocados.py` (162, 1 skip herdado), `test_forge_tamanho.py` (23) | módulo novo no mapa | passou |

## Cenários e resultado real
- Locais com TMPDIR: os quatro módulos acima, todos OK. A suíte inteira roda só no CI do PR; não há PR aberto nem check-run `bateria` deste sha, então não a cito.
- Vermelho antes do verde: não rodei `forge-testes --vermelho`; a prova é por mutação (19 mutantes mortos). Registro como limite.
- Mutação (`bin/forge-mutante`, 3 specs, `--processos 2`): M1 a M19 todos `morreu` (M5 morreu por erro do teste declarado sob o mutante, que passa sem ele).
- Cobertura (`--cobertura --base 3d8ad440`): toda condição Python mudada em bin/forge-check tem mutante; `spec editada · i4-checks-exigidos.json`; `não coberto: bin/forge-fechar` (shell; M14 a M17 cobrem à mão as linhas 522, 536, 537 e 1275).
- Sondei à mão a leitura que falha (gh ausente, `contexts` nulo): cai nos `except` sem erro.

## Bugs

## Revalidação (delta 9f497b0f..27c4c567)
- A1 anterior (falha do `gh pr view` aprovava calada) corrigido em `bin/forge-check`: `gh_json` devolve o motivo, `checks_do_head` avisa, soma a `CHECKS_NAO_CONFERIDOS` e o `main` grava reprovado para o hook; `GH_SEM_PR` mantém sem PR, sem remoto e sem login como passagem; `forge-fechar` passo 1 põe `FORGE_FECHAR_PASSO_1=1`.
- Testes locais com TMPDIR: `test_fechar_forge_check_real` 5 OK, `test_forge_check_pr` 28 OK, `test_forge_tamanho` 24 OK, `test_testes_tocados` 162 OK (1 skip herdado). Suíte inteira: só no CI do PR (não cito check-run `bateria` deste sha).
- `forge-mutante --processos 2 --base 9f497b0f` (specs -4 e -5): `base=9f497b0f... mb=9f497b0f...`; M20 a M30 todos `morreu` (forge-check 1457, 1492, 1493, 1539, 10245, 10246, 10254, 10255, 10257; forge-fechar 1222).
- `--cobertura --base 9db0705e`: toda condição Python mudada coberta; `não coberto: bin/forge-fechar` (shell; M28 cobre a linha 1222 à mão); specs editadas só realinhadas por linha.
- `tests/catraca.py --base origin/develop`: só a exigência `afrouxa-regra` do dono (R-CONFORMIDADE, mudança em `bin/forge-check`); nenhuma guarda sem mutante.
- Vermelho antes do verde: prova por mutação (11 mutantes novos mortos), não `forge-testes --vermelho`; limite registrado.

## Revalidação (delta 27c4c567..cc4934de, E3.185)
- Delta no domínio: `bin/forge-check` (`GH_SEM_PR` ganha "set the GH_TOKEN environment variable", o gh do GitHub Actions sem token), `bin/forge-testes`, `tests/test_forge_check_pr.py`, `tests/test_pr_hook_prazo.py`, `tests/test_testes_tocados.py`, spec `-5` (M31).
- Local com TMPDIR: `test_pr_hook_prazo` 18 OK; de novo com `env -u GH_TOKEN -u GITHUB_TOKEN GITHUB_ACTIONS=true GH_CONFIG_DIR=<pasta vazia>`: 18 OK; `test_forge_check_pr` 28 OK; `test_testes_tocados` + `test_ambiente_git` 182 OK (1 skip herdado). Suíte inteira: só no CI do PR (não cito `bateria` deste sha).
- `forge-mutante tests/mutantes/v0474-merge-checks-5.json --base 27c4c567`: `base=27c4c567... mb=27c4c567... rev=cc4934de...`; M28, M29, M30, M31 todos `morreu` (M31 em forge-check:1445), rc 0.
- `tests/catraca.py --base origin/develop`: só a exigência `afrouxa-regra` do dono (R-CONFORMIDADE, mudança em `bin/forge-check`); nenhuma guarda sem mutante.
- Vermelho antes do verde: prova por mutação (M31 morto); não rodei `forge-testes --vermelho`; limite registrado.

## Revalidação (delta cc4934de..d8f33e1b, merge da develop, E3.219)
- Delta: só o merge da `origin/develop` (791d94e8) com a contagem 97 em `tests/test_testes_tocados.py` (+ `test_forge_check_pr`, desta branch, sobre os 96 da develop). As linhas de `bin/forge-check` e `tests/test_forge_tamanho.py` que o `forge-check parecer delta` lista vêm da develop (E3.48); `git diff 791d94e8...HEAD` não toca `ROTULO_DO_DESTINO`.
- Local com TMPDIR: `test_testes_tocados` 162 OK (1 skip herdado), `test_pr_hook_prazo` 18 OK, `test_forge_tamanho` 24 OK, `test_ambiente_git` 20 OK. Suíte inteira só no CI do PR.
- `tests/catraca.py --base origin/develop`: rc 1 só pela exigência `afrouxa-regra` do dono (R-CONFORMIDADE, `bin/forge-check`); nenhuma guarda sem mutante. Sem guarda nova no delta, sem mutante novo.
- Vermelho antes do verde: sem teste novo no delta; n/a.
