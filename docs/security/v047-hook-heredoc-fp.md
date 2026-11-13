---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-heredoc-fp
commit: 0eee14533b579e8a7117666faad15f421fe4b17b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047, E4.13 (revalidação por delta da volta E4.11 do heredoc no hook `parecer`)

Head revisado: `0eee1453` (delta `58312004..0eee1453`, volta E4.11; base do pedido `9b2c6474`). Parecer anterior (E4.9, head `58312004`): aprovado com A1 a A4 recomendados. Escopo do delta: `hooks/parecer.py` (`LANCA_PROCESSO`, `comando_de_pr_no_python`, `chamada_muda_o_corpo`, `interprete_do_corpo`, `leitores_dos_corpos` e o uso em `conferir_linha`), `docs/hooks.md:103`, a emenda v047 na ADR 0011 (linha 44), o fragmento do changelog, as 12 fixtures novas `tests/hooks/parecer/heredoc-interpretador-*` (36 no total) e os mutantes `tests/mutantes/v047-hook-heredoc-fp*.json` (25).

**Veredito: aprovado, com uma recomendação nova (A5).** Os quatro achados anteriores estão resolvidos, provado pelas sondas refeitas no head (tabela abaixo):
- **A1 resolvido:** `LANCA_PROCESSO` (`hooks/parecer.py:176`) usa `(?<![A-Za-z0-9])` e pega `create_subprocess_shell`/`_exec`, `posix_spawnp`, `getattr`, `globals`, `vars`, `__import__`, `__dict__`, `modules`, `builtins`, `compile`; o comando de PR é procurado nas constantes de texto do corpo pelo `ast` (`comando_de_pr_no_python`, linha 181), menos as expressões soltas (docstring), o que pega a lista montada em várias linhas, a concatenação, a f-string e o `bytes`. Corpo que o `ast` não lê conta como tendo o comando (linha 189: falha fechado; sonda da sintaxe inválida).
- **A2 resolvido:** `chamada_muda_o_corpo` (linha 194) devolve a regra de antes para todos os corpos quando a chamada tem atribuição solta (`PATH=<pasta>;` na mesma linha ou na de cima).
- **A3 resolvido:** a mesma função devolve a regra de antes quando a chamada tem `git` fora dos corpos (também `g''it`, pelo valor da palavra).
- **A4 resolvido:** emenda v047 na ADR 0011 (linha 44) com o que sai da opção D, o motivo (equivalência ao `python3 -c`, N-HOOK1), os limites, "Afrouxa; rótulo `afrouxa-regra`" e o critério de reversão.

As fixtures pedidas existem e rodam: as 5 sondas do QA (asyncio exec com `git pull` e com `gh pr merge`, asyncio shell, `posix_spawnp`, `getattr` com nome montado), o M7 (`dono-misto-python-e-sh-bloqueia`), o `PATH=` (`path-solto-python-bloqueia`, `env-s-path-python-bloqueia`), mais concatenação, lista em duas linhas, `fsmonitor` com `git` e corpo ilegível. Os 25 mutantes morrem.

## Gatilhos
`R-SEGURANCA`: mudança em controle do Forge (hook PreToolUse que guarda `gh pr`, merge e pull), com afrouxamento de regra de ADR (emenda v047 da ADR 0011).

## Achados
- A5 (recomendado) hooks/parecer.py:176 · lançador que acha a função pelo nome em texto fora da lista passa no head (a base barrava): operator.methodcaller e operator.attrgetter com 'sys'+'tem', inspect.getmembers; equivale ao python3 -c que a base libera e a doc declara a lista como não fronteira

## Sondas

## Detalhe dos achados
Sondas refeitas pela máquina das fixtures (`Fixture.montar` e `rodar` de `tests/test_hooks.py`, hook `parecer`, repositório temporário sem a branch `feat/x`), com o mesmo texto na base `9b2c6474`, no head anterior `58312004` e no head `0eee1453`; `MRG` é `merge`. Código 2 com "branch `feat/x` não existe" ou "python3 (fora da lista de programas)" quer dizer que o corpo foi conferido; 0, que passou.

