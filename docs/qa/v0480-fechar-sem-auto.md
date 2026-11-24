---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-sem-auto
commit: a34b33bf1bd6a4e2e726846eb68fd0e397e5196f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0480-fechar-sem-auto (FECHAR-NUNCA-AUTO, PR #855), delta pós-volta

Delta desde o parecer anterior (f5143cea): `bin/forge-testes` (o mapa passa a rodar `test_fechar_sem_auto` quando o `bin/forge-fechar` muda; A2 do review) e `tests/mutantes/v0478-fechar-checks.json` (FCK-M5 e FCK-M6 alinhados ao forge-fechar novo, com `falta_q`). Lógica de produção intacta; os critérios e os testes do parecer anterior seguem valendo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Mapa roda o teste novo quando `bin/forge-fechar` muda | `test_testes_tocados` (196 testes) | n/a | passou |
| FCK-M5: execução mais recente rodando ou ausente não vira verde | `test_rodando_ou_ausente_espera_e_para_no_prazo_sem_merge` | ausente/rodando | mutante morreu |
| FCK-M6: pendente no prazo para sem merge, com o texto novo do die | `test_exigido_vermelho_rodando_ou_ausente_recusa_o_merge`, `test_nome_mais_longo_verde_nao_vale_pelo_exigido` | prazo | mutante morreu |
| Obrigações anteriores (sem `--auto`, todo check-run verde, cópia velha) | `test_fechar_sem_auto` (12 testes) | mínimo de arquivos, 5 conclusões | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_fechar_sem_auto.py`: 12 testes, OK (19,4 s).
- `python3 -I -m unittest discover -s tests -p test_testes_tocados.py`: 196 testes, OK (skipped=1, shellcheck ausente no ambiente; o CI o roda).
- Suíte inteira: não rodei; vale o check-run `bateria` do CI do PR no mesmo sha.

### Vermelho antes do verde
`bin/forge-testes --vermelho c752c227 --modulos test_fechar_sem_auto,test_fechar` (head a34b33bf):
```
tests.test_fechar_sem_auto.CopiaDaDevelop.test_develop_sem_o_arquivo_recusa · H=ok · B=falha · prova (asserção)
tests.test_fechar_sem_auto.SemAutoNaFonte.* (3) · H=ok · B=ok · não prova (passa na base)
tests.test_fechar_sem_auto.TodoCheckRunDoHead.* (3) · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=113; prova (asserção)=9; pulado=1
```
Nenhum teste cai no HEAD. Os 3 de `SemAutoNaFonte` passam na base de propósito (guarda de regressão; o `--auto` já saíra do script).

### Mutação
`bin/forge-mutante tests/mutantes/v0478-fechar-checks.json --processos 2` (rev=a34b33bf1bd6), rc 0:
```
FCK-M1 · morreu · bin/forge-fechar:940
FCK-M2 · morreu · bin/forge-fechar:947
FCK-M3 · morreu · bin/forge-fechar:1705
FCK-M4 · morreu · bin/forge-fechar:944
FCK-M5 · morreu · bin/forge-fechar:948
FCK-M6 · morreu · bin/forge-fechar:961
FCK-M7 · morreu · bin/forge-fechar:1343
FCK-M8 · morreu · bin/forge-fechar:960
```
FCK-M5 e FCK-M6 morrem (linhas 948 e 961 do `bin/forge-fechar`; os trechos `de` casam com a fonte nova). Os mutantes N1 a N10 do parecer anterior cobrem as linhas de guarda do diff, que o delta não tocou.
