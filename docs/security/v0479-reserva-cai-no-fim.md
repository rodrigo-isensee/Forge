---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-reserva-cai-no-fim
commit: 0998e8ab569bf2d5eff92324dc3811365d179ba6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-reserva-cai-no-fim (revalidação)

Etapa E60.7 do pedido v0478. Revalidação por delta: `forge-check parecer delta` de `50e06ac6..0998e8ab`. No domínio: `hooks/agentes.py` (2 linhas em `iniciar`) e `tests/test_agentes_interrompidos.py` (6 testes novos em `FimDoAgente`). Fora do domínio: `tests/mutantes/v0479-reserva-cai-no-fim.json`. A rodada anterior (head 50e06ac6) está no git.

## Gatilhos
Gatilhos: hook de controle (reserva de escrita por branch do R-TETO), estado de controle do Forge.

## Sondas
- S1 · `FimDoAgente`: B sem `tool_use_id` (melhoria/B), A com; início de A, início de B, fim de A · espera: `['melhoria/B']` presa · obtido: `['melhoria/B']` no head 0998e8ab (com o hook de 50e06ac6, `[]`)

## Detalhe
**A1 da rodada anterior (recomendado): corrigido.** `hooks/agentes.py:1295` agora filtra primeiro as reservas com `tool_use_id == uso` e só cai nas que não têm `tool_use_id` quando não há nenhuma do próprio disparo. A reserva de outro `tool_use_id` continua sem casar por tipo. A sonda S1 refaz a de A1 e o resultado mudou de `[]` (B vivo sem branch) para `['melhoria/B']`. O teste `test_reserva_do_proprio_disparo_vem_antes_da_antiga_sem_tool_use_id` guarda o caso: passa no head e falha com o hook de 50e06ac6 (`[] != ['melhoria/B']`).

**O que a mudança não abre.** Sem reserva própria nem antiga, a lista fica vazia e o início cria um registro sem branch, como antes. Isso é fechado no lado da integridade. Os testes novos de forma (`tool_use_id` do disparo e do meta fora da forma, `agent_id` fora da forma, fim sem `agent_id`) só confirmam o que a rodada anterior já tinha conferido no código. Na dúvida, o casamento volta à ordem de antes e nunca fica mais largo, e o fim sem `agent_id` não solta reserva nenhuma.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum. Testes rodados no head: `tests.test_agentes_interrompidos.FimDoAgente` (10), todos OK. A suíte inteira fica com o CI, que continua sendo o portão do merge. Faltaram no ambiente: `gitleaks` e `semgrep`, fora do PATH. O delta não toca credencial nem dependência.
