---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-til-link
commit: 9451e78c19bbbe44b640c04ff1f6a135e0b41767
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-conformidade-til-link (v0478 E80.6, revalidação)

Delta lido (`forge-check parecer delta`): `481d2855..9451e78c`. No domínio estão `hooks/conformidade.py` (`normalizada`, `valores_em_sequencia`, `fechado_em_vigor`, `OPACO_EM_VIGOR`, `FECHADO_NA_LINHA`, `LONGA_DO_LINK` e `EM_VIGOR_NO_TEXTO`), `tests/test_hooks.py` e o corpus `tilsubst-*` e `linkcopia-*`. Também li o texto de `docs/hooks.md` que declara os limites. A rodada anterior está no git (841b4ba4).

## Gatilhos
Gatilhos: controle do Forge (hook `conformidade`), escrita em arquivo em vigor e na pasta de controle

## Resultado
**A mudança só aperta.** Rodei 141 sondas com o mesmo fixture no hook da base (481d2855) e no do head, e mais 12 só no head. Nenhuma passou de recusa (2) para liberação (0). Foram 56 de 0 para 2, 41 ficaram em 2 e 44 ficaram em 0. O corpus legítimo continua liberando: `d=~/tmp`, `$(pwd)/a.txt`, `~/.claude-notas`, `d=~/.claude; cat …`, `python3 -c "print(1)"`, `perl -Mstrict -e … .githooks/pre-push`, `python3 x.py`, `cp -p` e `cp -v`. Os testes `test_fixtures_do_til_em_substituicao`, `test_fixtures_do_link_por_copia` e `test_fixtures_do_controle_so_jarvis` passam no head (3 OK).

Estado dos achados anteriores:
- **A1** foi corrigido para `.claude`. As sondas S1 a S5 da rodada anterior recusam (`$HOME`, `${HOME}`, `$PWD`, `$CLAUDE_PROJECT_DIR`, as três reatribuições, `for` e `read`). Também recusam `+=`, `printf -v`, `mapfile` e `$(cd ~ && pwd)`. O resíduo da família ficou com o estreitamento (a) e virou a A4.
- **A2** foi corrigido nas formas que listei. S6 a S11 recusam todas, assim como `busybox unzip|cpio`, `7z -y x`, `7za`, `cpio -p`, `dpkg -x`, `rsync --lin` e `tar --file … --extr`. Dois resíduos seguem abertos: o extrator fora da lista (A5) e o git que restaura link, que o autor declarou como limite (A6).
- **A3** foi corrigido para `.claude` (`python3 -c`, `-I -c`, `perl -e`, `node -e` e `-c "$s"`). O resíduo com `.git` está na A4.

Os dois estreitamentos do autor:
- **(a)** A citação de "arquivo em vigor" só por `.claude` **não afrouxa**: as sondas dela já davam 0 na base. A leitura do `.githooks/` com perl segue livre, e isso é aceitável, porque a escrita no `.githooks/` por variável já recusa por outra regra (`$d com ação crítica`; sondas com `for`, `read`, `-c` e `tar -C $d` dão 2). O estreitamento deixa aberta, porém, a mesma família para `.forge/` e `.git/` (A4).
- **(b)** Deixar livre o listar e o criar pacote (`7z l`, `cpio -o`, `bsdtar -tf`, `tar -cf`, `tar -tf`) **não afrouxa** e é aceitável: nenhum desses modos põe um link no disco. O `cpio -p` copia e recusa.

Os limites declarados em `docs/hooks.md`:
- **O nome montado por variável sem `.claude` no texto** (`c=.cla; for d in ~/${c}ude; …` e `c=.cla; read d <<< ~/${c}ude; …` dão 0) é **aceitável como limite**. Fechá-lo pede a recusa de todo destino opaco com sufixo, e o `denyWrite` do sandbox (BP-5) cobre `~/.claude` e o `.claude` do projeto.
- **O git que restaura link** (`git clone`, `checkout`, `stash pop` e `worktree add` na mesma linha) **não é aceitável como limite**: veja a A6.

