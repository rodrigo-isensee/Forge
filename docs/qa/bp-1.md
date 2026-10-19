---
tipo: qa
contrato: 1
pedido: bp-1
branch: melhoria/bp-1
commit: d986c37136ceb9a7790fa8c1dba993b6ae28ee0d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# QA - BP-1 (guarda contra remoção de `.forge/versao` e contorno dos hooks)

Links: `~/.forge-contrib/docs/pedidos/bp-1.md` (E1, E2), `docs/reviews/bp-1.md` (r9, aprovado), `docs/security/bp-1.md` (r9, aprovado), `docs/hooks.md`, ADR 0009. Não há UX nem API. Offline, só disco local (`R-CUSTO`). Testado `d986c37`; o HEAD da worktree (`36abadc`) só soma os dois pareceres por cima.

## Ambiente
Raiz da worktree `~/.forge-contrib/wt/bp-1` para a suíte e o `validar-plugin`; cópia descartável em `$TMPDIR/qa-bp1` (`proj/`: repositório com `.forge/versao`, `.forge/config.json`, `.githooks/`, `.claude/`, `src/`, `docs/`; `plugin/`: `git archive` do HEAD; `base/`: `git archive f636d27`). O `SessionStart` do `vigia` rodou antes (cria a marca em `.git/forge/`). Hooks chamados como o Claude Code chama: JSON no stdin, `agent_type: forge:dev`, `CLAUDE_PROJECT_DIR` no projeto.

