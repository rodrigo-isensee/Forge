---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-resto
commit: ec5c7040a3176579a18b8c2429a540ab7e2b44d6
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: D2 forge-check pronto, primeira fatia (v0481 E11.11, PR #881, classe C)

Escopo lido: diff `30dde21..ec5c704` (bin/forge-check, bin/forge_pronto.py, bin/forge-testes, docs/indice-forge.md, tests/pesos-d4.json, tests/test_forge_pronto.py, 3 specs de mutante). Sem plano antecipado: o pedido é de corrigir/entregar, sem `CA-n` de UX. Obrigações: o brief (não trocar nem afrouxar checagem existente; rc 2 nunca vira passa).

## Critério → teste → resultado
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `pronto` só reúne, sem checagem nova: os passos são os comandos existentes (`forge-testes --registros/--texto/--afetados`, classes `Neutralidade` e `NeutralidadeDoNucleo`, pr-texto da catraca com `--base` = ancora, o mesmo do CI) | `Agregador.test_passos_cobrem_as_checagens_do_cartao`; mutante `v0481-d2-resto-2:M7` | lista de passos, base repassada | passou |
| Nenhuma checagem existente é afrouxada: o diff só soma (31 linhas em `forge-check`, 1 palavra no mapa do `forge-testes`, 1 linha no índice, 1 peso); nada removido | leitura do diff | n/a | passou |
| rc 2 nunca vira passa: comando que não abre sai 2 em `rodar`, e todo `rc != 0` de passo conta como reprovado (saída final 1) | `test_comando_que_nao_abre_sai_2`; mutante `d2-resto:M1` (2→0) e `M5` morrem | OSError, rc 2 de passo | passou |
| base ausente, corpo ilegível: saída 2, não 0 | `CmdPronto.test_base_ausente_sai_2`, `test_corpo_ilegivel_sai_2` | base ausente, arquivo ilegível | passou |
| corpo ausente (sem `--corpo` e sem PR aberto, ou PR fechado) reprova, nunca passa | `test_sem_corpo_e_sem_pr_reprova`, `test_pr_aberto_da_o_corpo_e_fechado_nao`, `TamanhoECorpo.test_sem_corpo_reprova_sem_rodar_a_catraca` | corpo None, PR CLOSED | passou |
| teto H1: 150 passa, 151 sem motivo reprova, 151 com `teto: excedido` passa | `test_acima_do_teto_*` | 150/151 | passou |
| pr-texto reprovado reprova com o corpo no ambiente | `test_pr_texto_reprovado_reprova_com_o_corpo_no_ambiente` | rc da catraca | passou |

## Provas
- Módulo do item: `python3 -I -m unittest discover -s tests -p test_forge_pronto.py` → `Ran 14 tests ... OK` (1,7 s). A suíte inteira fica para o CI do PR; não rodei.
- Vermelho (`bin/forge-testes --vermelho 30dde2189bb... --modulos test_forge_pronto`): `contagem: não prova (passa na base)=9; prova (asserção)=5`, rc 0 (ao menos um prova, nenhum cai no HEAD). Os 5 que provam são os `CmdPronto` (subcomando inexistente na base); os 9 do agregador testam o módulo novo com falsos e o harness os marcou "passa na base".
- Cobertura (`bin/forge-mutante --cobertura --base 30dde21...`): todas as linhas Python mudadas `coberta · ... declarado, não provado`; única linha fora: `não coberto: tests/pesos-d4.json` (dado, sem guarda).
- Mutantes, cada spec separada, `--processos 3`: `v0481-d2-resto.json` M1..M8 `morreu`, rc 0; `-2` M1..M8 `morreu`, rc 0; `-3` M1..M2 `morreu`, rc 0. Nenhum sobrevivente, nenhum equivalente.
- Rodada única das três specs (como a skill manda): `forge-mutante: spec inválida; nada foi executado. - id de mutante repetido entre as specs: M1, M2, M3, M4, M5, M6, M7, M8` (ver A1).

## Achados
- A1 (bloqueante) tests/mutantes/v0481-d2-resto-3.json:6 · ids M1 e M2 repetem os de `v0481-d2-resto.json` e `-2.json` (e M3..M8 se repetem entre esses dois): `forge-mutante` das 3 specs numa rodada sai "spec inválida; nada foi executado". Renumerar com id único no conjunto (M1..M18).
- A2 (recomendado) bin/forge_pronto.py:57 · o rc 2 de um passo (ex.: `--afetados` sem veredito, comando que não abre) vira "reprovado (saída 2)" e a saída final é 1; seguro (nunca passa), mas o help diz "2 não verificável". Documentar que 2 só vem de base/corpo, ou propagar.

## Melhoria vista
O `forge-check pronto` não aceita `--corpo -` (stdin) nem avisa quando o `gh` falha por rede, que cai no mesmo "corpo não conferido"; vale distinguir os dois.
