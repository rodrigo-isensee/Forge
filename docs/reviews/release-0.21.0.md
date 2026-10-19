---
tipo: review
contrato: 1
pedido: release-0.21.0
branch: melhoria/release-0.21.0-fragmento
commit: b7cf5775be1168c85c17af586378070ead7d87bd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Review: release 0.22.0 (E6, subida de versão sobre a junção da 0.21.0)

Escopo: delta `36696f3..b7cf577`, 3 arquivos (`CHANGELOG.md` e os dois `plugin.json`). Revisor diferente do autor. Substitui o parecer anterior (e65a7a8). Decisão do dono (2026-10-19, "B"): a 0.21.0 fica como decidida e VV-2 e reconciliação viram a 0.22.0.

- `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.22.0, batendo com o CHANGELOG.
- A entrada `## [0.22.0] - 2026-10-19` está acima da `[0.21.0]` e traz as 4 linhas literais dos fragmentos `vv-2` e `reconcilia-homolog-main` (`grep -cxF`, 1 ocorrência cada), nas subseções de origem: `### Adicionado` (1), `### Alterado` (2) e `### Corrigido` (1).
- A entrada `[0.21.0]` é idêntica à da develop (c0d85ee), verificada por `cmp` do trecho até `[0.20.0]`.
- `bin/forge-changelog conferir --base origin/develop`: rc 0 (versão base 0.21.0, versão do PR 0.22.0; changelog fechado conferido na promoção). `conferir-release`: rc 0 ("ok: changelog.d/ sem fragmentos pendentes").
- `R-NEUTRO`, `R-CUSTO`: só texto de changelog e versão; nada que custe dinheiro; nenhuma regra afrouxada.

## Achados
