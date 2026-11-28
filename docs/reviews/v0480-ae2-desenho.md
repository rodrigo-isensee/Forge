---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ae2-desenho
commit: 1d9424e205571ff82b6233bb6251432b804e1373
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E121.6, revalidação do desenho do AE2, o quadro anda com o PR)

Revalidação da volta (H3, `R-REVIEW`) no head 1d9424e2 sobre o parecer reprovado de 82e577a0 (head 0cf8b8ae). Desenho só de texto: sem suíte, sem mutante.

Delta lido: `forge-check parecer delta docs/reviews/v0480-ae2-desenho.md`, intervalo 0cf8b8ae..1d9424e2, no domínio só `docs/propostas/ae2-quadro-anda-com-pr.md` (+69/-23). Nada fora do domínio foi relido. As referências novas foram conferidas no head: `bin/forge-fechar:1349`, `:1354`, `:1357`, `:1432`, `:1438`, `:1622`; `hooks/quadro.py:24`; `bin/forge-check:5065`; DECISÃO DO DONO 20/11 13:51, 20/11 21:34, 21/11 20:54 e ORDEM DO DONO 20/11 08:44 no pedido.

## Conferência dos achados de 82e577a0
- A1 resolvido: a regra do P3 só entra na lista que o hook barra com `docs/kanban/arquivo/KANBAN-antes-do-ae2.md` presente; sem ele, só `aviso:` no comando de linha. `--migrar` no P3, texto aos projetos no P5, modelo já migrado no P4, oráculo `nao-migrado` na seção 7 e reversão pela primeira edição barrada.
- A2 resolvido: `PR #N` no motivo do `--limpar` (da mesma `lista` de `:1349`) e nos dois caminhos do `ja_mesclado`; sem PR próprio o motivo diz que não conta. Oráculo `merge-sem-pr`.
- A3 resolvido: a recusa de título saiu (vai à lista do dono); a linha do `--cartao` tira a trava manual da ORDEM DO DONO 20/11 08:44, que tem o prazo "até o AE2 entrar".
- A4 resolvido: linha "decidido pelo time na ausência do dono" com o "reabre quando" no topo e a volta ao trailer na seção 8.
- A5 resolvido: o aviso "quadro editado fora do movimento" fica.
- A6 resolvido: a linha `quadro:` sai só na `main` do `forge-check`, fora da lista do `cmd_kanban`.
- A7 resolvido: P4 depende do P3.
- A8 resolvido: a recusa de título saiu do P2; P4 traz `tests/mutantes/<spec do P4>.json` com teste do ramo de falha.
- A9 resolvido: o texto do `--limpar --cartao` vai no P1.
- A10 resolvido: X é a seção do cartão no `KANBAN.md`, não o `coluna_do_cartao`.
- A11 resolvido: a lacuna em projeto está no risco e é a condição do "reabre quando".

## Parecer
Aprovado. Os quatro bloqueantes e os sete recomendados estão resolvidos no texto. O delta não traz merge automático nem trava sem par na regra 3 de 21/11. O P1 e o P3 continuam abaixo de 150 linhas (~110 cada).
