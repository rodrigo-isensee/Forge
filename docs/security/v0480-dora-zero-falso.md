---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-dora-zero-falso
commit: 38d9c349c671dd76f5a71f30f3734bac2d0d64d3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E160.4, dora sem zero falso, PR #844)

Base 789fc141, head 38d9c349. Delta: `bin/forge_dora.py`, `tests/test_forge_dora.py`, `tests/mutantes/v0457-dora.json` (sai o M7), `tests/mutantes/v0480-dora-zero-falso.json` (novo) e o fragmento do changelog.

## Gatilhos
Gatilhos: métrica do Forge (`forge-check dora`, só leitura), remoção de teste e de mutante que fixavam o comportamento antigo.

## Só aperta ou neutro
- Nenhum portão lê a saída do dora: fora do próprio módulo, `dora` só aparece no despacho do `forge-check` (`bin/forge-check:10873-10874`, chama `executar` e imprime) e na lista e no mapa de testes de `bin/forge-testes:160,195`; nenhuma ocorrência em `.github/`, `.githooks/`, `hooks/`, `scripts/`, `agents/`, `skills/` nem `templates/`. O `rc` segue 0 (`bin/forge_dora.py:182-185`). Mudar o formato de `vazao`, `taxa_de_falha` e `recuperacao_h` não abre nem fecha nenhuma trava.
- `linhas_do_quadro` (`bin/forge_dora.py:65-72`): aperta. Arquivo que `ler_texto` não lê (ausente, pasta, link simbólico, acima do teto de bytes; `bin/forge_governanca.py:94-101`, intocado) agora sai `nao-medido` com motivo, e não 0 escape ou 0 cartão. Antes, um `escapes.md` trocado por link simbólico ou apagado dava taxa de falha 0 em silêncio; agora o leitor vê que não houve medida.
- `vazao` e `falhas`/`calcular` (`:92-97`, `:109-116`, `:159-166`): aperta pelo mesmo motivo; o arquivo existente e vazio segue 0 (teste `test_quadro_vazio_existente_segue_zero`).
- `nao_medido` (`:30-31`): o motivo usa só `arq.name`, que é constante (`historico.md`, `escapes.md`), e a saída passa por `json.dumps`; sem entrada externa no texto, sem injeção de linha.
- Teste removido `test_quadro_ausente_vale_vazio_sem_recusado` e mutante M7 de `v0457-dora.json`: neutro. Fixavam o 0 falso que o pedido corrige; o substituto `test_quadro_ausente_ou_ilegivel_sai_nao_medido_e_nao_zero` cobre o ausente e o ilegível (pasta no lugar) e é mais estrito. A isenção em `v0480-dora-zero-falso.json` aponta o trecho apagado (`ler_texto(arq) or ""`), não esconde guarda viva.
- `Brutos` (`tests/test_forge_dora.py:173-174`): cria `escapes.md` vazio para manter a conta de `taxa_pct`; neutro.

## Achados

## Sondas

## Detalhe dos achados
Sem achado. Verificação no head 38d9c349: `python3 -m unittest tests.test_forge_dora`, 17 testes, OK; `bin/forge-mutante tests/mutantes/v0480-dora-zero-falso.json`, M1 a M4 morreram. Suíte inteira só no CI: run 45331048764 no head 38d9c349, em andamento quando este parecer foi escrito (instalação, catraca, passos e verificações longas verdes; `bateria (pareceres)` vermelha à espera dos pareceres); o merge depende do CI verde.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: leitura do diff, grep dos consumidores, testes do arquivo tocado e o executor de mutantes; nenhuma varredura externa necessária para o delta.
