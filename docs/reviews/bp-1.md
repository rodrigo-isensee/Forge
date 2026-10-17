---
tipo: review
contrato: 1
pedido: bp-1
branch: melhoria/bp-1
commit: 95a1140b65db1cccc053cdeb627c1f6b830400c1
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
