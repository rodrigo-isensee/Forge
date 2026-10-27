---
tipo: review
contrato: 1
pedido: prop-tempo-cpu
branch: melhoria/prop-tempo-cpu
commit: f0a5194c1254591e29a9346741bb17618b2e4c61
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: prop-tempo-cpu

Pedido PROP-TEMPO-CPU (revisão no PROP-TEMPO-CPU-REV, E1.1). Rodada 3, revalidação por delta sobre o parecer `fb081571e4d2cb58887e6123ee9515305005546b` (head anterior `650dbf9`).

## Delta lido
`bin/forge-check delta --parecer docs/reviews/prop-tempo-cpu.md` (intervalo `650dbf9..f0a5194`): o único commit do autor é `c3214f1` (os outros, `fb08157`, `99dceb6`, `f0a5194`, são pareceres). Lido por inteiro: `changelog.d/prop-tempo-cpu.md:2`, `tests/test_hooks_volta_propriedades.py:142`, `tests/test_hooks_volta_lancador.py:140` e `:355`. Já lido (rodadas 1 e 2, sem mudança): o resto do diff `9620160...650dbf9`; nada além de texto mudou em `c3214f1` (4 linhas de docstring e 1 do fragmento).

## Achados

## Parecer
Aprovado. Os quatro achados da rodada 2 estão resolvidos:
- A1: o fragmento diz os limites novos (corpus 90 s por trabalhador, lançador 120 s, T 2 s), o afrouxamento por decisão do dono e o motivo.
- A2: o docstring do T diz "menos de 2 s de CPU", igual à asserção.
- A3 e A4: os docstrings do lançador dizem "120 s de CPU", igual às asserções (`:153` e `:372`).

Teto M14: 142 linhas de código e teste no PR inteiro (`git diff --numstat --no-renames 9620160...f0a5194`, `bin/` e `tests/*.py`), sem mudança; não toca `hooks/` nem `tests/catraca.py`. `R-NEUTRO` e `R-CUSTO` preservadas; PA-7 sem achados registrados. Segurança e QA têm pareceres próprios, em paralelo; não refeitos aqui. Recomendações da rodada 1 seguem como recomendação (`tests/apoio_volta_unica.py:423`, `:53`; `tests/test_hooks_volta_corpus.py:37`).
