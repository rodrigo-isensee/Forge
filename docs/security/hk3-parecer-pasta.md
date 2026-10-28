---
tipo: revisao-seguranca
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: bfd9e70ad2325fd5a04a2104fe041d4346384042
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: hk3-parecer-pasta (HK3-PARECER, PR A, E1 e E3), volta 1

Diff revisado: `ff3936ae4011a95f25c37280fe32e4fa5ced0d95...bfd9e70ad2325fd5a04a2104fe041d4346384042`. Revalidação por delta sobre o parecer `0178739` (`forge-check delta --parecer`, intervalo `212203a..bfd9e70`): `hooks/parecer.py` +61 -17 (`SENSIVEIS`, `com_til` com o HOME da linha, `entre_apostrofos`, `juntar_crases`, `resolver` com crase e `$( )`, `depois_do_cd` com o CDPATH mexido, `conferir` com o valor None), 22 fixtures `pasta-*` novas e as specs de mutantes 1 a 3 e 5 a 8. Requisito: a regra que separa, do modelo de ameaças (`~/.forge-contrib/docs/security/hk3-parecer-ameacas.md`, E1 e E3), e a decisão técnica de 2026-10-28 11:49.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`hooks/parecer.py`, o portão R-REVIEW/R-QA na entrada da integração). A mudança não toca pipeline, contêiner nem IaC, não mexe em segredo e não usa rede.

## Achados
- A3 (bloqueante) hooks/parecer.py:582 · regressão (defeito provado), critério mudou: a forma com variável a partir da integração prova regressão; `W=<wt>; (cd $W); git merge`, `cd $W | true; git merge` e `cd $W & git merge` passam (rc=0, na base rc=2), e o bash mescla na integração
- A4 (bloqueante) hooks/parecer.py:55 · regressão (defeito provado), critério mudou: a forma a partir da integração prova regressão; `W=<integração>; test -d /nao && W=<wt>; cd $W && git merge` passa (rc=0, na base rc=2), e o bash fica com o W da integração
- A5 (bloqueante) hooks/parecer.py:262 · regressão (defeito provado), critério mudou: a forma com variável a partir da integração prova regressão; `W=<wt>; cd $W/nao/..; git merge` passa (rc=0, na base rc=2), e o cd do bash falha e mescla na integração
- A9 (bloqueante) hooks/parecer.py:257 · regressão (defeito provado), mesma classe do A2: `$` que o bash não expande fora dos apóstrofos é substituído; `W=<wt>; cd \$W; git merge`, `cd "$"W;`, `cd $\W;`, `cd "$"{W};` e a forma com quebra de linha passam a partir da integração (rc=0, na base rc=2)
- A7 (recomendado) hooks/parecer.py:577 · gh pr com pasta não resolvida (pushd, cd $UNK) usa o cwd da sessão; igual na base
- A8 (recomendado) hooks/parecer.py:57 · source e . (e os invólucros env, env -C, command, exec, builtin cd, função) não tornam a pasta nem o GIT_DIR desconhecidos; igual na base; cartão próprio
- A10 (recomendado) hooks/parecer.py:134 · cd depois de palavra-chave (then, do, else, `{`) não é visto: a partir da worktree, `if :; then cd <integração>; fi; git merge`, `{ cd <integração>; }; git merge` e `for d in 1; do cd <integração>; done; git merge` passam (rc=0, igual na base)
- A11 (recomendado) hooks/parecer.py:240 · CDPATH e HOME por `for`/`select` (`for CDPATH in <integração>; do cd src && git merge; done`) e por nameref (`declare -n R=CDPATH; R=<integração>`) não tornam a pasta desconhecida (rc=0, igual na base); nameref é ofuscação, fora do lote

## Revalidação dos achados anteriores
- **A1 (CDPATH da linha): resolvido.** Sondas a partir da worktree, todas rc=2 em `bfd9e70` e rc=0 na base: `export CDPATH=`, `declare -x`, `declare` sem `-x`, `typeset -x`, `readonly`, `read`, `IFS= read -r`, `mapfile -t`, `printf -v`, `export CDPATH+=`, atribuição simples `CDPATH=x;`, prefixo `CDPATH=x cd src` e a forma em três linhas. Os casos de `for`/`select` e de nameref ficam no A11, como recomendado: não estão na lista da decisão de 11:49 e já passavam na base.
- **A2 (`$NOME` entre apóstrofos): resolvido para os apóstrofos.** `cd '$W'`, `cd '${W}'` e a forma com quebra de linha dão rc=2, e `cd $'$W'` também. A desincronia do `entre_apostrofos` com apóstrofo em comentário, em heredoc ou em `$'\''` não abre contorno: as três formas recusam por outra guarda (rc=2). A classe, porém, não fechou: o `$` escapado por barra invertida ou cortado por aspas cai no A9.
- **A6 (HOME na linha): resolvido pelo delta.** `export HOME=<integração>; cd ~` e `cd` sozinho, `HOME=<integração> cd`, `read HOME; git -C ~` dão rc=2. Sai da lista.
- **Crase e `$( )` na pasta (A1 do QA):** `git -C` com crase sem aspas, com crase entre aspas duplas e com `$(echo <wt>)`, e `cd` com crase, dão rc=2 (na base, a crase sem aspas passava).
- **GIT_DIR por `read` e `printf -v` com `export`:** rc=2.

