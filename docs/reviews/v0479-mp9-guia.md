---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-mp9-guia
commit: 048b5baa53dc327d642bece4b0b90310b19b28dd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E24.28, MP9 guia "vários projetos", revalidação no head 048b5baa)

Revalidação (H3, R-REVIEW) do parecer aprovado no head e266490b. Delta lido: `forge-check parecer delta docs/reviews/v0479-mp9-guia.md`, intervalo `e266490b..048b5baa`; no domínio só `tests/test_conferir_reversao.py`.

- O `setUp` do repositório falso passa a gravar `tests/test_guia_varios_projetos.py`, e o comentário do plano dirigido cita o módulo. Bate com o MAPA de `bin/forge-testes:251` (`README\.md` -> `test_forge`, `test_doutor`, `test_guia_varios_projetos`): sem o arquivo, o plano dirigido do falso citava um módulo ausente. O acoplamento declarado no comentário segue valendo.
- Sem guarda mudada; teto H1 não se aplica (só teste).

`docs/engineering/praticas.md` sem regra "decidida por: leitura" que alcance o delta. Suíte: só no CI do PR (R-REVIEW). Rodados (em `tests/`): `python3 -m unittest test_conferir_reversao test_guia_varios_projetos`, 17 testes, OK.

## Parecer
Aprovado no head 048b5baa.
