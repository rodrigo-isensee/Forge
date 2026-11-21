---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: dd1fc980fa57547c88dbf3d98fe35577b05fe522
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0478 E63.12 (hooks/conformidade.py: controle só do jarvis, escrita no índice, substituição no envio do git; head 0f4facab, segunda revalidação)

## Achados
- A4 (recomendado) hooks/conformidade.py:332 · `git apply --cached p.patch` e `git read-tree` gravam no índice conteúdo que nunca esteve na árvore e saem 0 no head e48a2e60; declarar o limite em docs/hooks.md ou recusar.

## Critério → teste → resultado
O pedido não tem especificação de UX nem contrato de API; as obrigações são as três regras do E63.1 (nome da regra no changelog e em docs/hooks.md).
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CONTROLE-PEDIDOS-E-BRIEFS-SO-JARVIS: só o jarvis grava pedido e brief da pasta de controle | Hooks.test_fixtures_do_controle_so_jarvis (cpb-*, 44 arquivos) | permissão por papel, leitura livre, pasta vizinha (propostas), variável, teto | passou no head; 31 fixtures falham na base |
| CONFORMIDADE-ESCRITA-NO-INDICE: git add e update-index em quem: [] | Hooks.test_fixtures_da_escrita_no_indice (idx-*, 30 arquivos) | S1-S4, `--cacheinfo` nas duas formas, curinga, pasta mãe, lista pela entrada, varredura sem caminho | passou no head; 22 falham na base; sonda achou `git stage` (A1) e `git apply --cached` (A4) |
| CONFORMIDADE-SUBSTITUICAO-NO-PROJETO: envio com parte opaca | Hooks.test_fixtures_da_substituicao_no_projeto (sub-*, 26 arquivos) | programa, subcomando, flag, destino, xargs, pipe para shell; commit em heredoc e leitura com `$(…)` livres | passou no head; 16 falham na base; sonda achou o pipe na sessão do Forge (A2) e o envolvedor (A3) |
| Custo do corpus | tests/provas/v0479-corpus-custo.md (diff) | filtro barato antes da leitura | lido no diff; sem execução local (sem suíte local, brief) |

## Cenários e resultado real
vermelho (`forge-testes --vermelho d4f0b10a --modulos test_hooks`, duas rodadas, `timeout 900`, saída em `/root/.forge-contrib/wt/qa-e634-vermelho.txt`): rc=124 nas duas, sem veredito (a ferramenta reserva 600 s por módulo e cópia; o módulo inteiro passa de 900 s no sandbox). Cabeçalho obtido: `vermelho: base=d4f0b10aead7 head=6c0b0f039a3a módulos=test_hooks (restrito por --modulos)`; `revertidos à base: ... hooks/conformidade.py ...`. Não vale como vermelho.

Vermelho à mão, no lugar dele (cópia do head com só `hooks/conformidade.py` da base, `python3 -I -m unittest discover -s tests -p test_hooks.py -k <os três testes>`): base `Ran 3 tests ... FAILED (failures=69)` (31 controle, 22 índice, 16 substituição); head `Ran 3 tests in 5.804s OK`.

Mutantes, uma chamada por spec, `timeout 900`, rc=0 em todas: trilha.json C1-C5 mortos; trilha-2 I1-I6 e I8 mortos; trilha-3 S1-S9 mortos; trilha-4 K1-K8 mortos; trilha-5 L1-L8 mortos. Total 37 mortos, nenhum sobrevivente (o brief diz 36; as specs somam 37). `forge-mutante --cobertura --base d4f0b10a`: rc=0, 32 linhas `coberta · ... · declarado, não provado`, nenhuma `não coberto`.

Sondas fora das fixtures (hook rodado por script próprio sobre a montagem das fixtures, `qa-e634-sonda.py`): controle, 38 formas (`tee`, `sed -i`, `mv`, `ln`, `install`, `dd`, `rsync`, `tar`, `unzip`, `cd` mais redirecionamento relativo, `..`, `//`, `${HOME}`, glob, python com `expanduser`) recusam; passam as leituras, `propostas/` e os limites já aceitos (`curl -o`, editor interativo, python com caminho relativo, nome da pasta numa variável). Índice, 40 formas: recusam o caminho com `--`, `./`, `..`, `:/`, `:(top)`, curinga, pasta mãe, `-C`, `cd`, `$PWD`, `--chmod`, `-f`, `--cacheinfo` separado, `--stdin`, `--index-info`, `--pathspec-from-file` e abreviação; `--cacheinfo=…` é rejeitado pelo próprio git (`takes no value`), então a passagem é inócua. Substituição, 60 formas: recusam `$(…)`, crase, `<(…)`, aspas, `xargs`, `env`, `command`; `bash <<<` e `bash -c "$(…)"` recusam pelas regras antigas; passam o commit com heredoc, `git status $(pwd)`, `git push origin melhoria/x 2>&1 | tail`, `git fetch origin $(…)` e o `echo … | cat`. Falso positivo aceito pelo desenho: `git push origin "melhoria/$(date +%s)"` recusa (destino por substituição).

