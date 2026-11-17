---
tipo: revisao-seguranca
contrato: 1
pedido: v047-texto-dir32-33
branch: melhoria/v047-texto-dir32-33
commit: ac34647c888de410dc1a97bd65f878cd0ed6725c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047-texto-dir32-33

Gatilhos: tests/config.json (invariantes novas), texto do Jarvis e do tech-lead (diretrizes 32 e 33, H6).

## Achados

## Sondas

## Detalhe
- Invariantes: o diff de `tests/config.json` (4cc2153e..ac34647c) não tem nenhuma linha removida; só acréscimos em `invariantes`, `invariantes_motivo` e `invariantes_motivo_trecho`, cada um com regra e motivo (R-FLUXO, R-TETO). Nada saiu nem afrouxou. JSON de config e fixture válidos.
- Permissões: `agents/jarvis.md:37` e `agents/tech-lead.md:38` só acrescentam restrições (teto de 20 agentes e 12 branches, lote de até 3, "nunca sem os testes verdes nem pela exceção do GitHub", silêncio noturno). Nenhuma ferramenta, escopo, `R-MAIN`, `R-VERIFY` ou `R-DECISAO` mudou; a main segue do dono. O modelo de projeto (`templates/projeto/CLAUDE.md`) e o `ritmo-e-corte.md` são só texto de processo.
- Fixture `diretrizes-do-dono.json`: 26 e 27 passam de pendente a fábrica com trechos que existem em `docs/fechamento-integrador.md`; 30 e 31 entram como pendentes; 32 e 33 apontam trechos presentes no Jarvis.
- Prova: `python3 -m unittest tests.test_jarvis_nucleo` verde (43 testes). A suíte inteira roda no CI do PR (ainda sem PR, sem sonda de CI a citar).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem ferramenta de varredura necessária (só texto e JSON); sem lacuna.
