---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: c792b567222a828209c6435b71f571cc925c1dd0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E51.28, revalidação de CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)

Delta lido (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0479-conformidade-sessao-forge.md`, intervalo `b22efaae..c792b567`, sem o que veio da `develop`; no domínio, `docs/hooks-fixtures.md`, `docs/hooks.md`, `tests/apoio_volta_unica.py` e `tests/provas/v0479-corpus-custo.md`. O aviso sobre o merge 741e235 fora da `origin/develop` é o merge da própria branch remota (pareceres E51.24 e E51.25), sem código.

## Parecer
Aprovado. O merge da `develop` (0f1aec8a) teve conflito só em `docs/hooks.md`: a linha "Falha fechada" ficou com o texto da `develop` (a branch não a mudava desde a base comum, sha igual), e as três linhas da E51 (travas, "Ainda não coberto", `vigia`) ficaram com o texto já aprovado; contra a `develop`, `tests/apoio_volta_unica.py` e a prova são só o commit c792b567. O índice das fixtures (12e3b7bc) está em dia: `scripts/indice-fixtures.py --conferir` deu "em dia", rc 0.

Teto do corpus (c792b567): `interpretador` 5893967 para 5896135, exatamente os +2168 passos autorizados pelo dono em 20/11 às 19:55 só para o E51; o motivo está no código (`tests/apoio_volta_unica.py:193-194`) e na prova (`tests/provas/v0479-corpus-custo.md`, "Teto do E51"); falta escrevê-lo no PR #742, como a decisão pede, antes do merge. A soma com o E50 (+1084) fica para quem integrar o segundo, como a decisão manda.

Execução: `python3 -m unittest tests.test_hooks_volta_corpus` no head: 33 testes, OK (171,9 s; o teto é a medida exata). Tamanho (H1): 1 linha de código, nenhuma guarda mudada. Suíte completa: CI do PR #742 (em andamento no head; a "bateria (pareceres)" espera os pareceres deste head).
