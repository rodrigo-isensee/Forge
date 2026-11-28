---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-brief-sonda-escrita
commit: 61ab461ec3cbc099baf4c24aa7dc7e7803427dbf
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v0481 BRIEF-SONDA-ESCRITA (#952, E45.60)

- ci: 61ab461ec3cbc099baf4c24aa7dc7e7803427dbf verde

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Fixture igual ao brief tl-443 sela (sonda do parecer, caminho `.git/hooks/...` na entrada, sem `escrita: barrada`) | `test_volta_com_a_sonda_do_parecer_nao_barra_a_escrita` | entrada da sonda com caminho de hook | passou; vermelho na base (prova por asserção) |
| Linha comum do Entregar com `.git/hooks/...` segue barrada | `test_linha_comum_do_entregar_com_o_caminho_segue_barrada` | só a entrada da sonda é isenta | passou; passa na base por desenho (guarda de não regressão), M1 e M2 a cercam |
| Sem `--ref` ou sem `Volta-de:` a entrada segue barrada | `test_sem_ref_ou_sem_volta_de_a_entrada_segue_barrada` | sonda não relida | passou; mortos M2, M3, M4 |
| Sonda alterada, a mais ou S3 repetida com outra entrada é recusada | `test_sonda_alterada_ou_sem_par_no_parecer_e_recusada` | par (tipo, id, entrada) exato | passou; vermelho na base; mortos M5, M7 |

## Vermelho antes do verde
`bin/forge-testes --vermelho b414714c --modulos test_brief_sonda_escrita` (log `qa159-v0481-vermelho.log`), rc=0:
```
vermelho: base=b414714cd2ba head=61ab461ec3cb módulos=test_brief_sonda_escrita (restrito por --modulos)
revertidos à base: bin/forge-check, bin/forge-testes, changelog.d/v0481-brief-sonda-escrita.md
...test_linha_comum_do_entregar_com_o_caminho_segue_barrada · H=ok · B=ok · não prova (passa na base)
...test_sem_ref_ou_sem_volta_de_a_entrada_segue_barrada · H=ok · B=ok · não prova (passa na base)
...test_sonda_alterada_ou_sem_par_no_parecer_e_recusada · H=ok · B=falha · prova (asserção)
...test_volta_com_a_sonda_do_parecer_nao_barra_a_escrita · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=2; prova (asserção)=2
```
Os dois que passam na base são guardas de limite (comportamento que deve ficar); a mutação os prova (M2 a M4 e a spec do I62).

## Mutantes
`bin/forge-mutante tests/mutantes/v0481-brief-sonda-escrita.json` (log `qa159-v0481-mutantes.log`), rc=0: M1 a M7 morreram (bin/forge-check:9059, 9066, 9141, 9141, 4923, 4922, 4921). Um mutante por linha de guarda mudada no diff: conferido (4921-4923, 9059, 9066, 9141, 9143).

Realinhamento do I62 (`tests/mutantes/v0433-integracao-4.json`, só `de`/`para` ganharam o argumento `relidas`): `forge-mutante --ids I62` estourou o prazo do runner (9 módulos); conferi à mão, no mesmo `de`/`para` da spec, numa cópia descartável: `tests.test_brief_forma_aceita` cai com o mutante (`FAIL test_o_branch_do_brief_decide_a_entrada_de_ramo`, 1 falha em 18) e passa sem ele (18 OK, controle verde). O I62 segue morto (logs `qa159-v0481-i62-test_brief_forma_aceita.log`, `qa159-v0481-i62-controle.log`).

## Cenários e resultado real
Limites exercidos pelos testes do autor, lidos contra o brief: fixture tl-443 sela; linha comum com `.git/hooks` barrada; sonda alterada recusada. Sem UI, sem acessibilidade aplicável. Sem teste novo do QA.
