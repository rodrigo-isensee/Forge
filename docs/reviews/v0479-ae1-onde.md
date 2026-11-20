---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-ae1-onde
commit: b11db7154c0b4eb2d91b50a15242e46ed7aa297b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E58.6 e E58.15, AE1.1 `forge-check onde`, head b11db715)

Escopo lido: `git diff 5ccac0bf..bef021c1` (3 commits; `bin/forge_onde.py`, o subcomando em `bin/forge-check`, `tests/test_forge_onde.py`, 7 specs de mutante, changelog, índice, peso D4, `bin/forge-testes`). Desenho: AE1.1 de `docs/propostas/v0479-melhorias-anti-erro.md` (origin/melhoria/v0479-melhorias-anti-erro).

## Ferramentas citadas (sem refazer)
- Suíte: só no CI do PR (`R-REVIEW`); não rerrodada aqui.
- Teste novo: `python3 -I -m unittest discover -s tests -p test_forge_onde.py` com ambiente limpo: 30 testes, OK.
- `bin/forge-changelog conferir --base origin/develop`: ok, 1 fragmento novo.
- Specs de mutante: 49 mutantes em 7 arquivos (8 por arquivo, o último com 1); a mutação é do autor (V2), não rerrodada.
- Tamanho (H1): `bin/forge_onde.py` 143 linhas com docstrings, mais 6 no `forge-check` e 1 no `forge-testes`: dentro do teto.

## Leitura
- Faz o que o desenho pede: presença em develop, homolog e main por `merge-base --is-ancestor` contra `origin/<base>` com o sha lido; PR por `gh pr view` (state, base, mergedAt, mergedBy); só leitura, sem fetch.
- Riscos do desenho cobertos: alvo que começa com `-` ou branch com `..` sai rc 2 sem chegar ao git; `rev-parse` com `--end-of-options`; o `gh` lento sai pelo teto do `gh_json` como `nao-verificavel`, nunca `sim`; toda linha passa por `sem_controle`.
- Falso do `gh` no teste confere o nome exato da branch (`headRefName ==`), como o script (checklist 12); resposta de outro PR é recusada pelo número.
- Commits em Conventional Commits, em português, com a etapa citada.

## Revalidação (E58.15, head b11db715)
Delta lido só pelo `forge-check parecer delta docs/reviews/v0479-ae1-onde.md`: intervalo bef021c1..b11db715; no domínio `bin/forge_onde.py`, `changelog.d/v0479-ae1-onde.md`, `tests/mutantes/v0478-ae1-onde-7.json` e `tests/test_forge_onde.py` (commit b11db715, E58.13, A1 e A2 da segurança).
- `onde` recusa o sha curto que o git resolve para tag ou branch de mesmo nome (`not sha.startswith(valor)`, só no tipo `commit`; `SHA` aceita só hex minúsculo, então não há recusa falsa por caixa) e sai `nao-verificavel` rc 2.
- `executar` pega o `TimeoutExpired` que o `git` do forge-check deixa subir e sai `nao-verificavel (git sem resposta)` rc 2, não o rc 1 de alvo inexistente.
- Teste novo com ambiente limpo e `-I`: `test_forge_onde.py`, 32 testes, OK. Mutantes M50 e M51 rodados numa cópia: os dois mortos pelo teste declarado. Changelog com a entrada em `### Corrigido`. Suíte: CI do PR (`R-REVIEW`).
- Sem achado novo no delta; A1 a A3 abaixo seguem recomendados (cartão depois do merge).

## Achados
- A1 (recomendado) bin/forge_onde.py:23 · a docstring diz que nada com `..` chega ao git, mas `VERSAO` aceita `..` no sufixo (`v1.2.3-..`) e o alvo chega ao `rev-parse`; sondado: `--verify` recusa o intervalo e sai `nao-existe` rc 1, sem efeito; tirar `.` repetido do sufixo ou corrigir o texto.
- A2 (recomendado) bin/forge_onde.py:107 · `--max-count=200` corta antes do filtro do ID inteiro: se os 200 commits mais novos com a substring (`AE1` em `AE10`, `AE1.1`) não citam o ID inteiro, sai `nao` falso; filtrar sem teto ou dizer `nao-verificavel` quando o teto encher.
- A3 (recomendado) bin/forge_onde.py:60 · `#0723` sai `nao-verificavel` rc 2 porque compara `"723"` com `"0723"`; normalizar o número (`str(int(...))`) antes de comparar.

## Parecer
Aprovado no head b11db715 (revalidação E58.15; antes, aprovado no bef021c1). O subcomando cumpre o AE1.1 e trata os riscos que o desenho listou, com teste do ramo de falha de cada guarda e mutantes declarados. Os três achados são recomendados (`R-REVIEW`): nenhum leva a `sim` falso; viram cartão depois do merge.
