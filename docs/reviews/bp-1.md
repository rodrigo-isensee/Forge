---
tipo: review
contrato: 1
pedido: bp-1
branch: melhoria/bp-1
commit: d986c37136ceb9a7790fa8c1dba993b6ae28ee0d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Code review: BP-1 (`.forge/versao` protegido contra o git; hook que não desliga sem ele)

Diff revisado: `f636d27...95a1140` (3 commits, 17 arquivos). Brief do autor: `bp-1-tech-lead-1.md`, "Entregar" 1 a 4.
Ferramentas: `python3 -m unittest tests.test_hooks -q` rodado nesta revisão em 95a1140: `Ran 16 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO; provas do autor e do conferente). Segurança: parecer próprio do `security-engineer` (E3.2), não refeito aqui.

## Contra o "Entregar"
- **1 (E1, git rm/mv/checkout/restore):** cumprido no caso direto. `git_caminhos` (`hooks/conformidade.py:813`) manda os caminhos para `checar_escrita`/`checar_remocao`, com curinga expandido. Conferido rodando o hook num projeto temporário: `git rm .forge/versao`, `git rm -r --cached .forge`, `git -C .forge rm versao`, `git rm .forge/vers*`, `git restore -s HEAD .forge/versao` e `git checkout HEAD~0 .githooks` dão rc=2; `git checkout -- src/a.js`, `git checkout .`, `git restore .` e `git checkout develop` dão rc=0, então não há falso positivo nos usos comuns. Lacuna em B1.
- **2 (E1, marca de sessão e falha fechada):** cumprido. O `SessionStart` do `vigia` grava `.forge/run/projeto` com `.gitignore` `*` (`hooks/_comum.py:96`); um `startup` sem `.forge/versao` apaga a marca, e `resume`/`compact`/`clear` a mantêm. Sem `.forge/versao` e com a marca presente, `barrar_sem_versao` (`hooks/_comum.py:653`) barra com R-CONFORMIDADE as ações críticas do `conformidade` e do `parecer` (conferido: `git push` e `gh pr merge` dão rc=2; `git commit` e `git checkout develop` passam), e não age em PostToolUse. `FORGE_GUARDA_ABERTA` continua abrindo a guarda.
- **3 (E2, fixtures):** as 4 pedidas, a do vigia (`tests/hooks/vigia/versao-sumiu-avisa.json`) e a de `git checkout -- <arquivo comum>` passando, mais 4 extras (restore, curinga, pasta, sem marca libera). O passo `remover` do harness (`tests/test_hooks.py:161`) é o mínimo para simular o arquivo sumido, e a docstring foi atualizada junto (o conferente já registrou isso como escopo).
- **4 (E2, docs e changelog):** ADR 0009, limite 2 (`docs/adr/0009-conformidade-dos-agentes.md:13`), e `docs/hooks.md` (`versao-sumiu`, `hooks_desligados`) atualizados, e o que fica pendente está declarado. O fragmento `changelog.d/bp-1.md` é neutro (R-NEUTRO). `tests/config.json` não foi tocado.
- Commits: 3, em Conventional Commits em português e coerentes (fix, test, docs).

## Achados que bloqueiam
- **B1 · `hooks/conformidade.py:821` e `:826` · a mesma guarda escapa com uma variação de uma opção.** Os candidatos são as palavras que não começam com `-`, tomadas como caminho literal. Por isso:
  - (a) pathspec com "magia" passa. `git rm ':(top).forge/versao'` sai com rc=0 e apaga o arquivo; o mesmo vale para `:(literal)`, `:(glob)` e `:(icase)`.
  - (b) `--pathspec-from-file=<arquivo>` (e `=-`, pela entrada padrão) em `rm`, `checkout` e `restore` também passa com rc=0: o caminho nem chega à conferência.

  Sugestão: tirar o prefixo de magia (`:(...)`, `:/`, `:!`/`:^` de exclusão) antes de resolver o caminho. Com `--pathspec-from-file`, ler o arquivo quando ele for legível e, quando não der (entrada padrão, variável), recusar se o comando citar caminho protegido ou simplesmente recusar (na dúvida, recusa, como a `checar_escrita`). Fixtures: `git-rm-pathspec-magica-bloqueia` e `git-rm-pathspec-from-file-bloqueia`.

  Severidade: bloqueia. O item 1 do brief é justamente que esses subcomandos passem pela conferência, e a variação custa só uma opção. A marca de sessão limita o estrago, mas é a segunda camada, e ela mesma é apagável (ver R1).

## Recomendados
- **R1 · fora da lista do E1, vira cartão para o `security-engineer` ou para um BP seguinte:**
  - `git stash push -- .forge/versao` sai com rc=0 e tira o arquivo da árvore de trabalho.
  - `git clean -fdx` sai com rc=0 e apaga `.forge/run/projeto`. Junto com B1, isso desliga de novo as duas camadas. O apagamento da marca é o limite já declarado no ADR 0009 (limite 2, "Resta").
- **R2 · `hooks/_comum.py:653` · `barrar_sem_versao` ignora `hooks_desligados`.** Com `{"hooks_desligados": ["conformidade","parecer"]}`, `git push` continua com rc=2, o que contraria o contrato de `docs/hooks.md` ("nomes dos hooks a desligar"). O erro é para o lado fechado e só aparece sem o `.forge/versao`, mas o comportamento deve seguir a config, ou o doc deve dizer a exceção.
- **R3 · `hooks/_comum.py:659` · a mensagem manda "restaure o arquivo", mas restaurar pelo agente é barrado.** `git checkout -- .forge/versao` dá rc=2 pela mesma regra, porque `.forge/` está no `CRITICO`. Sugestão: "peça ao usuário que restaure o .forge/versao (R-DECISAO)".
- **R4 · `hooks/vigia.py:321` · o aviso diz "os hooks do Forge estão desligados".** Depois desta entrega, o `conformidade` e o `parecer` ainda barram as ações críticas. Sugestão: "os hooks do Forge só barram as ações críticas até o arquivo voltar".
- **R5 · troca de branch:** `git checkout` para uma branch ou tag anterior ao Forge (sem `.forge/versao`) liga a falha fechada até a volta. Isso está documentado como intencional (`docs/hooks.md`, `hooks_desligados`). Registro como risco de falso positivo para o QA exercitar.

## Parecer
**Reprovado** por B1. R1 a R5 são recomendados: R1 vai como cartão de segurança, e R2 a R4 podem ir no mesmo brief de volta ao autor.

## Revalidação após o retrabalho 1
Diff revisado: `78259ed...99648a3` (3 commits: 75f7ab4, c641dee, 99648a3; 17 arquivos). Brief do autor: `bp-1-tech-lead-3.md`, "Entregar" 1 a 6.
Ferramentas: `python3 -m unittest tests.test_hooks -q` rodado nesta revisão em 99648a3: `Ran 17 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO). Segurança: parecer próprio do `security-engineer` (E3.2), revalidado em paralelo.

### Primeira rodada
- **B1 · fecha nos casos pedidos.** O pathspec agora é resolvido pelo git (`git ls-files`, `hooks/conformidade.py:881` e `:887`), e as opções globais `--*-pathspecs` chegam ao `ls-files` (`:789`). `--pathspec-from-file`, inclusive abreviado (`--pathspec-from=x`), é recusado sempre (`:827`). Conferido rodando o hook: `:(top)`, `:(literal)`, `:(glob)`, `:(icase)`, `:/`, `'*/versao'`, `-r .`, `--cached -r .`, `-r ':!src'`, `./.forge/../.forge/versao`, `git --icase-pathspecs rm .FORGE/VERSAO` e `git restore --staged .forge/versao` dão rc=2. `git checkout develop`, `checkout -b`/`-B`, `git switch -c`, `git checkout -- src/app.js`, `git rm src/app.js`, `git checkout -- .` e `git restore .` dão rc=0. As fixtures pedidas existem, e o subTest cobre as outras formas (`tests/test_hooks.py:307`). Lacuna da mesma classe em B2.
- **R1 · fecha pela proposta A.** A marca foi para `<git-common-dir>/forge/projeto` (`hooks/_comum.py:91` e `:101`) e está protegida em `hooks/conformidade.json:33` e no `CRITICO` (`hooks/conformidade.py:30`). `rm .git/forge/projeto` dá rc=2. As fixtures `sparse-checkout-sem-versao-bloqueia`, `git-clean-X-mantem-marca-bloqueia` e `vigia/sparse-checkout-avisa` mostram que a marca sobrevive. `git stash push -- .forge/versao` continua fora (só tira o arquivo, e a segunda camada segura).
- **R2 · fecha.** `desligado_na_config` (`hooks/_comum.py:667`) entra em `barrar_sem_versao` (`:674`) depois de `versao_sumiu()`, então com a raiz ausente não lê a config.
- **R3 · fecha.** A mensagem manda pedir ao usuário e diz por que o agente não pode (`hooks/_comum.py:680`).
- **R4 · fecha.** O aviso diz que os hooks só barram as ações críticas até o arquivo voltar (`hooks/vigia.py:321`).
- **Docstring do harness:** contra a base `f636d27`, `tests/test_hooks.py` só ganha linhas (`:22`-`:23`, `:162`-`:165`), como o brief pediu.
- Docs (ADR 0009, limite 2; `docs/hooks.md`; `changelog.d/bp-1.md`) estão atualizados e neutros (R-NEUTRO). Commits estão em Conventional Commits em português, coerentes (fix, fix, docs).

