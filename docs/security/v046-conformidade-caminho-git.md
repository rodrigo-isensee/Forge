---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: 22187bae11aba23d2e8fe705b6302647d7a34134
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v046 (E20.8, conformidade-caminho-git)

Diff revisado: `8b5a44d5..22187bae` (`hooks/conformidade.py` `resto_no_git`, `nomes_do_git`, `alvos_da_escrita`; 20 fixtures `gitcomum-*`; `tests/test_hook_git_comum.py`; 7 mutantes). É a correção do A2 do parecer `docs/security/v046-pr-hook-prazo.md` (E20.4): escrita em `.git/forge/`, `.git/config` e `.git/hooks/` por um caminho com `$(…)`, crase ou variável.

Veredito: **reprovado**. As sondas S1 e S2 da E20.4 e as variantes com resto depois do opaco (aspas, `${d}`, `$d"/x"`, `$d/./x`, `$d//x`, `$(…)` aninhado, `/../.git/`, `git -C`, worktree) agora recusam. A brecha do A2 não fecha por inteiro: o mesmo mecanismo (valor opaco que é o diretório do git) passa quando não há resto depois do opaco, quando a variável usa operador de `${…}` e com a crase sem aspas. As três sondas abaixo passam (rc 0) no head e na base, e a entrega declara fechar essa família.

## Gatilhos
`R-SEGURANCA`: controle do Forge (hook `conformidade`, guarda de escrita em `.git/`), analisador de comando.

## Achados
- A1 (bloqueante) hooks/conformidade.py:974 · resto vazio depois do opaco não vai ao .git: `cp x "$(git rev-parse --git-path hooks/pre-push)"`, o mesmo com `config`, `cp x "$(git rev-parse --git-dir)/"` e `d=$(git rev-parse --git-dir); cp x $d` passam rc 0 (raiz e worktree)
- A2 (bloqueante) hooks/conformidade.py:325 · SO_VARIAVEL não casa `${d%…}`, `${d#…}` nem outro operador de `${…}`: o resto começa no operador e não casa nome do git; `d=$(git rev-parse --git-dir); cp x "${d%/}/config"` passa rc 0
- A3 (bloqueante) hooks/conformidade.py:968 · crase sem aspas: `cp x ` + "`git rev-parse --git-dir`" + `/config` passa rc 0, embora a fixture com a crase entre aspas recuse; o resto depois da crase não chega a resto_no_git como `/config`
- A4 (recomendado) hooks/conformidade.py:954 · cd para o opaco: `cd "$(git rev-parse --git-dir)" && cp ../x config` e `cd "$(git rev-parse --git-dir)/hooks" && cp ../../x pre-push` passam rc 0; já existia na base 8b5a44d5 (AR-7); cartão de segurança
- A5 (recomendado) hooks/conformidade.py:1466 · `cp x --target-directory=.git/hooks` (literal, sem variável) passa rc 0, enquanto `cp -t .git/hooks x` recusa: a leitura aceita `--target-directory` separado e não com `=`; já existia na base; cartão de segurança com prioridade
- A6 (recomendado) hooks/conformidade.py:954 · link de pasta para o opaco: `ln -s "$(git rev-parse --git-dir)" g && cp x g/config` passa rc 0; já existia na base; cartão de segurança
- A7 (recomendado) hooks/conformidade.py:974 · falso positivo maior que o limite declarado: `cp x $TMPDIR/logs/a.log`, `cp x $TMPDIR/info/a` e `cp x "$(mktemp -d)/config"` recusam com mensagem de `.git/`; o corpus de legítimos `gitcomum-*` não tem esses casos

## Sondas
- S1 · cp x "$(git rev-parse --git-path hooks/pre-push)" · espera: rc 2 R-CONFORMIDADE (.git/hooks/) · obtido: rc 0, stderr vazio (head 22187bae e base 8b5a44d5; também na worktree)
- S2 · d=$(git rev-parse --git-dir); cp x "${d%/}/config" · espera: rc 2 R-CONFORMIDADE (.git/config) · obtido: rc 0, stderr vazio (head e base)
- S3 · cp x `git rev-parse --git-dir`/config · espera: rc 2 R-CONFORMIDADE (.git/config) · obtido: rc 0, stderr vazio (head e base); com aspas recusa (fixture gitcomum-crase-forge-bloqueia)
- S4 · cp x "$(git rev-parse --git-dir)/" · espera: rc 2 R-CONFORMIDADE (.git/) · obtido: rc 0, stderr vazio (head e base)
- S5 · d=$(git rev-parse --git-dir); cp x $d · espera: rc 2 R-CONFORMIDADE (.git/) · obtido: rc 0, stderr vazio (head e base)

## Detalhe dos achados
Método das sondas: o próprio montador de `tests/test_hooks.py` (`Fixture.montar` e `rodar`), papel `forge:tech-lead`, projeto em branch `melhoria/x` e worktree `{tmp}/wt`, entrada esperada rc 2; nada foi escrito em `.git` real (só repositórios temporários em `$TMPDIR`). A mesma bateria rodou no head 22187bae (worktree destacada) e na base 8b5a44d5 (cópia por `git archive` em pasta de rascunho). 48 variantes no head: 37 recusam, 11 passam; as que passam estão nos achados.

