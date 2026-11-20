---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s1-atalho
commit: 3e53ae726c2891e00dbcdcc66cb0ebc54318cba8
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478, BP3 S1 atalho durável (E39.11)

Diff revisado: `004ce869..3e53ae72` (`scripts/jarvis`, `scripts/jarvis-forge`, README, fragmento, `tests/test_atalho_duravel.py`, 4 arquivos de mutantes).

## Achados
- A1 (bloqueante) scripts/jarvis-forge:230 · H1: `forge-check pr --previo` mede 236 linhas (teto 150) e o item é cortável: `resolver_claude`, `registrar_queda` e `supervisionar` estão copiados nos dois atalhos; um arquivo comum em `scripts/` lido por `source` cai para cerca de 130. Ou corte o resolver em item próprio.
- A2 (recomendado) scripts/jarvis:124 · `FORGE_QUEDA_JANELA=0` (ou `FORGE_QUEDA_ESPERA=0`) aceito como válido: com janela 0 nenhuma reabertura fica na conta e o teto de 3 da D1 nunca chega (reabre sem fim). Exija janela de pelo menos 1 e espera de pelo menos 1, com teste do ramo.

## Sondas

## Parecer
Reprovado só pelo A1 (`R-REVIEW`, requisito H1 com a medida da ferramenta). A lógica está correta na leitura: reabre só em 128 ou mais fora 129 e 130, teto de 3 na janela com a 4.ª queda desistindo, `--continue` único, modo `auto` mantido, `quedas.log` sem texto do `claude`; o resolver compara só caminhos absolutos executáveis, deduplica pelo caminho real, o empate fica com o instalador e o `PATH` que não responde `--version` mantém o comportamento antigo (D1 e D4 do dono atendidas). Testes: `bin/forge-testes tests/test_atalho_duravel.py` com 68 testes, OK em 13,7 s; mutantes declarados em 4 arquivos. `shellcheck` fica com o CI do PR (não instalado aqui). Na volta, a mutação e os testes do item rodam de novo com a base no head aprovado; o A2 vira cartão se não entrar junto.
