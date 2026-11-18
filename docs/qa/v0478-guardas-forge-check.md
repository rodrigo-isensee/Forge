---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-forge-check
commit: 63326514fc2bd1ba092acc22455176f04c0c6963
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 (guardas do forge-check, E2.5)

Cartões FC-PR-PARECER-FORJADO e FILTROS-L08-G2-ORIGIN-LOCAL; o CONFIG-TETO-SEM-GUARDA ficou fora. Head `63326514`, base `4182a6b9`. Sem suíte local (o CI do PR roda a bateria); só os testes dos arquivos tocados.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Mais de um parecer do mesmo tipo/pedido/branch com veredito, revisor ou commit divergentes recusa e nomeia os arquivos (FC-PR-PARECER-FORJADO) | test_fc_pr_parecer_forjado (aprovado forjado, revisor, commit) | dois arquivos na pasta | passou |
| Dois iguais, outra branch ou um só não recusam | test_fc_pr_parecer_forjado (iguais/outra branch, sem branch, um só) | falso positivo | passou |
| Tipo não exigido forjado não esconde o reprovado (P5) | test_tipo_nao_exigido_forjado_nao_esconde_o_reprovado | caminho `nao_exigidos_que_nao_aprovam` | passou |
| Filtros L08, G2 e E2 só tiram do escopo a base ancorada; origin/develop reescrita segue no escopo (FILTROS-L08-G2-ORIGIN-LOCAL) | test_filtros_l08_g2_ancora (L08, G2, E2, caso ancorado) | ref local reescrita | passou |
| Sem regressão nos testes que o diff tocou | test_conferida_por_branch, test_selo_e_entrega, test_testes_tocados | n/a | passou |

## Cenários e resultado real
- Testes tocados (python3 -I, TMPDIR): test_fc_pr_parecer_forjado 7 OK; test_filtros_l08_g2_ancora 4 OK; test_conferida_por_branch, test_selo_e_entrega, test_testes_tocados OK.
- Vermelho antes do verde: `forge-testes --vermelho 4182a6b9` não tem mapa para `bin/forge-testes` e caiu na suíte completa; estourou o prazo meu (rc=124), sem veredito. Refeito por cópia da base em `$TMPDIR` com os dois testes novos: test_fc_pr_parecer_forjado 4 falhas em 7; test_filtros_l08_g2_ancora 2 falhas e 1 erro em 4. Os que passam na base são os de não recusa (esperado).
- Mutantes: `forge-mutante tests/mutantes/v0478-guardas-forge-check.json tests/mutantes/v0478-guardas-forge-check-2.json --base 4182a6b9`: M1 a M12 morreram, rc=0. `--cobertura --base 4182a6b9`: toda condição mudada de `bin/forge-check` tem mutante declarado; `tests/pesos-d4.json` é dado (não coberto, sem guarda).
- Fora do que o diff muda: sem achado.
