---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-hook-propria-copia
commit: bde062d7d009f4d2670967a03f5d05fb507fbc43
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 E88.7, hook `copia` (HOOK-AGENTE-FORA-DA-PROPRIA-COPIA), revalidação

Esta é uma revalidação por delta (R-REVIEW, H3). A rodada anterior foi o parecer reprovado no head 4ee59dfc, que está no git no commit cb4bb0b8. A suíte inteira não rodou aqui: ela roda só no CI, conforme o brief. As sondas rodaram no processo contra `hooks/copia.py`, com repositório, worktree e clones reais numa pasta temporária, e com `branches_do_agente` fixado na reserva `melhoria/x`.

Gatilhos: hook de controle (R-CONFORMIDADE), guarda de escrita do time, leitura do registro do R-TETO.

## Delta lido
Saída de `forge-check parecer delta`, intervalo `4ee59dfc..bde062d7`. No domínio, foram lidos `hooks/copia.py` (relido inteiro), `docs/hooks.md` (a linha do `copia` e os limites) e as 9 fixtures novas de `tests/hooks/copia/`. Fora do domínio, e por isso não relidos: changelog, `docs/hooks-fixtures.md`, mutantes e `tests/test_copia.py`.

## Achados anteriores
- A1 (bloqueante): corrigido. Com reserva e sem cópia achada, a raiz e tudo o que fica fora do controle recusam (`copia.py:226-233`). A raiz nunca vale como cópia (`copia.py:181`). `symbolic-ref` e `update-ref` contam como escrita. As sondas S1 a S3 foram refeitas e todas recusam.
- A2 (recomendado): corrigido (`copia.py:119-123` e `:80-103`). Prefixos, caminho do git, `GIT_DIR=`, `--git-dir` e `--work-tree` recusam.
- A3 (recomendado): corrigido (`copia.py:21-23`; o apelido por `-c` em `:93-98`).
- A4 (recomendado): corrigido nas formas sondadas (`copia.py:35-47`). Sobra o `<<` entre aspas ou em comentário, que virou o A5.

## Achados
- A5 (recomendado) hooks/copia.py:41 · O `<<FIM` entre aspas ou em comentário (`echo "<<EOF"`, `# <<EOF`) corta as linhas seguintes até `EOF`, e o bash executa essas linhas: um `git -C <raiz> commit` na linha 2 passa (S7). É o resto do A4: achar o `<<` fora de aspas e de comentário.
- A6 (recomendado) hooks/copia.py:119 · O git que vem depois de palavra do shell não é lido: `if …; then git commit; fi`, `do git add`, `! git`, `{ git …; }`, crase `` `git …` ``. Com o cwd na raiz (o do agente), `if ! git diff --quiet; then git commit -am x; fi` grava na raiz (S8).
- A7 (recomendado) hooks/copia.py:124 · Trocar de pasta por outro caminho que não `cd <dir>` deixa a pasta atual como alvo: `cd -P <raiz>`, `cd -- <raiz>`, `pushd <raiz>`, `env -C <raiz> git`, `export GIT_DIR=<raiz>/.git; git commit`, `git -c core.worktree=<raiz> checkout -f`. Rodados da própria cópia, todos passam (S9).
- A8 (recomendado) hooks/copia.py:77 · A opção de leitura vale em qualquer posição: `git stash push -- list` e `git worktree remove list` passam como leitura na raiz (S10). Em 4ee59dfc o `stash` recusava sempre: é o único afrouxamento não pedido do delta.
- A9 (recomendado) docs/hooks.md:14 · Limite não declarado: o hook julga a pasta, não a ref. Na própria cópia, `git push origin HEAD:<outra>` e `git switch -c outra && git commit` na mesma linha passam (S11). Basta declarar junto dos limites (só documentação).

