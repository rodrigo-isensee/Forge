---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae3-1-controle
commit: 40244cc20339c7438a9a20ec66e8b92ccfc405d1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E108.15, revalidação do AE3.1 bin/forge_controle.py no head 40244cc2)

Revalidação por delta (H3, `R-REVIEW`): li só `forge-check parecer delta docs/reviews/v0480-ae3-1-controle.md`, intervalo ba201c86..40244cc2, sem o que veio da `develop`. No domínio: `bin/forge_controle.py` (1 linha, só a docstring) e `tests/test_forge_controle.py` (+24 linhas, 1 substituída).

- Módulo: a única linha mudada é a docstring, que troca o caminho `docs/propostas/v0479-melhorias-anti-erro.md` por "a proposta v0479 de melhorias anti-erro". Nenhuma guarda, chamada ao `git` nem constante mudou: a regra do módulo é a mesma do parecer aprovado em 59ad2edc. Sem guarda no delta, sem mutante a declarar; teto H1 não se aplica (1 linha).
- Testes: nenhuma asserção removida nem afrouxada. A única linha tirada é o `mock.patch.dict` do `setUp`, que passa a acrescentar o `PATH` com o embrulho à frente; `HOME` e `XDG_CONFIG_HOME` seguem isolados e as `GIT_*` herdadas seguem fora.
- O isolamento funciona porque o `_git` do módulo chama `git` pelo `PATH` (`bin/forge_controle.py:35`), e o embrulho liga `GIT_CONFIG_NOSYSTEM=1` depois que o módulo limpou as `GIT_*`. A config de sistema falsa com `filter.lfs` fica sempre apontada por `GIT_CONFIG_SYSTEM`, então a queda do isolamento deixa a suíte inteira vermelha, e o teste novo prova os dois ramos: sem `NOSYSTEM`, `nao-verificavel` sem commit; com ele, `salvo`.

## Parecer
Aprovado no head 40244cc2.

Provas lidas:
- `forge-check parecer delta`: no domínio só `bin/forge_controle.py` e `tests/test_forge_controle.py`.
- `python3 -m unittest tests.test_forge_controle`: `Ran 42 tests ... OK`; o teste novo sozinho: `Ran 1 test ... OK`.
- CI do PR #795 no head 40244cc2: as 5 partes da suíte verdes; `bateria (pareceres)` vermelha só por este parecer estar no commit ba201c86 (`R-REVIEW: ... commit: desatualizado`), o que este commit corrige.
