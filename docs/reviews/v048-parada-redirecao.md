---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v048-parada-redirecao
commit: 101050172f9ce1e6717263a826cde736e4117917
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v048 (HOOK-PARADA-CONTA-REDIRECAO, E12.3)

1ª rodada, completa, no head 10105017 (E12.5). Base d056c2ca.

## Achados
- A1 (recomendado) hooks/vigia.py:68 · `cat .git/config >/dev/null 2>&1` depois do Write barrado segue acusado: o `2>&1` deixa o `>` em verbos. Forma comum do descarte; cartão para tirar também a duplicação de descritor (`N>&M`) antes de `_ESCRITA`.

## Parecer
Aprovado. O diff faz o que o E12.3 pede, nem mais nem menos: 5 linhas em `hooks/vigia.py` (dentro do teto H1), a regex `_DESCARTE` aplicada antes do `shlex.split` em `perfil_da_chamada`, de modo que a redireção para /dev/null deixa de ser alvo e verbo. Nome e comentário dizem o porquê e citam o cartão.

Conferido, pelo `eh_contorno` contra um Write barrado em `.git/config`:
- o falso some nas três formas pedidas: `cat .git/config 2>/dev/null`, `2> /dev/null` e `&>/dev/null` dão `False` (na base d056c2ca, `True`); também com `| head`, `&&true` e dentro de `( )`;
- a escrita real segue acusada: `cp a .git/config 2>/dev/null`, `tee .git/config >/dev/null` e `cat .git/config 2>/dev/null>.git/config` dão `True`;
- sem regressão: comparei com a base as formas coladas (`>/dev/null>.git/config`, `sh -c '...' 2>/dev/null`, `echo x >.git/config 2>/dev/null`); o resultado é o mesmo antes e depois. A última já não era acusada na base (o token `>.git/config` vira alvo inteiro): limitação anterior, fora deste diff.

Testes: `tests/test_vigia_descarte.py` cobre o ramo de descarte e o ramo de falha (escrita no alvo, `/dev/null` colado a outra grafia, redireção colada à palavra anterior), por comportamento, sem ler a fonte nem subprocesso; o fixture `descarte-dev-null-nao-conta.json` cobre o hook de ponta a ponta e está no índice de `docs/hooks-fixtures.md`. Guardas: uma linha de chamada e uma regex com três partes condicionais; os quatro mutantes declarados (M1 a M4) cobrem a chamada, o lookahead, o lookbehind e o `>>?`. Commit único em Conventional Commits, com fragmento em `changelog.d/`.

Ferramentas (cito, sem refazer):
- `python3 -m unittest tests.test_vigia_descarte tests.test_vigia`: 17 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v048-parada-redirecao.json`: M1 a M4 morreram.
- `bin/forge-mutante --cobertura --base d056c2ca...`: sem condição mudada sem mutante.
- ci: 101050172f9ce1e6717263a826cde736e4117917 verde

O A1 não bloqueia: o pedido nomeia as três formas, todas resolvidas, e o caso restante continua a gerar só o falso que já existia, sem afrouxar a recusa.