| Entrada (resumo) | base | 58312004 | 0eee1453 |
|---|---|---|---|
| `python3 -c 'import os; os.system("gh pr MRG feat/x")'` | 0 | 0 | 0 |
| `python3 - <<'EOF'` + `subprocess.run(["gh","pr","MRG",…])` | 2 | 2 | 2 |
| … + `subprocess.run("gh " + "pr MRG feat/x", shell=True)` (A1) | 2 | 0 | 2 |
| … + lista montada (`c=["gh","pr"]; c+=["MRG",…]; s.run(c)`) (A1) | 2 | 0 | 2 |
| … + `asyncio.create_subprocess_shell("gh pr MRG feat/x")` (A1) | 2 | 0 | 2 |
| … + `os.posix_spawnp("gh",[…"MRG"…],…)` (A1) | 2 | 0 | 2 |
| … + `getattr(os,"sys"+"tem")("gh pr MRG feat/x")` (A1) | 2 | 0 | 2 |
| … + `os.system("git pull origin develop")`, `os.execvp`, `exec("…os.system…")`, f-string, `b"…".decode()` | 2 | 2 | 2 |
| … + `os.system("gh pr MRG feat/x"` (sintaxe inválida, falha fechado) | 2 | 2 | 2 |
| `PATH=/tmp/evil:/usr/bin:/bin; python3 -c 'gh pr MRG feat/x'` | 0 | 0 | 0 |
| `PATH=/tmp/evil:…; python3 - <<'EOF'`⏎`gh pr MRG feat/x`⏎`EOF`, na mesma linha e na de cima (A2) | 2 | 0 | 2 |
| `export PATH=…`, `hash -p /bin/sh python3`, função `python3() { sh; }` antes | 2 | 2 | 2 |
| `python3 -c "open('.git/config','a').write('…fsmonitor = gh pr MRG…')"`⏎`git status` | 0 | 0 | 0 |
| o mesmo com `python3 - <<'EOF'` + `git status`, + `g''it status`, e gancho `pre-commit` + `git commit` (A3) | 2 | 0 | 2 |
| o mesmo + `env -S 'git status'` | 2 | 2 | 2 |
| `python3 - <<'EOF' \| sh`; `python3 - <<'EOF' > x.sh` + `sh x.sh`; Python grava `x.sh` + `sh x.sh` | 2 | 2 | 2 |
| `python3 - <<EOF` com `$(gh pr MRG …)`; corpo com CRLF | 2 | 2 | 2 |
| `python3 - <<'EOF'`⏎`print(1)`⏎`EOF` seguido de `gh pr MRG`, `sh -c '…'` ou `eval '…'` | 2 | 2 | 2 |
| docstring `"""Mescla com gh pr MRG 12."""`; `print("gh pr MRG 12")`; `> saida.txt` (legítimos) | 2 | 0 | 0 |
| Python grava `Makefile` com `gh pr MRG` + `make a` (heredoc e `-c`) | 0 | 0 | 0 |
| … + `operator.methodcaller("sys"+"tem","gh pr MRG feat/x")(os)` (A5) | 2 | 0 | 0 |
| … + `operator.attrgetter("sys"+"tem")(os)("gh pr MRG feat/x")` (A5) | 2 | 0 | 0 |
| … + `inspect.getmembers(os)` filtrado por `"sys"+"tem"` (A5) | 2 | 0 | 0 |
| … + `operator.methodcaller(codecs.decode('flfgrz','rot13'),…)(os)` (A5) | 2 | 0 | 0 |

Execução real do caminho do A5, com um `gh` registrador no PATH e `pr list` no lugar de `pr merge`: `python3 - <<'EOF'`⏎`import operator, os`⏎`operator.methodcaller("sys" + "tem", "gh pr list feat/x")(os)`⏎`EOF` grava `gh-rodou: pr list feat/x`.

**A5, caminho de ataque:** o agente da sessão, deliberadamente, quer mesclar sem parecer e esconde o nome do lançador atrás de `operator` ou `inspect`. **Por que recomendado:** a mesma entrada com `python3 -c` passa na base (primeira linha da tabela), fora da regra pela ADR 0011 (N-HOOK1); o critério de reversão da emenda (linha 44) não é atingido, porque o `-c` equivalente roda o mesmo comando; e `docs/hooks.md:103` declara que a barreira é lista de nomes e não cobre o lançador fora dela. O uso por engano não forma esse texto. Severidade: baixa. É a dimensão "lançador por nome em texto" da matriz do analisador, que a volta cobriu com `getattr`, `globals`, `vars`, `__dict__` e `modules`, mas não com os afins da biblioteca padrão.
**A5, correção mínima** (P, `tech-lead`): acrescentar a `LANCA_PROCESSO` os nomes `attrgetter`, `methodcaller` e `getmembers` (o `__getattribute__` já casa por `getattr`), com uma fixture `heredoc-interpretador-python-methodcaller-bloqueia`; ou, sem mudar o código, citar `operator` e `inspect` entre os exemplos do que a lista não cobre em `docs/hooks.md:103`.

**Observação (sem achado):** a lista nova casa por prefixo sem fronteira à direita (`system` em `systematic`, `exec` em `execute`, `modules`, `compile`), o que só torna o corpo de Python com marcador crítico mais recusado: falha fechado, custo de falso positivo pequeno (precisa também do marcador nas constantes de texto).

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. Suíte: sem PR aberto para a branch (brief: não abrir), sem CI a citar; carga da máquina ~13,5 em 12 CPUs. Rodados só o teste afetado, `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_heredoc_interpretador_libera_e_bloqueia` (OK, 1 teste, 36 fixtures), os mutantes `bin/forge-mutante tests/mutantes/v047-hook-heredoc-fp*.json` (25 de 25 morreram, rev `0eee14533b57`) e as sondas acima. A suíte inteira fica para o CI do PR. Ferramentas: só leitura do código e o próprio hook; nenhuma varredura externa.