### Achados novos
- **B2 · `hooks/conformidade.py:789` e `:887` · o modo de pathspec pela variável de ambiente escapa da resolução.** O hook leva ao `ls-files` só a opção `--icase-pathspecs` (e as irmãs), e não a variável equivalente. Por isso `GIT_ICASE_PATHSPECS=1 git rm .FORGE/VERSAO` sai com rc=0, e o mesmo acontece com `env GIT_ICASE_PATHSPECS=1 git rm ...`, com `export GIT_ICASE_PATHSPECS=1; git rm ...` e com `GIT_ICASE_PATHSPECS=1 git checkout HEAD -- .FORGE`. Conferi num repositório temporário: o git apaga `.forge/versao` com esse comando.
  - Sugestão: tratar `GIT_ICASE_PATHSPECS`, `GIT_GLOB_PATHSPECS`, `GIT_NOGLOB_PATHSPECS` e `GIT_LITERAL_PATHSPECS` como as opções `--*-pathspecs`. Ou elas passam ao ambiente do `ls-files` (o hook já lê as atribuições da linha: `self.ambiente`, `GIT_DIR`, `:269`/`:615`), ou, mais simples, recusar `git rm|mv|checkout|restore` quando a linha atribui ou exporta uma `GIT_*_PATHSPECS` (na dúvida, recusa).
  - Fixture: `git-rm-icase-por-ambiente-bloqueia`, mais as formas `env` e `export` no subTest.
  - Severidade: bloqueia, pelo mesmo critério de B1: a primeira camada escapa trocando uma opção pela variável equivalente. A segunda camada (marca dentro do `.git/`) agora segura as ações críticas, então o estrago fica limitado às ações não críticas, mas o item 2 do brief é justamente que o git resolva o pathspec como ele o entende.
- **R6 · `hooks/conformidade.py:856` (`pathspecs_do_git`) · falso positivo esperado:** `git checkout HEAD .` (origem sem `--`) dá rc=2 porque alcança `.forge/config.json`. Fica do lado fechado, coerente com "com origem o pathspec vale pelo que alcança", e está documentado. É risco para o QA exercitar, não ajuste.

### Parecer da revalidação
**Reprovado** por B2. B1 (casos pedidos), R1 (proposta A), R2, R3 e R4 fecham. R5 e R6 são riscos de falso positivo do lado fechado, para o QA.

## Revalidação após o retrabalho 2
Diff revisado: `7594a24...9f3fa2b` (2 commits: 086dcca, 9f3fa2b; 22 arquivos). Brief do autor: `bp-1-tech-lead-5.md`, "Entregar" 1 a 8.
Ferramentas: `python3 -m unittest tests.test_hooks -q` rodado nesta revisão em 9f3fa2b: `Ran 19 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO). Segurança: parecer próprio do `security-engineer` (E3.2), revalidado em paralelo (`docs/security/bp-1.md`, rodada 3, achados F e G); não refeito aqui.

### B2: fecha
- `PATHSPECS_NO_AMBIENTE` (`hooks/conformidade.py:41`) liga as quatro `GIT_*_PATHSPECS` às opções `--*-pathspecs`, e `VARIAVEIS_DA_LINHA` (`:43`) as guarda no ambiente da linha (`:619`, `:655`, o que cobre atribuição, `env`, `export` e `declare -x`). `pathspecs_da_linha` (`:790`) passa a opção ao `ls-files` (`:798`), e só um falso explícito a desliga (na dúvida, recusa).
- Conferido rodando o hook num projeto temporário: `GIT_ICASE_PATHSPECS=1 git rm .FORGE/VERSAO`, `GIT_ICASE_PATHSPECS=yes git rm -r .FORGE`, `declare -x GIT_ICASE_PATHSPECS=1; git rm ...`, `env -i GIT_ICASE_PATHSPECS=1 git rm ...`, `sudo GIT_ICASE_PATHSPECS=1 git rm ...` e `GIT_ICASE_PATHSPECS=1 bash -c 'git rm .FORGE/VERSAO'` dão rc=2. `GIT_LITERAL_PATHSPECS=1 git rm src/app.js`, `git rm src/app.js` e `git checkout develop` dão rc=0, sem falso positivo.
- Fixture `git-rm-env-icase-pathspecs-bloqueia` e o subTest com as formas `env`, `export`, `checkout`, glob, falso explícito e caminho comum (`tests/test_hooks.py:332`), só por acréscimo.

### O resto do retrabalho (D e E da segurança, conferido como código)
- Marca por raiz: `marca_de_projeto` (`hooks/_comum.py:105`) usa o hash do caminho real da raiz. `marcar_projeto` (`:117`) só grava, e o `vigia` a chama sem distinguir a origem (`hooks/vigia.py:334`). `projeto_marcado` (`hooks/_comum.py:127`) falha fechado com `.git` que existe e não se resolve, e `raiz_do_projeto` (`:45`) trata a raiz marcada como projeto, então a conferência roda inteira. Conferido: sem `.forge/versao` e com a marca, `echo x > .claude/settings.json`, `cat .forge/config.json`, `rm .git` e `echo 'gitdir: /x' > .git` dão rc=2, e `echo x > src/app.js` e `git commit -m x` dão rc=0. Numa worktree, a marca é a dela, e a do clone não se apaga (`tests/test_hooks.py:353`).
- `.git` protegido por igualdade exata (`hooks/conformidade.json:34`): `mv .git .git2`, `rm -rf .git` e `cd .git && rm -r forge` dão rc=2, enquanto `.gitignore` e `.github/` continuam livres (rc=0).
- O texto do ADR 0009 (limite 2), o de `docs/hooks.md` (`versao-sumiu`) e o de `changelog.d/bp-1.md` batem com o código: marca por raiz, nada a apaga, conferência inteira com a marca, `.git` protegido, `GIT_*_PATHSPECS`. O "Resta" declara o `.git` renomeado por fora (conferido: rc=0 nesse caso).
- Commits: 2, em Conventional Commits em português e coerentes (fix, docs).

### Achados novos
Nenhum que bloqueie do lado do code review.
- **R7 · `hooks/_comum.py:127`-`:136` · falso positivo fora do Forge, com mensagem enganosa.** Uma pasta sem Forge, com um `.git` que não se resolve (por exemplo `gitdir:` de uma worktree já apagada) e que é a raiz da sessão, conta como projeto marcado. Conferido: `gh pr merge 1` dá rc=2 com "o .forge/versao da sessão sumiu", num projeto que nunca teve o arquivo. Esse caminho segue a decisão técnica (".git que existe e não se resolve falha fechado") e cai do lado fechado, então não bloqueia. Sugestão: a mensagem citar também o `.git` que não se resolve. Fica como risco para o QA.
- **R8 · `hooks/_comum.py:45` · custo:** num repositório sem Forge, cada `raiz_do_projeto` agora roda um `git rev-parse` a mais (`marca_de_projeto`). É recomendado guardar o resultado por raiz dentro da chamada do hook, se o QA medir lentidão.

### Parecer da revalidação
**Aprovado** do lado do code review: B2 fecha, e o retrabalho de D e E está coerente com o ADR 0009 e com as fixtures. R5 a R7 são riscos de falso positivo do lado fechado, para o QA; R8 é recomendado. Os achados F e G da segurança (rodada 3) são do parecer dela e seguem valendo para o portão: se o retrabalho deles mexer em `hooks/_comum.py`, este parecer se revalida na proporção do que mudar (`commit_vale`).

## Revalidação após o retrabalho 3
Diff revisado: `5cfa661...7ec8c60` (3 commits: 96032bd, faa4f06, 7ec8c60; 19 arquivos). Brief do autor: `bp-1-tech-lead-7.md`, "Entregar" 1 a 7.
Ferramentas: `python3 -m unittest tests.test_hooks -q` rodado nesta revisão em 7ec8c60: `Ran 19 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO). Segurança: parecer próprio do `security-engineer` (E3.2), revalidado em paralelo; F e G são dele e não os refaço, só registro o que conferi rodando o hook.