## Sondas
- S1 · Write em `<raiz>/x`, reserva `melhoria/x`, worktree `wt` em `melhoria/x` · espera: recusa (2) · obtido: recusa (2)
- S2 · depois de `git switch -c outra` em `wt`: Write em `<raiz>/x`, Write em `wt/x`, `cd wt && git switch melhoria/x` · espera: recusa (2) nos três · obtido: recusa (2) nos três
- S3 · `git -C <raiz> symbolic-ref HEAD refs/heads/melhoria/x`; e, com o HEAD da raiz já na reserva, Write em `<raiz>/x` · espera: recusa (2) · obtido: recusa (2) nos dois
- S4 · A2: `timeout 60 git -C <raiz> push`, `env git`, `command git`, `/usr/bin/git`, `GIT_DIR=<raiz>/.git git commit`, `--git-dir=`, `--work-tree <raiz>` (cwd `wt`) · espera: recusa (2) · obtido: recusa (2) em todas
- S5 · A3: `git -C <raiz>` com `symbolic-ref`, `update-ref`, `branch -f`, `worktree add`, `read-tree -u`, `checkout-index -a -f`, `init`, `clone`, `-c alias.ci=commit ci` · espera: recusa (2) · obtido: recusa (2) em todas
- S6 · A4: `echo '<<'; cd <raiz> && git commit`, `cat <<< a; git -C <raiz> commit`, `cat <<EOF\nx\nEOF\ngit -C <raiz> commit` · espera: recusa (2) · obtido: recusa (2) nas três
- S7 · `echo "<<EOF"\ngit -C <raiz> commit -m x\nEOF` e `# <<EOF\ngit -C <raiz> commit -m x\nEOF` · espera: recusa (2) · obtido: libera
- S8 · `if ! git diff --quiet; then git commit -am x; fi` (cwd raiz); `true && { git -C <raiz> commit; }`; `for f in a; do git -C <raiz> add $f; done`; `! git -C <raiz> commit`; ``echo `git -C <raiz> commit` `` · espera: recusa (2) · obtido: libera em todas
- S9 · cwd `wt`: `cd -P <raiz> && git commit`, `cd -- <raiz> && git commit`, `pushd <raiz> && git commit`, `env -C <raiz> git commit`, `export GIT_DIR=<raiz>/.git; git commit`, `git -c core.worktree=<raiz> checkout -f HEAD -- .` · espera: recusa (2) · obtido: libera em todas
- S10 · cwd raiz: `git stash push -- list`, `git worktree remove list` · espera: recusa (2) · obtido: libera
- S11 · cwd `wt`: `git push origin HEAD:melhoria/outra`, `git switch -c outra && git commit -m x` · espera: limite declarado · obtido: libera, sem menção no docs/hooks.md
- S12 (corpus de legítimos) · Write em `wt/x`; `cd wt && git commit -m "$(cat <<'EOF' … EOF)" && git push`; `git log`, `git -C <raiz> show`, `git status`, `git diff`, `git branch -a`, `git worktree list` na raiz; clone próprio em `~/.forge-contrib/wt/` e em `<raiz>/.forge/wt/item`; Write em `~/.forge-contrib/docs/` · espera: libera · obtido: libera em todas
- S13 (`.forge/wt/`) · Write em `.forge/wt/outro` (HEAD `melhoria/y`), em `.forge/wt/novo` (não existe), na base `.forge/wt/a`, por symlink `.forge/wt/link -> <raiz>`, e `git clone -b melhoria/x <raiz> <raiz>/.forge/wt/novo` · espera: recusa (2) · obtido: recusa (2) em todas

## Detalhe dos achados
**A5.** Evidência: `copia.py:41`. O regex acha `<<` em qualquer lugar da linha, sem olhar aspas nem `#`. Caminho: forma deliberada, em que a linha que o bash executa some da leitura. Severidade: baixa. Correção mínima: ignorar o `<<` dentro de aspas e depois de `#`, tokenizando a linha com `shlex` antes de procurar o marcador. Outra saída: se o marcador aparece numa linha cujo `shlex` não mostra o token `<<`, ler o texto inteiro. Esforço P. Dono: autor do E88.1.

**A6.** Evidência: `copia.py:119-123`. O nome do comando é o primeiro token que não é atribuição, e só os `PREFIXOS` são pulados. Caminho: é o mais realista desta rodada. O cwd do agente volta à raiz da sessão e `if`, `for` e `{ }` são formas comuns, então o agente que esquece o `cd` grava na raiz sem recusa. Severidade: média. Correção mínima: somar a `PREFIXOS` as palavras do shell `if then elif else while until do ! { time` e tirar a crase do começo do token. Uma regra mais curta, que cobre também `sudo`, `xargs` e `find -exec` (hoje limites declarados): tomar o primeiro token do segmento cujo `basename`, sem crase, é `git`. Esforço P. Dono: autor do E88.1.

**A7.** Evidência: `copia.py:124-126` (o `cd` lê só o primeiro argumento e não conhece opção), `:83` (`GIT_DIR=` só vale como atribuição do próprio comando) e `:89-92` (`-c core.worktree=` não é lido). Caminho: forma deliberada, rodada da própria cópia, que executa o git na raiz. Severidade: baixa. Correção mínima:
- no `cd`, pular `-P`, `-L`, `-e` e `--`;
- tratar `pushd` como `cd`, e `popd` como pasta incerta;
- ler `env -C` e `--chdir=` como troca de pasta;
- fazer `export GIT_DIR=` e `GIT_WORK_TREE=` valerem para os comandos seguintes da linha;
- pôr `-c core.worktree=<p>` em `extras`, como o `--work-tree`.