## Resultados
| ID | Obrigação / cenário | Fronteira protegida | Resultado |
|---|---|---|---|
| CT-01 | Suíte inteira (`python3 -m unittest discover -s tests`) na raiz da worktree | n/a | Passou: 788 testes, OK, 128,6 s (nenhuma outra suíte rodando antes) |
| CT-02 | `scripts/validar-plugin.sh` na raiz da worktree | n/a | Passou: `Validation passed` (marketplace, plugin, `dev/`); rc=0. O sandbox nega `api.anthropic.com` e o datadog; não afeta o resultado |
| CT-03 | Dia a dia de um agente: 80 comandos (E1): `git add/commit/status/diff/log/fetch/stash/branch`, `git checkout -- src/..`, `checkout .`, `restore .`, `checkout develop`, `checkout -b`, `switch -c`, `git rm src/app.js`, `git mv` em `src/`, `push origin melhoria/x`, `sed -i` e `-i.bak` em `src/`, `sed` de leitura (`/w/p`, `s/www/w/g`, `w out.txt`, `w /dev/stdout`), `python3 -c` e `node -e` lendo `.forge/versao`, `python3 -m unittest`, `node src/app.js`, `cat`/`head`/`grep`/`find` em `.forge/`, `.githooks/`, `.claude/`, `.git/config`, `perl -ne`, `ruby -e`, `awk`, `perl -pi`/`ruby -i`/`gawk -i inplace` em `src/`, `npm test`, `make`, `pytest`, `cp`/`mv`/`rm`/`touch`/`mkdir`/`chmod` em `src/`, `cd src && ls`; 13 heredocs (`cat <<'EOF' > src/new.js`, `python3 - <<'X'`, `node <<'X'`, `git commit -F - <<'X'`, `git commit -m "$(cat <<'X'...)"`, `p''erl <<'X'`, `"py"thon3 <<'X'`, `c''at <<'X' > docs/nota.md`) | caminho protegido x caminho comum | 75 de 80 com rc=0; 5 com rc=2, todos explicados em CT-04 (falso positivo do lado fechado, declarado ou anterior à base) |
| CT-04 | Os 5 rc=2 do dia a dia | n/a | `ls -la .git/forge` (cita a marca; declarado, `docs/hooks.md:36`); `ionice -c3 npm test` e `flock /tmp/l true` (lançadores recusados com `.forge/versao` presente; declarado, ADR 0009 item 2); `perl -e 'open F,q(.forge/versao); ...<F>...'` (2 linhas, ver QA-OBS-1: anterior à base) |
| CT-05 | Falsos positivos listados pelos revisores, um por um (rc) | ver linhas | `sed -n 'w .forge/versao'` rc=2; `sed -n '/w .git/p'` rc=2 (aceitos: palavra depois de `w` que é caminho protegido barra); `sed -n '/w/p' .git/config` rc=0; `cat .forge/versao \| sed 's/a/b/w out.txt'` rc=0; `awk '/inplace/'` rc=0; `grep -rn inplace src/` rc=0; `awk 'BEGIN{print "inplace"}'` rc=0; `awk -f prog.awk` rc=0; `gawk -i ordchr` rc=0; `gawk -i inplace ... src/app.js` rc=0; `ionice -c3 cat .git/forge/x`, `cat .git/forge/projeto-*` rc=2 (R6, declarado); `flock src/lock npm test`, `script -q /dev/null npm test`, `unshare -r id`, `taskset -c 0 make`, `chrt -i 0 make` rc=2 (declarado); `git checkout develop` rc=0; `perl -Mstrict -ne print .forge/versao` rc=0 (R10); `perl -0777 -ne ... .forge/versao` rc=0; `sed -n 's/saw/x/;p'` rc=0; `sed ...;w /dev/stdout` rc=0; `perl -i~`, `ruby -i.bak`, `perl5.34.0 -pi` em `src/` rc=0; `/usr/bin/perl <<'X'` rc=0; `x"perl" <<'X'` rc=0 (informativa da segurança) | Passou: todos como os revisores previram; os rc=2 são do lado fechado e estão na documentação |
| CT-06 | R5: sessão de projeto numa branch anterior ao Forge (sem `.forge/versao`) | marca presente, arquivo ausente | `git status`, `ls`, `sed -i`, `git commit`, `git checkout feat`, `git switch feat` rc=0; `git push origin melhoria/x` e `git push origin develop` rc=2 (falha fechada, intencional, documentada); voltar para `feat` restaura o `push` |
| CT-07 | E1: remoção de `.forge/versao` pelas formas do pedido: 51 linhas (`rm`, `rm -rf .forge`, `mv`, `>`/`>>`, `truncate`, `unlink`, `git rm` (`-r --cached`, curinga, `-r .`, `-C .forge`, pathspec mágico `:(top)` e `:(glob)`, `--literal-pathspecs`, `--pathspec-from-file`), `git mv`, `git checkout [HEAD] --`, `git restore [-s]`, `sed -i`, `perl -pi`, `perl -e unlink`, `python3 -c os.remove`, `node -e unlinkSync`, `ruby File.delete`, `cp /dev/null`, `tee`, heredocs com `python3`, `perl`, `node`, `p''erl`, `cat <<EOF >`, marca `.git/forge`, `.git/config`, `core.hooksPath`, `--no-verify`, `push --force`, `push origin develop`, `sed w .git/config`, `.githooks`, `.claude`) | caminho em vigor | 49 de 51 com rc=2. Os 2 com rc=0 são `find .forge -name versao -delete` e `git clean -fdx .forge` (arquivo rastreado: o `clean` não o toca): fora das formas do pedido, com dono (BP-5; segurança, `docs/security/bp-1.md:143`, `:232`, `:297`) |
| CT-08 | Vermelho antes do verde: a mesma bateria contra a base `f636d27` (`git archive`) | n/a | Base: 23 das 51 linhas com rc=0 (todo `git rm/mv/checkout/restore`, `--pathspec-from-file`, `perl -pi`, `ruby File.delete`, `p''erl <<`, `rm .git/forge/...`, `sed w .git/config`). `d986c37`: 2 (CT-07). O teste falha sem a implementação |
| CT-09 | Falha fechada: marca presente, `.forge/versao` removido por fora (como o usuário ou um contorno) | sessão sem o arquivo | `git status/ls/diff/add/commit`, `sed -i src/`, `python3 -c`, heredoc em `src/`, `npm test` rc=0 (comuns seguem); `git push`, `git merge`, `gh pr create`, `push --force`, `commit --no-verify`, `git checkout -- .forge/versao`, `git restore .forge/versao`, `echo 0 > .forge/versao` rc=2 com a mensagem "o .forge/versao da sessão sumiu"; `rm -rf .forge` rc=2. `parecer.py`: `gh pr create` e `gh pr merge` rc=2. `vigia` `Stop` avisa `versao-sumiu` ao usuário. Novo `SessionStart` sem o arquivo não apaga a marca e o `push` continua rc=2. Com o arquivo devolvido, o `push` volta a rc=0 |
| CT-10 | Worktree (`.git` é arquivo): marca por raiz, `.git` protegido | `.git` da raiz | Marca nova `projeto-<hash>` ao lado da principal; comuns rc=0; `git rm`, `rm`, `git checkout -- .forge/versao` rc=2; `echo x > .git` e `rm .git` rc=2 (mensagem do `.git` da raiz); sem o arquivo, `push` rc=2 e `vigia` avisa |
| CT-11 | Mutação nas duas linhas do último retrabalho (cópia em `$TMPDIR`; `tests.test_hooks`, 19 testes) | n/a | M1 (`conformidade.py:64` sem o lookahead): 2 fixtures falham (`o-sed-w-depois-de-w-bloqueia`, `o-sed-w-mascarado-bloqueia`). M2 (`:642` sem tirar aspas e barra do dono): 3 fixtures falham (`b10-heredoc-dono-aspas-no-meio-bloqueia`, `n-heredoc-dono-aspas-bloqueia`, `n-heredoc-dono-barra-bloqueia`). Mutantes mortos; original: OK |

