---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-fechar-sem-homolog
commit: e3e38dc8f2716cce938fee31019f87ae37703de8
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047 fechar-sem-homolog (E2.124, FECHAR-SEM-HOMOLOG-LOCAL)

Pedido de correção sem especificação de UX: as obrigações são as de `changelog.d/v047-fechar-sem-homolog.md` e do código (`R-FLUXO`, `R-MAIN`). Diff de `bf475209` a `e3e38dc8`: `bin/forge-fechar`, `tests/test_fechar.py`, `tests/mutantes/v047-fechar-sem-homolog.json`, fragmento do changelog. A suíte inteira roda no CI do PR; aqui só os testes do item. Os commits `6d765e45` e `0cd58c71` (pareceres) vieram por merge e não tocam código.

## Achados
- A1 (recomendado) bin/forge-fechar:822 · FH-M2 cobre só o aviso; trocar o refspec `+refs/heads/homolog:refs/remotes/origin/homolog` por `origin homolog` sobrevive (QA-M2, equivalente com o refspec padrão do clone de teste). Sem teste de clone de ramo único.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 1c sem origin/homolog busca só ela | test_1c_sem_origin_homolog_no_clone_busca_so_ela_antes_do_promover | ref ausente | passou; prova (asserção) |
| 1c com a ref no clone não busca | test_1c_com_origin_homolog_no_clone_nao_busca | ref presente (só leitura) | passou; guarda negativa (mutante FH-M1 morre) |
| Busca que falha avisa e o promover decide | test_1c_busca_da_homolog_que_falha_avisa_e_o_promover_decide | falha de rede, rc 0 e 1 | passou; prova |
| Remota apagada com PR MERGED no head: limpa sem pedir push | test_2_remota_apagada_com_pr_merged_no_head_nao_pede_push_e_limpa | branch ausente | passou; prova |
| Remota apagada com head já na base | test_2_remota_apagada_com_o_head_ja_na_base_nao_pede_push | head na base | passou; prova |
| Sem PR, PR aberto, fork, outra base, outro head: continua pedindo push | test_2_remota_apagada_sem_merge_do_head_no_alvo_continua_pedindo_push | 5 casos de PR que não prova merge | passou; guarda negativa |
| Remota com outro head não é dispensada | test_2_remota_com_outro_head_e_o_conferido_mesclado_continua_parando | head divergente | passou; guarda negativa |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar`: 106 testes, OK (166 s).
- Vermelho antes do verde, `forge-testes --vermelho bf475209 --modulos tests.test_fechar`: rc=0; `contagem: não prova (passa na base)=102; prova (asserção)=4`. Os 4 que provam são os de 1c sem ref, 1c com busca que falha, PR MERGED e head na base. Os 3 restantes são guardas negativas (passam na base por construção) e morrem pelos mutantes FH-M1, M3, M5 a M8.
- Mutação, `bin/forge-mutante tests/mutantes/v047-fechar-sem-homolog.json` (rev=e3e38dc8f271), rc=0: FH-M1 a FH-M8 todos `morreu` (linhas 821, 822, 1175, 832, 835 x4). A lista cobre cada condição mudada (rev-parse do 1c, aviso, porta do passo 2, merge-base, os quatro termos do awk).
- Mutantes extras do QA (rev=348d3265, só pareceres a mais): QA-M3 (`remoto_sha` não vira o conferido) morreu; QA-M2 (refspec) sobreviveu, ver A1.
- `forge-mutante --cobertura --base bf475209`: `não coberto: bin/forge-fechar` (shell não é checado pela ferramenta; a conferência foi manual contra o diff).
- Revisado: AR-1 (lista de mutantes completa contra o diff: sim) e AR-2 (ramo de falha com teste: busca que falha e leitura do gh vazia/sem merge têm teste).
- Acessibilidade e E2E de navegador: n/a (script de linha de comando).
- Bugs: nenhum. TESTE-FECHAR-L5-CORRIDA: fora do diff (resolvido antes, segundo o pedido); não retestado.
- CI do PR: sem PR (brief); o check-run `bateria` do sha não existe ainda e é do portão de merge.
