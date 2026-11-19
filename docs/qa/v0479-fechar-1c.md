---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-fechar-1c
commit: ef6b06e61476178a4d6dc4a5bd4c07bb8ccdc699
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-18
---
# QA: v0478 E30.1 (1c no merge do 2b, antes do envio)

Diff lido contra a base 738424449cf9: `bin/forge-fechar` (1c no commit do merge, antes do envio; `promovivel` aceita `<onde>`; texto do dry-run), `tests/test_fechar_base_andou.py`, `tests/mutantes/v0478-fechar-1c.json`, fragmento do changelog. Sem suíte local: só o módulo tocado; a bateria completa é do CI do PR.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E30.1: base com release não promovida recusa o merge sem envio (R-FLUXO) | test_e30_1_base_com_release_nao_promovida_recusa_o_merge_sem_envio (promover-homolog real) | head local e remoto inalterados, sem PR nem merge | passou |
| E30.1: merge não promovível para antes do envio, head antigo passou | test_e30_1_merge_nao_promovivel_para_antes_do_envio_e_o_head_antigo_passou | 1c roda no head antigo e depois no merge de pais [antigo, develop] | passou |
| E30.1: dry-run descreve o 1c no merge | test_e30_1_dry_run_descreve_o_1c_no_merge_antes_do_envio; test_c5_dry_run_imprime_o_2b_e_nao_le_o_servidor | n/a | passou |

## Vermelho antes do verde
`bin/forge-testes --vermelho 738424449cf9eb9b2b41d0663d3973d93a138324 --modulos test_fechar_base_andou --prazo 400` (rc 0):
```
vermelho: base=738424449cf9 head=ef6b06e61476 módulos=test_fechar_base_andou (restrito por --modulos)
revertidos à base: bin/forge-fechar, changelog.d/v0479-fechar-1c.md
mantidos no HEAD: tests/mutantes/v0478-fechar-1c.json, tests/test_fechar_base_andou.py
...test_c5_dry_run_imprime_o_2b_e_nao_le_o_servidor · H=ok · B=falha · prova (asserção)
...test_e30_1_base_com_release_nao_promovida_recusa_o_merge_sem_envio · H=ok · B=falha · prova (asserção)
...test_e30_1_dry_run_descreve_o_1c_no_merge_antes_do_envio · H=ok · B=falha · prova (asserção)
...test_e30_1_merge_nao_promovivel_para_antes_do_envio_e_o_head_antigo_passou · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=36; prova (asserção)=4
```

## Mutação
Uma linha de guarda mudada no diff (a chamada `promovivel "$novo"`), um mutante declarado (M1).
```
forge-mutante: pedido=v0478-fechar-1c rev=ef6b06e61476 spec=10fbbbdc2b44465a5c2b5ab6674a0aa3eb471edb1c4ce617fb5977fce6916df4
M1 · morreu · bin/forge-fechar:844
```
Saída 0: nenhum sobrevivente.

## Execução
`python3 -I -m unittest discover -s tests -p test_fechar_base_andou.py`: 40 testes, OK.
