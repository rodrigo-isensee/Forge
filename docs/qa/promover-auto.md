---
tipo: qa
contrato: 1
pedido: promover-auto
branch: melhoria/promover-auto
commit: 5c31a5fbbe2f0e3cdd36f3ccae05525f46b578d8
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: promover-auto

Escopo: E1 e E2 do pedido (`scripts/promover-homolog.py` lê só os checks do evento `pull_request` por `gh pr checks <PR> --json name,bucket,event,link` e imprime sempre o merge com `--auto`). Sem gatilho de segurança (`R-SEGURANCA`): o script só lê checks e imprime o comando. Diff conferido contra o pedido (`99315cf...5c31a5f`, 5 arquivos): sem escopo além de E1/E2.

## Achados

## Critério → teste → resultado
O pedido não traz `CA-n`; as obrigações são as do escopo E1/E2 (`R-QA`).
| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Só contam checks do evento pull_request | test_so_checks_do_push_nao_sao_verdes_e_o_merge_sai_com_auto | só check de push (PR recém-aberto): não é verde, sai 0 com `--auto` | passou |
| Check do push não decide vermelho nem verde | test_check_do_push_nao_decide_o_vermelho_nem_o_verde | push fail + PR pass = verde; push pass + PR fail = para (rc 1) | passou |
| Leitura pede o JSON com o evento | test_le_os_checks_em_json_com_o_evento | argumentos exatos da chamada ao gh | passou |
| Saída que não é lista JSON para; "no checks reported" não para | test_saida_que_nao_e_lista_json_para | texto tabulado, objeto JSON, sem check reportado | passou |
| Merge impresso leva sempre `--auto --match-head-commit` | test_abre_o_pr_para_a_homolog_..., test_sem_checks_ainda_..., test_check_pendente_... | pendente, vazio, verde | passou |
| Vermelho para; Catraca vermelha pede rótulo (rc 3) | test_check_vermelho_para, test_catraca_vermelha_sem_rotulo_aguarda_o_dono | fail em um check | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_promover_homolog`: 29 testes, OK (carga de 1 min abaixo de 7 antes e depois).
- Vermelho antes do verde (`bin/forge-testes --vermelho 99315cfb42c6852c7d7959cd6dca8161e2bd5c08 --modulos test_promover_homolog`, rc 0): `vermelho: base=99315cfb42c6 head=5c31a5fbbe2f`; revertidos à base: changelog.d/promover-auto.md, docs/promocao-integrador.md, scripts/promover-homolog.py; contagem: prova (asserção)=9, não prova (passa na base)=20. Provam, entre outros: test_so_checks_do_push_nao_sao_verdes_e_o_merge_sai_com_auto, test_check_do_push_nao_decide_o_vermelho_nem_o_verde, test_le_os_checks_em_json_com_o_evento, test_saida_que_nao_e_lista_json_para. Os que passam na base são regressão de comportamento intocado.
- Mutantes (`bin/forge-mutante tests/mutantes/promover-auto.json`), saída 0: M1 a M6 todos "morreu" (promover-homolog.py:196, 218, 187, 192, 244, 244).
- `bin/forge-mutante --cobertura --base 99315cf`: coberta :192 (M4), :196 (M1), :244 (M5, M6); as três "apagada" são linhas da leitura tabulada removida. A linha `--auto` (M2, :218) já existia na base e a spec a cobre. Nenhuma linha de guarda mudada sem mutante, conferido contra o diff.
- Documentação (`docs/promocao-integrador.md`) coerente com o código: passos 5 e 7.

## Riscos
Nenhum bug aberto. O `gh` real não foi exercitado (os testes usam gh falso): o formato `--json name,bucket,event,link` é o do contrato do próprio gh.
