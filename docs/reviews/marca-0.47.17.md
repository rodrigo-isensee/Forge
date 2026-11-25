---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/marca-0.47.17
commit: 8d9f51d3d8c3ae37afc68618fdd5521e069ee6bf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E12.3, marca da 0.47.17; PR #882, classe C)

Escopo: `7e8c9c19..8d9f51d3` (Base-sha do brief até o Revisar-sha), 23 arquivos, um commit (`chore(release): marca da 0.47.17 na develop`). Primeira revisão da branch, sem parecer anterior.

Verificado nesta revisão:
- Nada de código mudou: o diff toca só `.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md` e 20 apagamentos em `changelog.d/`; depois deles a pasta fica só com o `README.md`.
- Versão: `0.47.17` em `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3`, as duas antes em `0.47.16`. O `.claude-plugin/marketplace.json` não tem campo `version` (nem na base), então nada a subir ali.
- Fragmentos: um script lê cada um dos 20 fragmentos apagados no Base-sha e procura cada linha de item, literal, sob o mesmo cabeçalho (`### Adicionado`, `### Alterado`, `### Corrigido`) da seção `## [0.47.17] - 2026-11-25`. Resultado: 20 fragmentos, 21 linhas de item (o `v0480-graphql-ilegivel.md` traz duas), 21 itens na seção, 0 faltas. A seção não tem item além dos fragmentos, e nenhuma linha antiga do `CHANGELOG.md` foi removida (diff só com `+`).
- Data: o commit da marca é de 2026-11-24 23:31:46 -0300, ou seja, 2026-11-25 02:31 UTC. A data `2026-11-25` (UTC) do cabeçalho está certa.
- Ferramenta: CI do PR #882 no head `8d9f51d3`, com 20 checks `pass` e 7 `skipping` (os de push na develop e a cobertura informativa), nenhum vermelho; inclui suíte 3.12 e 3.14 (5/5), instalação e teto de pulados. A suíte não foi rodada de novo aqui (`R-REVIEW`).
- Guardas: o diff não muda guarda nenhuma, então não há mutante a declarar.

## Achados
- A1 (recomendado) CHANGELOG.md:7 · A develop andou depois do Base-sha: o #880 (6959cec2) trouxe changelog.d/v0481-fechar-ci-topo.md. Mesclada a marca, a 0.47.17 leva o código do #880 sem o item dele, que fica para a 0.47.18. Antes do merge, refaça o corte sobre a develop atual ou registre o desvio.

## Parecer
Aprovado. A marca faz o que o brief pede: os 20 fragmentos estão na seção 0.47.17 com o texto literal e sob o cabeçalho certo, foram apagados, a versão bate nos dois manifestos que têm versão, nenhum código muda, a data UTC confere e o CI do head está verde. A1 é recomendado: o defeito não está no diff revisado, e sim na develop, que andou depois do corte. A escolha (refazer a marca ou aceitar que o #880 entre na 0.47.18) é de quem fecha a release.