A suíte inteira não rodou. Não há PR nem CI para este head. A suíte fica com o CI.

## Achados
- A4 (bloqueante) hooks/conformidade.py:3907 · a falha fechada vale só para `.claude`, e os outros alvos em vigor continuam abertos. `for d in .forge; do echo x > "$d/versao"; done`, `read d <<< .forge; … "$d/config.json"` e `d=.git; python3 -c "open('$d/config','a')"` dão 0. É o resíduo das A1 e A3. Ver S1 a S3.
- A5 (bloqueante) hooks/conformidade.py:3898 · faltam extratores na lista. `python3 -m tarfile -e|--extract` (a linha 2432 isenta o `-m`) cria o link em `wt/` e grava o pedido. `-m tarfile|zipfile -e` extrai direto em `~/.claude/`. `unrar x` e `unsquashfs` também dão 0. Ver S4 a S6.
- A6 (bloqueante) hooks/conformidade.py:3908 · o git que restaura link na linha que cita o controle (`clone`, `checkout`, `stash pop`, `worktree add`) está declarado como limite, mas é o mecanismo da A2, tem ataque provado e o motivo da A10 não se aplica, porque o jarvis já fica fora. Feche no hook ou peça o aceite do usuário. Ver S7 e S8.

## Sondas
- S1 · fixture tilsubst-for-bloqueia (tech-lead): `for d in .forge; do echo x > "$d/versao"; done` (também `"$d/run/a"`) · espera: código 2 · obtido: código 0 (base e head); `d=.forge; echo x > "$d/versao"` dá 2
- S2 · mesmo fixture: `read d <<< .forge; echo x > "$d/config.json"` · espera: código 2 · obtido: código 0 (base e head)
- S3 · mesmo fixture: `d=.git; python3 -c "open('$d/config','a')"` (também dentro de `for d in .git; do …; done`) · espera: código 2 · obtido: código 0; com o caminho literal `.git/config` dá 2
- S4 · fixture linkcopia-7z-bloqueia: `python3 -m tarfile -e ~/l.tar ~/.forge-contrib/wt/ && echo x >> ~/.forge-contrib/wt/q/docs/pedidos/v1.md` (também `--extract`) · espera: código 2 · obtido: código 0
- S5 · fixture tilsubst-for-bloqueia: `python3 -m tarfile -e ~/l.tar ~/.claude/`, `python3 -m zipfile -e ~/l.zip ~/.claude/` e `d=~/.claude; unrar x ~/l.rar $d/` · espera: código 2 · obtido: código 0
- S6 · laboratório em $TMPDIR: `ln -s /etc/hostname src/lk; tar -cf l.tar -C src lk; python3 -m tarfile -e l.tar t` · espera: link criado (a sonda é real) · obtido: `t/lk -> /etc/hostname`
- S7 · fixture linkcopia-7z-bloqueia, com o sufixo `&& echo x >> ~/.forge-contrib/wt/q/docs/pedidos/v1.md`: `git clone ~/r ~/.forge-contrib/wt/q`, `git -C ~/.forge-contrib/wt/q checkout x`, `… stash pop` e `git worktree add ~/.forge-contrib/wt/q` · espera: código 2 · obtido: código 0
- S8 · laboratório em $TMPDIR: um repositório com `q -> /etc` versionado e depois `git clone r c` · espera: link criado (a sonda é real) · obtido: `c/q -> /etc`

