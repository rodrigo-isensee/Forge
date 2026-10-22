---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: a1a9f846f4c8521b9be147ea1890f407348b7fea
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: lote-leitura-hook

Escopo: a entrega inteira (`git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 a1a9f846f4c8521b9be147ea1890f407348b7fea`), com revalidação por delta desde o parecer anterior sobre f8e00ae (`forge-check delta --parecer`): 419bcdf (lista positiva dos outros comandos do comando lógico), 09d8ce5 (o comando lógico junta linhas com `(`, aspa ou crase sem par) e a1a9f84 (`sort` fora dos leitores). O delta toca controle do Forge (`hooks/_comum.py`, usado pelo `conformidade` e pelo `parecer`) e foi relido inteiro, com sondas.

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: a entrega muda a leitura da linha nos hooks `conformidade` e `parecer`, que garantem R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA.

## Achados
- A1 (bloqueante) hooks/_comum.py:997 · git push na lista positiva aceita qualquer opção e atribuição antes: cat > x.sh <<'EOF' && git push --receive-pack='sh x.sh' . HEAD (ou --exec=, ou GIT_SSH=sh git push ssh://x.sh/r) roda o corpo e libera push main e merge que a base recusava

## Detalhe dos achados
Sondas: cópias por `git archive` da base (ad6d96c) e do HEAD (a1a9f84) em `$TMPDIR`, hook real pelo `Fixture`, `montar_proc` e `rodar` de cada cópia, com os modelos `conformidade/heredoc-outro-comando-make-push-main-bloqueia` e `parecer/forge-clone-pr-merge-no-corpo-de-heredoc-pipe-com-bash-depois-do-fim-bloqueia` (review reprovado). No corpo, `git push origin main` ou `gh repo delete d/p --yes` (conformidade) e `gh pr merge feature/x --repo … --merge` (parecer). A execução foi confirmada no bash local com `env -i`, num repositório descartável em `$TMPDIR`, só com `echo`.

**A1 (média; regressão de 419bcdf nos dois hooks).** Evidência: `hooks/_comum.py:997` aceita `git` com subcomando em `GIT_OUTRO_SEM_O_CORPO` (`hooks/_comum.py:843`: `add`, `push`, `status`) sem olhar os argumentos, e `programas_da_linha` (`hooks/_comum.py:977`) descarta as atribuições antes do programa. O `git push` roda um programa escolhido na própria linha: `--receive-pack=<cmd>` e `--exec=<cmd>` (e os prefixos únicos que o git aceita) com destino local o rodam pelo shell; `GIT_SSH=sh` antes de `git push ssh://x.sh/r` roda `sh x.sh …`. Confirmei no bash local que `cat > x.sh <<'EOF' && git push --receive-pack='sh x.sh' . HEAD` e `cat > x.sh <<'EOF' && GIT_SSH=sh git push ssh://x.sh/r HEAD` rodam o corpo. Resultados (base, HEAD): `--receive-pack` com `git push origin main` no corpo dá 2 (R-MAIN) e 0 no `conformidade`; com `gh repo delete` no corpo, 2 e 0; `--exec=./x.sh`, 2 e 0; `GIT_SSH=sh`, 2 e 0. No `parecer`, `--receive-pack` e `GIT_SSH=sh` com `gh pr merge` no corpo dão 2 (R-REVIEW) e 0. Formas com espaço no valor da atribuição ou com `${IFS}` seguem recusadas (o espaço faz o hook ler outro programa, e o `${` com ação crítica cai no marcador da ADR 0011), e `chmod` fora da lista fecha `GIT_SSH_COMMAND=./x.sh` e afins.
Caminho de ataque: o mesmo do A1 anterior. A sessão, por erro ou por instrução injetada num texto não confiável, grava o comando num arquivo pelo heredoc e o roda no mesmo comando lógico por um `git push` com opção ou ambiente que executa programa. O push para a `main` ou o merge sem review passam pelos dois hooks, que na base os seguravam. Isso afrouxa o processo, o que a decisão do dono de 2026-10-15 veda.
Correção mínima: no `outro_sem_o_corpo`, o comando com atribuição antes do programa sai da lista positiva (o `programas_da_linha` passa a informar a atribuição, ou o `outro_sem_o_corpo` relê o trecho), e o `git push` só entra sem opção que o git leia como `--receive-pack` ou `--exec` (mais fechado: só com opções de uma lista curta, como `-u`, `--set-upstream`, `--tags`, `--follow-tags`, `-n`, `--dry-run`). O caso medido pelo review (`git add x && git commit -m "$(cat <<'EOF'` … `&& git push origin feature/x`) segue passando, como sondei no HEAD (0). Mais uma fixture `-bloqueia` por forma (`--receive-pack`, `--exec`, `GIT_SSH=`) nos dois hooks. Esforço P. Dono: `tech-lead`.

**Revalidação dos achados anteriores (3e5d570).**
- A1 anterior (lista negativa `RODA_TEXTO`): resolvido no que pedia. `&& chmod +x x.sh && ./x.sh`, `; ./x.sh`, `|| ./x.sh`, `&& make`, `&& git -c alias.x='!sh x.sh' x` e o `./x.sh` noutra linha dão 2 nos dois hooks do HEAD. A lista positiva (`cd`, `mkdir`, leitores, `git add/push/status` sem `-c`) está certa na forma; sobra o furo dos argumentos do `git push` e das atribuições (A1 acima).
- A2 anterior (substituição que fecha noutra linha): resolvido. `x=$(cat <<'EOF'`⏎corpo⏎`EOF`⏎`); eval "$x"` e `) && $x` dão 2 no `parecer` do HEAD (0 em f8e00ae). `abertos_na_linha` lê aspas simples sem escape, `$(` entre aspas duplas, crase e comentário no começo de palavra; na dúvida a pilha cresce e o comando lógico também, o que só deixa o hook mais desconfiado. Sondei ainda `${y%)}` numa linha do meio e `$'…'` com aspa escapada: dão 2.
- A3 anterior (`sort --compress-program`): resolvido. `sort` saiu de `LEITORES_DO_CORPO` (`hooks/_comum.py:956`); `cat <<'EOF' | sort -S 1k --compress-program=sh` dá 2 no `parecer`, e a fixture nova do `conformidade` cobre o `<<` direto.
- Risco apontado pelo autor (`git push`/`git status` na lista com heredoc que grava o hook de pre-push): fechado por outra camada. `cat > .git/hooks/pre-push <<'EOF' && git push origin feature/x` e `cat > .githooks/pre-push <<'EOF' && git push …` dão 2 na base e no HEAD (R-CONFORMIDADE, escrita em `.git/hooks/` e em arquivo em vigor). O `git status` com `core.fsmonitor` só chega por `-c` (fora da lista), por `--config-env`/`GIT_CONFIG_*` (hoje recusados por espaço, `${` ou `chmod` na linha) ou pela configuração do repositório (protegida); a correção do A1 sobre as atribuições também fecha esse caminho.
- R6 (script gravado e executado na linha seguinte) segue como recomendação, no limite documentado em `docs/hooks.md`.

## Recomendações
- R1: `cat > .gitconfig <<'EOF' && HOME=. git status` com `core.fsmonitor` no corpo dá 0 na base e no HEAD. Não é regressão, mas a correção do A1 (atribuição antes do programa sai da lista) o fecha sem custo.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check delta --parecer`, leitura do diff, sondas do hook real em cópias por `git archive` da base e do HEAD em `$TMPDIR`, e bash local com `env -i`, só com `echo`, num repositório descartável sem remoto, para confirmar a execução. `gitleaks`, `zizmor` e `actionlint` não se aplicam, porque a entrega não tem segredo, workflow nem dependência. Nada foi instalado, nada saiu da máquina e nada foi gravado fora de `$TMPDIR`, além deste parecer.
