---
tipo: review
contrato: 1
pedido: release-0.21.0
branch: melhoria/release-0.21.0-fragmento
commit: e65a7a88a80e1a16d41d18641178859be8a48e78
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Review: release 0.21.0 (junção dos fragmentos reconcilia-homolog-main e vv-2)

Escopo: `origin/develop...e65a7a8`, 3 arquivos (`CHANGELOG.md` e os dois fragmentos apagados). Revisor diferente do autor. Substitui o parecer anterior (06b6a9e), que cobria a primeira junção.

- As 4 linhas dos dois fragmentos estão literais na entrada `[0.21.0] - 2026-10-19` (`grep -cxF`, 1 ocorrência cada), nas subseções do próprio fragmento: `### Adicionado` (vv-2, 1 linha), `### Alterado` (vv-2, 2 linhas, subseção nova, aceita pela decisão técnica do Jarvis; fica antes de `### Corrigido`, como no Keep a Changelog) e `### Corrigido` (reconcilia-homolog-main, 1 linha).
- Versão 0.21.0 e data 2026-10-19 inalteradas; `plugin.json` e `dev/.claude-plugin/plugin.json` batem com o CHANGELOG.
- Só `CHANGELOG.md` e os dois fragmentos mudaram em relação à develop; `changelog.d/` sem fragmentos pendentes.
- `bin/forge-changelog conferir-release`: rc 0 ("ok: changelog.d/ sem fragmentos pendentes").
- `R-NEUTRO`, `R-CUSTO`: sem texto novo além de changelog, nada que custe dinheiro; nenhuma regra afrouxada.

## Achados

