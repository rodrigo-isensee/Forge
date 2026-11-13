---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-pre-envio-modelo
commit: 27c401073885775dff35b8c15d29f2595f3c2d85
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: melhorias-de-projeto-1311 (pré-envio no modelo de projeto, E1.33)

## Achados
- A1 (recomendado) bin/forge-upgrade:1 · o diff passa de 150 linhas de código e teste (cerca de 420, pelo numstat contra a base); o corpo do PR deve trazer `teto: excedido, <n> linhas, <motivo>` (M14).
- A2 (recomendado) templates/projeto/.githooks/pre-push.local:10 · com `set -u`, `"${arquivos[@]}"` vazio falha em bash anterior a 4.4 (stack sem `Detecção`); só afeta bash antigo, o teste do caso passa em bash 5.

## Sondas

## Parecer
Aprovado. Lido no head 27c40107: forge-init (extração do pronto rápido e da detecção, pulo do `pre-push.local` sem pronto rápido), migração `migrar-pre-envio` (idempotente, não sobrescreve, stack validada por regex antes de formar o caminho, exclude por prefixo), `forge-upgrade` com vários passos por versão (ordem por versão e nome), modelo de PR e `pre-push.local`. Sem defeito provado nem requisito faltando. Os itens do Entregar do E1.16 têm commit. Guardas com mutantes declarados (três arquivos, `<pedido>-2` e `-3`); todos morreram na execução. Testes `PreEnvioDoModelo`: 14 passam. Sem PR aberto, então sem CI para citar; suíte completa fica para o CI do PR.