Fixtures `pesado/mesma-sessao-libera` e `meta/v0454-caminhos-extra-*`: não rodadas por mim; o brief as dá como falhas na base também.

CI: este parecer não cita check-run `bateria`; o head ainda não tem PR (brief: sem PR). A suíte inteira não rodou aqui.

Provas de reprovação (reproduzíveis com a sonda, base `sub-sessao-forge-commit-heredoc-libera.json`, papel `forge:tech-lead`, e `idx-s4-add-chmod-bloqueia.json`, papel `forge:dev`):
- A1: `git stage .githooks/pre-push` rc=0; `git add .githooks/pre-push` rc=2.
- A2: `echo "git push origin develop" | sh` rc=0; `echo git push origin develop | sh` rc=2; `$(echo git) push origin develop` rc=2. Causa: na sessão do Forge a recusa passa por `trava_da_sessao_do_forge` → `toca_uma_trava`, que só marca shell no nível aninhado.

Bugs: não gravei `docs/qa/bugs/` (o brief manda commit só do parecer); A1 e A2 foram ao autor pelo bloco Achados e estão fechados na revalidação abaixo.

## Revalidação no head e48a2e60 (escopo incremental)
`forge-check parecer delta`: intervalo 6c0b0f03..e48a2e60; hooks/conformidade.py, fixtures idx-/sub-/cpb-/oraculo-, specs de mutante -6 a -9, docs e corpus.

Achados do parecer anterior, todos fechados (sonda `qa-e638-sonda.py`, saída em `/root/.forge-contrib/wt/qa-e638-sonda-*.txt`):
- A1 (bloqueante, era `git stage`): `git stage .githooks/pre-push` rc=2 (dev); `git reset .githooks/pre-push` rc=2; `git reset HEAD -- caminho` rc=2; `git stage src/x.py` e `git add src/x.py` rc=0. Fechado.
- A2 (bloqueante, pipe com aspas na sessão do Forge): `echo "git push origin develop" | sh`/`| bash`, com aspas simples e sem aspas, rc=2 para tech-lead, dev e jarvis. Fechado.
- A3 (recomendado, envolvedor): `| env bash`, `| sudo bash`, `| timeout 5 bash` rc=2 nos três papéis; `source /dev/stdin`, `. /dev/stdin`, `bash <(…)`, `source <(…)`, `. <(…)` rc=2; `git push --git-dir=x origin develop` e `git --git-dir x push origin develop` rc=2; `xargs git` sem subcomando rc=2. Livres: `echo oi | cat`, `git push origin melhoria/x 2>&1 | tail`, `git push origin melhoria/x`. Fechado.
- A4 (recomendado, `git apply --cached`, `git read-tree`): continuam rc=0; o limite segue aberto e o changelog diz que os limites abertos estão em docs/hooks.md. Fica como cartão, não bloqueia.

Mutantes novos, uma chamada por spec, `timeout 1500`, rc=0 em todas, nenhum sobrevivente nem sem veredito: -6 (S9, T1-T7) 8 mortos; -7 (U1-U8) 8 mortos; -8 (V1-V8) 8 mortos; -9 (W1) 1 morto. Total 25 mortos. Saídas em `qa-e638-mut6.txt` a `qa-e638-mut9.txt`.
`forge-mutante --cobertura --base d4f0b10a`: rc=0, cabeçalho `base=d4f0b10aead7 mb=d4f0b10aead7 rev=e48a2e60a11d`, 48 linhas `coberta · … · declarado, não provado`, nenhuma `não coberto`, `isenta velha` ou `só equivalente`.

Fixtures `pesado/mesma-sessao-libera`: não rodada por mim (falha no sandbox também na base, conforme o brief). A suíte inteira roda só no CI do PR; o head ainda não tem PR, sem check-run `bateria` a citar.

## Revalidação no head 0f4facab (E63.12, escopo incremental)
`forge-check parecer delta`: intervalo e48a2e60..0f4facab; hooks/conformidade.py, 30 fixtures cpb-/idx-/sub-, specs de mutante -10, -11, -12 (novas) e -3, -6, -8 e a base (reapontadas), docs/hooks.md, docs/hooks-fixtures.md, changelog e corpus de custo. Nenhum achado aberto do parecer anterior além do A4 (cartão, inalterado).

