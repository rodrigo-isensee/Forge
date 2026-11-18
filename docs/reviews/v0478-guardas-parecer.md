---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 56bb90b555cc63d4f035dd27d0d35a6541e3647a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E3.12 (melhoria/v0478-guardas-parecer), volta do E3.7

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo c41f7fe5..56bb90b5 (commit 56bb90b5, E3.10; o merge c0c3af4f só trouxe os pareceres). No domínio: `hooks/parecer.py`, `tests/test_hooks_parecer_repo.py`, 4 fixtures `incidente-r-copia-alheia-*gh-repo*`, `tests/mutantes/v0478-guardas-parecer{,-4}.json`, `docs/hooks-fixtures.md` (gerado) e o fragmento `changelog.d/`. Nada fora do delta relido.

## Achados
- A2 (bloqueante) hooks/parecer.py:605 · `mexidas_na_linha` não vê o GH_REPO que `source`/`.` exporta: na cópia alheia, `source env.sh; gh pr ready feature/x` (env.sh com `export GH_REPO=dono/forge`) dá 0 sem parecer (S6, S7; R-REVIEW). Mesmo achado que o A5 da segurança (E3.13).

## Sondas
- S1 · cwd {tmp}/alheio (cópia alheia da fixture `incidente-r-copia-alheia-export-gh-repo-ready-bloqueia`), sessão no clone com remoto dono/forge, `export GH_REPO=dono/forge; gh pr ready feature/x`, sem parecer · espera: código 2 (R-REVIEW) · obtido: código 2 (R-REVIEW, GH_REPO mexido antes na linha)
- S2 · mesma montagem, `GH_REPO=dono/forge gh pr ready feature/x` (controle) · espera: código 2 · obtido: código 2 (R-REVIEW, sem parecer)
- S3 · mesma montagem, `set -a; GH_REPO=dono/forge; gh pr ready feature/x` · espera: código 2 · obtido: código 2
- S4 · mesma montagem, `env GH_REPO=dono/forge gh pr ready feature/x` · espera: código 2 · obtido: código 2 (sem parecer)
- S5 · mesma montagem, `typeset -x`, `read GH_REPO <<<…; export GH_REPO`, `printf -v GH_REPO`, subshell `( export …; gh pr ready … )` · espera: código 2 · obtido: código 2 nas quatro
- S6 · mesma montagem, `env.sh` na cópia com `export GH_REPO=dono/forge`, `source env.sh; gh pr ready feature/x` · espera: código 2 (R-REVIEW) · obtido: código 0
- S7 · mesma montagem, `. ./env.sh && gh pr ready feature/x` · espera: código 2 · obtido: código 0

## Conferências
- A1 (meu, E3.7) fechado: `repo_indicado` (hooks/parecer.py:920-923) faz do GH_REPO mexido na linha, sem `-R` nem prefixo, um repositório incerto, e `pasta_do_gh` recusa fora de clone e de projeto (:942). `GH_REPO` entra nos `SENSIVEIS` (:113), que só alimentam `mexidas`; nenhum outro uso de `mexidas` muda por ele (`com_til`, `depois_do_cd`, `pasta_do_git` olham `HOME`, `CDPATH` e `DESVIOS`). Mesmo achado que o A5 da segurança.
- Mutação dirigida (`bin/forge-mutante tests/mutantes/v0478-guardas-parecer-4.json`, 1 processo): M22 a M26 `morreu`, rc=0. O M26 substitui a isenta velha de `raiz_declarada() or pasta` (A1 da QA, E3.9).
- Cobertura (`bin/forge-mutante --cobertura --base 4182a6b9`, Base-sha do brief): as guardas do delta `:914` (M26), `:923` (M23), `:942` (M24) `coberta`; o resto como na volta anterior; rc=0.
- Teste do item: `python3 -m unittest tests.test_hooks_parecer_repo`: 5 testes, OK; o mínimo de `incidente-r-*` sobe de 19 para 23.
- Leitura (checklist 1 a 4, 7, 9): a guarda é mais estrita, nunca mais frouxa; a mensagem diz a saída (`-R <dono/repo>` ou `cd <clone>`). `gh pr create --draft` com GH_REPO exportado na cópia alheia também recusa (sonda minha, código 2): falha fechada com saída dita, aceitável. Commit único e coerente; fragmento do changelog com a prova no head anterior.
- Tamanho (H1): cerca de 20 linhas de código no delta, um comportamento.
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Parecer
Reprovado por A2. O A1 da volta anterior está fechado nas formas em que a linha atribui o GH_REPO (export, `&&`, `set -a`, `declare -x`, `typeset -x`, `read`, `printf -v`, subshell), com fixture de recusa por forma e mutante morto por guarda; mas o arquivo lido por `source`/`.` pode exportá-lo sem que o hook veja (S6, S7, confirmando o A5 da segurança). Sugestão: fora de clone e de projeto, `source`/`.` antes do gh na linha conta como GH_REPO mexido (REPO_INCERTO), com fixture por forma e mutante na guarda. Segue fora deste item, para cartão próprio, o `gh api -X PUT repos/<dono>/<forge>/pulls/<n>/merge` com cwd fora de cópia de trabalho (código 0, já registrado no parecer anterior; `merge_por_api`, linha não tocada pelo delta).
