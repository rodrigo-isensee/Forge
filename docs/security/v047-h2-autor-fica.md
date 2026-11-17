---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 7848dd5cfd55d51a7d8bb1afcef4a7718a8a8d11
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474, H2-AUTOR-FICA-ATE-O-MERGE (E2.83, volta por delta)

Delta lido (`forge-check parecer delta`, `32c4832a..7848dd5c`): no domínio só `bin/forge-testes` (mapa de testes: `test_hooks_agentes_autor` entra em `FORGE_CHECK` e em `REAPROVEITAM_O_LOTE`, linhas 112 e 117). Fora do domínio: `tests/test_testes_tocados.py` (contagem 92 → 93) e este parecer. O mapa só escolhe quais módulos o envio e o CI rodam; acrescentar um módulo amplia a cobertura e não afrouxa guarda nem toca `hooks/agentes.py` (igual a `32c4832a`). Já lido (no git, `32c4832a` e antes): o resto do H2, o fixture do `iniciar`, o M25 e as sondas S1 a S12.

## Gatilhos
Gatilhos: guarda em hook de controle (`R-TETO`, uma delegação de escrita por branch), leitura de estado que um agente pode corromper (`.forge/run/agentes.json`).

## Achados
- A3 (recomendado) tests/test_hooks.py:838 · corrigido: rpartition e a cauda exigida em "/.forge/run/agentes.json"
- A4 (recomendado) hooks/agentes.py:987 · sem mudança: SubagentStart do retomado depois de RESERVA_S acha a reserva vencida (sonda S8 do parecer em f26b0721); segue recomendado
- A5 (recomendado) hooks/agentes.py:745 · sem mudança: a recusa por reserva de retomada anuncia a expiração por expiracao_horas, não RESERVA_S (sonda S11 do parecer em f26b0721)

## Detalhe
Sem achado novo: o delta é registro de módulo no mapa de testes, sem efeito em decisão de hook nem em leitura de estado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira: só no CI (PR 639), que o portão do merge exige verde; rodei `tests/test_testes_tocados.py` no head (162 testes, OK, 1 pulado). `gitleaks` ausente do PATH (lacuna; o delta não traz credencial nem configuração).
