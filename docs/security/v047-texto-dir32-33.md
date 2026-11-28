---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-texto-dir32-33
commit: 9fd5d7716a9881fca225ddb5ec27e100bfba5de3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047-texto-dir32-33 (revalidação por delta)

Gatilhos: tests/config.json (invariantes novas), texto do Jarvis e do tech-lead (diretrizes 32 e 33, H6); na volta, teto de teste afrouxado (MAX_PENDENTES).

## Achados

## Sondas

## Detalhe
- Delta lido: `forge-check parecer delta` em ac34647c..9fd5d771 dá "nenhum arquivo do domínio mudou"; fora do domínio, `tests/fixtures/diretrizes-do-dono.json` e `tests/test_jarvis_nucleo.py`. Li os dois por serem afrouxa-regra.
- `tests/fixtures/diretrizes-do-dono.json`: a diretriz 27 volta de `fabrica` a `pendente` com o cartão `RELEASE-EM-1H`; perde só os trechos que a davam por cumprida. Não toca permissão, hook, `R-MAIN`, `R-VERIFY` nem invariante de `tests/config.json`.
- `tests/test_jarvis_nucleo.py:29`: `MAX_PENDENTES` 7 → 8, com motivo no código e no commit f42808f7 (27 pendente, 30 e 31 posteriores à P4). O afrouxamento tem a liberação do dono para o plano v047 (DECISÃO DO DONO de 2026-11-16 05:13 em `docs/pedidos/v0474.md`, `R-CONFORMIDADE`, `R-DECISAO`). Sem caminho de ataque: é teto de contagem de diretrizes pendentes, não controle de acesso.
- Prova: `python3 -m unittest tests.test_jarvis_nucleo` verde no head 9fd5d771 (43 testes). A suíte inteira roda no CI do PR.
- Achados anteriores (rodada ac34647c): nenhum; estado mantido.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem ferramenta de varredura necessária (só texto e JSON); sem lacuna.