## Detalhe dos achados
**A4.** Evidência: `hooks/conformidade.py:3907` (`EM_VIGOR_NO_TEXTO = r"\.claude(?![\w-])"`), usado em :1731 (destino opaco) e em `fechado_em_vigor`. Caminho de ataque: um papel que não é o jarvis, ou um conteúdo injetado, grava `.forge/versao`, `.forge/config.json` ou `.forge/run/` pela variável do `for` ou do `read`, ou grava `.git/config` (por exemplo, o `core.hooksPath`) por `$d` no texto do `-c`. O caminho literal e a atribuição única recusam (S1 e S3); só a forma opaca passa. Severidade: alta para `.git/config` (desliga os hooks do git, `R-VERIFY`) e média para `.forge/`. O sandbox nega `.git/config` e `.forge/versao` na sessão, mas não `.forge/config.json` nem `.forge/run/`. Correção mínima: `EM_VIGOR_NO_TEXTO` cobre os alvos em vigor do projeto que não ficam livres, que são `\.claude(?![\w-])`, `\.forge/(?:versao|config\.json|run)(?![\w-])` e `\.git(?![\w-])`. O `.githooks` continua fora, como no estreitamento (a), porque já recusa por outra regra. Fixtures novos: S1 a S3. O corpus legítimo tem de continuar passando, e a ele somam-se `cat .forge/config.json` e `git -C x log`. Esforço: P. Dono: o autor do hook (o tech-lead da E80.5).

**A5.** Evidência: `hooks/conformidade.py:3898` (`FECHADO_NA_LINHA` só casa `python … -c`) e :2432 (`args[0] != "-m"`). O próprio hook roda nesse interpretador, então esse extrator existe em toda máquina onde o hook roda. Nesta estação, `unrar`, `unsquashfs`, `bsdtar`, `7z`, `cpio` e `pax` não estão instalados. Caminho de ataque: igual ao da A2 da rodada anterior. O link vai num pacote gravado antes, a extração e a escrita no pedido ficam na mesma linha, e o hook resolve o caminho antes de o link existir (S4 e S6). Do mesmo jeito, a extração direta em `~/.claude/` passa (S5). Severidade: alta. Correção mínima: incluir em `FECHADO_NA_LINHA`, no modo que extrai, as formas `(python|pypy)… -m tarfile` com `-e` ou `--extract`, `(python|pypy)… -m zipfile` com `-e` ou `--extract`, `unrar` e `rar` com `x` ou `e`, `unsquashfs`, `bsdcpio` com `-i` ou `-p`, `unar` e `aunpack`. Também tirar a isenção do `-m` em :2432 quando o módulo é `tarfile` ou `zipfile`. Fixtures novos: S4 e S5, mais `python3 -m tarfile -l` como legítimo. Esforço: P. Dono: o mesmo da A4.

**A6.** Evidência: `hooks/conformidade.py:3908` (`CAMINHO_TROCADO_NA_LINHA` não tem o git) e o limite declarado em `docs/hooks.md` ("o git que restaura link … segue fora"). Caminho de ataque: o papel versiona `q -> ~/.forge-contrib` num repositório próprio, numa chamada sem o controle. Depois roda `git clone ~/r ~/.forge-contrib/wt/q && echo x >> ~/.forge-contrib/wt/q/docs/pedidos/v1.md` e grava as linhas `DECISÃO DO DONO` (S7 e S8). O sandbox não cobre essa pasta (A14). O motivo da A10 ("recusaria o git do dono") não vale aqui, porque a regra já exclui o jarvis e só dispara na linha que cita o pedido ou o brief da pasta de controle. Severidade: alta. Correção mínima, já pedida no item (3) da A2 anterior: na linha que cita o controle, para o papel que não é o jarvis, recusar o git que põe arquivos na árvore, que são `clone`, `checkout`, `switch`, `restore`, `stash` (`pop`, `apply` e `branch`), `reset --hard`, `worktree add`, `pull`, `merge`, `rebase`, `am`, `cherry-pick`, `read-tree -u` e `checkout-index`. A alternativa é manter o limite com o aceite do usuário (`R-DECISAO`). Um limite declarado pelo time não substitui esse aceite. Fixtures novos: S7. Esforço: P. Dono: o mesmo da A4.

## Riscos aceitos e ferramentas
Não há risco aceito. Ferramentas usadas: as sondas rodaram pelo `Fixture` e pelo `rodar` de `tests/test_hooks.py` sobre a base (`git archive 481d2855`) e sobre o head, mais um laboratório local em `$TMPDIR`. Lacunas: não há CI para o head (sem PR), e a suíte inteira não rodou.
