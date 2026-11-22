---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae3-1-controle
commit: ba201c86c80fd9d74ac7e8ca88fdd18550630fd7
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E108.11, revalidação do AE3.1 bin/forge_controle.py no head ba201c86)

Revalidação por delta (H3, `R-REVIEW`): li só `forge-check parecer delta docs/reviews/v0480-ae3-1-controle.md`, intervalo 59ad2edc..ba201c86, sem o que veio da `develop`. No domínio: `docs/indice-forge.md` (uma linha, commit ba201c86, E108.10) e `tests/pesos-d4.json` (a entrada `test_ambiente_recriacao`, que veio do merge da base 97ae707f e é a mesma do commit 7c4ee3c1 da `develop`; o commit do autor não o toca). Sem código no delta: teto H1 e mutantes não se aplicam.

A linha nova do índice descreve `bin/forge_controle.py` com o mesmo texto da primeira linha da docstring do módulo e entra na ordem alfabética (entre `forge_comparar.py` e `forge_corrigidos.py`).

## Parecer
Aprovado. O parecer anterior (head 59ad2edc, E108.7) segue valendo para o código e os testes, que não mudaram no delta.

Provas lidas:
- `forge-check parecer delta`: no domínio só `docs/indice-forge.md` e `tests/pesos-d4.json`, diff de 2 linhas.
- `git diff 7c4ee3c18 ba201c86 -- tests/pesos-d4.json`: só a entrada `test_forge_controle` da própria branch; a de `test_ambiente_recriacao` é da base.
- Suíte inteira: fica no CI do PR (não rerrodada aqui).