## Achados por classe (VV-1)
Nenhum bug da entrega. Observações, com o comando que reproduz (projeto descartável com a marca criada pelo `SessionStart`; `<hook>` é `hooks/conformidade.py` com o JSON de `PreToolUse` do Bash, como no `docs/security/bp-1.md`):
- **QA-OBS-1 · leitura com `<F>` em `perl -e` barra (baixa, anterior à base, lado fechado):** `perl -e 'open F,q(.forge/versao); while(<F>){print}'` dá rc=2 em `d986c37` e em `f636d27` (o `<`/`>` do `<F>` é lido como redirecionamento); a mesma linha sem `<F>` (`... print 1`) dá rc=0, e `python3`/`node` lendo o arquivo dão rc=0. Contorno: `perl -ne 'print' .forge/versao`. Não é da BP-1: não conta nos bugs desta entrega; sugiro cartão na BP-5.
- **Declarados, do lado fechado (aceitos pelas decisões do dono e do Jarvis):** lançadores `ionice`, `chrt`, `taskset`, `flock`, `unshare`, `script` e citar `.git/forge` barram numa sessão de projeto com `.forge/versao` presente (CT-04, CT-05); R5 (CT-06); `git add docs/qa/bp-1.md` e `git push` barram quando a falha fechada está ligada (caminho protegido como marcador crítico). Não verifiquei se algum fluxo do Forge usa esses lançadores; um projeto que use `flock` nos próprios scripts de teste vai topar com o bloqueio; vale uma linha no guia de suporte, se o dono quiser.
- **Abertos com dono (BP-5), fora da promessa:** `find -delete`, `rm $(find ...)`, `git clean` com o arquivo não rastreado, `setpriv`/`busybox`/`ed`/`patch`/`sponge`, grafia montada em tempo de execução, `inplace.awk` copiado (L, K, M do parecer de segurança). Reproduz: `find .forge -name versao -delete` dá rc=0.

## Pendências do QA
- Mutação: o Forge não declara ferramenta de mutação; fiz mutação manual nas duas linhas do último retrabalho (CT-11). As linhas dos retrabalhos 1 a 7 não foram mutadas uma a uma: a cobertura delas está nas 790 fixtures e na bateria dos revisores.
- Acessibilidade e E2E de navegador: não se aplicam (sem tela).
- Bug aberto: nenhum; portanto sem `aceite_usuario`.

## Parecer
**Aprovado** para `d986c37`. Suíte 788 OK; `validar-plugin` OK; o dia a dia passa; a remoção de `.forge/versao` pelas formas do pedido é barrada (vermelho na base, verde aqui); a sessão sem o arquivo falha fechada nas ações críticas e o `vigia` avisa.