## Detalhe dos achados
Sondas: `$TMPDIR/security-engineer-hk3-parecer-pasta/sondas2/` (`r1.json` a `r5.json`, rodadas com `../sondas/sonda.py`, a mesma fixture do corpus: `proj` em `develop`, worktree `home/wtx` em `melhoria/x`, sem parecer). Cada sonda rodou contra o hook de `bfd9e70`, o de `212203a` (worktree `~/.forge-contrib/wt/wt-seg-hk3-v0`) e o da base `ff3936a` (`~/.forge-contrib/wt/wt-seg-hk3-base`). As saídas estão em `novo-*.txt` e `base-*.txt`. "Integração" é o cwd em `proj`. O que o bash faz com cada forma foi conferido no shell (`cd \$W`, `cd "$"W`, `cd $\W` e `cd "$"{W}` dão "No such file or directory" e ficam na pasta de antes).

**Por que A3, A4 e A5 passam a bloquear (critério mudou).** No parecer `0178739`, A3, A4 e A5 ficaram como recomendados com a nota "já na base". Isso só vale para a forma literal, que a base já resolvia. Na forma com variável, a partir da integração, a base recusava (ela não resolvia `$W`), e a branch passa. É a mesma classe de regressão que fez o A2 bloquear. As formas já passavam em `212203a`: a falha foi da minha varredura da primeira rodada, que mediu esses três só pela forma literal. O delta não as introduziu. Vão juntas nesta passada, com o A9, para não abrir outra rodada por achado.

**A3 · cd fora do shell de fora (bloqueante, regressão).** Evidência: `conferir` (`:582`) aplica o `cd` sem olhar `soltos` (`:183`). Sondas a partir da integração: `W=<wt>; (cd $W); git merge melhoria/x`, `W=<wt>; cd $W | true; git merge melhoria/x` e `cd $W & git merge` dão rc=0 em `bfd9e70` e em `212203a`, e rc=2 na base. O bash roda o `cd` num subshell e mescla na integração. A forma `cd $W || git merge` não faz dano, porque o merge só roda quando o cd falha, e aí a pasta não existe e o hook recusa. Caminho de ataque: erro honesto de agrupamento (`( )`, pipeline, `&`) a partir do cwd da sessão. O merge local entra na integração sem parecer. Severidade: baixa (o envio segue barrado pelo pre-push e pela proteção de branch). Correção mínima: `cd` que não é solto (`soltos(leitura)[i]` falso) não muda a pasta dos comandos seguintes. Esforço: P. Dono: `tech-lead`.

**A4 · atribuição à direita de `&&` (bloqueante, regressão).** Evidência: `SEGUE` (`:55`) conta `&&` como ligação sem condição também para o comando à direita, então `efeito_nas_variaveis` (`:233`) fixa o `W`. Sonda a partir da integração: `W=<integração>; test -d /nao && W=<wt>; cd $W && git merge melhoria/x` dá rc=0 (na base, rc=2). O bash não roda a segunda atribuição e mescla na integração. Severidade: baixa. Correção mínima: a atribuição cujo comando vem depois de `&&` (ou de `||`) vai para `ruins` (valor None), e o `&&` só vale como ligação sem condição para o comando à esquerda. Esforço: P. Dono: `tech-lead`.

**A5 · `normpath` antes da existência (bloqueante, regressão).** Evidência: `resolver` (`:262`) passa o caminho por `os.path.normpath`, que apaga `nao/..` antes do `is_dir`. Sonda a partir da integração: `W=<wt>; cd $W/nao/..; git merge melhoria/x` dá rc=0 (na base, rc=2). O `cd` do bash falha, porque `nao` não existe, e o merge roda na integração. Correção mínima: conferir `os.path.isdir` do caminho cru (sem normalizar) antes de aceitar o `cd`. No `-C`, usar `os.path.realpath`, porque o git faz `chdir` físico e segue o link antes do `..`. Esforço: P. Dono: `tech-lead`.

