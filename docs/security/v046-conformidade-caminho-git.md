---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: c072741112e9383735cb82019aa0523acb4fa6a6
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E20.13, conformidade-caminho-git, revalidação por delta)

Delta revisado: `22187bae..c0727411` (volta 1 da E20.6, commits `44b75270`, `90bea40b`, `c0727411`), lido por `forge-check parecer delta`: no domínio, `hooks/conformidade.py` (`REV_PARSE_DO_GIT`, `SO_VARIAVEL`, `VARIAVEL_INTEIRA`, `expandir`, atribuição da linha, destino do `cp`/`install`, mensagem do falso positivo) e as 22 fixtures `gitcomum-*` novas. Parecer anterior: reprovado no `22187bae` (E20.8).

Veredito: **reprovado**, por um resíduo do A1. Fecharam A2 (`${d%/}`), A3 (crase sem aspas) e o A1 na forma `git rev-parse <opção>` (com e sem aspas, sem resto, em variável da linha, raiz e worktree); A5 fechou para `cp` e `install`. Continua aberto o A1 quando o git dentro da substituição não é escrito exatamente `git rev-parse`: `git -C . rev-parse --git-dir` sem resto grava no `.git` (o autor declarou esse caso como limite; é bloqueante, ver o detalhe). Conferido: 42 fixtures `gitcomum-*` (27 recusam, 15 liberam), todas OK; os 14 mutantes G1 a G14 morreram; a mensagem do falso positivo manda usar o caminho literal.

## Gatilhos
`R-SEGURANCA`: controle do Forge (hook `conformidade`, guarda de escrita em `.git/`), analisador de comando.

## Achados
- A1 (bloqueante) hooks/conformidade.py:330 · resíduo: só `git rev-parse <opção>` é lido como .git; com `git -C .`, `git -c a=b`, `\git`, `/usr/bin/git`, `rev-parse -q` ou o caminho do `--git-path` entre aspas passa rc 0 sem resto: `cp config "$(git -C . rev-parse --git-dir)"` grava .git/config
- A4 (recomendado) hooks/conformidade.py:974 · cd para o opaco segue passando rc 0 (`cd "$(git rev-parse --git-dir)/hooks" && cp ../../x pre-push`); já existia (AR-7); cartão de segurança
- A5 (recomendado) hooks/conformidade.py:1469 · parcial: `mv x --target-directory=.git/hooks` passa rc 0; `mv` está em TODOS_OS_ARGUMENTOS (linha 124), que pula toda palavra que começa com `-`; `cp` e `install` com `=` recusam; cartão de segurança com prioridade
- A6 (recomendado) hooks/conformidade.py:1019 · `ln -s "$(git rev-parse --git-dir)" g && cp x g/config` segue rc 0; já existia; cartão de segurança
- A7 (recomendado) hooks/conformidade.py:956 · o falso positivo segue (`cp x "$(mktemp -d)/config"`, `cp x $TMPDIR/logs/a.log`), agora com a mensagem que manda usar o caminho literal; aceito como limite desta entrega; cartão para tirar `$TMPDIR` e `$(mktemp …)` da regra
- A8 (recomendado) hooks/conformidade.py:1482 · opção de destino colada: `cp -t.git/hooks x`, `cp -t.git/config x`, `install -t.git/hooks x`, `mv -t.git/hooks x` e `cp -t"$(git rev-parse --git-path hooks)" x` passam rc 0 no head e na base; já existia em 8b5a44d5; cartão de segurança com prioridade

