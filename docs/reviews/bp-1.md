---
tipo: review
contrato: 1
pedido: bp-1
branch: melhoria/bp-1
commit: 7ec8c60b7a793fb911e8ab6c6230f725a6dffbcc
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-17
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
