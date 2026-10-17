---
tipo: review
contrato: 1
pedido: bp-1
branch: melhoria/bp-1
commit: 99648a358622b2f75eba5e1210da04d52cfa9670
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
