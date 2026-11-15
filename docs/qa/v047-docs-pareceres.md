---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-docs-pareceres
commit: 7d32017c69de41a8ef9e8d19cb8943c2fb0755d3
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 docs-pareceres (E1.276)

Intervalo `origin/develop..7d32017c`. Sem especificação de UX: as obrigações são as da etapa E1.252 do pedido v047 (o `pedido:` do parecer é id de `docs/pedidos/` ou `release-X.Y.Z`; `forge-check docs <arquivo>`; mensagem do bloco Achados vazio; modelo do review). Bug em `docs/qa/bugs/` não aberto: o defeito é um teste do repositório que cai no head.

## Achados
- A1 (bloqueante) bin/forge-check:407 · SaidaSanitizada.test_todo_valor_de_caminho_numa_fstring_passa_pelo_sanitizador cai no head (verde na base): f'{CONTRATOS[tipo][0]}/{real.name}' é interpolação crua de caminho; use sem_controle/nome_seguro (R-QA)
- A2 (recomendado) tests/test_forge.py:7485 · 8 dos 10 testes novos dão TypeError na base (cmd_docs sem o 2º argumento), então o vermelho sai rc 2 (sem veredito); só 2 provam por asserção. Chamar por forma que a base aceite dá veredito por teste (R-QA)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 pedido inexistente ou nome da branch recusado, mensagem com o id | test_pedido_inexistente_e_nome_da_branch_sao_recusados_com_o_id_na_mensagem; sonda S1 | id fora de docs/pedidos, nome da branch inteiro e sem prefixo, `../`, `release-0.47` | passou |
| CA-2 pedido registrado, `release-X.Y.Z` e raiz de pedidos valem | test_pedido_registrado_release_e_branch_que_e_pedido_valem; test_pedido_da_raiz_de_pedidos_vale_e_sem_pasta_de_pedidos_nada_a_conferir | sem pasta de pedidos nada a conferir; `release-1.2.3x` recusado (sonda) | passou |
| CA-3 FC-DOCS-CAMINHO: só os arquivos dados, estrito, cópia fora da raiz com critério da pasta do tipo | test_copia_fora_da_raiz_...; test_dentro_da_raiz_a_pasta_errada...; test_arquivo_ausente_ou_que_nao_e_md_e_recusado; test_linha_de_comando_com_arquivo | ausente, não `.md`, diretório, tipo desconhecido, sem frontmatter | passou |
| CA-4 sem arquivos o pedido só se confere no delta | test_sem_arquivos_o_pedido_so_e_conferido_no_delta | delta vazio, delta com o arquivo, base ilegível | passou |
| CA-5 mensagem do bloco Achados vazio e aprovado sem o bloco | test_parecer_aprovado_sem_o_bloco_achados_passa; teste da cópia fora (mensagem nova) | "Nenhum." dentro do bloco | passou |
| CA-6 modelo do review diz o id e o parecer sem achados | test_modelo_do_review_diz_o_id_do_pedido_e_o_parecer_sem_achados | n/a | passou |
| Regressão da suíte | SaidaSanitizada (8 testes, `python3 -m unittest tests.test_forge.SaidaSanitizada`) | interpolação crua de caminho | FALHOU (A1) |

## Cenários e resultado real
- Classe nova: `python3 -m unittest tests.test_forge.DocsPareceresPedidoECaminho` · 10 testes, OK.
- Sondas com `--raiz-pedidos ~/.forge-contrib docs <copia>`: `pedido: v047` rc=0; `melhoria/v047-docs-pareceres` rc=1 "é o nome da branch"; `v047-docs-pareceres` rc=1 "é o nome da branch"; `release-1.2.3` rc=0; `release-1.2.3x` rc=1 "não está em docs/pedidos/".
- Vermelho (`forge-testes --vermelho origin/develop --modulos tests.test_forge --prazo 1500`), rc=2:
  `vermelho: base=c5c3a449d7c3 head=7d32017c69de módulos=test_forge (restrito por --modulos)`
  `revertidos à base: bin/forge-check, changelog.d/v047-docs-pareceres.md, templates/projeto/docs/reviews/_modelo.md`
  `tests.test_forge.DocsPareceresPedidoECaminho.test_linha_de_comando_com_arquivo · H=ok · B=falha · prova (asserção)`
  `tests.test_forge.DocsPareceresPedidoECaminho.test_modelo_do_review_diz_o_id_do_pedido_e_o_parecer_sem_achados · H=ok · B=falha · prova (asserção)`
  8 testes da classe nova: `H=ok · B=erro · sem veredito` (TypeError na base)
  `tests.test_forge.SaidaSanitizada.test_todo_valor_de_caminho_numa_fstring_passa_pelo_sanitizador · H=falha · B=ok · regressão`
  `contagem: não prova (passa na base)=609; prova (asserção)=2; regressão=1; sem veredito=8`
- Mutantes (`bin/forge-mutante tests/mutantes/v047-docs-pareceres.json tests/mutantes/v047-docs-pareceres-2.json --processos 3`), rc=0, 13 de 13 morreram (M1..M13; M6, M8, M13 por erro do teste declarado sob o mutante). `--cobertura --base c5c3a449` lista as 12 condições do diff como cobertas, nenhuma sem mutante.
- A suíte inteira roda só no CI do PR; sem PR ainda, não há check-run `bateria` do sha para citar. A1 indica que ela falhará.
