---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 39351c755290a37abf829fedb17fe65744183491
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E50.28 (ENTREGA-PARECER-MESCLADO, índice das fixtures e teto do corpus)

Revalidação pelo delta (`forge-check parecer delta`, intervalo `9f4c3ca3..39351c75`; H3, `R-REVIEW`). No domínio: `docs/hooks-fixtures.md`, `tests/apoio_volta_unica.py` e `tests/provas/v0479-corpus-custo.md`. Os pareceres de QA e segurança do delta ficam fora do domínio.

## Parecer
Aprovado no head 39351c75.

- `docs/hooks-fixtures.md`: regerado pelo script; `python3 -I scripts/indice-fixtures.py --conferir` → `docs/hooks-fixtures.md: em dia`, rc=0. A contagem bate com a árvore: 3135 fixtures, 2309 em `conformidade` (o grupo novo `pp-*`, 38 casos, é o corpus do PARECER-PELO-PAPEL).
- `tests/apoio_volta_unica.py`: só o `interpretador` de `MEDIDA_DO_CORPUS` muda, de 5893967 para 5895051 (+1084, os mesmos passos que o CI do #734 reprovou); ruído segue 0, subprocessos e execuções iguais. O comentário traz a autorização do dono de 20/11 19:09 ("+1.084 passos, só para este item") e diz que não é precedente. Nenhuma guarda mudou, então não há mutante a declarar.
- `tests/provas/v0479-corpus-custo.md`: registra a medida e a autorização no formato das medidas anteriores.

Rodei o teste do item: `python3 -m unittest tests.test_hooks_volta_corpus` → `Ran 33 tests · OK`, rc=0. A suíte inteira fica com o CI do PR #734; no head 39351c75 a `bateria (pareceres)` estava vermelha porque os pareceres ainda apontavam para o head anterior. Falta ainda o motivo do teto escrito no PR, que a decisão do dono pede; isso fica com quem integra.