### R7 e R8
- **R7 · fecha.** `motivo_da_falha` (`hooks/_comum.py:164`) separa `raiz`, `git` e `versao`, e `TEXTO_DA_FALHA` (`:173`) dá a mensagem de cada um. `barrar_sem_versao` (`:725`) e o aviso do `vigia` (`hooks/vigia.py:320`) usam o motivo. Conferido: numa pasta sem Forge com `.git` = `gitdir: /nada/x`, `gh pr merge 1` dá rc=2 com "o .git da raiz da sessão não se resolve", e não mais "o .forge/versao sumiu". A falha fechada continua como estava. Fixture: `r7-git-nao-resolve-mensagem-bloqueia`.
- **R8 · fecha.** `marca_de_projeto` agora usa `diretorio_comum` (`hooks/_comum.py:95`), que só lê o disco. Sai o `git rev-parse` que `raiz_do_projeto` (`:45`) rodava a cada chamada.

### O resto do retrabalho (conferido rodando o hook num projeto temporário)
- `.git/` inteiro (`hooks/conformidade.json:37`): `touch .git/commondir`, `cp ... .git/worktrees/x/gitdir`, `ln -s /x .git/commondir`, `echo x > ./.git/info/exclude` e `cd .git && echo x > commondir` dão rc=2. `git commit`, `git fetch`, `cat .git/HEAD`, `echo x > .github/w.yml`, `echo x > .gitignore` e `touch src/b.js` dão rc=0, sem falso positivo nos usos comuns. `commondir` e `\.git/` estão na regex `CRITICO` (`hooks/conformidade.py:30`).
- G: depois de `mv proj x`, `git push` dá rc=2 com a mensagem `raiz`. `motivo_da_falha` e o `vigia` tratam a raiz que sumiu sem recriá-la.
- O `diretorio_comum` saiu de `conformidade.py` para `_comum.py` com as duas conferências novas, `commondir` no clone principal e `commondir` da worktree (`hooks/_comum.py:95`-`:116`). O `raiz_do_parecer` passa a usar a versão mais estrita.
- O texto do ADR 0009 (limite 2), de `docs/hooks.md` (`:35` caminhos, `:53` `versao-sumiu`, `:81` `hooks_desligados`, o que fecha H) e de `changelog.d/bp-1.md` bate com o código e é neutro (R-NEUTRO).
- Commits: 3, em Conventional Commits em português, coerentes (fix, fix, docs).

### Achados novos
- **B3 · `hooks/conformidade.py:680` e `:687` · regressão do commit faa4f06: `perl -i` deixou de passar pela conferência de texto de interpretador.**
  - Com `perl_no_lugar`, o ramo `INTERPRETES` (o `checar_texto`) é pulado, e o código do `-e` vai só para a `checar_escrita`, como se fosse um caminho.
  - Conferido em 7ec8c60, todos com rc=0:
    - `perl -pi -e 'unlink q(.forge/versao)' src/a.js`
    - `perl -pi -e 'open(F,">.claude/settings.json")' src/a.js`
    - `perl -pi -e 'unlink q(.git/forge/projeto-<hash>)' src/a.js`, que apaga a marca da sessão e anula a segunda camada.
  - Na base `5cfa661`, os dois primeiros davam rc=2 ("arquivo em vigor"). Sem o `-i` (`perl -e 'unlink q(.forge/versao)'`), continua rc=2.
  - Não é a exceção "interpretador" da BP-5: o caminho está em literal no texto, e a guarda o pegava antes desta entrega.
  - Sugestão: com `perl_no_lugar`, rodar as duas conferências, `checar_texto` em cada argumento e `checar_escrita` nos arquivos. Por exemplo, tirar o `and not perl_no_lugar` de `:687` e manter o `or perl_no_lugar` de `:699` num `if` próprio, fora da cadeia de `elif`. Fixture: `perl-pi-texto-protegido-bloqueia`, com as três formas acima no subTest.
  - Severidade: bloqueia. A entrega afrouxa uma guarda que já existia (R-CONFORMIDADE) e reabre a remoção da marca por um caminho literal.
- **B4 · `hooks/_comum.py:100` e `:115` · falso positivo novo, fora do Forge, numa worktree aberta por um caminho com link simbólico.**
  - `diretorio_comum` compara o `gitdir` de volta, que está resolvido (`realpath`), com `Path(topo) / ".git"`, que não está. Com `CLAUDE_PROJECT_DIR` passando por um link (por exemplo `/tmp` ou `/var` no macOS, ou uma pasta de projetos ligada por link), a worktree legítima não se resolve. `projeto_marcado` a toma como marcada, e as ações críticas falham fechado num repositório sem Forge.
  - Conferido: numa worktree sem Forge, `gh pr merge 1` dá rc=0 pelo caminho real e rc=2 pelo caminho com link ("o .git da raiz da sessão não se resolve").
  - Na base, com `git rev-parse`, isso não acontecia. Num projeto com Forge, a mesma worktree fica sem marca gravável.
  - Sugestão: resolver o topo antes de comparar, `marca = Path(os.path.realpath(topo)) / ".git"` (ou `esperado == os.path.realpath(marca)`), mantendo a checagem de `is_symlink` no `.git` em si. Fixture: worktree aberta por link, rc=0 sem Forge.
  - Severidade: bloqueia. Barra `git push` e `gh pr merge` legítimos em qualquer repositório com o plugin ativo, a correção é de uma linha, e a entrega já volta ao autor por B3.
- **R9 · `hooks/vigia.py:321` · recomendado.** Com a raiz movida, o estado vai para `copia_de_trabalho(cwd) or cwd`. Fora de uma cópia de trabalho, isso cria `.forge/run/` na pasta corrente, qualquer que seja. Sugestão: só a cópia de trabalho, e, sem ela, não gravar (o aviso no `Stop` basta).

### Parecer da revalidação
**Reprovado** por B3 (regressão de guarda) e B4 (falso positivo fora do Forge). R7 e R8 fecham. `.git/` protegido, `commondir` e G se comportam como pedido, e a documentação bate com o código. R5 e R6 continuam como riscos para o QA, e R9 é recomendado. A volta é pequena (`hooks/conformidade.py:680`-`:699` e `hooks/_comum.py:100`-`:115`). Este parecer se revalida só nesse trecho.

