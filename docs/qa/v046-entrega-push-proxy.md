---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/entrega-push-proxy
commit: 843e6b752849bf4b62fcf3d41dcc83c22a6f74e5
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-11
---
# QA: v046-entrega-push-proxy (E12.1)

Revalidação (volta 1) do delta a5fec3a0..843e6b75, head 843e6b75. Base 11ba4fa6, head anterior a5fec3a0 (dois commits: fix do `git()` e mapa do `forge-testes`). Leitura numa worktree descartável; nada escrito na branch.

## Achados
- A1 (bloqueante, resolvido em 843e6b75) tests/test_testes_tocados.py:66 · `Mapa.test_forge_check_roda_os_modulos_dele` fixa 68 módulos do forge-check e o head traz 69 (`test_git_rede_config`): falha no head, passa na base. Atualizar o 68 e o comentário (R-QA).

## Critério → teste → resultado
O pedido E12.1 não tem `CA-n` de UX; as obrigações vêm do `## Escopo` do pedido.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E12.1-a: `ls-remote` herda GIT_CONFIG_COUNT/KEY/VALUE | `test_ls_remote_herda_a_configuracao_do_ambiente` | remoto só alcançável por insteadOf do ambiente | passou (vermelho na base) |
| E12.1-a: `fetch` herda | `test_fetch_herda_a_configuracao_do_ambiente` | segundo comando de rede | passou (vermelho na base) |
| E12.1-a: herda GIT_CONFIG_PARAMETERS | `test_ls_remote_herda_git_config_parameters` | forma alternativa do mesmo canal | passou (vermelho na base) |
| E12.1-b: GIT_DIR segue apagado em rede | `test_ls_remote_continua_sem_git_dir` | GIT_DIR inexistente no ambiente | passou (vermelho na base) |
| E12.1-b: GIT_CONFIG_GLOBAL segue apagado | `test_ls_remote_continua_sem_git_config_global` | variável GIT_CONFIG_* que não é do ambiente | passou (verde já na base: guarda de regressão, coberta por M3) |
| E12.1-c: comando local não herda | `test_comando_local_nao_herda_a_configuracao_do_ambiente` | só rede muda | passou (verde na base; guarda de M2) |
| Mapa de `bin/forge-testes` cobre o módulo novo | `test_testes_tocados.Mapa.*` | contagem do mapa | passou em 843e6b75 (contagem 69; A1 fechado) |

## Cenários e resultado real
- Teste novo no head: `python3 -m unittest tests.test_git_rede_config` → `Ran 6 tests ... OK`.
- Vermelho (manual, worktree da base 11ba4fa6 com só o arquivo de teste do head): `Ran 6 tests`, `FAILED (failures=4)`: fetch_herda, ls_remote_continua_sem_git_dir, ls_remote_herda_a_configuracao, ls_remote_herda_git_config_parameters. Os 2 que passam na base são guardas de limite (não provam a correção, por desenho).
- `bin/forge-testes --vermelho 11ba4fa6`: roda a suíte inteira (bin/forge-testes mexido invalida o mapa) e morreu duas vezes sem veredito no sandbox (processo some, log vazio, "fatal library error, lookup self"). Sem veredito, não vale como vermelho; o vermelho acima é o manual.
- Mutantes: `bin/forge-mutante tests/mutantes/v046-entrega-push-proxy.json` rc=0, M1..M6 morreram (linhas 482, 484, 475, 475, 474, 475). `--cobertura --base 11ba4fa6`: linhas 482 e 484 cobertas (M1, M2), "declarado, não provado"; sem condição mudada sem mutante. Nenhum sobrevivente.
- Suíte: o mapa manda suíte completa; ela é do CI do PR (não há check-run `bateria` deste sha ainda: sem PR). Localmente, `tests.test_forge_mutante` 91 OK; `tests.test_testes_tocados` 143 testes, 1 falha (A1).
- Borda lida no diff: o filtro olha `args[0]`; os dois chamadores (`bin/forge-check` 7065 e 9254) passam o subcomando primeiro, então valem. `_git_da_area` e o env da ~9401 seguem fora do escopo (já anotados no pedido).
- Prova de uso: conferência de 19:34 com o bin da branch, registrada no pedido (ls-remote = a5fec3a0); não reexecutada aqui (sandbox sem rede de remoto).
- Acessibilidade e UX: n/a.

## Revalidação a5fec3a0..843e6b75
- Delta: `tests/test_testes_tocados.py:66` 68 -> 69 com comentário; `bin/forge-check:475` regex `\d+` -> `[0-9]+` (sem mudança de comportamento para ASCII; exclui dígitos Unicode); spec de mutantes M3/M4/M6 com o trecho `de` atualizado.
- `tests.test_testes_tocados` 143 testes OK (skipped=1, pré-existente); `Mapa` + `tests.test_git_rede_config` 23 OK; `tests.test_forge_mutante` 91 OK.
- `bin/forge-mutante tests/mutantes/v046-entrega-push-proxy.json`: M1..M6 morreram (482, 484, 475, 475, 474, 475); nenhum sobrevivente; M3/M4/M6 aplicam no trecho novo (o `de` casou).
- `forge-check parecer delta` não rodou (o sha anterior não existe na cópia local do `.forge-contrib`); o delta foi lido no `git diff` da branch.
- A suíte inteira segue sendo do CI do PR (check-run `bateria` do sha 843e6b75 ainda não existe; sem PR).
- Bug v046-e121-mapa-contagem: fechado.
