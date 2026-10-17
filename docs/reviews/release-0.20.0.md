---
tipo: review
contrato: 1
pedido: release-0.20.0
branch: melhoria/release-0.20.0
commit: b52c9451432eaa29f6d76590bb9d4b722a5d3464
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-17
---
# Review: release 0.20.0

Escopo: `ecf553d...b52c945` (base ecf553d3c7651a4c97d314956893800ee156293b), 1 commit, 6 arquivos. O revisor não é o autor.

Veredito: **APROVADO**, sem achados que bloqueiem.

## Conferido (leitura do diff)
- `.claude-plugin/plugin.json`: 0.19.0 -> 0.20.0, só a linha da versão. Minor coerente com "melhoria compatível" do CLAUDE.md.
- `dev/.claude-plugin/plugin.json`: 0.19.0 -> 0.20.0. Fora do escopo original, mas a decisão técnica está registrada no pedido (R-DECISAO): `test_versao_igual_a_do_forge` exige as duas versões iguais. Aceito.
- `CHANGELOG.md`: seção `## [0.20.0] - 2026-10-17` com 3 entradas, texto idêntico aos 3 fragmentos (aq, conf-tabela-rotulo, s-15-main-merge-commit), agrupados em Adicionado/Alterado; `## [Não publicado]` mantido vazio acima.
- `changelog.d/`: os 3 fragmentos apagados; nada mais removido.
- Nenhum outro arquivo mudou; sem código, sem afrouxar regra, sem custo (R-CUSTO), sem termo de projeto (R-NEUTRO). Commit único, Conventional Commits. Segurança: sem gatilho (só versão e texto).

## Ferramentas
Suíte e `scripts/validar-plugin.sh` ficam com o QA e o CI; não os refiz.

## Recomendado (não bloqueia)
Nenhum.