## Revalidação após o retrabalho 4
Diff revisado: `ae998d1...740d7dd` (4 commits: 7a3114a, 2827834, 56e8144, 740d7dd; 16 arquivos). Brief do autor: `bp-1-tech-lead-9.md`, "Entregar" 1 a 8.
Ferramentas: `python3 -m unittest tests.test_hooks -q` rodado nesta revisão em 740d7dd: `Ran 19 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO). Segurança: parecer próprio do `security-engineer` (E3.2), revalidado em paralelo; não refeito aqui.

Como reproduzir: projeto temporário com `git init`, `.forge/versao`, `.githooks/pre-push`, `.claude/settings.json` e `src/a.js` commitados; cada linha é o `command` de um PreToolUse Bash de `forge:dev`, com `CLAUDE_PROJECT_DIR` no projeto, passado a `python3 hooks/conformidade.py`. "Base" é o mesmo hook extraído de `ae998d1` (`git archive ae998d1 hooks`).

Cobertura declarada (VV-1): `perl`, `perl5.34.0`, `ruby`, `awk`/`gawk`, `sed`, com `-i` nas formas `-i`, `-pi`, `-0pi`, `-0777pi`, `-p -i`, `-i.bak`, `-i''`, `-pie`, `-i~`, `-pi~`, `-i_bak`, `-i,o`, `-i'orig_*'`; script por `-e`, `-e` colado, `--expression=`, argumento solto e comando `w`/`W`; alvos `.forge/versao`, `.githooks/pre-push`, `.claude/settings.json` e a marca `.git/forge/projeto-<hash>`; casos comuns em `src/a.js`. Fora da cobertura: script lido de arquivo ou da entrada padrão (BP-5, declarado em `docs/hooks.md`), `python3`/`node`/`php` (só o subTest do autor), worktree por link e vigia (só as fixtures do autor, que passam).

### B3, B4 e R9
- **B3 · fecha.** `hooks/conformidade.py:690`-`:697`: o ramo `INTERPRETES` roda sempre a `checar_texto`, e, com `no_lugar` (`:683`), roda também a `checar_escrita` nos alvos; nenhuma pula a outra. As três cadeias de B3 dão rc=2: `perl -pi -e 'unlink q(.forge/versao)' src/a.js`, `perl -pi -e 'open(F,">.claude/settings.json")' src/a.js` e `perl -pi -e 'unlink q(.git/forge/projeto-<hash>)' src/a.js`. Também dão rc=2: `-0777pi`, `-0pi`, `-p -i`, `-i.bak`, `-pie`, `-i -pe ... -- <alvo>` e `env perl -pi`, além de `ruby -i -pe`, `ruby -i.bak` e `ruby -pi -e 'File.delete(...)'`. Já `perl -pi -e 's/a/b/' src/a.js` e `ruby -i -pe 'x' src/a.js` dão rc=0, sem falso positivo.
- **B4 · fecha.** `hooks/_comum.py:117`-`:118` comparam o `gitdir` de volta com o caminho real do topo, e a checagem `is_symlink` continua sobre o `.git` em si (`:101`-`:102`). A fixture `b4-worktree-por-link-libera` (rc=0) passa.
- **R9 · fecha.** Com a raiz movida, `hooks/vigia.py:324` usa só `copia_de_trabalho(cwd)`, e `:331` não grava sem ela. A fixture `vigia/r9-raiz-apagada-nao-cria-run` (`sem_caminho`) passa. O `sem_caminho` do harness (`tests/test_hooks.py:28` e `:303`) entra só por acréscimo.

### Achados novos (por classe)
- **B5 · `hooks/conformidade.py:683` e `:47` · classe "interpretador com edição no lugar": o `-i` com sufixo fora de `[0-9a-zA-Z.]` e o interpretador de nome versionado escapam.**
  - O `-i` do perl e do ruby aceita qualquer sufixo de cópia, e o resto do grupo depois do `i` é o sufixo. A regex só aceita letras, dígitos e ponto.
  - Com rc=0, e o arquivo de fato reescrito (conferido numa cópia: `.githooks/pre-push` passou de `#!/bin/sh` a `#!/bin/XX`):
    - `perl -i~ -pe 's/a/b/' .githooks/pre-push`
    - `perl -pi~ -e ...`
    - `perl -i_bak ...`
    - `perl -i,o ...`
    - `perl -i'orig_*' ...`
    - `ruby -i~ -pe 'x' .githooks/pre-push`
  - `INTERPRETES` (`:47`) só reconhece `perl` e `ruby` pelo nome exato, então `perl5.34.0 -pi -e ... .githooks/pre-push` e `perl5.34.0 -e 'unlink q(.forge/versao)'` também dão rc=0. Esse binário existe em `/usr/bin` nesta máquina. Não é a exceção do "nome montado" da BP-5: o nome está literal na linha, como o `python[\d.]*` que a regex já aceita.
  - Base: rc=0 nas mesmas cadeias, então não é regressão. Mas o item 1 do brief pede "`-i` em qualquer combinação", e o ADR 0009 (limite 2) e `docs/hooks.md:36` dizem que isso está coberto.
  - Sugestão:
    - `re.fullmatch(r"-[0-9a-zA-Z]*i.*", a)`, porque tudo depois do `i` é sufixo.
    - `perl[\d.]*` e `ruby[\d.]*` em `INTERPRETES` e no `no_lugar`.
    - Fixtures `perl-i-til-bloqueia` e `perl-versionado-bloqueia`, mais as formas acima no subTest.
  - Severidade: bloqueia. É o item 1 do brief, e a documentação afirma uma cobertura que o código não tem.
- **B6 · `hooks/conformidade.py:703` e `:731`-`:734` (com `:49`) · classe "script do awk/sed que escreve": as variantes da mesma forma que o retrabalho declarou coberta escapam.**
  - Com rc=0, e o efeito conferido numa cópia:
    - `gawk -i inplace.awk 1 .githooks/pre-push` reescreve o arquivo. O mesmo vale para `--include=inplace.awk` e para `-i /usr/share/awk/inplace.awk`. O teste em `:703` só aceita a palavra exata `inplace`.
    - `sed --expression='w .claude/settings.json' src/a.js` grava `.forge/versao`/`.claude/settings.json` (conferido). Também escapam `sed -e'1w .githooks/pre-push' src/a.js` (`-e` colado), `sed '1W .githooks/pre-push' src/a.js` (`W` maiúsculo, conferido) e `sed -i --expression='w .githooks/pre-push' src/a.js`. Em `:732`, o laço pula tudo que começa com `-`, e `SED_ESCREVE` só casa `w` minúsculo.
  - Base: rc=0, então não é regressão. Mas `docs/hooks.md:36` e o ADR 0009 dizem "`awk -i inplace` confere os alvos" e "o `w arquivo` do `sed` conta como escrita", e o item 7 do brief pede rc=2 para toda forma de passar o script (`-e`) no `sed` e no `awk -i inplace`.
  - Sugestão:
    - awk: qualquer argumento de `-i`/`--include` cujo nome-base, sem `.awk`, seja `inplace` liga a conferência dos alvos. Do lado fechado, basta qualquer argumento que contenha `inplace`.
    - sed: aplicar a `SED_ESCREVE`, com `[wW]`, ao valor de `-e`, de `-e<colado>` e de `--expression=` (não só às palavras sem `-`).
    - Fixtures `gawk-include-inplace-awk-bloqueia` e `sed-expression-w-bloqueia`.
  - Severidade: bloqueia, pelo mesmo critério de B1 e de B5: a variação custa uma opção, o caminho é protegido e o texto da entrega declara a cobertura. Fica no mesmo trecho que B5, o que dá uma volta pequena.
- **R10 · `hooks/conformidade.py:683` · recomendado, falso positivo do lado fechado, já na base.** `perl -Mstrict -e 'print 1' .githooks/pre-push`, uma leitura, dá rc=2: `-Mstrict` contém `i` e liga o `no_lugar`. Sugestão: no grupo, parar em `-M`/`-m`/`-I`/`-x`/`-C` (o resto do grupo é valor dessas opções) antes de procurar o `i`. Isso entra junto com B5.
- **R11 · `hooks/vigia.py:360` · recomendado, cosmético.** Com R9, quando nada é gravado, o `systemMessage` continua apontando para `.forge/run/violacoes.jsonl`. Sugestão: omitir o caminho quando `hook.raiz` é `None`.

### `ed`, `patch`, `sponge` e `chmod` em `.githooks/`
Vão para outra BP, não para esta. Na HEAD e na base, dão rc=0: `chmod -x .githooks/pre-push`, `sponge .githooks/pre-push < src/a.js` e `patch .githooks/pre-push x.diff`. O `ed -s .githooks/pre-push <<< $'1d\nw'` dá rc=2 nas duas, mas outras formas do `ed` podem passar, como o autor relatou.

O motivo para ficarem fora é que essa é a classe "comando do shell que escreve e não está em `TODOS_OS_ARGUMENTOS`/`SO_DESTINO`" (`hooks/conformidade.py:54`-`:55`), e não a de interpretador com edição no lugar que a decisão técnica trouxe para a BP-1. Também não é regressão, e a correção é de lista de política, noutro trecho.

Viram cartão para o `security-engineer` (BP-5 ou uma BP nova). A prioridade é o `chmod -x .githooks/pre-push`, que desliga o `pre-push` (R-VERIFY, R-MAIN) e merece o mesmo tratamento do `rm`.

### Parecer da revalidação
**Reprovado** por B5 e B6, os dois da mesma classe que esta volta pretendia fechar e já presentes na base: a documentação da entrega declara uma cobertura que o código não tem. B3, B4 e R9 fecham. R10 e R11 são recomendados e podem ir no mesmo brief, e R5 e R6 seguem como riscos para o QA. A volta é pequena: `hooks/conformidade.py:47`, `:683`, `:703` e `:731`-`:734`, mais as fixtures. Este parecer se revalida só nesse trecho.

Para não abrir uma rodada 6, o autor deve repetir antes do push a cobertura declarada acima, com as formas de sufixo e de opção longa ou colada.

