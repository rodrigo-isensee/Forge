---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-qa-testing-sob-demanda
commit: 2c6b6f8193c1f3c4046cd436bef423193274d079
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 (qa-testing sob demanda, PR #958), volta 1 (delta)

- ci: 2c6b6f8193c1f3c4046cd436bef423193274d079 verde

Delta do 87575570 ao 2c6b6f81 (`forge-check parecer delta`): 2 arquivos de texto, +4 -4. Não toca `hooks/`, `bin/`, `.githooks/` nem `tests/catraca.py`: sem mutante a declarar, sem vermelho-antes-do-verde (nenhum teste novo nem regra de código mudada).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 da 1ª rodada: frase do `--cobertura` literal | `skills/qa-testing/referencia.md:45-47` lido palavra por palavra contra `skills/qa-testing/SKILL.md:91` da develop: "lista a condição Python mudada sem mutante declarado ("declarado, não provado"; shell e outros saem `não coberto: <arquivo>`; as `isentas` da spec, até 8, saem `isenta · arq:L · motivo`, e a que não cruza, `isenta velha`, rc 1)" idêntica; `bin/forge-mutante:715` ("declarado, não provado"), `:717` (`isenta ·`), `:880` (`não coberto:`) e `:895` (rc 1 em `isenta velha`) conferem | texto movido sem mudar palavra | passou, A1 resolvido |
| Ponteiro do oráculo cobre também revisar | `SKILL.md:35` traz "ao escrever o oráculo ou ao revisar um"; a seção "review do oráculo" está em `referencia.md` | gatilho de leitura na SKILL.md | passou |
| Invariantes de `tests/config.json` | padrões de qa na SKILL.md e `agents/qa-engineer.md`: nenhum ausente | n/a | passou |
| Orçamento do qa-engineer | `python3 -m unittest tests.test_orcamento_instrucao`: 8 testes, OK | teto 21480 | passou |
| Catraca e teste de custo (ordem do dono 28/11) | diff sem hook, bin/ nem arquivo protegido; `catraca` e `catraca (conferência)` pass; suíte 1/5 a 5/5 pass | n/a | passou |

## Cenários e resultado real
CI do head: `gh run view 46146179731` com `headSha` igual ao Revisar-sha; verdes: passos, python 3.14, verificações longas, instalação, suíte 1/5 a 5/5, teto de pulados, árvore já provada, catraca, catraca (conferência). `bateria` e `bateria (pareceres)` falham só por esperar os pareceres (excluídos por G3). Suíte não rerrodada. `forge-check docs --base develop`: `docs: ok`, rc=0.
