---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: 96c0215fff321bb1192c84fc712987b59496e8bc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E51.31, revalidação de CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)

Delta lido (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0479-conformidade-sessao-forge.md`, intervalo `c792b567..96c0215f`; no domínio, `docs/hooks-fixtures.md`, `docs/hooks.md`, `hooks/conformidade.py`, `tests/apoio_volta_unica.py`, `tests/provas/v0479-corpus-custo.md` e `tests/test_hooks.py`. O aviso sobre o merge 835f39d fora da `origin/develop` é o merge do parecer de QA E51.29 (só `docs/qa/`); os trechos de `hooks/conformidade.py`, `docs/hooks.md` e `tests/test_hooks.py` são o E50 já na `develop` (f96ede50, #734, com pareceres próprios), sem mudança do merge.

## Parecer
Aprovado. O merge 96c0215f (develop f96ede50 na branch) mudou, além das duas pontas, só três arquivos (`git show --remerge-diff`): `docs/hooks-fixtures.md` (conflito, regerado: 3196 fixtures; `scripts/indice-fixtures.py --conferir` deu "em dia", rc 0; `ls tests/hooks/*/*.json` conta 3196), `tests/apoio_volta_unica.py` (conflito: a medida vai a 5897219 e o comentário traz as duas autorizações) e a prova, seção "Soma do E50 e do E51".

Teto da soma: 5893967 + 1084 (E50, autorização de 20/11 às 19:09) + 2168 (E51, 20/11 às 19:55) = 5897219, sem passo a mais da junção; +3252 fica abaixo de +3300, o limite do aviso da decisão de 19:55, e as duas autorizações estão no código (`tests/apoio_volta_unica.py:192-198`), na prova e no corpo do PR #742.

Execução: `python3 -m unittest tests.test_hooks_volta_corpus` no head 96c0215f: 33 testes, OK (149,9 s; o teto é a medida exata). Nenhuma guarda mudada pelo merge. Suíte completa: CI do PR #742 (em andamento no head); a Catraca deste head reprovou só pelo rótulo `afrouxa-regra`, que vale aplicado depois do último push (ADR 0008).
