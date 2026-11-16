---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-tempo-a15
commit: 9050109479c1f4850cb5b92256b958f8d0eb08b5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (A15, `forge-check voltas --tempo`)

Etapa E2.359, instância que não fez a entrega. Diff revisado: `1b88640e..90501094` (bin/forge-check, bin/forge_voltas.py, tests/test_voltas.py, tests/mutantes/v047-tempo-a15.json, tests/mutantes/v047-tempo-a15-2.json, changelog.d/v047-tempo-a15.md).

## Gatilhos
Nenhum gatilho da `R-SEGURANCA` no diff: sem autenticação, dado pessoal, segredo, dependência, endpoint, banco, CI, IaC nem controle do Forge (`hooks/`, `docs/regras/`, `tests/catraca.py`, `tests/config.json` intocados). A mudança é um relatório só de leitura; o parecer é o portão da classe.

## Achados

## Sondas

## Detalhe dos achados
Verificado sem achado:
- Só leitura: `linha_do_tempo` (bin/forge_voltas.py:137) reaproveita os movimentos já lidos por `cmd_voltas` de `docs/kanban/historico.md` e as rodadas de `rodadas_de_brief`; não abre arquivo novo, não grava, não chama processo nem rede.
- Saída: a linha `tempo:` imprime só o nome do pedido (já impresso pelas linhas existentes) e números ou `nao-medido`; o texto livre do motivo não sai na saída, sem novo canal de injeção no terminal ou no agente que lê.
- Robustez: divisão por zero guardada (`not tempo["autor"]`, bin/forge_voltas.py:132); movimentos ordenados por hora com fuso (`_hora`, bin/forge-check:5088), sem trecho negativo; custo linear no tamanho do histórico.
- A opção `--tempo` é booleana (`store_true`, bin/forge-check:9487), sem valor do usuário; sem ela a saída é a de antes (teste `test_sem_tempo_nao_ha_linha_de_tempo`).
- PA-7: AR-4 e AR-5 conferidos, os testes novos rodam o `forge-check` com `-I` e ambiente limpo (tests/test_voltas.py:366); AR-1 a cargo do QA; demais itens não se aplicam (sem hook, curinga, `gh api` nem lista de ambiente).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff; teste do item rodado no clone: `python3 -m unittest tests.test_voltas` (46 testes, OK, 1 pulado preexistente). Suíte inteira: só no CI, que ainda não rodou para esta branch (sem PR); o portão de merge a exige. Faltaram no ambiente: gitleaks e Semgrep (sem segredo nem dependência no diff).