## Revalidação após o retrabalho 5
Diff revisado: `bbacc2c...592098a` (2 commits: b500364, 592098a; 10 arquivos). Brief do autor: `bp-1-tech-lead-11.md`, "Entregar" 1 a 7.
Ferramentas: `python3 -m unittest tests.test_hooks -q` rodado nesta revisão em 592098a: `Ran 19 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO). Segurança: parecer próprio do `security-engineer` (E3.2), revalidado em paralelo; não refeito aqui.

Como reproduzir: o mesmo da rodada anterior (projeto temporário com `.forge/versao`, `.githooks/pre-push`, `.claude/settings.json` e `src/a.js` commitados; cada linha é o `command` de um PreToolUse Bash de `forge:dev` passado a `python3 hooks/conformidade.py`). "Base" é o hook de `bbacc2c` (`git archive bbacc2c hooks`), igual ao de 740d7dd. O efeito real das fugas foi conferido numa cópia do projeto.

Cobertura declarada (VV-1): as cadeias de B5, B6, R10 e da mitigação listadas abaixo; nomes de binário presentes nesta máquina (`perl`, `perl5.34.0`, `perl5.34-x86_64-linux-gnu`, `python3.10`, `gawk` 5.1.0, `mawk`, GNU `sed`); `ruby3.2` só pelo hook (não instalado); opções do perl `-C`, `-l`, `-x`, `-I`, `-s`, `-e` antes do `-i`; opções longas abreviadas do `sed` e do `gawk`; heredoc para interpretador versionado. Fora da cobertura: `ed`, `patch`, `sponge`, `chmod` e script lido de arquivo (BP-5, declarados); `node`, `php` e `deno` versionados; o vigia (R11 não está no diff).

### B5, B6, R10 e a mitigação
- **B5 · fecha nas formas pedidas.** `edita_no_lugar` (`hooks/conformidade.py:212`) toma o resto do grupo depois do `i` como sufixo e para nas opções que levam valor (`OPCAO_COM_RESTO`, `:49`). `PERL_OU_RUBY` e `INTERPRETES` (`:47`-`:48`) aceitam a versão no nome. Na HEAD dão rc=2, e na base rc=0: `perl -i~`, `perl -pi~`, `perl -i_bak`, `perl -i,o`, `perl -i'orig_*'`, `ruby -i~`, `perl5.34.0 -pi -e ...` e `ruby3.2 -i -pe ...` sobre `.githooks/pre-push`, além de `perl5.34.0 -e 'unlink q(.forge/versao)'`. Também dão rc=2 `perl -l -i`, `-x -i`, `-I lib -pi`, `-e 1 -i`, `-s -i` e `ruby -r json -i`. Lacuna da mesma classe em B7.
- **B6 · fecha nas formas pedidas.** `awk_no_lugar` (`:229`), `script_do_sed` (`:240`), `SED_ESCREVE` com `[wW]` (`:54`) e o laço do sed (`:782`-`:785`). Dão rc=2, e na base rc=0: `gawk -i inplace.awk`, `gawk --include=inplace.awk`, `gawk -i /usr/share/awk/inplace.awk`, `sed --expression='w .claude/settings.json'`, `sed -e'1w ...'`, `sed '1W ...'`, `sed -i --expression='w ...'` e `sed -E -e'1W ...'`. Lacuna da mesma classe em B8.
- **R10 · fecha.** `perl -Mstrict -e 'print 1' .githooks/pre-push` dá rc=0 (na base, rc=2). `perl -CSDi -e 'print 1' .githooks/pre-push` também dá rc=0, o que está certo: o `i` ali é flag do `-C`.
- **Mitigação · cumprida.** `CITA_A_MARCA` (`:51`) é conferida em `:581`, e `LANCADORES_RECUSADOS` (`:52`) em `:718` e `:623`. `cat .git/forge/projeto-x`, `ionice -c3 rm src/a.js`, `flock /tmp/l true`, `script -qc 'rm .forge/versao' /dev/null`, `taskset 1 true`, `bash -c 'ionice ...'`, `env flock ...` e `nice script ...` dão rc=2.
- **Sem falso positivo nos usos comuns:** rc=0 em `perl -pi -e 's/a/b/' src/a.js`, `ruby -i -pe 'x' src/a.js`, `sed -i 's/a/b/' src/a.js`, `sed -n '1p' .githooks/pre-push`, `gawk -i inplace '{print}' src/a.js`, `ls .git`, `git log`, `grep -rn 'git/forge' docs` e `npm run script`.
- **Falso positivo da mitigação · relevante? Não.** Ela vale só numa sessão de projeto (`raiz_e_projeto`). O clone do Forge sem `.forge/versao` não é afetado, e nesta worktree não há `.forge/`. Os casos que achei são raros e têm saída simples:
  - `git commit -m '... .git/forge ...'`, ou um `gh pr create --body` que cite a marca, dá rc=2. A saída é `-F`/`--body-file`.
  - Um executável do projeto chamado `script` (`./script`) dá rc=2, porque o nome-base coincide.

  Registro os dois como risco para o QA, não como ajuste.
- **Documentação:** o ADR 0009 (limite 2) e `docs/hooks.md:36` passaram a listar o que fica com a BP-5 (`ed`, `ex`, `vim -es`, `patch`, `sponge`, `split`, `chmod`/`chown`, `chmod 000 .forge`, script lido de arquivo, `busybox`), e o fragmento `changelog.d/bp-1.md` também, em texto neutro (R-NEUTRO). O texto ainda afirma duas coberturas que o código não tem (B7 e B8).
- Commits: 2, em Conventional Commits em português, coerentes (fix, docs).

### Achados novos (por classe)
- **B7 · `hooks/conformidade.py:620` e `:47`-`:48` · classe "interpretador com versão no nome", item 1 do brief: o nome versionado não é reconhecido em todos os pontos.**
  - (a) O heredoc. O dono do heredoc é testado por uma terceira lista, `\b(python[\d.]*|node|nodejs|perl|ruby|...)\b` (`:620`), que não ganhou a versão, e `\bperl\b` não casa `perl5.34.0`. Com rc=0 (base também rc=0):
    - `perl5.34.0 <<'X'` / `unlink q(.forge/versao)` / `X`
    - `ruby3.2 <<'X'` / `File.delete(".forge/versao")` / `X`

    Na mesma forma, `perl <<'X'` e `python3.10 <<'X'` dão rc=2.
  - (b) O nome com arquitetura. `perl5.34-x86_64-linux-gnu`, que existe em `/usr/bin` nesta máquina (é o nome do Debian e do Ubuntu), não casa `perl[\d.]*`. Com rc=0, e o arquivo de fato reescrito numa cópia (`#!/bin/sh` virou `#!/bin/XX`):
    - `perl5.34-x86_64-linux-gnu -pi -e 's/sh/XX/' .githooks/pre-push`
    - `perl5.34-x86_64-linux-gnu -e 'unlink q(.forge/versao)'`

    Na base, também rc=0.
  - Por que bloqueia: o item 1 do brief pede que o "nome de interpretador com versão" seja "reconhecido como o interpretador", e `docs/hooks.md:36` e o ADR 0009 dizem "também com versão no nome" para "`-e`, heredoc".
  - Sugestão: uma fonte única para o nome. Por exemplo, `NOME_INTERPRETE = r"(python|perl|ruby)[\d.]*(-[\w-]+)?|node(js)?|php|deno|bun"`, usada em `INTERPRETES`, em `PERL_OU_RUBY` e no teste do heredoc (`:620`, com `Path(dono).name` em vez de `\b`).
  - Fixtures: `b7-heredoc-perl-versao-bloqueia` e `b7-perl-arquitetura-bloqueia`.
  - Severidade: bloqueia.
- **B8 · `hooks/conformidade.py:233`-`:234`, `:243` e `:765` · classe "opção longa abreviada": o GNU `sed` e o `gawk` aceitam qualquer prefixo único da opção longa, e o hook só reconhece o nome inteiro.**
  - Com rc=0 (base também rc=0), e o efeito conferido numa cópia:
    - `sed --expr='1w .githooks/pre-push' src/a.js` grava o arquivo. O mesmo vale para `--e=`.
    - `sed --i 's/sh/XX/' .githooks/pre-push` reescreve o arquivo (`--i` é o `--in-place`). O mesmo vale para `--in-pl`.
    - `gawk --inc=inplace '{sub(/sh/,"XX")}1' .githooks/pre-push` reescreve o arquivo. O mesmo vale para `--incl inplace`.
  - Na mesma classe "carrega `inplace` sem passar pelo `-i`/`-f`":
    - `gawk -E /usr/share/awk/inplace.awk .githooks/pre-push` dá rc=0 e esvazia o arquivo (conferido).
    - `gawk -l inplace 'BEGINFILE{inplace_begin(...)} ...' .githooks/pre-push` dá rc=0.
  - Por que bloqueia: `docs/hooks.md:36` e o ADR 0009 declaram `--expression=` e `--include=` cobertos, o item 2 do brief pede "`--include` que carregue inplace" e "`--expression=`", e a variação custa só apagar letras (o critério de B1, B5 e B6).
  - Sugestão, que fecha a classe e não só as variantes:
    - Normalizar `--<prefixo>[=v]` para a opção longa que ele abrevia, à maneira do `getopt_long`. No sed, `expression`, `in-place` e `file`. No gawk, `include`, `file`, `exec` e `load`. Na ambiguidade, recusar.
    - No awk, do lado fechado, qualquer argumento que contenha `inplace` liga a conferência dos alvos, o que cobre `-E`, `-l`, `--load` e `@load`.
  - Fixtures: `b8-sed-expr-abreviada-bloqueia`, `b8-sed-in-place-abreviada-bloqueia` e `b8-gawk-inc-abreviada-bloqueia`.
  - Severidade: bloqueia.