Os quatro testes do domínio, `python3 -I -m unittest discover -s tests -p test_hooks.py -k <nome>`, `timeout 1500`, TMPDIR em `scratchpad/tmp` (fora de `~/.forge-contrib`): `test_travas_do_conformidade`, `test_fixtures_da_substituicao_no_projeto`, `test_fixtures_do_controle_so_jarvis`, `test_fixtures_da_escrita_no_indice`: `Ran 1 test ... OK` nos quatro (3,6 s, 3,7 s, 5,4 s, 3,1 s).
Ressalva de ambiente: com TMPDIR dentro de `/root/.forge-contrib/wt/` (como o brief indicou), 17 fixtures sub-* e `idx-reset-codigo-libera` falham no head, e também em e48a2e60 (`git archive`, mesma falha no teste do índice): o hook trata o projeto montado sob `~/.forge-contrib` como sessão do Forge (`R-CONTRIB: ... a sessão de projeto não cria branch`). Não é regressão da volta; saída em `/root/.forge-contrib/wt/qa-e6312/{sub,idx,testes}.txt`. Os testes valem rodados com TMPDIR fora dessa pasta.

Mutantes, uma chamada por spec, `timeout 1500`, rc=0 em todas, nenhum sobrevivente nem sem veredito (`rev=0f4facab2db2`): -10 (X1-X8) 8 mortos; -11 (Y1-Y8) 8 mortos; -12 (Z1-Z4) 4 mortos; reapontadas: trilha (C1-C5) 5, -3 (S1-S8) 8, -6 (S9, T1-T7) 8, -8 (V1-V8) 8 mortos. Total 49 mortos. Saídas em `qa-e6312/mut10.txt`, `mut11.txt`, `mut12.txt`, `mutr*.txt`.
`forge-mutante --cobertura --base d4f0b10a`: rc=0, cabeçalho `base=d4f0b10aead7 mb=d4f0b10aead7 rev=0f4facab2db2`, 63 linhas `coberta · … · declarado, não provado`, nenhuma `não coberto`, `isenta velha` ou `só equivalente`.

Sonda `qa-e6312/sonda.py` (a de E63.8 apontada para este clone; hook sobre a montagem das fixtures; papéis tech-lead, dev, jarvis):
- Controle, 20 formas: `cd ~/.forge-contrib/wt/x && sed … docs/pedidos/v1.md > $TMPDIR/e.txt` rc=0 (corrigido); `cd` para `wt/x/..`, `wt/x && cd ..`, `cd ../..`, `wt`, a pasta mãe, `wt/../`, `wt/x/../..` com escrita em pedido ou brief, `echo x > ~/.forge-contrib/docs/pedidos/…`, `…/wt/../docs/…`, `tee ../../docs/…`, variável `d=~/.forge-contrib` rc=2 para tech-lead e dev; jarvis rc=0 em tudo. Leituras (`ls`, `cat`) rc=0. Limite já aceito: `python3 -c 'open("../../docs/pedidos/v1.md","w")'` a partir de `wt/x` rc=0.
- Entrada de arquivo do shell, 36 formas: `| bash < /dev/stdin`, `/dev/fd/0`, `/dev/fd/00`, `/proc/self/fd/0`, `/proc/$$/fd/0`, `/proc/thread-self/fd/0`, `0<`, `//dev/stdin`, `/dev/./stdin`, `/dev/../dev/stdin`, aspas, `/dev/tty`, `/dev/fd/3`, variável com o caminho rc=2 (tech-lead e dev); `bash < script.sh`, `sh < build.sh`, `bash < ./scripts/run.sh`, `echo oi | cat`, `git push origin melhoria/x 2>&1 | tail` rc=0.
- `help.autocorrect`: `git -c help.autocorrect=…` (e `HELP.AUTOCORRECT`) rc=2; `git config help.autocorrect 1`, `--global`, `--local`, `set`, `--add` rc=2 e `git config alias.p push` rc=2 no projeto; `git config --get help.autocorrect` e `git config help.autocorrect` rc=0. `git -chelp.autocorrect=1` rc=0 é inócuo (o git não aceita `-c` colado). Na montagem da sessão do Forge, `git config help.autocorrect 1` e `alias.p` passam (rc=0), igual ao alias antes da volta; fora das fixtures da volta.

Fixture `pesado/mesma-sessao-libera`: não rodada por mim (falha no sandbox também na base, conforme o brief). A suíte inteira roda só no CI do PR; o head ainda não tem PR, sem check-run `bateria` a citar.

## Revalidação no head 7a739fca (E63.16, escopo incremental)
`forge-check parecer delta`: intervalo 0f4facab..7a739fca; hooks/conformidade.py (`CAMINHO_TROCADO_NA_LINHA`, `GuardaDaProva.bash`, `sem_copia_de_wt`), 11 fixtures cpb-, specs de mutante -10 e -13, docs, changelog e corpus de custo. Achado aberto: só o A4 (cartão, inalterado).

