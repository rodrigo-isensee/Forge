---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: deaf35704182bc20c1bcc2e630f044480e1ddb06
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-19
---
# Review: v0478 E3.35 (melhoria/v0478-guardas-parecer), revalidação do A12 da segurança da E3.32

## Revalidação
- Delta lido: `forge-check parecer delta docs/reviews/v0478-guardas-parecer.md`, intervalo 460a8a00..deaf3570 (E3.33: deaf3570; pareceres e merge 946926e9 fora do domínio). No domínio: `pasta_do_gh` (hooks/parecer.py:1049 a 1069), a linha D6 da matriz em `docs/hooks.md`, a classe `SessaoNaCopiaAlheia` do gerador `tests/test_hooks_parecer_matriz.py`, o M76 de `tests/mutantes/v0478-guardas-parecer-12.json` e o fragmento `changelog.d/`. Nada fora do delta relido.

## Sondas
- S38 · montagem do gerador, sessão na cópia alheia, `d=proj; cd "$d"`, `cd "$(echo ~/proj)"` e `` cd `echo proj` `` antes de `gh pr ready feature/x` · espera: código 2 · obtido: código 2 nas três, mensagem do A12
- S39 · mesma montagem, `cd ../proj && gh pr ready feature/x` (resolvido) e `gh pr ready feature/x` (sem cd) · espera: 2 pelo parecer ausente no clone e 0 · obtido: 2 (falta parecer de `feature/x`) e 0
- S40 · sessão num projeto com `hooks_desligados: ["parecer"]`, `gh pr ready feature/x` e `d=x; cd "$d" && gh pr ready feature/x` · espera: 0 e 0 (hook desligado) · obtido: 0 e 2 (base do A1)

## Conferências
- A12 fechado: com a sessão numa cópia fora de clone, o `cd` sem resolver não cai mais na pasta da chamada (hooks/parecer.py:1065); o gh sem `cd` segue em 0 (S39).
- Mutação dirigida (`bin/forge-mutante --processos 1`, `-12.json`): M72 a M76 `morreu`; M76 em hooks/parecer.py:1065.
- Cobertura (`bin/forge-mutante --cobertura --base 460a8a00`): guarda de :1065 `coberta` pelo M76.
- Teste do item: `python3 -m unittest tests.test_hooks_parecer_matriz.SessaoNaCopiaAlheia`: 1 teste, OK.
- Leitura (checklist 1 a 4, 7): o teste exercita o ramo de falha por comportamento (subprocesso com o hook), com controle resolvido e legítimo sem `cd`; a D6 descreve o código.
- Tamanho (H1): cerca de 5 linhas de código no delta, um comportamento.
- Suíte: sem PR, sem CI a citar; não rerrodada (R-REVIEW).

## Achados
- A1 (recomendado) hooks/parecer.py:1065 · o ramo também alcança a sessão num projeto com `parecer` em `hooks_desligados` (S40: 2); a docstring diz, mas a D6 de docs/hooks.md e o changelog.d falam só de cópia alheia. Declarar o caso nos dois.

## Parecer
Aprovado: A12 fechado, S38 em código 2, controles de S39 como esperado, M76 morto e guarda coberta. A1 é recomendado (cartão), sem volta.