- **R11 · segue recomendado** (`hooks/vigia.py`, cosmético). Não entrou no brief desta volta.

### Parecer da revalidação
**Reprovado** por B7 e B8, as duas da mesma classe de B5 e B6 e já presentes na base (não são regressão). B5, B6 (nas formas pedidas), R10 e a mitigação fecham, sem falso positivo relevante. R5, R6 e os dois casos da mitigação seguem como riscos para o QA, e R11 é recomendado.

A volta é mecânica e cabe em `hooks/conformidade.py:47`-`:48`, `:229`-`:246`, `:620` e `:765`, mais as fixtures. Há outra saída para os dois achados, que é uma decisão técnica de quem conduz o pedido e não deste parecer: o texto do ADR 0009 e de `docs/hooks.md:36` deixa de afirmar essas formas, e elas viram cartão da BP-5. Este parecer se revalida só nesse trecho.

Para não abrir uma rodada 7, o autor deve repetir antes do push as cadeias de B7 e B8, as de B5 e B6 e a busca da classe acima: nome versionado em todos os pontos (opção, `-e` e heredoc) e opções longas por prefixo.

## Revalidação após o retrabalho 6
Diff revisado: `f56e9ae...de999e0` (2 commits: 14b3ac5, de999e0; 10 arquivos). Brief do autor: `bp-1-tech-lead-13.md`, "Entregar" 1 a 6.
Ferramentas: `python3 -m unittest tests.test_hooks -q` rodado nesta revisão em de999e0: `Ran 19 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO). Segurança: parecer próprio do `security-engineer` (E3.2), revalidado em paralelo; não refeito aqui.

Como reproduzir: o mesmo das rodadas anteriores (projeto temporário com `.forge/versao`, `.githooks/pre-push`, `.claude/settings.json` e `src/a.js` commitados; cada linha é o `command` de um PreToolUse Bash de `forge:dev` passado a `python3 hooks/conformidade.py`, com `CLAUDE_PROJECT_DIR` na raiz). "Base" é o hook de `f56e9ae` (`git archive f56e9ae hooks`), igual ao de 592098a. O efeito real da fuga nova (B9) foi conferido com `bash` numa cópia do projeto.

Cobertura declarada (VV-1): as cadeias de B7, B8 e do K listadas abaixo; as cadeias de B1, B5, B6, R10 e da mitigação das rodadas anteriores (todas seguem rc=2, e R10 segue rc=0); o dono do heredoc escrito com espaço, colado ao `<<`, entre aspas, com redirecionamento colado, por pipe, com caminho e por `env`; nomes de binário `perl5.34.0`, `perl5.34-x86_64-linux-gnu`, `ruby3.2`, `ruby3.2-x86_64`, `python3.12`, `python3-dbg`; GNU `sed` e `gawk` 5.1.0 com as opções longas por prefixo. Fora da cobertura: L e M e o restante da BP-5 (declarados); `inplace.awk` alcançado por link simbólico ou cópia com outro nome (programa lido de arquivo, BP-5); o vigia (R11 não está no diff).

### B7 e B8
- **B7 · fecha como classe nos pontos de opção e de `-e`.** `INTERPRETES` e `PERL_OU_RUBY` (`hooks/conformidade.py:49`-`:50`) aceitam qualquer sufixo que comece por dígito, e o teste do heredoc (`:641`) passou a usar `INTERPRETES`, a fonte única. Na HEAD dão rc=2, e na base rc=0: `perl5.34-x86_64-linux-gnu -pi -e 's/sh/XX/' .githooks/pre-push`, `perl5.34-x86_64-linux-gnu -e 'unlink q(.forge/versao)'`, `/usr/bin/perl5.34-x86_64-linux-gnu -pi ...`, `ruby3.2-x86_64 -e 'File.delete(".forge/versao")'`, `python3-dbg -c 'import os;os.remove(".forge/versao")'`, e o heredoc `perl5.34.0 <<'X'`, `perl5.34-x86_64-linux-gnu <<'X'`, `ruby3.2 <<'X'`, `cat <<'X' | perl5.34.0`, `env perl5.34.0 - <<'X'` e `/usr/bin/perl5.34.0 <<'X'` com `unlink q(.forge/versao)` no corpo. No heredoc, a troca abriu uma regressão (B9, abaixo).
- **B8 · fecha como classe.** `longa_do_gnu` (`:238`) resolve o prefixo como o `getopt_long` contra as listas `SED_LONGAS`/`GAWK_LONGAS` (`:57`-`:61`), `sed_no_lugar` (`:264`) e `script_do_sed` (`:255`) a usam, e `awk_no_lugar` (`:248`) liga a conferência para qualquer argumento que cite `inplace`. Na HEAD dão rc=2, e na base rc=0: `sed --expr='1w ...'`, `sed --e='1w ...'`, `sed -n --e='$w ...'`, `sed --i`, `sed --in-pl`, `sed --in-pl=.b` sobre `.githooks/pre-push`; `gawk --inc=inplace`, `gawk --incl inplace`, `gawk -E /usr/share/awk/inplace.awk`, `gawk -l inplace 'BEGINFILE{inplace_begin(...)} 1'`, `gawk --lo=inplace`, `gawk --exe /usr/share/awk/inplace.awk`, `gawk -e '@load "inplace"' -e 1` e `nawk -i inplace`. Também dão rc=2 `sed --expr '1w ...'` (valor separado), `gawk --sou='@include "inplace"'`, `gawk -i "inp"'lace'` e `gawk -i inpla\ce`.
- **K (resto barato) · fecha.** `SED_ESCREVE` (`:63`) com `!`, `,`, `$`, `~`, `+` e `M` antes do `w`/`W`: `sed '$w ...'`, `'/x/!w ...'` e `'s/a/b/Mw ...'` dão rc=2 (na base, rc=0); `'1,2w'`, `'1~2w'`, `'0,/x/w'`, `'/x/Iw'` e `-n '/x/,+3W .claude/settings.json'` seguem rc=2.
- **Sem falso positivo nos usos comuns:** rc=0 em `perl -pi -e 's/a/b/' src/a.js`, `perl5.34.0 -pi ... src/a.js`, `sed -i`/`sed --i 's/a/b/' src/a.js`, `sed -n '1p'`, `sed -n '/w/p'`, `sed -n '$p'` e `sed --expr='s/a/b/'` sobre `.githooks/pre-push`, `sed 's/$/w/' src/a.js`, `sed -e 's/a/w/' .claude/settings.json`, `sed 's/x/y/w out.txt' src/a.js`, `gawk -i inplace '{print}' src/a.js`, `gawk '{print}' .githooks/pre-push`, `grep -rn inplace docs`, `sed --help`/`--version`, `gawk --version`, `ls .git`, `git log` e `npm run script`.
- **Falso positivo do awk que cita `inplace` · aceitável.** `awk '/inplace/{print}' .githooks/pre-push`, uma leitura, dá rc=2 (na base, rc=0): `awk_no_lugar` não separa o texto do programa das opções. É do lado fechado, só ocorre quando o programa cita a palavra e o alvo é caminho protegido, e a saída é simples (`grep inplace .githooks/pre-push`); a alternativa, separar programa de opção com as abreviações do `gawk`, reabriria a classe B8. Fica como risco para o QA, não como ajuste.
- **Documentação:** o ADR 0009 (limite 2), `docs/hooks.md:36` e `changelog.d/bp-1.md` dizem o que o código cobre (plataforma no nome, heredoc, `nawk`, `-E`/`-l`/`--load`/`@load`, endereço antes do `w`, opção longa abreviada) e listam L e M com a BP-5, em texto neutro (R-NEUTRO). O "também no dono do heredoc" só fica verdadeiro com B9 corrigido.
- Fixtures: as 6 pedidas (`b7-perl-plataforma-bloqueia`, `b7-heredoc-perl-versao-bloqueia`, `b8-sed-expr-abreviado-bloqueia`, `b8-gawk-inc-abreviado-bloqueia`, `b8-gawk-E-inplace-bloqueia`, `k-sed-endereco-w-bloqueia`), rc=2. Commits: 2, em Conventional Commits em português, coerentes (fix, docs).

### Achados novos (por classe)
- **B9 · `hooks/conformidade.py:641` · classe "dono do heredoc", regressão do próprio retrabalho.** O teste do dono passou de `re.search(r"\b(...|perl|ruby|...)\b", dono)` para `INTERPRETES.match` sobre as palavras de `re.split(r"[\s;&|()`]+", dono)`. Como o corte não inclui `<`, `>` nem aspas, o nome colado a esses caracteres não é mais reconhecido. Com rc=0 na HEAD e rc=2 na base, e o `.forge/versao` de fato apagado numa cópia ao rodar a linha com `bash`:
  - `perl<<'X'` / `unlink q(.forge/versao)` / `X`
  - `"perl" <<'X'` / o mesmo corpo / `X`
  - `perl>/dev/null <<'X'` / o mesmo corpo / `X`

  Na mesma classe, já com rc=0 na base: `perl5.34.0<<'X'` e `'perl5.34.0' <<'X'`.
  - Por que bloqueia: é regressão (a base barrava), no trecho que esta volta mexeu, e a documentação da entrega diz "também no dono do heredoc".
  - Sugestão: cortar também em `<`, `>`, aspas e `\` (por exemplo, `re.split(r"[\s;&|()`<>'\"\\]+", dono)`), ou tirar as palavras do dono com o mesmo tokenizador da linha.
  - Fixtures: `b9-heredoc-colado-bloqueia` (`perl<<'X'`) e `b9-heredoc-aspas-bloqueia` (`"perl5.34.0" <<'X'`).
  - Severidade: bloqueia.
- **R11 · segue recomendado** (`hooks/vigia.py`, cosmético). Não entrou no brief desta volta.

### Parecer da revalidação
**Reprovado** por B9, regressão de uma linha introduzida em `hooks/conformidade.py:641`. B7 (nos pontos de opção e `-e`), B8 e o resto do K fecham como classe, sem falso positivo relevante; o do awk que cita `inplace` é aceitável e vai como risco para o QA, com R5, R6 e os dois casos da mitigação. R11 é recomendado.

A volta cabe em `hooks/conformidade.py:641` e duas fixtures. Este parecer se revalida só nesse trecho: antes do push, o autor roda as cinco cadeias de B9 acima, mais as de heredoc desta seção (com espaço, pipe, `env`, caminho), e lista o rc de cada uma.

## Revalidação após o retrabalho 7
Diff revisado: `3789092...61ddf7e` (2 commits: e79e971, 61ddf7e; 8 arquivos). Brief do autor: `bp-1-tech-lead-15.md`, "Entregar" 1 a 5.
Ferramentas: `python3 -m unittest tests.test_hooks -q` rodado nesta revisão em 61ddf7e: `Ran 19 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO). Segurança: parecer próprio do `security-engineer` (E3.2), revalidado em paralelo; não refeito aqui.

