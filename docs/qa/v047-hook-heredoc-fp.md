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

Revalidação E4.14 por delta `58312004..0eee1453` (volta E4.11), sobre o parecer de E4.10 (reprovado no head `58312004`, A1 e A2 bloqueantes, A3 recomendado; base `9b2c6474`). Sem PR aberto: só testes leves e os afetados, local; a bateria completa fica para o CI do PR.

## Achados
- A1 (recomendado) hooks/parecer.py:176 · Aceito e documentado (docs/hooks.md:103, ADR 0011 emenda v047), não bloqueia: corpo de Python com lançador e comando sem constante de texto que o traga (chr, base64, f-string, reverso, rot13, "g"+"h" em item de lista, arquivo) passa rc 0; a base barrava.

Resolvidos da volta anterior: A1 bloqueante (as cinco sondas agora rc 2, fixtures `*-bloqueia` somadas), A2 bloqueante (M7 morre; fixture `dono-misto-python-e-sh-bloqueia`) e A3 (doc e ADR dizem que a barreira é lista de nomes e o que não cobre).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E4.4-a: corpo de heredoc lido só por `python3 -` não é conferido como comando de PR | fixtures `heredoc-interpretador-python-*-libera`, `timeout-python*-libera` | corpo que só cita o comando (docstring, texto, print) | passou |
| E4.4-b: corpo de `sh` que só lê segue conferido, sem ligar a rede D | `sh-echo-cita-pr-libera`, `dois-sh-sem-pr-no-segundo-libera` | corpo que só lê ou espera | passou |
| E4.4-c: caso verdadeiro (subprocess, `gh pr` pelo sh) segue barrado | `python-subprocess-pr-merge-bloqueia`, `os-system-pull-bloqueia`, `sh-*-bloqueia` | lançador conhecido no corpo | passou |
| E4.4-d: nenhum caminho real afrouxado (lançador depois de `_`, `getattr`) | sondas S1 a S5 e fixtures `asyncio-*`, `posix-spawnp`, `getattr-nome-montado` | lançador não listado | passou |
| E4.4-e: dono misto python e sh fica como antes | `dono-misto-python-e-sh-bloqueia`, M7 | tipos diferentes | passou |
| E4.4-f: `PATH=`, `env -S PATH`, PATH solto e `git` na chamada voltam à regra de antes | `env-s-path`, `path-solto`, `grava-fsmonitor-e-git`, M18 a M20, M24 | atribuição, git | passou |
| E4.4-g: corpo ilegível ao `ast` e lista em duas linhas seguem conferidos | `python-ilegivel`, `lista-em-duas-linhas`, `concatenacao` | falha fechado | passou |
| Mutantes por linha de guarda | `forge-mutante` das 4 specs | guardas de heredoc e do `ast` | 25 morreram |

## Cenários e resultado real

Suíte afetada: `python3 -m unittest tests.test_hooks_parecer_pasta` no head: `Ran 4 tests in 51.888s · OK` (36 fixtures `heredoc-interpretador-*`, mínimo do teste 36).

Mutantes: `bin/forge-mutante tests/mutantes/v047-hook-heredoc-fp{,-2,-3,-4}.json --processos 3`: M1 a M4 e M6 a M26, todos `morreu`, nenhum sobrevivente (M7 agora morre). `--cobertura --base 9b2c6474`: toda condição mudada `coberta`, nenhuma `não coberta` nem `só equivalente`.

Vermelho antes do verde: `forge-testes --vermelho` não rodado nesta janela (carga ~21 em 12 CPUs), sem veredito. A prova vale pelas sondas, que falhavam em `58312004`, e pela mutação de cada guarda nova.

## Sondas
- S1 asyncio.create_subprocess_exec gh pr merge · espera: rc 2 · obtido: rc 2 (antes, em 58312004: rc 0)
- S2 asyncio.create_subprocess_shell gh pr merge · espera: rc 2 · obtido: rc 2 (antes: rc 0)
- S3 os.posix_spawnp gh pr merge · espera: rc 2 · obtido: rc 2 (antes: rc 0)
- S4 getattr(os,"sy"+"stem") gh pr merge · espera: rc 2 · obtido: rc 2 (antes: rc 0)
- S5 asyncio.create_subprocess_exec git pull · espera: rc 2 · obtido: rc 2 (antes: rc 0)
- X bytes.decode, join, sys.modules, __import__ montado, __dict__, from os import system, gh api, pty.spawn, os.execvp, Popen importado · espera: rc 2 · obtido: rc 2 em todos
- X chr, base64, f-string, reverso, rot13, "g"+"h", "p"+"r" em itens, arquivo, lançador mais docstring · espera: rc 2 (como a base) · obtido: rc 0 (A1 recomendado, limitação documentada)
- C print("gh pr merge 5") e docstring · espera: rc 0 (a correção) · obtido: rc 0

## Revalidação
`forge-check parecer delta docs/qa/v047-hook-heredoc-fp.md` lista o resto do delta; a UX não mudou.
