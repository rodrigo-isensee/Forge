---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-d3-modelo
commit: 60be3dffce7a93a6d1ee0434efb632ecbcc54eba
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-pv-d3-modelo (E57.79)

Escopo: o bloco novo do `templates/projeto/.githooks/pre-push` (chave `registros` do `.forge/config.json`), a classe `ConferenciaDeRegistros` em `tests/test_prepush_so_docs.py` e as duas specs de mutantes. Sem suíte local (o `bateria` do CI é a prova da suíte inteira). A falha de `test_forge.ForgeCheck.test_raiz_depois_do_subcomando_e_git_isolado` é do ambiente e já está na triagem; não foi rodada aqui.

## Achados
- A1 (recomendado) templates/projeto/.githooks/pre-push:332 · o ramo `except` (config ilegível, aviso e segue) e as partes `0*` e `???????*` do `case` do prazo não têm mutante próprio; o M7 troca o `case` inteiro. Somar mutantes que removam só essas partes.

## Critério → teste → resultado
Sem `CA-n` de UX nesta etapa; as obrigações são as regras do bloco PR-VERDE D3 (E57.75).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem a chave, chave vazia ou sem config: nada roda | `test_sem_a_chave_ou_sem_o_config_nada_roda` | vazio | passou (não prova na base: comportamento antigo; guardado pelo M6) |
| Comando verde roda também no envio só de texto | `test_comando_verde_roda_tambem_no_envio_so_de_texto` | só docs | passou; vermelho na base |
| Saída fora de 0 barra | `test_saida_fora_de_zero_barra_o_envio` | rc 1 e 2 | passou; vermelho na base |
| Chave que não é comando de uma linha barra sem rodar | `test_chave_que_nao_e_comando_de_uma_linha_barra_sem_rodar` | lista, null, número, quebra de linha | passou; vermelho na base |
| Config ilegível avisa e segue | `test_config_ilegivel_avisa_e_o_envio_segue` | JSON inválido | passou; vermelho na base |
| Config que é link não é lido | `test_config_que_e_link_nao_e_lido` | link simbólico | passou (guardado pelo M2; a base já não lia o config) |
| Prazo inválido barra sem rodar | `test_prazo_invalido_barra_sem_rodar` | `abc`, `--help`, 0, -5, vazio, 7 dígitos | passou; vermelho na base |
| Prazo estourado barra (124) | `test_prazo_estourado_barra_o_envio` | prazo 1 s | passou; vermelho na base |
| Envio só de remoção não roda | `test_envio_so_de_remocao_nao_roda` | sem branch com commit | passou (guardado pelo M1) |

## Cenários e resultado real
### Vermelho antes do verde (`bin/forge-testes --vermelho 8ee73d15 --modulos test_prepush_so_docs`, rc=0)
```
vermelho: base=8ee73d156db5 head=146b40503055 módulos=test_prepush_so_docs (restrito por --modulos)
revertidos à base: changelog.d/v0479-pv-d3-modelo.md, stacks/node-react/pronto.md, stacks/python/pronto.md, templates/projeto/.githooks/pre-push, templates/projeto/CLAUDE.md
mantidos no HEAD: tests/mutantes/v0479-pv-d3-modelo-2.json, tests/mutantes/v0479-pv-d3-modelo.json, tests/test_prepush_so_docs.py
contagem: não prova (passa na base)=58; prova (asserção)=6; pulado=9
```
Os 6 que provam são da `ConferenciaDeRegistros`; os 3 que passam na base (sem a chave, link, remoção) são casos negativos guardados pelos mutantes M6, M2 e M1. Os 9 pulados são da trava da checagem (pasta de outro dono), preexistentes e fora do diff.

### Mutantes (`bin/forge-mutante tests/mutantes/v0479-pv-d3-modelo.json tests/mutantes/v0479-pv-d3-modelo-2.json`, rc=0)
```
forge-mutante: pedido=v0479-pv-d3-modelo rev=146b40503055 spec=29ba446a... spec=6ee9b99a...
M1 · morreu · pre-push:339    M2 · morreu · pre-push:325    M3 · morreu · pre-push:326
M4 · morreu · pre-push:335    M5 · morreu · pre-push:340    M6 · morreu · pre-push:341
M7 · morreu · pre-push:343    M8 · morreu · pre-push:351    M9 · morreu · pre-push:346
```
Nove de nove mortos, nenhum sobrevivente nem equivalente. `forge-mutante --cobertura --base 8ee73d15` sai `não coberto: templates/projeto/.githooks/pre-push` (shell, fora do alcance da ferramenta); conferi a lista à mão contra o diff: as guardas (refs de branch, config ausente ou link, python3, tipo e linha única, falha do comando, chave vazia, prazo, timeout, rc) têm mutante, salvo o que o A1 cita.

### Sonda do hook num projeto de teste (`/root/.forge-contrib/wt/sonda-5779.sh`, saída em `sonda-5779.txt`)
| Caso | Resultado |
|---|---|
| config `{}` | rc 0, nada roda |
| comando `false` | rc 1, mensagem "saiu 1" |
| prazo `0120` | rc 1, "precisa ser um inteiro", comando não rodou |
| prazo ` 5` (espaço) | rc 1, barrado |
| prazo `99` | rc 0, comando rodou |
| chave só com espaços | rc 0, nada roda |
| config `["x"]` (raiz não objeto) | rc 0 com aviso de config ilegível |
| comando `pwd; touch M` | roda da raiz do projeto, rc 0 |
| config que é link | rc 0, comando não rodou |

Nenhum defeito encontrado. Sem bug aberto em `docs/qa/bugs/`.

## Revalidação no head 60be3dff (E57.87, escopo incremental)
Delta lido por `forge-check parecer delta` (146b4050..60be3dff): `9>&-` nas duas chamadas do comando de registros no `pre-push` do modelo, o teste espelho `test_trava_nao_passa_para_os_registros` (com e sem `timeout`), os mutantes M10 e M11 e o fragmento do changelog. Nada do 1º parecer mudou de resultado; o A1 recomendado segue como estava.

### Vermelho (`bin/forge-testes --vermelho 8ee73d15 --modulos test_prepush_so_docs`, rc=0)
```
vermelho: base=8ee73d156db5 head=60be3dffce7a módulos=test_prepush_so_docs (restrito por --modulos)
tests.test_prepush_so_docs.TravaDaChecagem.test_trava_nao_passa_para_os_registros · H=ok · B=falha · prova (asserção)
contagem: não prova (passa na base)=58; prova (asserção)=7; pulado=9
```
O 7º que prova é o espelho novo; nenhum cai no HEAD.

### Mutantes (`bin/forge-mutante tests/mutantes/v0479-pv-d3-modelo.json tests/mutantes/v0479-pv-d3-modelo-2.json`, rc=0)
```
forge-mutante: pedido=v0479-pv-d3-modelo rev=60be3dffce7a spec=29ba446a... spec=44c4f540...
M1..M9 · morreu
M10 · morreu · templates/projeto/.githooks/pre-push:347
M11 · morreu · templates/projeto/.githooks/pre-push:349
```
Onze de onze mortos. As duas linhas de guarda mudadas (`9>&-` com e sem `timeout`) têm um mutante cada. Parecer segue aprovado.
