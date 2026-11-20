---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-reserva-cai-no-fim
commit: f61799dd400216033de34e16c09c2c17890e5818
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-reserva-cai-no-fim (revalidação)

Etapa E60.12 do pedido v0478. Revalidação por delta: para `0998e8ab..f61799dd`, `forge-check parecer delta` responde "nenhum arquivo do domínio mudou". Fora do domínio, a branch só mudou `tests/mutantes/v0479-reserva-cai-no-fim.json` (1f10f9c4, f61799dd). O resto do intervalo veio do merge f35cd528, cujo segundo pai é o Base-sha e1f12f9f da `develop`. `hooks/agentes.py` e `tests/test_agentes_interrompidos.py` não mudaram desde 0998e8ab, então a leitura da rodada anterior (está no git) continua valendo. O A1 de 50e06ac6 continua corrigido.

## Gatilhos
Gatilhos: hook de controle (reserva de escrita por branch do R-TETO), estado de controle do Forge.

## Detalhe
**Os mutantes cobrem as guardas da reserva.** A spec declara 16 mutantes, um para cada condição das guardas em `hooks/agentes.py`: a forma do `tool_use_id` do disparo e do meta, a forma do `agent_id`, o casamento por `tool_use_id` com volta ao `id`, a reserva própria antes da antiga, o fim sem `agent_id` e a remoção só dos agentes parados. Rodados no head f61799dd, os 16 morreram. `forge-mutante --cobertura --base e1f12f9f` não acha nenhuma condição mudada sem mutante: as linhas 1210, 1266, 1269, 1275 a 1277, 1294, 1295 e 1383 a 1386 estão cobertas. Com `--conferir`, cada trecho aparece no lugar. O M13 do H2 (`tests/mutantes/v047-h2-autor-fica-2.json`), ajustado em 50e06ac6 ao novo casamento, também morre no head.

O que isso traz para a segurança: quem afrouxar uma dessas guardas faz um teste nomeado falhar. Exemplos: voltar a casar a reserva de outro disparo, ou soltar uma reserva no fim sem `agent_id`. A spec é só dado lido pelo `forge-mutante`: não executa nada e não muda o hook.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Rodados no head: `forge-mutante` da spec (16 de 16 morreram), `--ids M13` da spec do H2 (morreu), `--cobertura` e `--conferir` contra o Base-sha. A suíte inteira fica com o CI, que continua sendo o portão do merge. Faltaram no ambiente `gitleaks` e `semgrep` (fora do PATH). O delta não toca credencial nem dependência.
