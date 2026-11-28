---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0476-nucleo-teto
commit: 8a91fe3b46138da9de651979c17a28fa68672a2d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0474 (E3.302, núcleo do Jarvis no teto)

Diff lido inteiro (`038249c5..8a91fe3b`, base da develop): `agents/jarvis.md:37` (sai o parêntese "(revisão, conserto, teste vermelho)") e o fragmento `changelog.d/v0476-nucleo-teto.md`.

Gatilhos: texto de regra protegida do agente orquestrador (R-TETO, invariantes)

## Achados

## Sondas

## Detalhe dos achados
**A regra não afrouxa.** `agents/jarvis.md:37` mantém o trecho protegido `agente livre termina o que está aberto` (`tests/config.json:197`), o teto `Teto do time (H6): até 20 agentes e 12 branches abertas` e a ordem de ler `skills/trabalho-em-paralelo/ritmo-e-corte.md` antes de abrir item novo. O detalhe removido segue, mais completo, em `skills/trabalho-em-paralelo/ritmo-e-corte.md:26` (revisão, conserto, teste vermelho, CI vermelho), protegido por `tests/config.json:608`. Nenhum trecho de `invariantes` sumiu, `tests/config.json` e `docs/regras/` não mudaram; nada de hook, workflow, script ou segredo no diff. Sem caminho de ataque: a obrigação continua a mesma e a fonte do detalhe é lida por instrução explícita.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte: sem CI para este head (lacuna; o CI do PR confere a bateria). Rodei no head 8a91fe3b: `python3 -I tests/catraca.py --base origin/develop` (rc 0), `tests.test_metricas_texto` (2 testes, OK) e `tests.test_forge.RegrasInviolaveis` (OK). Ferramentas ausentes no PATH não se aplicam: o diff é só texto, sem workflow nem segredo.
