---
tipo: qa
contrato: 1
pedido: guarda-sem-mutante
branch: melhoria/guarda-sem-mutante
commit: 7c86f530cb491355a40f2699215ebd45f3d2c5d4
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: guarda-sem-mutante (PR 1, `forge-mutante --cobertura`)

Base `991cd092b42c88d86a16912ff8ddc1b72b8da026`, head `7c86f530cb491355a40f2699215ebd45f3d2c5d4`. Controle do Forge (`bin/`): a conferência de mutantes vale.

## Achados
- A1 (bloqueante) tests/mutantes/guarda-sem-mutante.json:6 · defeito provado, classe spec de mutante velha depois da volta 1: M1 (este arquivo), M19 e M20 e M22 (`guarda-sem-mutante-3.json:26,36,56`) têm `de` que não existe mais no `bin/forge-mutante` do head (a volta 1 mudou `ler_no_commit`, `if status == "D" or TESTE`, `or TESTE.fullmatch` e `if not eh_python(arquivo, depois)`); a rodada das 6 specs sai rc 2 com 4 `inválido`, não "M1 a M39 mortos"; o limite de 1 MiB (`len(r.stdout) > maximo`) fica sem mutante que o prove
- A2 (bloqueante) bin/forge-mutante:382 · requisito PQ-1 ("aprova com mutante") provado: condição editada (não nova) sai também como `apagada · arq:L(base)` e a saída é rc 1 mesmo com mutante que a cobre; no PR 1 não há `isentas`, então a edição de condição existente nunca chega a rc 0 (sonda abaixo); o próprio PR só passa porque o diff dele só adiciona condições

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PQ-1: reprova diff com condição mudada sem mutante | sonda manual (cópia em `$TMPDIR`) + `tests.test_forge_mutante.Cobertura` | condição nova sem mutante: rc 1 | passou |
| PQ-1: aprova com mutante | sonda manual: condição editada e coberta | edição de condição existente | FALHOU (rc 1 por `apagada`, A2) |
| Condição apagada conta (T3) | sonda manual | texto a menos que no merge-base | passou (rc 1) |
| Base inválida, diff vazio, `--base HEAD` (T4) | sonda manual + `Cobertura` | merge-base igual ao rev | passou (rc 2) |
| Mutante equivalente (`para` igual ao `de`) | sonda manual | spec inválida | passou (rc 2) |
| Mutantes declarados provam as guardas do diff | `forge-mutante` das 6 specs | 39 mutantes | FALHOU em 4 (A1) |
| PQ-2 (brief de volta) | n/a no PR 1 (E2.1 é o PR 2) | n/a | fora do escopo deste PR |

## Execução (real)
- `python3 -m unittest tests.test_testes_tocados tests.test_forge tests.test_forge_mutante`: 567 testes, OK (200 s).
- Vermelho: `forge-testes --vermelho 991cd09` estourou meu prazo de 550 s (rc 124, sem veredito; a suíte completa não roda fora do pre-push). Prova alvo no lugar: `bin/forge-mutante` da base com os testes do head, em cópia: `tests.test_forge_mutante` = 51 testes, `FAILED (failures=11, errors=13)` (`unrecognized arguments: --cobertura --base`); com o head, OK. A prova oficial do `--vermelho` fica com o autor/CI.
- `bin/forge-mutante --cobertura --base 991cd09`: rc 0, 25 condições `coberta ... declarado, não provado`, nenhuma `sem mutante`/`apagada`; primeira linha `base=991cd092... mb=991cd092... rev=7c86f530...`. Conferi cada linha de guarda mudada: todas têm ao menos um mutante declarado (M2 a M38), mas ver A1.
- `bin/forge-mutante` das 6 specs (M1 a M39): rc 2; M2-M18, M21, M23-M39 `morreu` (35); M1, M19, M20, M22 `inválido · o trecho aparece 0 vezes`. Nenhum sobrevivente.
- Sonda (clone em `$TMPDIR`, `bin/exemplo` com `if x > 10 and y`): mudada para `x > 11 and y or x == 3` sem spec = `sem mutante` + `apagada` rc 1; com spec de 2 mutantes = `coberta` + `apagada` rc 1 (A2); `para` igual ao `de` = rc 2; `--base HEAD` = rc 2.
- Acessibilidade e E2E: n/a (ferramenta de linha de comando).

## Para o autor
Corrigir A1 (atualizar os 4 `de` para o texto do head e rodar as 6 specs até rc 0) e A2 (edição de condição não pode ser `apagada` sem saída; ou o PR 1 traz a isenção/pareamento por linha, ou o pedido registra a decisão de que a edição só passa no PR 2 e o dono aceita). Responsável sugerido: `tech-lead`.
