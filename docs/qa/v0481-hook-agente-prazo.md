---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-agente-prazo
commit: fda308676fa86cd79217b7c2fe725889375ace04
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 (E50.4, HOOK-AGENTE-PEDIDO-GRANDE, #950)

- ci: fda308676fa86cd79217b7c2fe725889375ace04 verde

Passada única no head `fda30867`, em clone próprio. O branch avançou depois para `e56c45f2` (só `docs/security/v0481-hook-agente-prazo.md`, parecer de segurança). O run de `fda30867` terminou sem cancelamento e está verde fora `bateria (pareceres)`, `bateria` e `catraca`, que esperam pareceres (PARECER-LE-O-CI). O run novo de `e56c45f2` estava pendente na leitura.

## Critério → teste → resultado
O pedido não tem especificação de UX; as obrigações são as do brief e do pedido (E50.1).

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| O aviso de brief vencido dá as mesmas respostas com o git em lote | `PedidoGrande.test_mesma_resposta_em_toda_forma_de_pergunta` | ponta não sha40, faixa `a..b`, quebra de linha, tag anotada | passou; vermelho na base (API ausente) |
| Processos não crescem com o pedido (358 → ≤20) | `PedidoGrande.test_o_aviso_e_o_mesmo_com_processos_que_nao_crescem_com_o_pedido` | máximo de processos | passou; vermelho na base (asserção) |
| O lote ignora `GIT_*` do ambiente | `PedidoGrande.test_o_lote_ignora_o_git_do_ambiente` | ambiente hostil | passou; vermelho na base (API ausente) |
| Hook decide no prazo de 8 s com o pedido grande e as recusas seguem | `PedidoGrande.test_disparo_com_o_pedido_grande_sai_no_prazo_e_as_recusas_seguem` | prazo (R-TETO), recusa preservada | passou; não prova na base (passa nela; o ganho de tempo é coberto pela contagem de processos) |
| Nenhuma checagem sai e o prazo não muda | diff de `hooks/agentes.py` lido contra a base: só `GitEmLote` e o `with` em `avisos_de_brief_vencido`; originais restauradas no `__exit__` | `n/a` | conferido |

Leitura do diff, sem achado: `e_ancestral` com `antigo` abreviado ou não sha40 cai na chamada original; `antigo` fora do `rev-list` só vira `True` pela chamada original quando é commit de fato, como o `--is-ancestor`.

## Execução (logs em `/root/.forge-contrib/qa-v0481-logs/`, pasta só minha)
- Módulo tocado, `bin/forge-testes tests/test_hooks_agentes_autor.py`: `Ran 17 tests in 33.598s ... OK`.
- Vermelho antes do verde, `bin/forge-testes --vermelho 319a968df760dd6f991d2308676321f6a2719b65 --modulos test_hooks_agentes_autor`, rc 0: `vermelho: base=319a968df760 head=fda308676fa8 módulos=test_hooks_agentes_autor (restrito por --modulos)`; `revertidos à base: changelog.d/v0481-hook-agente-prazo.md, hooks/agentes.py`; `contagem: não prova (passa na base)=14; prova (API ausente)=2; prova (asserção)=1`.
- Mutantes, uma chamada por spec (o `forge-mutante` recusa specs de pedidos diferentes numa só):
  - `bin/forge-mutante tests/mutantes/v0481-hook-agente-prazo.json --processos 2`, rc 0, `rev=fda308676fa8`: M1 a M8 `morreu` (`hooks/agentes.py` 1095, 1097, 1099, 1101, 1104, 1106, 1114, 1123).
  - `bin/forge-mutante tests/mutantes/v0481-hook-agente-prazo-2.json`, rc 0, `rev=fda308676fa8`: M1 `morreu` (`hooks/agentes.py:1107`).
- Cobertura, `bin/forge-mutante --cobertura --base 319a968df760dd6f991d2308676321f6a2719b65`: toda condição Python mudada (1095, 1097, 1099, 1101, 1104, 1106, 1107, 1114) tem mutante declarado; nenhuma `não coberta`.
- R-PROVA: 9 mutantes mortos e 17 testes verdes no head, o que confere com o relato do autor (9 mutantes, contagem 358 → ≤20). Não localizei os logs do autor para comparar linha a linha; a conferência vale pelo meu rerun no `fda30867`.
- Não medi os 0,8-0,9 s em hook real; o ganho está provado pela contagem de processos.

## Cenários e resultado real
Sem bug aberto. Sem E2E nem acessibilidade (hook de linha de comando, sem tela).
