---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: 862d9ecb792c30e0b66e82d30f3794a19828cc65
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E24.18, MP9 guia "vários projetos", revalidação)

Revalidação (H3, R-REVIEW) do parecer aprovado no head abb581a5. Delta lido: `forge-check parecer delta docs/reviews/v0479-mp9-guia.md`, intervalo `abb581a5..862d9ecb`; no domínio `bin/forge-testes` e `tests/test_guia_varios_projetos.py`.

- `bin/forge-testes`: `test_guia_varios_projetos` entra em `LEITORES_DE_TEXTO` (logo em `CONTEUDO` e `PUBLICADO`, que cobrem `templates/projeto/CLAUDE.md`) e na regra de `README.md`. Conferido: `bin/forge-testes --listar` com `README.md`, `templates/projeto/CLAUDE.md` e `hooks/agentes.py` lista o módulo nos três.
- `tests/test_guia_varios_projetos.py`: `import agentes` estático, para o fecho de importadores do mapa ligar `hooks/agentes.py` ao teste; o módulo carregado por `spec` logo depois continua sendo o que o teste usa. Sem guarda mudada; teto H1 não se aplica.

`docs/engineering/praticas.md` sem regra "decidida por: leitura" que alcance o delta. Suíte: só no CI do PR (R-REVIEW). Rodados: `python3 -m unittest test_guia_varios_projetos test_testes_tocados` (em `tests/`), 200 testes, OK (1 pulado pelo sandbox de pid); `bin/forge-testes --registros --base origin/develop`, rc=0 (9 conferências).

## Parecer
Aprovado no head 862d9ecb.