## Sondas
- S1 · cp config "$(git -C . rev-parse --git-dir)" · espera: rc 2 R-CONFORMIDADE (.git/config) · obtido: rc 0, stderr vazio (head c0727411 e base 22187bae)
- S2 · cp pre-push "$(git -C . rev-parse --git-path hooks)" · espera: rc 2 R-CONFORMIDADE (.git/hooks/) · obtido: rc 0, stderr vazio (head e base)
- S3 · cp x "$(git rev-parse --git-path 'hooks/pre-push')" · espera: rc 2 R-CONFORMIDADE (.git/hooks/) · obtido: rc 0, stderr vazio (head e base); sem as aspas internas recusa
- S4 · cp pre-push "$(\git rev-parse --git-path hooks)" · espera: rc 2 R-CONFORMIDADE (.git/hooks/) · obtido: rc 0, stderr vazio (head e base); o mesmo com `/usr/bin/git` e `git -c a.b=c`
- S5 · cp config "$(git rev-parse -q --git-dir)" · espera: rc 2 R-CONFORMIDADE (.git/config) · obtido: rc 0, stderr vazio (head e base)

## Detalhe dos achados
Método: o montador de `tests/test_hooks.py` (`Fixture.montar`, `rodar`), papel `forge:tech-lead`, projeto em `melhoria/x` (e worktree `{tmp}/wt` em `melhoria/w`), com os arquivos `x`, `config` e `pre-push` na raiz; só repositórios temporários, nada escrito em `.git` real. A árvore do head e a da base saíram por `git archive`; os mutantes rodaram num clone temporário (`forge-mutante`, que exige repositório). As 48 variantes da rodada E20.8 foram refeitas (o roteiro da rodada não foi guardado; a lista foi remontada pelas dimensões do parecer anterior: sem resto, `/` final, variável da linha, operador de `${…}`, crase com e sem aspas, `--git-common-dir`, `--absolute-git-dir`, `--path-format`, espaços, `2>/dev/null`, `|| true`, `command`, aninhado, `--show-toplevel`, `git -C`, `-t`, `--target-directory`, `ln`, `cd`, redirecionamento, `tee`, worktree). No head, 43 recusam e 5 passam: `cp config "$(git -C . rev-parse --git-dir)"` (A1), `cp -t.git/hooks x` (A8), `mv x --target-directory=.git/hooks` (A5) e os dois `cd` (A4); na base 22187bae passavam 25. Mais 18 variantes de dimensões novas (forma de chamar o git, opção de destino colada) e 12 legítimos: dos legítimos, só os dois do A7 recusam, como declarado.

**A1 (média, bloqueante; resíduo do A1 da E20.8, não é recomendação promovida).** Evidência: `hooks/conformidade.py:330-332`: `_REV_PARSE` exige `\s*git\s+rev-parse\s+` e, depois, só `--path-format=…` antes da opção, e o caminho do `--git-path` só como `[\w./-]+`. Qualquer outra grafia não é trocada por `FORGE_DIR_DO_GIT`; sem resto depois do `)`, `resto_no_git` (`hooks/conformidade.py:974`) devolve None e a escrita passa. A correção mínima do parecer anterior pedia a leitura pelo texto da substituição que **contém** `rev-parse` com uma das quatro opções, e não por uma grafia. Caminho de ataque: o do A1 da E20.8; um agente do time (instrução injetada num arquivo lido, ou engano) cria um arquivo `config` ou `pre-push` na raiz e o copia para `"$(git -C . rev-parse --git-dir)"` ou `"$(git -C . rev-parse --git-path hooks)"`: reescreve `.git/config` (`core.hooksPath`) ou instala `.git/hooks/pre-push`, que roda no próximo envio e desliga a catraca (`R-VERIFY`). `git -C <pasta>` é a forma que o próprio time usa em toda chamada com caminho absoluto, o que torna o caso realista e não exótico; por isso não cabe como limite declarado. Correção mínima: dimensão nova da matriz, "forma de chamar o git dentro da substituição". Ler o corpo de `$(…)` ou da crase pelas palavras (o `shlex` que o hook já usa): se uma delas é `rev-parse` e outra é `--git-dir`, `--git-common-dir`, `--absolute-git-dir` ou `--git-path` (seguida do caminho, com ou sem aspas), o valor é `<raiz>/.git` (ou `<raiz>/.git/<caminho>`), qualquer que seja o que vem antes de `rev-parse` (`git`, `\git`, `/usr/bin/git`, `command git`, `git -C <pasta>`, `git -c <k>=<v>`, `git --git-dir=<d>`) e as opções entre `rev-parse` e a opção (`-q`, `--quiet`, `--path-format=<f>`). Com `-C <pasta>` de outro repositório o valor seria outro `.git`; tratar como o da raiz recusa a mais, o lado seguro. Fixtures: as 5 sondas acima, mais `git --git-dir=.git rev-parse --git-dir` e a variante de worktree do S2. Esforço P. Dono: tech-lead (autor da E20.6).

