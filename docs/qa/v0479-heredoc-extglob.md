---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-heredoc-extglob
commit: 3f94b916db826bc28fe14920abb28bdc2412b52a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-heredoc-extglob (E70.1)

Escopo: `hooks/parecer.py` (`corpos_de_dado`): alvo de redireção de heredoc de dado recusa curinga estendido (`@(`, `+(`, `!(`) e compara o nome sem caixa. Sem suíte local; só o módulo tocado.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E70.1 extglob `bin/@(ls)`, `bin/+(ls)`, `bin/!(cat)` recusam (código 2) | `test_hook_parecer_extglob.test_curinga_estendido_no_alvo_recusa` (3 fixtures `heredoc-dado-alvo-extglob-*`) | curinga estendido no nome do alvo | passou |
| E70.1 `bin/LS` com `ls` na chamada recusa | `test_nome_do_alvo_sem_caixa_recusa` (fixture `heredoc-dado-alvo-caixa-*`) | caixa do nome | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_hook_parecer_extglob.py`: 2 testes, OK.
- Vermelho: `forge-testes --vermelho` não aceita escopo por módulo e roda os 224 módulos (suíte inteira, vetada neste brief); interrompido. Vermelho feito à mão numa cópia em `$TMPDIR` com `hooks/parecer.py` da base `bead3e53`: `Ran 2 tests ... FAILED (failures=4)` (`AssertionError: 0 != 2`, as 4 fixtures passam a liberar).
- Mutação: `bin/forge-mutante tests/mutantes/v0478-hook-extglob-caixa.json`, rev=3f94b916db82: M1..M4 `morreu` (hooks/parecer.py:307), M5 `morreu` (hooks/parecer.py:309). Saída 0.
- `forge-mutante --cobertura --base bead3e53`: linha 307 coberta (M1-M4); a 309 (`casefold`) coberta por M5 na rodada; `tests/pesos-d4.json` "não coberto" (dado, não guarda).
- Mutantes cobrem as duas linhas de guarda mudadas no diff; nenhum sobrevivente.
