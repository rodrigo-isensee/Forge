---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: a8d4dce419e55c32c4d3fcf37e02b13db7ea8a18
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E24.6, MP9 guia "vários projetos", revalidação)

Revalidação (H3, R-REVIEW) do parecer aprovado no head 2054ef3b. Delta lido: `forge-check parecer delta docs/reviews/v0479-mp9-guia.md`, intervalo `2054ef3b..a8d4dce4`; no domínio só `tests/test_reval_delta.py`, 1 linha: apaga a cópia colada do comentário "v047 E2.222" na entrada `test_guia_varios_projetos.py` de `CITACOES_CONHECIDAS`. Resolve o A1 do parecer anterior; a chave e o motivo `teste-le` ficam iguais. O resto do intervalo são os pareceres de QA, segurança e review (fora do domínio) e o merge `f36f349d` da própria branch remota, que só trouxe pareceres.

Item inteiro (`0c47762a..a8d4dce4`): README (8 linhas), `templates/projeto/CLAUDE.md` (1 linha), fragmento `changelog.d/v0479-mp9-guia.md`, `tests/test_guia_varios_projetos.py` e a citação em `tests/test_reval_delta.py`. Só documentação e teste: sem guarda mudada, teto H1 não se aplica. O conteúdo do guia não mudou desde o parecer anterior, que conferiu cada afirmação contra o código.

`docs/engineering/praticas.md` sem regra "decidida por: leitura" que alcance o diff. Suíte: só no CI do PR (R-REVIEW); rodado o teste do diff: `python3 -m unittest test_guia_varios_projetos test_reval_delta` (em `tests/`), 14 testes, OK.

## Parecer
Aprovado no head a8d4dce4. O A1 recomendado da rodada anterior foi corrigido; nada novo.
