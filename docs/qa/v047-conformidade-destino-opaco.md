---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: e8c459de79e98bd22a65892b4605c97a7583de58
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 conformidade, destino opaco sem resto (A9, A10)

Lote B, classe C, `hooks/conformidade.py` (R-CONFORMIDADE), intervalo `origin/develop..e8c459de`. Não há especificação de UX: as obrigações são o oráculo `tests/test_oraculo_v047.py` (casos A9, A10 e os 9 desvios D2b da E1.170) e as fixtures e mutantes do autor. Sem tela, sem acessibilidade.

oraculo: tests/test_oraculo_v047.py commit 730843a99366f49e7560b32dbd413c15346f8614 blob 535134e940b2af9a3cf9941b7a4d54b661b57c4a

Prova de não edição do oráculo (conferida): `git merge-base --is-ancestor 730843a9 HEAD` ok; `git rev-parse HEAD:tests/test_oraculo_v047.py` = `535134e940b2af9a3cf9941b7a4d54b661b57c4a` (igual ao blob); `git log --format=%H 730843a9..HEAD -- tests/test_oraculo_v047.py` vazio. Rodou `python3 -m unittest tests.test_oraculo_v047`: 3 testes, OK, 178 s (os 9 casos D2b e os `plano` da A10 recusados; leituras legítimas liberam).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A9: destino opaco sem resto cai no `.git` pela regra única | `OraculoV047DestinoOpaco.test_hook_concorda_com_o_bash`; `test_conformidade_opaco.test_hook_concorda_com_o_bash`; fixtures `opaco-semresto-*` | destino vazio, curinga, variável, substituição; teto de execuções | passou; vermelho na base |
| A10: operador colado no rev-parse recusa e a liberação de link não se alarga | oráculo (casos `plano`); fixtures `opaco-colado-*` (`;`, `&&`, `\|`, `eval`, `sh -c`, ANSI-C, aninhado) | corpo de 1 comando libera, de 2 recusa | passou; vermelho na base |
| D2b: aspas, concatenação, `${var}` e função (9 casos) | oráculo; `test_hook_destino_opaco.test_fixtures_opaco_d2b`; `opaco-d2b-*` | variável sozinha e sufixo liberam, vazia e duas variáveis recusam | passou; vermelho na base |
| Leituras legítimas continuam liberadas | `OraculoV047DestinoOpaco.test_leituras_legitimas_liberam`; fixtures `*-libera.json` | cat, date, mktemp, mv fora do `.git` | passou (não prova na base, é regressão, esperado) |
| Orçamento do oráculo (até 150 execuções, 10 com prazo de produção) | `test_orcamento_e_cobertura`; `test_gerador_cobre_as_dimensoes_dentro_do_orcamento` | teto de execuções | passou (não prova na base, é guarda) |

## Cenários e resultado real
- Vermelho antes do verde, `bin/forge-testes --vermelho f4b0c2aeb42b2c08d0d9a1386e77939504b790e8 --modulos test_oraculo_v047,test_conformidade_opaco,test_hook_destino_opaco --prazo 1500`, saída 0: `vermelho: base=f4b0c2aeb42b head=e8c459de79e9 ... revertidos à base: bin/forge-testes, changelog.d/v047-conformidade-destino-opaco.md, docs/hooks-fixtures.md, docs/hooks.md, hooks/conformidade.py`; `contagem: não prova (passa na base)=3; prova (asserção)=5`. Os 3 que passam na base são regressão de liberação e guardas de orçamento. A rodada de suíte completa (sem `--modulos`) estourou o meu prazo de espera sob carga 20 a 30 e não vale como veredito; vale a restrita.
- Mutação: `bin/forge-mutante --processos 4 tests/mutantes/v047-destino-opaco*.json` (8 specs, 49 mutantes): 49 `morreu`, nenhum sobrevivente, rc=0. Cabeçalho `forge-mutante: pedido=v047 rev=e8c459de79e9 ...`.
- Cobertura de guardas: `bin/forge-mutante --cobertura --base f4b0c2aeb42b2c08d0d9a1386e77939504b790e8` rc=0, `base=f4b0c2aeb42b... mb=... rev=e8c459de...`; todas as condições mudadas `coberta`, 3 `isenta` com motivo lido (equivalentes pela seção 7 da ADR 0009 ou nome opaco da C18): aceitas.
- Diff conferido: o `test_testes_tocados` e o mapa de `bin/forge-testes` incluem os 2 módulos novos e descontam oráculos nas listas exatas (83); coerente com o oráculo ser incluído em todo plano dirigido.
- CI: `gh` não achou PR nem check-run `bateria` para `e8c459de` (pedido sem PR por ordem do brief); a suíte inteira fica para o CI do PR. Não cito `.verde` local.