O que não for corrigido entra nos limites do `docs/hooks.md`, um por um. Esforço P. Dono: autor do E88.1.

**A8.** Evidência: `copia.py:24-27` e `:77` (`OPCAO_DE_LEITURA.get(sub).intersection(args)`). Caminho: `list` ou `show` usado como caminho ou como nome de worktree. É pouco provável sem intenção, mas afrouxa frente a 4ee59dfc. Severidade: baixa. Correção mínima: em `stash` e `worktree`, só é leitura quando o primeiro argumento sem opção é `list` ou `show`; para as opções (`-l`, `--check`), manter a interseção. Esforço P. Dono: autor do E88.1.

**A9.** Evidência: `docs/hooks.md:14` e `:149` não falam de ref nem de refspec. Caminho: o agente erra a branch de destino no push. A branch remota é guardada por outro controle (proteção de branch, pre-push). Severidade: baixa. Correção mínima: uma frase nos limites: "o hook julga a pasta, não a ref: `git push origin HEAD:<outra>` e a troca de branch seguida de commit na mesma linha passam". Esforço P. Dono: autor do E88.1.

## Respostas ao brief
- **Clones em `.forge/wt/` como cópia.** Aceitável. Só vale o clone cujo HEAD está na reserva; o clone inexistente, a base, o de outra branch e o symlink para a raiz recusam (S13; `realpath` em `copia.py:69` e `:150`). Para criar ali um clone com o HEAD na reserva, o agente precisa de `git clone` ou `init` (recusam, porque o destino não tem HEAD) ou de `tee`/`cp` (limite declarado).
- **Agente preso depois de trocar de branch.** Correto pelo lado da segurança: falha fechada (S2), declarada no `docs/hooks.md:149` com a saída (a sessão principal faz o `switch`). O custo é operacional e raro.
- **`git worktree list` e o HEAD do clone citado.** Melhor que a varredura de `wt/`. Só o clone do alvo é lido, o custo de ler 2014 clones some e a raiz sai da lista (`copia.py:181`). Se o `git` falha (limite de 5 s), o `executar` sai com 0, o mesmo da HOOK-ESTADO-ILEGIVEL-LIBERA. O HEAD com `gitdir:` relativo cai em None e recusa.
- **Limites declarados** (`cp`, `mv`, `tee`, `rsync`, `ln`, `bash -c`, `sudo`, `xargs`, `find -exec`, alias em `.git/config`, destino em variável). Aceitos como limite: todos pedem uma forma deliberada de gravar ou rodar git fora da cópia, e a defesa de fundo são o sandbox e o CI. O agente pode gravar o `.git/config` da própria cópia (alias, `core.worktree`, hooks do git); isso cabe em "alias em .git/config" e em "script". As formas que não estão declaradas viraram A6, A7 e A9.
- **Tamanho (255 linhas, teto de 150).** Justificado: quase todo o crescimento vem da correção dos achados A1 a A4 desta frente e do A1 do review (heredoc, prefixos, opções do git, formas de leitura, troca da varredura). Para o código não crescer de novo a cada rodada, corrigir o A6 pela regra curta (primeiro token `git` do segmento) é melhor que somar listas.
- **Só aperta?** Frente à base, sem o hook, sim: o hook só acrescenta a saída 2, o erro interno sai com 0, a sessão principal fica de fora e a única gravação é no erros.log. Frente a 4ee59dfc, a mudança afrouxa de propósito em dois pontos: o clone de `.forge/wt/` na reserva e as formas de leitura (`tag -l`, `stash list`, `apply --check`, `branch -a`, `symbolic-ref --short`, `worktree list`). Afrouxa sem querer no A8. No resto, aperta (A1).

## Plano em cartões
- A5 a A9: autor do E88.1, nesta branch, antes do merge.
- Os cartões da rodada anterior continuam: ler o destino de `cp`, `mv`, `tee`, `sed -i`, `install`, `rsync`, `ln` (item futuro) e registrar no `docs/hooks.md` que a raiz vem de `hook.cwd()`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do delta e sondas no processo. A varredura de segredos e de dependências não se aplica, porque o delta não traz segredo nem dependência nova.
