---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pesado-corrida
commit: eb2f9b9d51f38bb4c6810ad5c228aaf966bf5f66
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: PESADO-CORRIDA-TRAVA-SOME (E89.4)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Trava que some entre `exists` e a leitura vale como livre e a espera pega a vez (E89.1) | `TravaQueSomeNaLeitura.test_trava_que_some_entre_o_exists_e_a_leitura_pega_a_vez` | arquivo some na janela | passou |
| Trava que existe e não se lê (permissão, JSON quebrado) segue levantando | `TravaQueSomeNaLeitura.test_trava_que_existe_e_nao_se_le_segue_levantando` | só `FileNotFoundError` é livre | passou |
| Caso do CI (job 729) | `ForgePesado.test_esperar_pega_a_vez_quando_a_trava_some` | corrida real | 20 de 20 rodadas sem falha |

## Cenários e resultado real
- Vermelho: `bin/forge-pesado` da base (37156f9c) com o teste do head: `TravaQueSomeNaLeitura` dá 1 erro (`FileNotFoundError ... pesado.json`), 2 testes rodados; com o conserto, `OK`. Árvore restaurada, limpa.
- Mutantes (`bin/forge-mutante tests/mutantes/v0478-pesado-corrida.json`): `M1 · morreu · bin/forge-pesado:56`; `M2 · morreu · bin/forge-pesado:56 · (erro)`. Um mutante por linha de guarda mudada: coberto.
- `test_forge_pesado`: 20 testes OK; `test_pesado_fila`: 8 testes OK. Nenhum `skip` nos dois arquivos. Sem suíte local; a suíte inteira é do check-run `bateria` do CI.