Os quatro testes do domínio, `python3 -I -m unittest discover -s tests -p test_hooks.py -k <nome>`, `timeout 1500`, TMPDIR em `/tmp/claude-0/qa6316tmp` (fora de `~/.forge-contrib`): `test_travas_do_conformidade` (7,2 s), `test_fixtures_da_substituicao_no_projeto` (5,7 s), `test_fixtures_do_controle_so_jarvis` (9,5 s), `test_fixtures_da_escrita_no_indice` (3,8 s): `Ran 1 test ... OK` nos quatro.

Mutantes, uma chamada por spec, `timeout 1500`, rc=0, nenhum sobrevivente nem sem veredito (`rev=7a739fca7bed`): -13 (W1, W2, W3, W5, W6, W7, W8) 7 mortos; -10 (X1-X8) 8 mortos. Total 15 mortos. Saídas em `/root/.forge-contrib/wt/qa-e6316/mut13.txt` e `mut10.txt`.
`forge-mutante --cobertura --base d4f0b10a`: rc=0, cabeçalho `base=d4f0b10aead7 mb=d4f0b10aead7 rev=7a739fca7bed`, 66 linhas `coberta · … · declarado, não provado`, nenhuma `não coberto`, `isenta velha` ou `só equivalente`.

Sonda (`qa-e6316/sonda.py`, a de E63.12 apontada para este clone; 20 formas; papéis tech-lead, dev, jarvis; saída em `sonda-novo.txt`): tech-lead e dev rc=2 para `HOME=…;`, `export HOME=`, `HOME=… sh -c`, `env HOME=`, `ln -s …;`, `mv a <pedido>`, `cp -s a <brief>`, `source`, `. x.sh`, `BASH_ENV=` e `wt/$X/docs/pedidos`, todos citando o pedido ou o brief; rc=0 para a leitura pela cópia (`cd wt/x && sed -n … > $TMPDIR/e.txt`, `ls`, `cat`), `mv a b`, `git mv a b`, `ln -s a b`, `cp -r a b`, `git commit -m 'HOME fix'` e `echo HOME > $TMPDIR/e.txt` (sem falso positivo). Jarvis rc=0 nas 20.

Fixture `pesado/mesma-sessao-libera`: não rodada por mim. A suíte inteira roda só no CI do PR; o head ainda não tem PR, sem check-run `bateria` a citar.

## Revalidação no head a247ae11 (E63.22, escopo incremental)
`forge-check parecer delta`: intervalo 7a739fca..9f91054b, sem o que veio da develop. No domínio: `docs/hooks.md`, `docs/hooks-fixtures.md` (índice regerado), `tests/mutantes/v0435-review.json` (R6 alinhado à tupla `("alias.", "help.autocorrect")`, que é o texto em `hooks/conformidade.py:2801`) e `tests/test_hooks.py` (um exemplo leve trocado de `--dirigida` para `--afetados`). Achado aberto: só o A4 (cartão, inalterado).

- `python3 scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`, rc=0 (3368 fixtures, 3 novas `pesado/forgetestes-*`).
- `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_formas_leves_e_citacoes`: `Ran 1 test ... OK`.
- `bin/forge-mutante tests/mutantes/v0435-review.json --base 7a739fca`: rc=0, `base=7a739fca7bed… rev=9f91054bda85…`, R1 a R14 todos `morreu`, nenhum sobrevivente nem sem veredito; o R6 morre em `hooks/conformidade.py:2801`.
- Sem vermelho-antes-do-verde novo: o delta não traz teste de regra nova (as fixtures `forgetestes-*` vieram da develop). Suíte inteira não rodada local; o head ainda não tem PR, sem check-run `bateria` a citar. Máquina com carga 23 durante a rodada.

## Revalidação no head dd1fc980 (E63.26, escopo incremental)
`forge-check parecer delta`: intervalo a247ae11..dd1fc980; no domínio só `docs/hooks.md` (a linha 56 ganha a frase "Limite: o link criado por cópia na mesma linha não recusa…", A18 da segurança). Sem código nem teste no delta.

- `test_sandbox_controle.py` e `test_hooks_parecer_matriz.py` (os módulos que leem `docs/hooks.md`), `python3 -I -m unittest discover -s tests -p <módulo>`: 14 testes `OK (skipped=2)` (skips já existentes no módulo, não meus) e 9 testes `OK`.
- `scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`, rc=0.
- O cartão CONFORMIDADE-LINK-POR-COPIA que a frase cita existe em `docs/kanban/historico.md` e em `docs/pedidos/v0478.md`; a frase confere com o comportamento já sondado (a forma por cópia não recusa).
- Sem vermelho novo (delta só de texto), sem mutante novo; suíte inteira não rodada local.
