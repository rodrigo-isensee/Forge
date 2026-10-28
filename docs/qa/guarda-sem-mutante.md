---
tipo: qa
contrato: 1
pedido: guarda-sem-mutante
branch: melhoria/guarda-sem-mutante
commit: 65a62c9677469556e2939392b61d3097682341cd
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: guarda-sem-mutante (PR 1, `forge-mutante --cobertura`), revalidação

Base `991cd092b42c88d86a16912ff8ddc1b72b8da026`, head `65a62c9677469556e2939392b61d3097682341cd` (delta `7c86f53..65a62c9`). Controle do Forge (`bin/`): a conferência de mutantes vale. Revalida o parecer anterior (reprovado em `6a23ddc`, A1 e A2).

## Achados
(nenhum)

A1 e A2 do parecer anterior estão resolvidos (evidência abaixo); nenhum achado novo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PQ-1: reprova diff com condição mudada sem mutante | `tests.test_forge_mutante.Cobertura` + sonda | condição nova sem mutante: rc 1 | passou |
| PQ-1: aprova com mutante (A2) | sonda: condição editada `x > 10 and y` para `x > 11 and y or x == 3`, spec com `de` de 8+ caracteres | edição de condição existente coberta: rc 0 | passou (`coberta`, rc 0) |
| Condição apagada conta (T3) | sonda: condição removida sem troca | removida sem substituta: rc 1 | passou (`apagada`, rc 1) |
| Base inválida, diff vazio, `--base HEAD` (T4) | `Cobertura` | merge-base igual ao rev: rc 2 | passou |
| Mutantes declarados provam as guardas do diff (A1) | `forge-mutante` das 7 specs, M1 a M47 | specs sem `de` velho | passou (47 mortos, 0 inválido, 0 sobrevivente) |
| Guardas do delta (binário/não UTF-8, hunk escondido por atributo, `\r` solto, edição) | `forge-mutante --cobertura --base 991cd09` | toda linha de guarda mudada tem mutante | passou (28 `coberta`, 0 `sem mutante`, 0 `apagada`) |
| PQ-2 (brief de volta) | n/a no PR 1 (é o PR 2) | n/a | fora do escopo |

## Execução (real)
- `python3 -m unittest tests.test_testes_tocados tests.test_forge tests.test_forge_mutante`: 570 testes, OK, rc 0 (107 s).
- `bin/forge-mutante tests/mutantes/guarda-sem-mutante*.json` (7 specs): rc 0, 47 `morreu`, 0 `inválido`, 0 sobrevivente. A1 resolvido: M1, M19, M20, M22 e o limite de 1 MiB (M46, M47 e vizinhos) morrem no head.
- `bin/forge-mutante --cobertura --base 991cd092b42c88d86a16912ff8ddc1b72b8da026`: rc 0, 28 `coberta ... declarado, não provado`, nenhuma `sem mutante`/`apagada`. Conferi o diff `7c86f53..65a62c9` contra a lista: cada linha de guarda mudada na volta 2 tem mutante declarado (a própria checagem confirma e as 7 specs matam todos).
- Sonda A2 (clone em `$TMPDIR`, `bin/exemplo2.py`): editada e coberta = `coberta`, rc 0; removida sem troca = `apagada`, rc 1; sem spec = `sem mutante`, rc 1.
- Vermelho: a prova alvo do parecer anterior (`bin/forge-mutante` da base com os testes do head: `FAILED`, 24 falhas e erros por `unrecognized arguments: --cobertura --base`) segue valendo para o PR; os testes do delta cobrem a edição, o binário e o `\r`, e caem pelos mutantes M40 a M47. `forge-testes --vermelho` oficial fica com o autor e o CI (a suíte completa não roda fora do pre-push).
- Acessibilidade e E2E: n/a (ferramenta de linha de comando).

## Observação (não bloqueia)
O `de` de um mutante precisa ter 8+ caracteres não brancos para cobrir a condição (regra do `--cobertura`); sonda com `de` curto sai `sem mutante`, comportamento previsto na documentação do módulo.
