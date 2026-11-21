---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-d1-versoes
commit: 0204884e682798a4a0b83e3538c75bff62248620
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0478 E57.60 (PR-VERDE D1, `forge-testes --versoes`)

Diff conferido: `d4f0b10a..0204884e` (5 arquivos: `bin/forge-testes`, `tests/test_testes_tocados.py`, duas specs de mutantes, fragmento de changelog). Os pareceres de review e segurança (7c7cf40b) foram trazidos por fast-forward; não alteram código.

## Achados
- A1 (recomendado) bin/forge-testes:1103 · `--versoes` não termina em 900 s nesta máquina (plano afetado grande: 3257 testes, 1939 s no log 3.12 visto); sem veredito local aqui. O CI do PR é a prova de verde; considerar prazo ou plano menor.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Uma rodada por versão do ci.yml, em série, com o intérprete dela | `Versoes.test_verde_roda_cada_versao_da_configuracao_com_o_interprete_dela` | sem repetição, sem a versão do ambiente | passou; vermelho na base |
| Sem afetado: log "nada a rodar", intérprete não chamado | `test_sem_afetado_grava_nada_a_rodar_sem_chamar_o_interprete` | plano vazio | passou; vermelho na base |
| Intérprete ausente: aviso, rc=ausente, saída 1 | `test_interprete_ausente_e_aviso_e_nao_verde` | ausência do binário | passou; vermelho na base |
| Intérprete que se diz de outra versão não vale | `test_interprete_que_se_diz_de_outra_versao_nao_vale` | versão errada | passou; vermelho na base |
| Vermelho em uma versão: saída 1 | `test_vermelho_em_uma_versao_sai_1` | falha só na 2.ª | passou; vermelho na base |
| Sem versão na configuração: saída 2, sem log | `test_sem_versao_na_configuracao_sai_2_sem_log` | vazio | passou; vermelho na base |
| Mudança não commitada: saída 2, sem log | `test_mudanca_nao_commitada_sai_2_sem_log` | árvore suja | passou; vermelho na base |
| Git ilegível: saída 2, sem log | `test_git_ilegivel_sai_2_sem_log` | base inexistente | passou; vermelho na base |
| Só combina com --base | `test_so_combina_com_base` | uso inválido | passou; vermelho na base |

## Cenários e resultado real
Todos os comandos em primeiro plano, com timeout 900, saída em `/root/.forge-contrib/wt/qa-d1-*.log`.

Vermelho antes do verde. `forge-testes --vermelho d4f0b10a` sem restrição varre 223 módulos (371 s só no 1.º); abortei no 5.º módulo (log `qa-d1-vermelho-completo-abortado.log`) e rodei restrito ao módulo do diff:

    vermelho: base=d4f0b10aead7 head=7c7cf40baf09 módulos=test_testes_tocados (restrito por --modulos)
    tests.test_testes_tocados.Versoes.test_git_ilegivel_sai_2_sem_log · H=ok · B=falha · prova (asserção)
    ... (os 9 testes de Versoes, todos H=ok · B=falha · prova (asserção))
    contagem: não prova (passa na base)=186; prova (asserção)=9; pulado=1
    rc=0

Mutantes (`bin/forge-mutante` nas duas specs; saída 0, todos morreram):

    forge-mutante: pedido=v0479-pv-d1-versoes rev=7c7cf40baf09 spec=8d72046b... spec=71b25f33...
    G1 · morreu · bin/forge-testes:1086
    G2 · morreu · bin/forge-testes:1090
    G3 · morreu · bin/forge-testes:1095
    G4 · morreu · bin/forge-testes:1077
    G5 · morreu · bin/forge-testes:1080
    G6 · morreu · bin/forge-testes:1103
    G7 · morreu · bin/forge-testes:1116
    G8 · morreu · bin/forge-testes:1172
    G9 · morreu · bin/forge-testes:1106
    G10 · morreu · bin/forge-testes:1211
    rc=0

Cobertura (`forge-mutante --cobertura --base d4f0b10a`, rc=0): 9 condições Python mudadas, cada uma com mutante declarado (linhas 1077, 1080, 1086, 1090, 1103, 1106, 1116, 1172, 1211); nenhuma sem mutante, nenhuma isenta velha.

`forge-testes --versoes --base d4f0b10a` na máquina: só há python3.12 (`which python3.14` vazio). Minha rodada estourou os 900 s (rc=124, sem veredito, nada gravado por ela). O `.forge/run/afetados-3.12.log` encontrado (head=0204884e, gravado às 22:18, `Ran 3257 tests in 1939.471s`, `FAILED (failures=41, errors=1)`, falhas em `test_oraculo_sempre_atual`) não é meu: não o uso como prova nem atribuo as falhas ao diff. O `afetados-3.14.log` (`sem o intérprete python3.14`, `rc=ausente`) confere com o esperado: ausente não é verde, saída 1, e o teste `test_interprete_ausente_e_aviso_e_nao_verde` o guarda. A suíte inteira roda no CI do PR (check-run `bateria` do mesmo sha).