Como reproduzir: o mesmo das rodadas anteriores (projeto temporário com `.forge/versao`, `.githooks/pre-push`, `.claude/settings.json` e `src/a.js` commitados; cada linha é o `command` de um PreToolUse Bash de `forge:dev` passado a `python3 hooks/conformidade.py`, com `CLAUDE_PROJECT_DIR` na raiz). "Base" é o hook de `3789092` (`git archive 3789092 hooks`), igual ao de de999e0. O efeito real das duas fugas novas foi conferido com `bash` e GNU `sed` numa cópia do projeto.

Cobertura declarada (VV-1): matriz de 225 linhas de heredoc, 9 donos (`perl`, `perl5.34.0`, `perl5.34-x86_64-linux-gnu`, `ruby`, `ruby3.2`, `python3`, `python3.12`, `python`, `node`) × 25 formas (com espaço, colado a `<<`, `<<X` sem aspas, `<<-`, `<<"X"`, `>`/`<` colado antes do `<<`, entre aspas duplas e simples, aspas coladas ao `<<`, com barra, caminho absoluto com e sem aspas, `env`, `command`, `exec`, `nice`, subshell, `2>&1`, `-`, pipe com e sem espaço, aspas no meio do nome); mais `$'perl'`, `{ perl; }`, atribuição antes, `time`, `sudo`, e as mesmas formas de nome na linha (`p''erl -e`, `"p"erl -e`, `p\erl -e`); 20 linhas do `w` do `sed` (delimitador do usuário, colado, `-e`, `;w`, `w` antes no script, usos comuns). Fora: L, M e o restante da BP-5 (declarados), inclusive a cópia do `inplace.awk` com outro nome; o vigia (R11 fora do diff).

