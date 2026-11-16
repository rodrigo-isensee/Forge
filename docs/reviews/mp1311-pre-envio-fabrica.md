---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-554-revalidacao
commit: 7b3604a19b06273ea09e2692c8474b6d6cb4dc18
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: mp1311-pre-envio-fabrica

## Parecer
Aprovado, head 7b3604a1 (classe C, PR #554 já integrado na develop em 2ac30111), revalidação por delta 48bf85e8..7b3604a1. Delta lido (`forge-check parecer delta`, rc=0, na branch de pareceres no topo da develop c5c3a449): nenhum arquivo do domínio difere da develop. Do próprio item, o delta tem 6035e27c (só `tests/mutantes/mp1311-pre-envio-fabrica-2.json`) e o merge 7b3604a1, com a develop f4b0c2ae.

A3 resolvido: o M10 da spec 2 virou M13, e os ids M1 a M13 das duas specs agora são únicos. `bin/forge-mutante tests/mutantes/mp1311-pre-envio-fabrica.json tests/mutantes/mp1311-pre-envio-fabrica-2.json` em c5c3a449: 13 mortos, rc=0 (era rc=2 na S1 da rodada anterior).

Merge: o único conflito, em `tests/test_testes_tocados.py:67`, juntou as duas entradas (o +test_pre_envio_brief do item e o +test_hook_erro_libera da develop) e foi de 81 para 82; `Mapa.test_forge_check_roda_os_modulos_dele` passa. No resto, o merge (`git show --cc`) é a develop sem retoque.

CI do #554 no 7b3604a1: a suíte parte 3/3 falhou em `CaminhoFiltroEAviso.test_test_hooks_pelo_caminho_roda_quem_reaproveita_o_lote_dele`, porque faltava test_hook_erro_libera em `REAPROVEITAM_O_LOTE`. O defeito já vinha da develop f4b0c2ae, sem relação com o item, e a develop o corrigiu em 0137e932 (#558, E1.204). O `bin/forge-testes` da develop difere do 7b3604a1 só nessa linha. A `catraca` passou; a `bateria (pareceres)` falhou por este parecer, que estava reprovado.

A2 (recomendado, sem ação): segue a duplicação consciente de `TESTES_DE_TEXTO` em bin/forge-check e bin/forge-testes. Parecer de segurança em docs/security/mp1311-pre-envio-fabrica.md, não refeito.
