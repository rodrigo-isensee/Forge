---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: c41f7fe58808dfae86c046611c39ee4de9825098
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0478 E3.7 (melhoria/v0478-guardas-parecer), volta do E3.3

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo d8e9aa8b..c41f7fe5 (commit c41f7fe5, E3.6). No domínio: `hooks/parecer.py`, `tests/test_hooks_parecer_repo.py`, 14 fixtures novas (`incidente-r-copia-alheia-*`, `graphql-*`), `tests/mutantes/v0478-guardas-parecer{,-2,-3}.json`, `tests/mutantes/v0457-fila27-2.json`, `docs/hooks-fixtures.md` (gerado) e o fragmento `changelog.d/`. Nada fora do delta relido.

## Achados
- A1 (bloqueante) hooks/parecer.py:932 · Na cópia alheia, GH_REPO exportado antes do gh na mesma linha (`export GH_REPO=dono/forge; gh pr ready feature/x`) não conta como repositório indicado: `pedido` None, decide pelos remotos da cópia e libera sem parecer (S1; R-REVIEW). Mesmo achado que o A5 da segurança (E3.8).

## Sondas
- S1 · cwd {tmp}/alheio (cópia alheia da fixture `incidente-r-copia-alheia-ready-r-bloqueia`), sessão no clone com remoto dono/forge, `export GH_REPO=dono/forge; gh pr ready feature/x`, sem parecer · espera: código 2 (R-REVIEW) · obtido: código 0
- S2 · mesma montagem, `GH_REPO=dono/forge gh pr ready feature/x` (controle) · espera: código 2 · obtido: código 2 (R-REVIEW, sem parecer)

## Conferências
- A1 (meu, E3.3) fechado: `pasta_do_gh` (hooks/parecer.py:925) só devolve a pasta do gh num clone do Forge ou num projeto; a cópia alheia com `-R`, `--repo`, `GH_REPO=` ou URL vai ao clone da sessão com remoto do slug, ou recusa. Fixtures `incidente-r-copia-alheia-{ready-r,merge-url,gh-repo-merge,create-r,cd-repo}-bloqueia` cobrem as sondas S1 a S3; `repo-desconhecido-bloqueia` e `sem-repo-libera` dão os dois lados.
- A2 (segurança) fechado: cópia sem manifesto e sem `-R` decide pelos remotos (`remotos(copia) & remotos(clone)`, :932-933); fixture `incidente-r-copia-alheia-remoto-do-forge-bloqueia`.
- A3 (segurança) fechado: `graphql_no_clone` (:981) usa a sessão quando a pasta não é clone nem projeto; `graphql-fora-do-clone-ready-bloqueia` e `-consulta-libera`, `graphql-copia-alheia-ready-bloqueia`.
- A4 (segurança) fechado: `arquivo_trocado_na_linha` (:993) recusa graphql com `=@`/`--input` quando a linha tem outro comando além do `cd`; `acompanhado` desce às substituições (:1093-1094). Sondas minhas no head: `cp m.txt l.graphql && gh api graphql -F query=@l.graphql` recusa (código 2, a mensagem nova); a troca dentro de `"$(cp …)"` ou de crase no argumento do próprio gh recusa (código 2, consulta ilegível, falha fechada).
- Mutação dirigida (`bin/forge-mutante` nas três specs do item, `--base d8e9aa8b`, 1 processo): M1 a M21 `morreu`, rc=0. Inclui M14 a M21 das guardas novas.
- Cobertura (`bin/forge-mutante --cobertura --base 4182a6b9`, Base-sha do brief): toda condição mudada `coberta`, `movida` ou `isenta` com motivo (`:913`, `CLAUDE_PROJECT_DIR` sempre definida; `:980(base)`, condição movida para `graphql_no_clone`, coberta por M21); rc=0.
- Teste do item: `python3 -m unittest tests.test_hooks_parecer_repo`: 5 testes, OK (inclui o novo `test_graphql_fora_do_clone_e_arquivo_trocado_na_linha`, mínimo de 6 fixtures; `incidente-r-*` sobe o mínimo para 19).
- Leitura (checklist 1 a 4, 7, 9): a guarda nova é mais estrita, nunca mais frouxa (a cópia alheia com `-R` de repositório que a sessão não tem passa a recusar, como pediu a segurança); funções pequenas (`remotos`, `sessao_ou`); docstrings atualizadas; commit único e coerente; fragmento do changelog com a prova no head anterior.
- Tamanho (H1): cerca de 50 linhas de código no delta, um comportamento (o alvo do gh e do graphql fora do clone).
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Parecer
Reprovado por A1. Os quatro achados da volta anterior (A1 do review e da QA; A2 a A4 da segurança) estão fechados nas formas cobertas, com fixture de recusa por caminho, mutante declarado por guarda e todos mortos; mas o repositório indicado ainda vem só do `GH_REPO=` prefixo do comando, e o `export` (ou `declare -x`, `set -a`) anterior na linha passa (S1, confirmando o A5 da segurança). Sugestão: tomar como `repo` o `GH_REPO` do ambiente que `conferir` já acompanha na linha (`ambiente`) e somar fixture `incidente-r-copia-alheia-*` por forma, com mutante na guarda. Fica fora deste item, para cartão próprio: `gh api -X PUT repos/<dono>/<forge>/pulls/<n>/merge` com cwd fora de cópia de trabalho e sessão no clone dá código 0 no `parecer` (sonda no head c41f7fe5; `merge_por_api` decide pela pasta, mesma classe do A3, linha não tocada pelo delta).
