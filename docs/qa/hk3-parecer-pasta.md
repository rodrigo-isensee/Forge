---
tipo: qa
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 212203a39fd4419c45dd797ea0737b7d05001d19
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: hk3-parecer-pasta (PR A do HK3: o hook parecer resolve a pasta do git)

Plano: o pedido é de correção do controle do Forge, sem especificação de UX; as obrigações são a decisão técnica e os casos P e B de `docs/security/hk3-parecer-ameacas.md` (em `~/.forge-contrib/docs/security/`). Teste de abuso: o corpus `pasta-*` (54 fixtures) e as 4 specs de mutantes.

## Achados
- A1 (bloqueante) hooks/parecer.py:240 · `git -C` com crase sem aspas (substituição) seguido de merge passa (rc=0) a partir de worktree de trabalho e funde na integração sem parecer; `$( )`, crase entre aspas e `cd` com crase recusam; sem fixture. Classe: pasta do -C com substituição (HK3-01)
- A2 (recomendado) hooks/parecer.py:555 · invólucros `env -C <integ> git merge`, `env GIT_DIR=... git merge`, `nice git -C <integ> merge` e `command git ...` passam (rc=0): o hook só lê `git` na primeira palavra; o modelo não os cita; registrar na limitação ou barrar

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| P: cd literal + pull --rebase + push, `-C` com til, variável, relativo repetido, cd em subshell, gh depois de pushd | `PastaDoGit.test_corpus_pasta_passa_e_barra` (15 fixtures `pasta-passa-*`) | permissão: pasta resolvida vale a branch dela | passou |
| B: `-C`, cd, variável, `--git-dir`, `--work-tree`, `GIT_DIR`, pushd, atribuição em subshell, if, `\|\|`, `&`, export, read, cd inexistente, CDPATH, cd com 2 argumentos (39 fixtures `pasta-barra-*`) | idem | pasta desconhecida, vazio, relativo sem base | passou |
| Merge e pull de integração sem parecer continuam barrados | sonda própria (HEAD de integração, `-C` repetido, `-C` com barra final, `~/..`, `cd` com `.`) rc=2 "nenhum parecer" | integração | passou |
| `-C` com crase sem aspas | sonda própria | substituição | FALHOU (A1, bug HK3-01) |

## Cenários e resultado real
- Corpus: `python3 -m unittest tests.test_hooks_parecer_pasta`: 1 teste, OK, 54 fixtures verificadas (1,4 s).
- Mutantes: `bin/forge-mutante tests/mutantes/hk3-parecer-pasta-{1,2,3,4}.json`: rc=0, M1 a M29 todos "morreu". Conferência da lista contra o diff: linhas de guarda sem mutante eram 200, 204, 242 (forma `=`), 529, 530 e 531; somei Q1 a Q6 em spec minha e todos morreram (parecer.py:529, 530, 531, 200, 204, 242). Sem achado por mutante.
- Vermelho antes do verde: `bin/forge-testes --vermelho ff3936ae4011a95f25c37280fe32e4fa5ced0d95 --modulos test_hooks_parecer_pasta` (rc=0): `vermelho: base=ff3936ae4011 head=212203a39fd4 módulos=test_hooks_parecer_pasta`; `revertidos à base: bin/forge-testes, changelog.d/hk3-parecer-pasta.md, hooks/parecer.py`; `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_pasta_passa_e_barra · H=ok · B=falha · prova (asserção)`; `contagem: prova (asserção)=1`.
- Sondas próprias (projeto em develop e worktree em `melhoria/x`, 36 comandos): o par do brief (`cd <wt> && git pull --rebase origin melhoria/x && git push origin HEAD:refs/heads/melhoria/x`) passa (rc=0); `git pull --rebase` e `git merge` com HEAD de integração, `git -C <integ> merge`, `$V`, `$HOME`, `$(echo)`, `GIT_DIR=`, `GIT_WORK_TREE=`, `--git-dir=`, `-c core.worktree=`, symlink, CDPATH, `cd -`, `||`, `&` e pipeline ficam barrados (rc=2). Falha: A1 e A2. `(cd <integ>); git merge` barra por "sem parecer" (conservador, sem bug).
- PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia ("nenhum ainda"); A1 é a primeira ocorrência da classe, sem linha AR a gravar.
- Suíte completa: não rodada por mim (o brief a limita ao pre-push); rodei o módulo do item, o forge-mutante e o vermelho.
- Bug: `docs/qa/bugs/HK3-01-dash-c-com-crase-sem-aspas-passa.md`.
