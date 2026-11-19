---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 993b6bb3f3a514753a8f21f0dcceb216f2791d67
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E3.39 (melhoria/v0478-guardas-parecer), revalidação do A13 da segurança da E3.34

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo deaf3570..993b6bb3 (E3.37: 86192822 e 993b6bb3). No domínio: `api_depois_de_cd_sem_resolver` e `tira_o_rascunho` (hooks/parecer.py:1150 a 1175), a chamada em `conferir` (hooks/parecer.py:1331), a linha D6 de `docs/hooks.md`, o gerador `gerar_sessao_alheia` de `tests/test_hooks_parecer_matriz.py`, M77 a M79 em `-12.json`, M80 e M81 em `-13.json` e o fragmento `changelog.d/`. Nada fora do delta relido.

## Sondas
- S41 · sessão na cópia alheia, `d=proj; cd "$d" && gh api -X PUT repos/dono/forge/pulls/1/merge` · espera: código 2 · obtido: 2, mensagem do A13
- S42 · mesma sessão, `d=proj; cd "$d" && gh api graphql -f query='query{viewer{login}}'` e `export HOME; cd ~/proj && gh api -X POST repos/outro/x/issues -f title=t` · espera: 0 e 0 (leitura legível; endpoint fora de merge e graphql) · obtido: 0 e 0
- S43 · sessão na cópia alheia e fora de cópia, `gh api -X PUT repos/dono/forge/pulls/1/merge` sem `cd` · espera: 0 (limite declarado em docs/hooks.md, "Fora:") · obtido: 0 e 0
- S44 · sessão na cópia alheia, `(cd proj; gh api -X PUT repos/dono/forge/pulls/1/merge)` · espera: 2 (cd de subshell deixa a pasta desconhecida, falha fechada) · obtido: 2, mensagem do A13

## Conferências
- A13 fechado: com a sessão fora de clone, o `gh api` de merge ou de graphql que muda depois do `cd` sem resolver recusa (S41); o GET e o graphql legível seguem (S42). A precedência em hooks/parecer.py:1161 (`or` com `and`) lê `merge or (graphql and tira_o_rascunho)`, como a docstring diz.
- Extração de `tira_o_rascunho` não muda `pronto_por_graphql` (M80 morre por `test_a2_ready_por_graphql_no_clone`).
- Mutação dirigida (`bin/forge-mutante --processos 1`, `-12.json` e `-13.json`): M72 a M81 `morreu`.
- Cobertura (`bin/forge-mutante --cobertura --base deaf3570`): :1156, :1158, :1161, :1181 e :1331 `coberta` (M77 a M81).
- Teste do item: `python3 -m unittest tests.test_hooks_parecer_matriz.SessaoNaCopiaAlheia tests.test_hooks_fila27.Fila27.test_a2_ready_por_graphql_no_clone`: OK (52 s); o gerador afirma mínimo de 110 casos.
- Leitura (checklist 1 a 4, 7, 11): ramo de falha por comportamento (subprocesso com o hook), controles resolvido, no clone e sem `cd`; a D6 e o changelog.d descrevem o código.
- Tamanho (H1): cerca de 30 linhas de código no delta, um comportamento.
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Achados
- A2 (recomendado) hooks/parecer.py:1162 · a mensagem lista "variável, ~ com HOME mexido, CDPATH, crase ou $( )", mas o `cd` literal em subshell também recusa (S44); incluir "subshell ou condicional" na mensagem e na D6.

## Parecer
Aprovado: A13 fechado, S41 em código 2, controles S42 e S43 como esperado, M77 a M81 mortos e guardas cobertas. A2 é recomendado (cartão), sem volta.
