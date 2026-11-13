---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-hook-heredoc-fp
commit: 0eee14533b579e8a7117666faad15f421fe4b17b
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
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


---

# Revalidação E4.14 (delta 58312004..0eee1453, volta E4.11)

Head `0eee14533b57`. Sem PR: só testes leves e os afetados, local; a bateria completa fica para o CI do PR. Parecer: **aprovado**.

## Achados
- A1 (resolvido) A1 do parecer anterior: as cinco sondas (asyncio exec e shell, `posix_spawnp`, `getattr(os,"sy"+"stem")`, `asyncio` com `git pull`) saem rc 2 no head; fixtures `*-bloqueia` somadas.
- A2 (resolvido) M7 morre; fixture `dono-misto-python-e-sh-bloqueia` somada.
- A3 (resolvido) docs/hooks.md:103 diz que a barreira é lista de nomes e o que não cobre; emenda v047 na ADR 0011.
- A4 (recomendado) hooks/parecer.py:176 · Aceito e documentado, não bloqueia: corpo de Python com lançador e comando montado sem constante de texto que o traga (`chr`, base64, f-string com variável, `[::-1]`, rot13, `"g"+"h"` em item da lista, comando lido de arquivo) passa rc 0; a base barrava (rc 2). A doc e a ADR assumem a limitação.

## Revalidação por critério
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E4.4-d: nenhum caminho real afrouxado | sondas S1-S5 rerodadas (abaixo) + fixtures novas | lançador depois de `_`, `getattr` | passou |
| E4.4-e: dono misto (python e sh) fica como antes | `heredoc-interpretador-dono-misto-python-e-sh-bloqueia`, M7 | tipos diferentes | passou |
| E4.4-f: `PATH=`, `env -S PATH`, PATH solto e `git` na chamada voltam à regra de antes | fixtures `env-s-path`, `path-solto`, `grava-fsmonitor-e-git`, M18-M20, M24 | atribuição, git | passou |
| E4.4-g: corpo ilegível ao `ast` e lista em duas linhas seguem conferidos (falha fechado) | `python-ilegivel`, `lista-em-duas-linhas`, `concatenacao` | `ast`, constantes | passou |

## Sondas
Corpo em `python3 - <<'EOF'` e o hook direto, esperado rc 2. Head: S1 `create_subprocess_exec` rc 2; S2 `create_subprocess_shell` rc 2; S3 `posix_spawnp` rc 2; S4 `getattr` com concatenação rc 2; S5 `create_subprocess_exec` com `git pull` rc 2 (antes, em 58312004, rc 0). Extras com lançador visível e comando em texto: `bytes.decode`, `" ".join`, `sys.modules`, `__import__` montado, `__dict__`, `from os import system as s`, `gh api`, `pty.spawn`, `os.execvp`, `Popen` importado: todos rc 2. Controles `print("gh pr merge 5")` e docstring: rc 0 (a correção pretendida). Passam em rc 0 (A4, recomendado): `chr`, base64, f-string, reverso, rot13, `"g"+"h"` em item da lista, `"p"+"r"`, arquivo, e lançador mais docstring que cita o comando.

## Provas
- `python3 -m unittest tests.test_hooks_parecer_pasta`: `Ran 4 tests in 51.888s · OK` (36 fixtures `heredoc-interpretador-*`, mínimo do teste 36).
- `bin/forge-mutante` das 4 specs, `--processos 3`: M1-M4 e M6-M26 todos `morreu` (25 mutantes; M7 agora morre), nenhum sobrevivente.
- `forge-mutante --cobertura --base 9b2c6474`: toda condição mudada `coberta`, nenhuma `não coberta` ou `só equivalente`.
- Vermelho antes do verde: `forge-testes --vermelho` não rodado nesta janela (carga ~21 em 12 CPUs); sem veredito, não vale. A prova de mutação cobre cada guarda nova e as sondas S1-S5 falhavam em 58312004.
