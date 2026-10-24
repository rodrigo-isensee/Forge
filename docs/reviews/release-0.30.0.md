---
tipo: review
contrato: 1
pedido: release-0.30.0
branch: melhoria/release-0.30.0
commit: dcb80ad7df0ef6ff0e361fcc6faa8cb35895c873
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: release-0.30.0

## Achados

## Parecer
Aprovado. Diff lido: `3d73bdc...dcb80ad`, 11 arquivos, só da release (um commit, `chore(release): versão 0.30.0 (#298 a #308)`).
- CHANGELOG: `## [0.30.0] - 2026-10-24` traz os 8 itens com o texto exato de cada fragmento (conf-base-dono, est-030-l4, est-030-l5, fechar-master, hook-raiz-contrib, limpeza-regra, lote-atualizar, release-dev-versao), agrupados em Adicionado, Alterado e Corrigido; `[Não publicado]` ficou vazio.
- `changelog.d/`: os 8 fragmentos foram apagados; nenhum restou (`git ls-tree` do head).
- Versão: 0.29.0 para 0.30.0 em `.claude-plugin/plugin.json` e em `dev/.claude-plugin/plugin.json` (DECISÃO TÉCNICA do REL-0300), iguais entre si.
- Classificação: minor é a certa (melhorias compatíveis e correções, sem quebra para os projetos; ADR 0005 trata de migração, a regra de SemVer está no CLAUDE.md do Forge).
- Itens de `achados-recorrentes.md` (PA-7): lista sem achados; nada a conferir. Sem segurança, pipeline ou modelagem no diff.
