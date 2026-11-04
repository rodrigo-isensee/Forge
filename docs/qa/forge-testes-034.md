---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/forge-testes-034
commit: 1d7a02fa45244ba44dbcb2863c2029f350798c8e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 1
aceite_usuario: sim
data: 2026-11-04
---
# QA: forge-testes 0.34 (cartões 15, 19 e 20)

Escopo: bin/forge-testes (CAMINHO de módulo sem mapa, aviso cedo de MAPA, `-k`). Comparação com a base b45e40a (develop) rodando o script dela sobre o mesmo diff. Suíte completa fica com o CI/pre-push (D-5); aqui rodou tests/test_testes_tocados.py.

## Achados
- A1 (recomendado) bin/forge-testes:LEITURA_DE_BIN · aviso falso quando o teste só passa "bin/x" como argumento; BUG forge-testes-034-aviso-falso-chamada, baixa, só ruído em stderr.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| FORGE-TESTES-SEM-MAPA | CT-01 `forge-testes tests/test_changelog.py` | módulo existente sem mapa | passou: roda só test_changelog, 46 testes, aviso "sem mapa" |
| FORGE-TESTES-SEM-MAPA | CT-02 `--listar tests/nao_existe.py` | caminho inexistente | passou: falha fechado, suíte completa |
| FORGE-TESTES-SEM-MAPA | CT-03 módulo + bin/forge-changelog | mistura | passou: suíte completa, igual à develop |
| MAPA-TESTES-AVISO-CEDO | CT-04 diff com test_testes_tocados | aviso | passou, com ruído (A1) |
| TESTES-DO-ITEM-FILTRO | CT-05 `-k Mapa`; `-k Mapa -k Sem` | 1 e 2 padrões | passou: 23 testes OK |
| TESTES-DO-ITEM-FILTRO | CT-06 `-k zzzz` | nenhum casa | passou: rc 5, NO TESTS RAN |
| TESTES-DO-ITEM-FILTRO | CT-07 `--vermelho -k Mapa` | combinação | passou: recusado, rc 2 |
| paridade | CT-08 `--listar` por diff (base b45e40a), com alteração em bin/forge-changelog e por CAMINHO | plano idêntico | passou: stdout igual; só difere o aviso de A1 |
| tests/test_testes_tocados.py | CT-09 módulo inteiro | n/a | passou: 23 OK |
| vermelho | CT-10 `--vermelho b45e40a --modulos test_testes_tocados` | testes novos | passou: rc 0, 5 provam por asserção |

## Cenários e resultado real
Observações: `-k` sem correspondência sai 5 (herdado do unittest), sem mensagem do forge-testes. test_changelog tem 1 skip herdado, não tocado. Mutantes: não se aplica a mutante declarado neste pedido (sem spec em tests/mutantes/); sem outro bloqueio.