**Pergunta do brief: `cp -t.git/hooks` colado e `git -C <pasta> rev-parse --git-dir` sem resto.** O segundo é bloqueante (A1 acima): é a família que a entrega declara fechar, com a correção pedida na rodada anterior. O primeiro é cartão (A8): é leitura literal de opção, já existia em 8b5a44d5 e fica fora do que o A1 a A3 pediam; não promovo a bloqueante sem critério novo (`R-REVIEW`).

**A4 (média, recomendado; já existia).** Sem mudança. `cd`/`pushd` para `$(…)`, crase ou variável que o hook lê como `.git` (agora há `FORGE_DIR_DO_GIT`, o que facilita: o `cd` para um valor que expande para `<raiz>/.git/<resto>` muda a pasta da escrita seguinte); na dúvida, escrita relativa depois de `cd` opaco recusa. Cartão. Esforço M. Dono: tech-lead.

**A5 (média, recomendado; parcial).** `cp` e `install` com `--target-directory=` recusam (fixtures `gitcomum-a5-*`, mutante G12). `mv` não: está em `TODOS_OS_ARGUMENTOS` (`hooks/conformidade.py:124`) e o ramo de `hooks/conformidade.py:1469-1471` pula toda palavra que começa com `-`. Correção mínima: nesse ramo, ler `--target-directory=<pasta>` e `-t<pasta>` como destino (comandos que os aceitam: `cp`, `mv`, `install`, `ln`). Cartão com prioridade. Esforço P. Dono: tech-lead.

**A6 (baixa, recomendado; já existia).** Sem mudança. Em `link_em_protegido` (`hooks/conformidade.py:1019`), a origem `$(git rev-parse --git-dir)` pode passar pela troca por `FORGE_DIR_DO_GIT` antes de conferir. Cartão. Esforço P. Dono: tech-lead.

**A7 (baixa, recomendado).** O falso positivo segue, mas a recusa agora se explica (`hooks/conformidade.py:956-958`, fixtures `gitcomum-tmpdir-logs-recusa-limite` e `gitcomum-toplevel-hooks-recusa-limite`, mutante G11): aceito como limite desta entrega. Cartão para não aplicar a regra a `$TMPDIR` e `$(mktemp …)`. Esforço P. Dono: tech-lead.

**A8 (média, recomendado; já existia).** `hooks/conformidade.py:1482` só reconhece `-t` como palavra própria; `cp -t.git/hooks x` (forma colada que o coreutils aceita) cai na busca do último não-opção, que é `x`. O mesmo para `install` e, pelo ramo do A5, `mv`. Caminho de ataque: o do A1, com caminho literal, sem variável. Correção mínima: `-t<pasta>` colado é o destino, junto da correção do A5. Cartão de segurança com prioridade. Esforço P. Dono: tech-lead.

Prazo do dono (develop até 18h): a correção do A1 é pequena (uma leitura por palavras no lugar da regex e 5 a 7 fixtures); A4 a A8 não seguram o merge.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `forge-check parecer delta`, `git archive`, o montador de fixtures do repositório, `tests/test_hook_git_comum.py` (OK, 42 fixtures) e `forge-mutante` (G1 a G14 morreram). `gitleaks`, `semgrep`, `zizmor` e `actionlint` não foram usados (o delta não toca workflow nem segredo; nada instalado, `R-CUSTO`).
