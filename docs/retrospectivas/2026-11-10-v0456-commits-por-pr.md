# v0456 E9.1: commits de parecer e de merge da base, por PR

Data: 2026-11-10. Só leitura (`gh`, repositórios remotos; nada escrito na pasta do projeto A).
Processo, não pessoa: o número serve para ver se E7.1 e E8.1 reduzem o commit que só carrega parecer ou merge da base.

## Método (igual nos dois repositórios)
- Commits por PR: `gh pr view <n> --repo rodrigo-isensee/<repo> --json commits --jq '.commits[]|.messageHeadline'`.
- Classe pelo título do commit (regex em script local, `python3 -I`), uma só por commit, na ordem:
  1. merge da base: título `Merge ...` ou `merge: ...`;
  2. parecer ou revalidação: `docs(review|seguranca|qa)` ou título com `parecer`/`revalida`, que não comece com `feat|fix|refactor|test`;
  3. correção de achado: `fix|test` que cita achado, `A<n>`, `M<n>` ou recomendado;
  4. código e teste: `feat|fix|refactor|test|perf`;
  5. outro: docs, release, chore.
- Limite do `gh`: o campo `commits` traz no máximo 100 por PR; PR com 100 é truncado e fica fora da conta.
- Marcas de `R-DECISAO`: `medido` (comando citado), `estimado` (com a base), `não medido`.

## Linha de base: projeto A (confere a base dada)
Janela: 38 PRs mesclados, de #249 a #286 (exclui as promoções #287 e #288, de 99 commits).
Lista: `gh pr list --repo rodrigo-isensee/<projeto A> --state merged --limit 40 --json number`.

| Item | Base dada | Esta medida | Marca |
|---|---|---|---|
| PRs | 38 | 38 | medido (`gh pr list`, #249 a #286) |
| Commits | 264 | 264 | medido (soma de `commits` por `gh pr view`) |
| Parecer ou revalidação | 128 (48%) | 123 (47%) | estimado (classe pelo título; diferença de 5) |
| Merge da develop | 61 (23%) | 59 (22%) | estimado (título; diferença de 2) |
| Código e teste | 58 (22%) | 54 (20%) | estimado (título; diferença de 4) |
| Corrige achado | 3 | 0 pelo título | não medido (o título dos 3 não cita achado; precisa do parecer) |
| Outro | 14 | 28 | estimado (sobra da regra; absorve os 3 de achado, os 4 de código e os 2 de parecer que a base dada contou a mais) |

Leitura: o total de 264 commits e os 38 PRs batem com a base dada; as classes batem dentro de 5 commits. A base dada vale.

## Linha de base: Forge
Janela: os 12 PRs de versão mesclados na `main` com menos de 100 commits: #469, #472 a #477, #480, #481, #483, #484 e #485 (versões 0.43.1 a 0.45.5). Ficam fora, por truncar em 100: #468, #470 e #471, e os de sincronização develop/homolog.
Lista: `gh pr list --repo rodrigo-isensee/Forge --state merged --limit 40 --json number,title,baseRefName,commits`.

| Item | Commits | % | Marca |
|---|---|---|---|
| Total | 296 | 100 | medido (`gh pr view`, soma de 12 PRs) |
| Parecer ou revalidação | 14 | 5 | estimado (título) |
| Merge da base | 36 | 12 | estimado (título) |
| Código e teste | 198 | 67 | estimado (título) |
| Corrige achado | 6 | 2 | estimado (título cita achado, A<n> ou M<n>) |
| Outro (docs, release, chore) | 42 | 14 | estimado (sobra) |

Por PR (parecer / merge / código+achado / outro, total): #469 3/0/37/20 (60); #472 0/0/32/5 (37); #473 0/0/19/6 (25); #474 0/1/6/5 (12); #475 0/1/31/2 (34); #476 0/0/28/6 (34); #477 0/0/4/1 (5); #480 0/1/17/4 (22); #481 0/1/1/1 (3); #483 0/5/17/2 (24); #484 9/4/7/4 (24); #485 4/5/5/2 (16).

Leitura (estimado): no Forge, parecer e merge da base pesam 17% dos commits, contra 69% no projeto A. O peso sobe nos dois últimos PRs: 13 de 24 (#484) e 9 de 16 (#485) são parecer ou merge da base. A janela é pequena (12 PRs, versões de natureza distinta); P50/P85 não se calculam abaixo de 20 PRs.
Não medido: os PRs de 100 commits (#468, #470, #471) e o commit que corrige achado sem citar achado no título.
Fonte: só o `gh`; o checkout `/workspaces/Forge` está atrás da origin, por isso não se usou o `git log` local.

## Depois (vazio; medir quando E7.1 e E8.1 estiverem na develop)
Condição: E7.1 (arquivo da base não desatualiza o parecer) e E8.1 (develop entra uma vez só, no fim) mescladas na develop. Medir os PRs de versão mesclados depois dessa data, com a mesma regra de classe do Método; comparar com os 12 da base (abaixo de 20 PRs, valores individuais).

Comando pronto (troque `<N>` pelos números dos PRs posteriores e `<repo>` por `Forge` ou o do projeto A):

```
for n in <N>; do gh pr view $n --repo rodrigo-isensee/<repo> --json commits --jq '.commits[]|.messageHeadline'; done > depois.txt
# classificar com a regra do Método, por título; somar por classe
```

| Item | Commits | % | Marca |
|---|---|---|---|
| Total | | | |
| Parecer ou revalidação | | | |
| Merge da base | | | |
| Código e teste | | | |
| Corrige achado | | | |

Meta a validar: parecer + merge da base abaixo da base (17% no Forge; 69% no projeto A), sem aumento dos escapes (`forge-check escape resumo`) nem das voltas.
