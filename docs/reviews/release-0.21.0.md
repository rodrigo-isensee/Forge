---
tipo: review
contrato: 1
pedido: release-0.21.0
branch: melhoria/release-0.21.0
commit: 06b6a9e0959474fb787a58cc60725cc65a837b60
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-19
---
# Review: release 0.21.0

Escopo: `7226ba7...06b6a9e` (1 commit, 7 arquivos). Revisor diferente do autor.

- Entrada `[0.21.0] - 2026-10-19` do `CHANGELOG.md`: as 5 linhas dos 4 fragmentos (`bp-1`, `conf-anexo-pareceres` com 2, `s-18`, `t-1`) estão presentes, literais (conferido com `grep -cxF`, 1 ocorrência cada), sob `### Adicionado` e `### Corrigido`. Sem perda.
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` passam de 0.20.0 para 0.21.0; batem entre si e com o CHANGELOG.
- SemVer: há funcionalidades novas compatíveis (`conferencia registrar`, `voltas`, `--entregas`) e correções, sem quebra para os projetos: minor correto.
- Os 4 fragmentos foram apagados (`changelog.d/` vazio); `## [Não publicado]` ficou vazio.
- Nada além dos 7 arquivos mudou.
- `R-NEUTRO`, `R-CUSTO`: sem texto novo fora do changelog, nada que custe dinheiro. Nenhuma regra afrouxada.

Pendências: nenhuma.
