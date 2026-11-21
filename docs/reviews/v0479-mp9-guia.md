---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: abb581a5b7e513cafa3cb5d391ccd4b516c19f73
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E24.11, MP9 guia "vários projetos", revalidação)

Revalidação (H3, R-REVIEW) do parecer aprovado no head a8d4dce4. Delta lido: `forge-check parecer delta docs/reviews/v0479-mp9-guia.md`, intervalo `a8d4dce4..abb581a5`; no domínio `templates/projeto/CLAUDE.md` e `tests/pesos-d4.json`.

- Merge `3efc67aa` da `develop`: limpo (`git show --cc` sem trecho de conflito). As 2 linhas de `templates/projeto/CLAUDE.md` ("Conferência de registros" e "Versões do intérprete") vêm iguais da `develop` (presentes em `3efc67aa^2`); o resto do diff de `tests/pesos-d4.json` também é da base. Patch do item intacto.
- `abb581a5`: 1 linha, `"test_guia_varios_projetos": 0.1` em `tests/pesos-d4.json`, o peso do módulo de teste do item. JSON válido, 197 chaves em ordem alfabética. Sem guarda mudada; teto H1 não se aplica.

`docs/engineering/praticas.md` sem regra "decidida por: leitura" que alcance o delta. Suíte: só no CI do PR (R-REVIEW); rodado o teste do delta: `python3 -m unittest test_pesos_teto test_guia_varios_projetos` (em `tests/`), 6 testes, OK.

## Parecer
Aprovado no head abb581a5. Nada novo.