### B9 (N da segurança)
- **Fecha nas formas pedidas, não como classe.** `hooks/conformidade.py:642` corta as palavras do dono também em `<`, `>`, aspas e `\`. Na HEAD dão rc=2 (na base, rc=0) as 72 linhas da matriz com o nome colado a `<<`/`<`/`>`, entre aspas inteiras (`"perl" <<'X'`, `'python3' <<'X'`, `"/usr/bin/perl"<<'X'`) e com barra na frente (`\python3 <<'X'`); as 135 que já davam rc=2 seguem rc=2. Nenhuma linha passou de rc=2 a rc=0.
- **Resta a mesma classe com o nome quebrado por aspas ou barra no meio** (B10, abaixo): o corte trata aspas e barra como separador, e o shell as tira. A linha comum já usa o tokenizador do shell e barra essas formas (`p''erl -e 'unlink q(.forge/versao)'` dá rc=2); só o dono do heredoc diverge.
- Fixtures: as 3 do N (`n-heredoc-dono-colado/aspas/barra-bloqueia`), rc=2.

### `w` do sed com delimitador do usuário (K)
- **Fecha nas formas pedidas.** `SED_ESCREVE` (`:64`) virou `[wW]\s*(\S+)`: `s|a|b|w .githooks/pre-push`, `\%a%w ...`, `sxaxbxw ...` e `s|a|b|w.githooks/pre-push` dão rc=2 (na base, rc=0). Fixture `k-sed-delimitador-w-bloqueia`, rc=2.
- **Abriu uma regressão** (B11, abaixo): o `findall` não se sobrepõe, e um `w` anterior no script engole o `w` do comando.
- **Falso positivo novo · aceitável.** Qualquer `w`/`W` seguido de palavra que seja caminho protegido conta como escrita: `sed -n '/show .githooks/p' src/a.js`, uma leitura, dá rc=2 (na base, rc=0). Só ocorre com o caminho protegido logo depois de um `w` no script, é do lado fechado e tem saída simples (`grep`); `sed -n '/w/p' .githooks/pre-push`, `sed 's/word/x/' .githooks/pre-push`, `sed 's/x/y/w out.txt' src/a.js` e `sed -i 's/a/b/' src/a.js` seguem rc=0. Vai como risco para o QA, junto com o do awk que cita `inplace`.

### Documentação
ADR 0009 (limite 2), `docs/hooks.md` e `changelog.d/bp-1.md` passam a citar o dono colado, entre aspas e com barra, o `w` depois de delimitador do usuário e a cópia do `inplace.awk` com outro nome na BP-5, em texto neutro (R-NEUTRO). "Entre aspas ou com barra" e o `s/a/b/w` só ficam verdadeiros com B10 e B11 corrigidos. Commits: 2, Conventional Commits em português, coerentes (fix, docs).

### Achados novos (por classe)
- **B10 · `hooks/conformidade.py:642` · classe "dono do heredoc", nome que o shell normaliza (aspas ou barra no meio).** rc=0 na HEAD e na base, com o `.forge/versao` de fato apagado ao rodar com `bash` (corpo `unlink q(.forge/versao)`, ou o equivalente de cada linguagem):
  - `p''erl <<'X'`, `"p"erl <<'X'`, `p\erl <<'X'`, `pe\rl<<'X'`
  - a mesma forma com `perl5.34.0`, `perl5.34-x86_64-linux-gnu`, `ruby`, `ruby3.2`, `python3`, `python3.12`, `python` e `node` (18 linhas da matriz)
  - Por que bloqueia: está na classe de B9, que a documentação desta entrega promete ("entre aspas ou com barra"), e a linha comum já barra as mesmas formas.
  - Sugestão (fecha a classe): tirar `"`, `'` e `\` do dono antes de cortar, `re.split(r"[\s;&|()`<>]+", re.sub(r"[\"'\\]", "", dono))`, ou usar o mesmo tokenizador da linha. Conferido fora do hook: a forma sugerida reconhece as 4 acima, `"/usr/bin/perl"<<X`, `'python3' <<'X'`, `perl>/dev/null <<X` e o pipe, e não reconhece `cat <<'X'`.
  - Fixture: `b10-heredoc-aspas-no-meio-bloqueia` (`p''erl <<'X'` e `p\erl <<'X'`).
  - Severidade: bloqueia.
- **B11 · `hooks/conformidade.py:64` · classe "`w` do sed precedido de outro `w`/`W` no script", regressão do próprio retrabalho.** `[wW]\s*(\S+)` com `findall` consome o primeiro `w` e a palavra colada a ele, e o `w` do comando, dentro dessa palavra, não é mais visto. rc=0 na HEAD, com o `.githooks/pre-push` de fato sobrescrito pelo GNU `sed`:
  - `sed 's/aw/b/w .githooks/pre-push' src/a.js` (na base, rc=2: regressão)
  - `sed 's|w|b|w .githooks/pre-push' src/a.js`, `sed 's/new/old/w .githooks/pre-push' src/a.js`, `sed -n '/www/w .githooks/pre-push' src/a.js` (na base, rc=0)
  - Por que bloqueia: regressão no trecho que esta volta mexeu, sobre a forma básica `s/a/b/w arquivo` que a documentação declara coberta.
  - Sugestão (fecha a classe): busca sobreposta, `SED_ESCREVE = re.compile(r"(?=[wW]\s*(\S+))")`; conferido fora do hook, acha `.githooks/pre-push` nas 4 linhas acima. O falso positivo aceito não muda.
  - Fixture: `b11-sed-w-engolido-bloqueia` (`s/aw/b/w .githooks/pre-push`).
  - Severidade: bloqueia.
- **R11 · segue recomendado** (`hooks/vigia.py`, cosmético), fora do diff.

### Parecer da revalidação
**Reprovado** por B10 e B11. B9 fecha nas formas pedidas (colado, aspas inteiras, barra na frente; 72 linhas que eram rc=0 passam a rc=2, nenhuma regride), mas a classe fica aberta com aspas ou barra no meio do nome; o `w` do sed com delimitador do usuário fecha nas formas pedidas, mas a regex nova perde o `w` do comando quando há outro `w` antes no script, inclusive em `s/aw/b/w`, que a base barrava. O falso positivo novo (palavra depois de `w`/`W` que é caminho protegido) é aceitável e vai como risco para o QA, com o do awk que cita `inplace`, R5, R6 e os dois casos da mitigação.

A volta cabe em duas linhas (`hooks/conformidade.py:64` e `:642`) e duas fixtures. Este parecer se revalida só nesses dois trechos: antes do push, o autor roda a matriz de heredoc desta seção (os 9 donos × as formas listadas, inclusive aspas e barra no meio) e as 20 linhas do `sed`, e lista o rc de cada grupo; nenhuma linha que dá rc=2 em 61ddf7e pode passar a rc=0.

## Revalidação após o retrabalho 8
Diff revisado: `1ad71cc...d986c37` (2 commits: ae55b7d, d986c37; 7 arquivos). Brief do autor: `bp-1-tech-lead-17.md`, "Entregar" 1 a 5.
Ferramentas: `python3 -m unittest tests.test_hooks -q` rodado nesta revisão em d986c37: `Ran 19 tests ... OK`. Suíte inteira e `scripts/validar-plugin.sh` não refeitos (R-TETO). Segurança: parecer próprio do `security-engineer` (E3.2), revalidado em paralelo (VV-4); não refeito aqui.

Como reproduzir: o mesmo das rodadas anteriores (projeto temporário com `.forge/versao`, `.githooks/pre-push`, `.claude/settings.json` e `src/a.js` commitados; cada linha é o `command` de um PreToolUse Bash de `forge:dev` passado a `python3 hooks/conformidade.py`, com `CLAUDE_PROJECT_DIR` na raiz). "Base" é o hook de `61ddf7e` (`git archive 61ddf7e hooks`); "HEAD", o de `d986c37`.

Cobertura declarada (VV-1): heredoc, 1925 linhas: os 9 donos da rodada 7 (`perl`, `perl5.34.0`, `perl5.34-x86_64-linux-gnu`, `ruby`, `ruby3.2`, `python3`, `python3.12`, `python`, `node`) com `''`, `""` e `\` inseridos em cada posição do nome e com aspas abrindo ou fechando no meio (`"p"erl`, `pe'rl'`), × 5 formas de abrir (`<<'X'` com e sem espaço, `<<X`, `<<-X`, `<<"X"`); 15 linhas com expansão antes do nome (`${X}"perl"`, `$(true)"perl"`, `` `true`"perl" ``, `"$X"perl`, e na linha comum), para ver se tirar as aspas do dono abre alguma; `sed`, 37 linhas: as 6 do brief, as 20 da rodada 7, 9 com `w` depois de `w` (`s/ww/ww/w`, `w x;w`, `/w/{w ...}`, `gw`, `w` com tabulação, `Ww`) e 8 usos comuns que devem seguir livres; a linha comum com aspas e barra no meio (9 linhas, não deve regredir). Fora: L (grafia não literal fora do heredoc), M e a cópia do `inplace.awk` com outro nome (BP-5, declarados); o vigia (R11, fora do diff).

### B10 (dono do heredoc com aspas ou barra no meio)
- **Fecha como classe.** `hooks/conformidade.py:642` tira `"`, `'` e `\` do dono antes de cortar (`re.split(r"[\s;&|()`<>]+", re.sub(r"[\"'\\]", "", dono))`), como o shell faz. As 1925 linhas dão rc=2 na HEAD; 495 eram rc=0 na base (as 18 do B10, `p''erl`, `"p"erl`, `p\erl`, `pe\rl<<'X'`, e as demais posições e donos) e 1430 já eram rc=2. Nenhuma linha passa de rc=2 a rc=0.
- As 15 linhas com expansão antes do nome seguem rc=2 na base e na HEAD (juntar os pedaços não esconde o nome de outra conferência); `cat <<'X'`, `cat<<X` com `perl` no corpo e `echo perl <<'X'` seguem rc=0 (sem falso positivo novo).
- Fixture: `b10-heredoc-dono-aspas-no-meio-bloqueia` (`p''erl <<'X'`), rc=2.

### B11 (`w` do sed depois de outro `w`; O da segurança)
- **Fecha como classe.** `hooks/conformidade.py:64` virou busca sobreposta, `(?=[wW]\s*(\S+))`: cada `w`/`W` do script é candidato, inclusive dentro da palavra de outro. As 6 do brief (`s/aw/b/w`, `s/saw/x/;w .git/config`, `s|w|x|;w`, `s/new/old/w`, `/www/w`, `y/w/w/;w .git/config`), `s|w|b|w` e as 9 de `w` depois de `w` dão rc=2 na HEAD (8 delas eram rc=0 na base; `-e 's/aw/b/' -e 'w ...'` já era rc=2); as 20 da rodada 7 seguem rc=2.
- Os usos comuns seguem rc=0: `sed -n '/w/p' .githooks/pre-push`, `sed 's/word/x/' .githooks/pre-push`, `sed 's/x/y/w out.txt' src/a.js`, `sed 's/aw/b/w out.txt' src/a.js`, `sed -n 's/www/x/p' src/a.js`, `sed -i 's/a/b/' src/a.js`. O falso positivo aceito na rodada 7 (palavra depois de `w`/`W` que é caminho protegido) não muda de alcance.
- Fixtures: `o-sed-w-mascarado-bloqueia` (`s/aw/b/w .githooks/pre-push`) e `o-sed-w-depois-de-w-bloqueia` (`s/saw/x/;w .git/config`), rc=2.

### Documentação
ADR 0009, `docs/hooks.md` e `changelog.d/bp-1.md` acrescentam só "inclusive no meio do nome (`p''erl`, `pe\rl`)" e "depois de outro `w` no mesmo script (`s/aw/b/w arq`, `;w arq`)": batem com o código desta volta e com a matriz acima; o resto de L, M e a cópia do `inplace.awk` seguem com a BP-5. Texto neutro (R-NEUTRO). Commits: 2, Conventional Commits em português, coerentes (fix com as fixtures, docs).

### Achados novos (por classe)
- Nenhum que bloqueie. Nenhuma regressão desta volta na cobertura declarada acima.
- **R12 · recomendado · `tests/hooks/conformidade/b10-heredoc-dono-aspas-no-meio-bloqueia.json` · dentro do que a documentação promete.** A fixture cobre só as aspas (`p''erl`); a documentação cita também a barra no meio (`pe\rl`), que a matriz confirma (rc=2), mas sem fixture que a prenda. Sugestão: uma fixture com `pe\rl<<'X'` numa próxima volta que mexa nesse trecho; não abre rodada.
- **R11 · segue recomendado** (`hooks/vigia.py`, cosmético), fora do diff.

### Parecer da revalidação
**Aprovado.** B10 e B11 fecham como classe nas linhas `hooks/conformidade.py:642` e `:64`: aspas ou barra em qualquer posição do nome do dono do heredoc e `w` do sed depois de outro `w` dão rc=2, nenhuma linha que dava rc=2 em 61ddf7e passa a rc=0, e os usos comuns seguem livres. A documentação diz o que o código cobre. Riscos para o QA, sem mudança: o falso positivo do `w` seguido de caminho protegido, o do awk que cita `inplace`, R5, R6 e os dois casos da mitigação; L, M e a cópia do `inplace.awk` ficam com a BP-5.
