---
tipo: qa
contrato: 1
pedido: guarda-sem-mutante-2
branch: melhoria/guarda-sem-mutante-2
commit: 43a8cc83559f3e49abffa08447b4bfaf4a04ae6c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: guarda-sem-mutante-2 (PR 2: shell, isentas, tetos de T7, A5 e o PQ no gerar_volta)

Base `ff3936ae4011a95f25c37280fe32e4fa5ced0d95`, head `43a8cc83559f3e49abffa08447b4bfaf4a04ae6c`. Controle do Forge (`bin/`): a conferência de mutantes vale. Em paralelo com o review e a segurança.

## Achados

Nenhum bloqueante. Recomendações (não devolvem; ficam no parecer, sem linha de achado): `until` e `case` não entram na lista de condições do shell (a lista da spec é if, elif, while, `[[ ]]`, `[ ]`, `test`, `&&`, `||`); `until cmd` sem colchetes muda sem cobrança.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Shell coberto (if, elif, while, `[ ]`, `[[ ]]`, test, `&&`, `||`) | sonda em repositório descartável + `Cobertura` | condição shell mudada sem mutante: rc 1; com mutante: rc 0 | passou (rc 1 com 3 `sem mutante`; rc 0 com 3 `coberta`) |
| `\|\| true` e `\|\| :` não contam | `Cobertura` (M52 a M55 da spec -8) | lado direito só `true` ou `:` | passou |
| Isenta válida libera sem mutante ou apagada (rc 0) | sonda: `isentas` com trecho exato e motivo de 20+ | condição shell isenta e condição Python apagada isenta | passou (`isenta · ...`, rc 0) |
| Isenta que não cruza condição, ou condição já coberta (rc 2) | sonda | trecho que não casa uma vez | passou (rc 2) |
| Isenta inválida (motivo curto, trecho curto) (rc 2) | sonda + `validar_isentas` (M48 a M51) | motivo de 19 ou menos, trecho de menos de 8 não brancos | passou (rc 2, "spec inválida") |
| Mais de 8 isentas somadas, diff acima de 4 MiB, 5000 condições (tetos de T7) | spec -8, -9, -11 (M48, M52, M73, M74) | limite e logo acima | passou (mutantes morrem) |
| A5: editada pareada pela posição do nó no hunk | sonda Python + specs -9 e -10 | editada coberta pela nova; sem nome ou número em comum fica `apagada` | passou |
| Condição apagada (rc 1) | sonda: `if x > 10 and x < 100` removido | apagada sem substituta | passou (`apagada`, rc 1) |
| Base inválida e diff vazio (rc 2) | sonda: `--base deadbeef`, `--base HEAD` | entrada inválida | passou (rc 2 nos dois) |
| PQ do `--cobertura` no brief de volta | `tests.test_volta_por_delta` (linhas 666 e 750) e leitura de `gerar_volta` | numeração `PQ-N` depois do PQ de merge | passou (`bin/forge-check:1433`, PQ-5 e PQ-6 nos testes) |
| Documentação: shell e isentas na skill | `skills/qa-testing/SKILL.md:88` | n/a | passou (texto atualizado) |

## Execução (real)
- `bin/forge-mutante tests/mutantes/guarda-sem-mutante*.json` (11 specs, M1 a M74): rc 0, 74 `morreu`, 0 sobrevivente, 0 inválido.
- `bin/forge-mutante --cobertura --base ff3936ae4011a95f25c37280fe32e4fa5ced0d95` sobre o próprio diff: rc 0, 22 `coberta ... declarado, não provado`, nenhuma `sem mutante`, nenhuma `apagada`. A linha de `bin/forge-check` (a nova `pronto.append`) não é condição; as specs editadas (-3, -5, -6, -7 e a base) aparecem como `spec editada` e as mutações antigas (M8, M22, M33, M37, M46, M47) seguem casando e morrendo no head. Conferi a lista contra o diff: cada condição mudada em `bin/forge-mutante` tem mutante.
- `python3 -m unittest tests.test_forge_mutante tests.test_volta_por_delta`: 124 testes, OK (55 s). A suíte completa fica com o pre-push.
- Vermelho: `forge-testes --vermelho ff3936a` estourou o prazo de 580 s (rc 124, sem veredito, não vale como vermelho; a suíte completa não cabe nesta rodada). Prova alvo no lugar: cópia do HEAD em `$TMPDIR` com `bin/forge-mutante` e `bin/forge-check` da base, módulos `test_forge_mutante` e `test_volta_por_delta`: `FAILED (failures=20, errors=12)`, 124 rodados; no HEAD, 0 falhas. O vermelho oficial do `forge-testes --vermelho` fica com o autor e o CI.
- Acessibilidade e E2E: n/a (ferramenta de linha de comando).

## Casos de abuso e riscos aceitos
A3 e A4 da segurança do PR 1 ficam como risco aceito (decisão técnica 2026-10-28 10:25). Sem gatilho novo no PR 2: a checagem lê `git show` e só faz `ast.parse` e regex, nada do diff é executado.
