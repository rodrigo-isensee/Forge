---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-hook-heredoc-fp
commit: 58312004dfd8940079d5232a98e1d2936e51e108
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v047, E4.9 (E4.4, falso positivo de heredoc no hook `parecer`)

Head revisado: `58312004` (base `9b2c6474`). Escopo: `hooks/parecer.py` (`leitor_da_entrada`, `interprete_do_corpo`, `leitores_dos_corpos`, `marcas_da_chamada` e os três pontos de uso em `conferir_linha`), `docs/hooks.md:103`, as 24 fixtures `tests/hooks/parecer/heredoc-interpretador-*` e os mutantes. Afrouxa a rede D da ADR 0011 (item 2, opção D) para o corpo de heredoc lido só pelo interpretador Python da entrada.

**Veredito: aprovado, com quatro recomendações.** O que o brief pede confere: o corpo lido só por `python3 -` sai da conferência como comando (fixtures `*-libera`); o corpo de `sh` que só lê ou espera segue conferido como comando e não liga a rede D (`sh-so-echo-libera` passa; `sh-gh-pr-merge`, `bash -s`, `echo … | sh`, `sh` com `sleep` e `bash -c` depois seguem barrados); o caso verdadeiro (Python que lança `gh pr merge` por `subprocess`, `os.system`, `os.execvp`, `exec(`, e o `gh pr merge` que o `sh` roda) segue barrado. O `<<` sem aspas com `$(` ou crase no corpo segue barrado antes da mudança (`tirar_heredocs`), e a mudança só vale com todo `<<` simples e sem `$` nem `\` nas linhas de comando (`heredocs_simples`).

Há caminhos de execução real que passavam barrados na base e passam no head (A1 a A3). Nenhum deles dá a quem ataca algo que ele já não tenha na base: cada um tem um equivalente de mesmo esforço com `python3 -c '…'`, que a base libera e que a ADR 0011 deixa fora da regra (`docs/adr/0011-analisador-de-comandos-gramatica-positiva.md:41`, cartão N-HOOK1). Por isso são recomendados, e não bloqueantes (proporcionalidade; `R-REVIEW`). A afirmação do brief "nenhum caminho de execução real passa" não vale no sentido estrito: ver A1 a A3.

## Gatilhos
`R-SEGURANCA`: mudança em controle do Forge (hook PreToolUse que guarda `gh pr`, merge e pull), com afrouxamento de regra de ADR.

## Achados
- A1 (recomendado) hooks/parecer.py:172 · reforço do caso verdadeiro só pega a forma literal: create_subprocess_shell do asyncio, posix_spawnp, lista montada em duas linhas, concatenação e getattr com gh pr merge passam no head (a base barrava); equivale ao python3 -c que a base libera
- A2 (recomendado) hooks/parecer.py:197 · só a atribuição do dono tira o corpo da regra; PATH=<pasta> solto antes (PATH=d; python3 - com o corpo gh pr merge) passa no head e o bash roda o corpo como shell se d/python3 for um sh; equivale a PATH=d; python3 -c, que a base libera
- A3 (recomendado) hooks/parecer.py:928 · corpo de Python que grava .git/config (core.fsmonitor) ou .git/hooks com gh pr merge, seguido de git status ou git commit na mesma chamada, passa no head; a base barrava (com gravação, nenhum git na lista); equivale ao python3 -c seguido de git status
- A4 (recomendado) docs/adr/0011-analisador-de-comandos-gramatica-positiva.md:39 · o afrouxamento da opção D para Python não tem emenda na ADR 0011 nem marca de afrouxa-regra, ao contrário da emenda H1-1 (linha 43); registrar a emenda, o critério de reversão e o rótulo no PR

## Sondas

## Detalhe dos achados
Sondas executadas pela máquina das fixtures (`Fixture.montar` e `rodar` de `tests/test_hooks.py`, hook `parecer`, repositório temporário sem a branch `feat/x`), no head `58312004` e na base `9b2c6474`, com o mesmo texto; `MRG` abaixo é `merge`. Código 2 com "branch `feat/x` não existe" quer dizer que o `gh pr merge` do corpo foi lido e conferido; código 0, que passou.

| Entrada (resumo) | base | head |
|---|---|---|
| `python3 -c 'import os; os.system("gh pr MRG feat/x")'` | 0 | 0 |
| `python3 - <<'EOF'` + `subprocess.run(["gh","pr","MRG",…])` | 2 | 2 |
| `python3 - <<'EOF'` + `subprocess.run("gh " + "pr MRG feat/x", shell=True)` | 2 | 0 |
| `python3 - <<'EOF'` + lista montada (`c=["gh","pr"]; c+=["MRG",…]; s.run(c)`) | 2 | 0 |
| `python3 - <<'EOF'` + `asyncio.create_subprocess_shell("gh pr MRG feat/x")` | 2 | 0 |
| `python3 - <<'EOF'` + `os.posix_spawnp("gh",[…"MRG"…],…)` | 2 | 0 |
| `python3 - <<'EOF'` + `getattr(os,'sys'+'tem')("gh pr MRG feat/x")` | 2 | 0 |
| `python3 - <<'EOF'` + `os.system("git pull origin develop")`, `os.execvp`, `exec("…os.system…")` | 2 | 2 |
| `PATH=/tmp/evil:/usr/bin:/bin; python3 -c 'gh pr MRG feat/x'` | 0 | 0 |
| `PATH=/tmp/evil:/usr/bin:/bin; python3 - <<'EOF'`⏎`gh pr MRG feat/x`⏎`EOF` (e na linha de cima) | 2 | 0 |
| `export PATH=…`, `declare PATH=…`, `readonly PATH=…`, `hash -p /bin/sh python3`, função `python3() { sh; }`, `alias` | 2 | 2 |
| `python3 -c "open('.git/config','a').write('…fsmonitor = gh pr MRG feat/x…')"`⏎`git status` | 0 | 0 |
| o mesmo com `python3 - <<'EOF'`, e com `.git/hooks/pre-commit` e `git commit -m x` | 2 | 0 |
| `python3 - <<'EOF' \| sh`, `python3 - <<'EOF' > x.sh` + `sh x.sh`, Python grava `x.sh` + `sh x.sh`, `source x`, `. ./x` | 2 | 2 |
| `python3 - <<EOF` com `$(gh pr MRG …)` ou crase no corpo; corpo com CRLF | 2 | 2 |
| `python3 - <<'EOF'`⏎`print(1)`⏎`EOF`⏎`gh pr MRG feat/x`; `… sh -c '…'`; `… eval …` | 2 | 2 |

Execução real do caminho do A2, com um `gh` registrador no lugar do verdadeiro e `pr list` no lugar de `pr merge`: `PATH=$D/evil:$D/bin:/usr/bin:/bin`⏎`python3 - <<'EOF'`⏎`gh pr list feat/x`⏎`EOF`, com `$D/evil/python3` igual a `exec sh`, grava `gh-rodou: pr list feat/x`: o bash roda o corpo como shell.

**Caminho de ataque (os três):** o agente da sessão, deliberadamente, quer mesclar sem parecer; numa chamada do Bash, põe o comando de PR num corpo que o hook agora trata como Python. **Por que recomendado:** o mesmo agente tem, na base, o `python3 -c` com o mesmo efeito e o mesmo esforço (primeira, nona e décima segunda linhas da tabela), fora da regra pela ADR 0011 (linha 41, N-HOOK1); e o hook é por marcador, então a ofuscação sem o texto literal (por exemplo, montar a palavra com `printf`) já passa na base. A mudança não abre classe nova; ela alinha o heredoc de Python ao `-c`. O uso por engano, que é o que a rede D pega na prática, não forma nenhum desses textos. Severidade: baixa.

**A1, correção mínima** (P, `tech-lead`): no `LANCA_PROCESSO`, trocar o `\b` inicial por `(?<![A-Za-z0-9])`, para pegar `create_subprocess_exec`, `create_subprocess_shell` e `posix_spawn`/`posix_spawnp` (o `_` antes do nome hoje impede o casamento); e, em `docs/hooks.md:103`, dizer que o reforço pega só o comando de PR escrito em sequência (lista ou texto literal), não o montado nem o concatenado.

**A2, correção mínima** (P, `tech-lead`): em `leitores_dos_corpos` (ou `interprete_do_corpo`), devolver `None` para todos os corpos quando a chamada, fora dos corpos, tem atribuição solta em qualquer comando (`programas_e_atribuicoes(comando)` com atribuições não vazias), e não só a do dono. Fixture nova `heredoc-interpretador-path-solto-bloqueia` com `PATH=/tmp/x:/usr/bin; python3 - <<'EOF'`⏎`gh pr merge 12`⏎`EOF`.

**A3, correção mínima** (P, `tech-lead`): só dar o tipo `python` quando nenhum outro programa da chamada é `git` (o arquivo que o corpo grava fica no disco e o `git` roda ganchos, filtros e `core.fsmonitor`, a mesma razão de "se o texto grava arquivo, nenhum `git` fica na lista" em `docs/hooks.md:101`). Fixture nova `heredoc-interpretador-python-e-git-status-bloqueia`.

**A4, correção mínima** (P, `tech-lead`): emenda na ADR 0011, item 2, no formato da H1-1 (linha 43): o que sai da opção D (corpo de `python3 -` e corpo de `sh` que só lê ou espera), por que (equivalência com o `-c`, N-HOOK1), "Afrouxa; rótulo `afrouxa-regra`" e o critério de reversão (uma sonda em que o corpo dado como Python ou como `sh` de leitura roda um comando de PR que o `python3 -c` equivalente não rodaria). O escopo E4 do pedido ("os 4 bloqueios falsos", `confirmado`) cobre o afrouxamento; a emenda registra-o.

## Riscos aceitos e ferramentas
Nenhum risco aceito por este parecer. Suíte: sem PR aberto para a branch (brief: não abrir), sem CI a citar; rodado só o teste afetado, `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_heredoc_interpretador_libera_e_bloqueia` (OK, 1 teste) e as sondas acima. A suíte inteira fica para o CI do PR. Ferramentas: só leitura do código e o próprio hook; nenhuma varredura externa.