**A1 (média, bloqueante).** Evidência: `hooks/conformidade.py:973-975`: com `partes` vazio, `resto_no_git` devolve None; `git rev-parse --git-path <x>` entrega o caminho inteiro dentro de `.git` sem resto, e `$(git rev-parse --git-dir)` sozinho ou com `/` final é o diretório (o `cp` grava `.git/<nome da origem>`; com a origem chamada `config` ou `HEAD`, o arquivo do git). Caminho de ataque: um agente do time (por instrução injetada num arquivo lido, ou por engano) instala `.git/hooks/pre-push`, que roda na máquina do usuário no próximo envio e desliga a catraca (`R-VERIFY`), ou reescreve `.git/config` (`core.hooksPath`) ou a marca `.git/forge/`. É exatamente a família do A2 da E20.4. Correção mínima: quando o texto da substituição visível (entre aspas o hook já o tem) contém `rev-parse` com `--git-dir`, `--git-common-dir`, `--absolute-git-dir` ou `--git-path`, tratar o valor como `<raiz>/.git` (com `--git-path <x>`, `<raiz>/.git/<x>`) e somar o resto, inclusive vazio; e, com resto vazio depois de opaco, conferir também `<raiz>/.git/<nome da origem>` como faz o `cp` para destino que é pasta. Variável atribuída na mesma linha a uma dessas substituições (`d=$(git rev-parse --git-dir)`) herda o mesmo valor. Fixtures novas: as 5 sondas acima mais a variante de worktree. Esforço P. Dono: tech-lead (autor da E20.6).

**A2 (média, bloqueante).** Evidência: `hooks/conformidade.py:325` (`\$\{?\w+\}?`) casa `${d` e para no `%`; o resto `%/}/config` começa por `%/}`, que não é nome do git. Com `${d:-…}`, `${d#./}/hooks/…` e `${d%/}/hooks/…` outra regra (`${` com ação crítica) recusa, mas `config` e `forge` não estão nela. Caminho de ataque: o mesmo do A1. Correção mínima: o fim da variável é o `}` que fecha `${…}` (regex `\$\{[^}]*\}|\$\w+|` + crase), e não o fim do nome. Esforço P. Dono: tech-lead.

**A3 (média, bloqueante).** Evidência: `hooks/conformidade.py:968`; a fixture `gitcomum-crase-forge-bloqueia` só cobre a crase entre aspas. Sem aspas, `cp x ` + "`git rev-parse --git-dir`" + `/config` passa (com `/hooks/` recusa por outra regra, a da crase com ação crítica, que não cobre `config` nem `forge`). Caminho de ataque: o do A1. Correção mínima: levar a crase sem aspas pela mesma leitura da crase entre aspas (o token que chega a `checar_escrita` com a crase, ou a regra da crase com ação crítica valendo para todo nome de `NOMES_DO_GIT`), com fixture da crase sem aspas para `config` e `forge`. Esforço P. Dono: tech-lead.

**A4 (média, recomendado; já existia).** `cd` para um opaco e escrita relativa depois: o hook resolve a escrita na pasta de antes do `cd`. Mesma classe do AR-7 (pasta do git diferente da do bash). Correção mínima: `cd`/`pushd` com `$(…)`, crase ou variável cujo resto ou texto aponte o diretório do git (mesma leitura do A1) faz a pasta corrente ser `<raiz>/.git/<resto>`; na dúvida, escrita depois de `cd` opaco recusa. Fora desta entrega: cartão de segurança. Esforço M. Dono: tech-lead.

**A5 (média, recomendado; já existia).** `cp x --target-directory=.git/hooks` passa com caminho literal: a leitura dos destinos (`hooks/conformidade.py:1466`) conhece `-t <pasta>` e `--target-directory <pasta>`, não `--target-directory=<pasta>` (só `link_em_protegido`, `hooks/conformidade.py:1009`, lê a forma com `=`). Caminho de ataque: o do A1, sem precisar de variável. Correção mínima: tratar `--target-directory=<pasta>` igual a `-t <pasta>` em todo comando que já lê `-t` (`cp`, `mv`, `install`, `ln`), com fixture literal e com variável. Fora do diff desta entrega, mas o achado é literal e simples: cartão de segurança com prioridade, de preferência na mesma volta. Esforço P. Dono: tech-lead.

**A6 (baixa, recomendado; já existia).** `ln -s "$(git rev-parse --git-dir)" g` cria um nome livre para o `.git`; o `ln -s .git g` literal recusa (N3), o opaco não. Correção mínima: em `link_em_protegido`, a origem opaca passa pela mesma leitura do A1. Cartão de segurança. Esforço P. Dono: tech-lead.

**A7 (baixa, recomendado).** O limite declarado na entrega é o falso positivo quando o resto começa por nome do git; ele morde casos comuns: `$TMPDIR/logs/…`, `$TMPDIR/info/…`, `"$(mktemp -d)/config"` recusam com a mensagem de `.git/`, o que confunde o agente. `nomes_do_git` soma tudo o que existe no diretório comum (`description`, `FETCH_HEAD`, `ORIG_HEAD`, `COMMIT_EDITMSG`, `packed-refs`, `branches`, `shallow`, `sequencer`, `rr-cache`, `lfs` e o que mais houver), o que alarga o alcance. Correção mínima: não aplicar a regra a `$TMPDIR`, `$HOME` e `$(mktemp …)` (o hook já expande `$HOME`) e pôr no corpus de legítimos `gitcomum-*` os três casos; com o A1 feito pelo texto da substituição, a lista por nome pode ficar só para variável de valor desconhecido. Esforço P. Dono: tech-lead.

Sem achado nos testes: `tests/test_hook_git_comum.py` roda as 20 fixtures (OK, 4,8 s); os 7 mutantes de `tests/mutantes/v046-conformidade-caminho-git.json` cobrem as condições novas, mas nenhum deles mataria A1–A3 (as fixtures não têm os casos), o que reforça pôr as sondas como fixtures.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só leitura do diff, o montador de fixtures do próprio repositório e `git archive` da base em pasta de rascunho. `gitleaks`, `semgrep`, `zizmor` e `actionlint` não foram usados (o diff não toca workflow nem segredo; sem ferramenta nova instalada, `R-CUSTO`).
