---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-hook-heredoc-fp
commit: 58312004dfd8940079d5232a98e1d2936e51e108
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 (E4.4, falso positivo de heredoc no hook de PR)

Head testado `58312004` (base `9b2c6474`). Sem PR aberto: só testes leves e os afetados, local; a bateria completa fica para o CI do PR.

## Achados
- A1 (bloqueante) hooks/parecer.py:172 · `LANCA_PROCESSO` não vê `asyncio.create_subprocess_exec`/`_shell`, `os.posix_spawnp` nem `getattr(os,"sy"+"stem")`: `python3 - <<'EOF'` com `gh pr merge` ou `git pull` real passa (rc 0). A base barrava (rc 2); regressão da rede D, provada abaixo.
- A2 (bloqueante) hooks/parecer.py:202 · Mutante M7 sobreviveu: trocar `len(tipos) == 1` por `tipos` não derruba nenhum teste. Falta fixture de dono com programas de tipos diferentes (python e sh), que deve seguir como antes (None). Sobrevivente bloqueia.
- A3 (recomendado) docs/hooks.md:103 · A doc deveria dizer que a barreira do corpo de Python é uma lista de nomes de lançadores, não fronteira, e listar o que ela não cobre (A1), para o usuário do hook não confiar nela.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E4.4-a: corpo de heredoc lido só por `python3 -` não é conferido como comando de PR | fixtures `heredoc-interpretador-python-*-libera`, `timeout-python*-libera` (test_corpus_heredoc_interpretador_libera_e_bloqueia) | corpo que só cita o comando (docstring, texto, print) | passou |
| E4.4-b: corpo de `sh` que só lê segue conferido, sem ligar a rede D | `heredoc-interpretador-sh-echo-cita-pr-libera`, `dois-sh-sem-pr-no-segundo-libera` | corpo que só lê ou espera | passou |
| E4.4-c: caso verdadeiro (subprocess com comando de PR, `gh pr` rodado pelo sh) segue barrado | `python-subprocess-pr-merge-bloqueia`, `os-system-pull-bloqueia`, `sh-pr-merge-por-numero-bloqueia`, `sh-eval-*`, `bash-merge-executado-bloqueia` | lançador conhecido no corpo | passou |
| E4.4-d: nenhum caminho de execução real passa pela rede D afrouxada para Python | sondas do QA (abaixo) | lançador não listado, ofuscado | FALHOU (A1) |
| Cada mutante por linha de guarda (M1 a M17) | `forge-mutante` das 3 specs | guardas de heredoc/interpretador | 16 morreram, M7 sobreviveu (A2) |

## Cenários e resultado real

Suíte afetada: `python3 -m unittest tests.test_hooks_parecer_pasta` no head: `Ran 4 tests in 34.967s · OK`.

Vermelho antes do verde: `forge-testes --vermelho 9b2c6474…` abriu com `vermelho: base=9b2c6474cc1e head=58312004dfd8`, listou `revertidos à base: changelog.d/…, docs/hooks-fixtures.md, docs/hooks.md, hooks/parecer.py`, mas estourou o prazo da minha janela (`rc=124`, máquina com carga ~11): sem veredito, não vale como vermelho. Prova equivalente, à mão: o teste novo e as 24 fixtures do HEAD sobre a árvore da base (`9b2c6474`), `python3 -m unittest test_hooks_parecer_pasta.PastaDoGit.test_corpus_heredoc_interpretador_libera_e_bloqueia` -> `FAILED (failures=6)` (as fixtures `*-libera`: `dois-sh-sem-pr…`, `python-docstring…`, `python-grava…`, `python-texto…`, `sh-echo-cita…`, `timeout-python…`); no head, passa.

Mutantes: `bin/forge-mutante tests/mutantes/v047-hook-heredoc-fp.json …-2.json …-3.json --processos 3` (rc=1):
```
M1 · morreu · hooks/parecer.py:182
M2 · morreu · hooks/parecer.py:182
M3 · morreu · hooks/parecer.py:185
M4 · morreu · hooks/parecer.py:185
M5 · morreu · hooks/parecer.py:197
M6 · morreu · hooks/parecer.py:197
M7 · sobreviveu · hooks/parecer.py:202
M8 · morreu · hooks/parecer.py:211
M9 · morreu · hooks/parecer.py:214
M10 · morreu · hooks/parecer.py:214
M11 · morreu · hooks/parecer.py:214
M12 · morreu · hooks/parecer.py:932
M13 · morreu · hooks/parecer.py:935
M14 · morreu · hooks/parecer.py:989
M15 · morreu · hooks/parecer.py:1002
M16 · morreu · hooks/parecer.py:1014
M17 · morreu · hooks/parecer.py:215
```
Conferência da lista contra o diff: as condições novas de `parecer.py` (`leitor_da_entrada`, `interprete_do_corpo`, `leitores_dos_corpos`, `marcas_da_chamada`, `conferir_linha`) têm mutante, exceto o `len(tipos) == 1` (coberto por M7, que sobrevive).

Sondas de abuso (A1): fixtures montadas a partir de `heredoc-interpretador-python-subprocess-pr-merge-bloqueia.json`, só o comando trocado, esperado rc 2, rodadas na base (`9b2c6474`) e no head. Corpo, dentro de `python3 - <<'EOF'`:
- `asyncio.run(asyncio.create_subprocess_exec("gh","pr","merge","5"))`
- `asyncio.run(asyncio.create_subprocess_shell("gh pr merge 5"))`
- `os.posix_spawnp("gh",["gh","pr","merge","5"],os.environ)`
- `getattr(os,"sy"+"stem")("gh pr merge 5")`
- `asyncio.run(asyncio.create_subprocess_exec("git","pull"))`

Base: as cinco saem rc 2 (`R-REVIEW: python3 (fora da lista de programas) na chamada com heredoc e gh pr, gh api, merge ou pull…`). Head: as cinco saem rc 0 (`AssertionError: 0 != 2`). Controle `print("gh pr merge 5")`: rc 0 no head, rc 2 na base (a correção pretendida). Causa: `\bspawn`, `\bsubprocess` e `\bexec` não casam depois de `_` (`posix_spawnp`, `create_subprocess_exec`), e a concatenação esconde `system`. Contorno sugerido ao tech-lead: tirar o `\b` inicial dos nomes (`subprocess|spawn|exec` em qualquer posição) e tratar `getattr`/`__dict__`/`globals(` como lançador; a ofuscação por concatenação só se fecha tratando todo corpo de Python com comando de PR como no caso de antes (fronteira que o próprio comentário do código chama de reforço).

Rede de segurança de conferência: A2 e A1 voltam ao autor da stack (`tech-lead`, dono da E4.4); nenhuma outra regressão achada no corpus `heredoc-interpretador-*` (24 fixtures, os dois lados).

## Revalidação
Voltando o autor: rerodar as sondas de A1 (somar três delas como fixtures `*-bloqueia`), a fixture de dono misto de A2 e `forge-mutante` das 3 specs (M7 deve morrer); `forge-check parecer delta docs/qa/v047-hook-heredoc-fp.md` lista o resto.
