---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-validar-yaml-workflow
commit: d7a8c8f9e4508668b497477e1283b08ae0322fb5
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: validador de YAML dos workflows (E13.6, revisão E13.18)

## Achados
- A1 (bloqueante) scripts/validar-yaml-workflow.py:44 · mutante sobrevivente (Q10, escrito pelo QA): trocar o `continue` de `if not par:` por `break` passa nos 13 testes; linha sem par (item `- v1`) passaria a calar o resto do arquivo. Falta teste com defeito depois de linha sem par. M10 morre por erro, não por asserção
- A2 (recomendado) tests/mutantes/v048-validar-yaml-workflow.json:12 · M2, M10 e M11 morrem por erro do teste (`if False:` deixa `mapas[col]` sem chave; `.strip()` em None). Troque por mutantes semânticos: Q2 (`- {chave}`) e Q11 (`or "x:"`) morrem por asserção; M10 só com `break` e o teste de A1
- A3 (recomendado) tests/test_validar_yaml_workflow.py:12 · o teste carrega o script no import; na base sem o script o módulo cai com FileNotFoundError e `forge-testes --vermelho` sai "sem veredito". Vermelho feito à mão (abaixo); carregar o script dentro de `setUpModule` daria veredito

## Critério → teste → resultado
Sem especificação de UX nem contrato de API: a obrigação é a ordem do dono E13.6 (VALIDAR-YAML-DO-WORKFLOW) e o brief.
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `: ` em valor simples recusado (#929) | test_dois_pontos_sem_aspas_no_valor_e_recusado | valor com `: ` no meio | passou |
| valor terminado em `:` recusado | test_valor_terminado_em_dois_pontos_e_recusado | `:` no fim | passou |
| tabulação recusada | test_tabulacao_na_indentacao_e_recusada | tab na indentação | passou |
| chave repetida no mapa recusada | test_chave_repetida_no_mesmo_mapa_e_recusada | duplicata vizinha | passou |
| mesma chave em itens de lista passa | test_mesma_chave_em_itens_diferentes_passa | item novo limpa o mapa | passou |
| bloco, comentário e linha em branco não conferidos | test_corpo_de_bloco_nao_e_conferido, test_comentario_com_dois_pontos_nao_e_conferido, test_linha_em_branco_dentro_do_bloco_nao_encerra_o_corpo | corpo do bloco, `#` | passou |
| workflows do repositório passam | test_workflows_do_repositorio_passam | rc 0, saída vazia | passou |
| CLI: rc 1 com arquivo:linha; rc 2 ilegível | test_cli_sai_1_com_defeito_e_nomeia_arquivo_e_linha, test_arquivo_ilegivel_sai_2 | rc 1 e 2 | passou |
| linha sem par não interrompe a conferência | nenhum | linha sem par antes de um defeito | sem teste (A1) |

## Cenários e resultado real
- Local: `python3 -m unittest tests.test_validar_yaml_workflow` = 13 testes OK.
- Vermelho (manual, base a1971853 mais só o teste novo): `FileNotFoundError: .../scripts/validar-yaml-workflow.py` na carga do módulo; os 13 não rodam. `bin/forge-testes --vermelho a19718532c83 --modulos test_validar_yaml_workflow` deu `sem veredito (prazo, sinal ou executor sem registro em B)` (A3).
- Mutantes declarados (`bin/forge-mutante tests/mutantes/v048-validar-yaml-workflow.json`, rev d7a8c8f9e450): M1 a M14 todos `morreu`; M2, M10 e M11 com `(erro) o teste declarado deu erro sob o mutante e passa sem ele` (A2).
- Mutantes do QA (spec fora do repositório): Q2 `morreu` (asserção); Q11 `morreu` (asserção); Q10 `sobreviveu` (A1).
- Caso do #929 sobre o ci.yml atual: `name:` do passo da linha 64 com ` (nota: sem aspas)` acrescentado dá `ci-ruim.yml:64: valor simples com ...`, rc 1; o ci.yml e o diario.yml reais, rc 0, e as versões históricas de 2bdf1a2e a 502c235b do ci.yml também. Os commits do #929 com o defeito original não estão no histórico (squash), então o caso é o reproduzido por injeção.
- Sondas sem defeito falso: URL, `12:30`, aspas multilinha, escalar multilinha, CRLF, itens de lista repetidos. Fora do subconjunto declarado na docstring: chave citada repetida, âncora, `[x: y]`.
- CI do head (`gh pr checks`, lido na hora): bateria (pareceres), (passos), (python 3.14), (verificações longas), catraca e catraca (conferência) em pass; suítes 1 a 5 de 5 ainda pending. Sem a linha `ci:` até concluírem; a volta a grava.