**A9 · `$` que o bash não expande fora dos apóstrofos (bloqueante, regressão, classe do A2).** Evidência: `resolver` (`:257`) substitui o `$NOME` da palavra que o `shlex` já tirou das aspas e da barra invertida. `entre_apostrofos` (`:197`) só marca os nomes entre apóstrofos. Sondas a partir da integração, rc=0 em `bfd9e70` e em `212203a` e rc=2 na base:
- `W=<wt>; cd \$W; git merge melhoria/x`
- a mesma linha com quebra de linha no lugar do `;`
- `W=<wt>; cd \${W}; git merge melhoria/x`
- `W=<wt>; cd "$"W; git merge melhoria/x`
- `W=<wt>; cd $\W; git merge melhoria/x`
- `W=<wt>; cd "$"{W}; git merge melhoria/x`

O bash tenta a pasta literal `$W` (ou `${W}`), falha e mescla na integração. Com `&&` o merge não roda. `git -C \$W merge` falha no git. Essas duas formas não fazem dano. `cd $''W` e `cd $""W` já recusam por outra guarda. Caminho de ataque e severidade: os do A2. Correção mínima: substituir só o `$NOME` ou `${NOME}` que, no texto cru da palavra, aparece inteiro e contíguo, fora de apóstrofos e sem `\` antes do `$`. Qualquer outro `$` que sobra na palavra tirada das aspas torna a pasta desconhecida (None). Uma marca no `leituras`, como o `OPACO`, ou uma tokenização que preserve as aspas resolve o A2 e o A9 juntos. Fixtures: `pasta-barra-cd-variavel-com-barra-invertida` (`;` e quebra de linha) e `pasta-barra-cd-variavel-com-dolar-entre-aspas` (`"$"W`, `$\W`, `"$"{W}`). Esforço: P a M. Dono: `tech-lead`.

**A7, A8, A10 e A11 (recomendados, não devolvem).** Todos passam igual na base, então não são regressão, e nenhum está na lista do requisito. Ficam como dimensões novas da matriz (skill `cyber-security`).
- A7: com a pasta desconhecida, `raiz_gh` (`:577`) usa o cwd da sessão. Correção: com a pasta desconhecida, `gh pr create`/`ready` sem `--head` recusa. P.
- A8: `source` e `.` estão em `LE_VARIAVEL` (`:57`) e só limpam as variáveis. Os invólucros `env GIT_DIR=`, `env -C`, `command git`, `exec git`, `builtin cd`, `command cd` e função não são reconhecidos. É classe vizinha da ofuscação. Cartão próprio. M.
- A10: `analisar` (`:134`) só reconhece o `cd` como primeira palavra, e depois de `then`, `do`, `else` ou `{` a palavra é a chave. A pasta não muda, e o merge seguinte é julgado no cwd. Correção: tirar a palavra-chave de `ABRE` antes do `analisar`, e o `cd` dentro do bloco torna a pasta desconhecida (ele não é solto). P.
- A11: o `for`/`select` não chega ao `LE_VARIAVEL` (`:240`) como comando, porque `ABRE` o trata como palavra-chave. O nameref (`declare -n`) liga um nome a outro. Correção: `for`/`select` com nome em `SENSIVEIS` torna a pasta desconhecida. O nameref fica com a ofuscação. P.

**Contornos do modelo de ameaças (E1 e E3): seguem barrados (rc=2).** A suíte do item (`python3 -m unittest tests.test_hooks_parecer_pasta`) dá OK, e as formas legítimas passam (rc=0): `cd <literal> && git pull --rebase origin <b> && git push`, `W=<wt>; cd "$W" && git pull --rebase ... && git push` e `cd src && git merge` na worktree.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. A3, A4, A5 e A9 precisam de correção, ou de aceite do dono por `docs/security/aceites/`. Os recomendados não pedem aceite.

Ferramentas: só sondas locais e passivas (Python da biblioteca padrão, o `tests/test_hooks.py` do repositório, o bash). Não houve rede, exploit nem sistema externo. `gitleaks`, `semgrep` e `zizmor` não se aplicam a este diff (só Python de hook e JSON de teste, sem segredo nem workflow). Não foram rodadas.

PA-7 (`docs/engineering/achados-recorrentes.md`): a lista estava vazia. A classe "pasta do git calculada diferente do bash" se repetiu neste pedido (A1 e A2 na primeira rodada, A9 e os promovidos A3 a A5 nesta), por isso entra como AR-1 no mesmo commit.
