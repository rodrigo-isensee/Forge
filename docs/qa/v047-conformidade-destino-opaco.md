---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 85043cc4008c8d1395412674e3aef71d77c2153e
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
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

## Revalidação por delta e8c459de..e25f079b (E1.281)
Domínio lido por `forge-check parecer delta`: `hooks/conformidade.py`, `docs/hooks.md`, `docs/hooks-fixtures.md`, fixtures `opaco-u4-*` e `opaco-semresto-u3-*`, `tests/test_hook_destino_opaco.py`, `tests/test_conformidade_opaco.py` e os mutantes O83 a O98 (specs `v047-destino-opaco-9` a `-15`). Mudança: U4 (lista positiva do valor calculado: palavras do corpo por regex, crase depois do `of=` do dd). Escopo do plano inalterado (A9, A10, D2b); o delta soma o U4 como obrigação (A1 da segurança E1.206, A1 do review E1.205).
- Oráculo: prova de não edição refeita (ancestral ok; blob `535134e9…` igual; `git log 730843a9..HEAD -- tests/test_oraculo_v047.py` vazio); `python3 -m unittest tests.test_oraculo_v047`: 3 testes, OK.
- Vermelho: `bin/forge-testes --vermelho e8c459de79e98bd22a65892b4605c97a7583de58 --modulos test_oraculo_v047,test_conformidade_opaco,test_hook_destino_opaco --prazo 1500`, saída 0: `vermelho: base=e8c459de79e9 head=e25f079b9834`, `revertidos à base: docs/hooks-fixtures.md, docs/hooks.md, …, hooks/conformidade.py`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`, `test_fixtures_opaco_sem_resto` e `test_hook_concorda_com_o_bash` também provam; `contagem: não prova (passa na base)=6; prova (asserção)=3` (regressão e guardas de orçamento, esperado).
- Mutação do delta: `bin/forge-mutante --processos 4 --base e8c459de79e98bd22a65892b4605c97a7583de58 tests/mutantes/v047-destino-opaco*.json`, cabeçalho `base=e8c459de79e9… mb=e8c459de79e9… rev=e25f079b9834`: 94 `morreu`, 1 `sobreviveu`: `O18 · sobreviveu · hooks/conformidade.py:1329`, rc=1. O mutante passava no e8c459de (49 de 49); o U4 do delta passou a recusar antes dele. Reproduzido à mão numa cópia: `test_fixtures_opaco_sem_resto` e `test_fixtures_opaco_u4` seguem OK com o mutante. A descrição da fixture `opaco-semresto-u3-variavel-duas-vezes-bloqueia` já diz que o U4 recusa antes do U3. Probável equivalente, mas o autor não o declarou (A1).
- Cobertura: `bin/forge-mutante --cobertura --base f4b0c2aeb42b…` rc=0, todas as condições `coberta`; 4 `isenta` com motivo lido (443, 586, 1316, 1330): aceitas, equivalentes pela seção 7 da ADR 0009 ou pelo U2.
- Fronteiras novas do U4 protegidas: crase partida no `of=` do dd (bloqueia e libera), `printf` com e sem `%s`, função recursiva ou redefinida, variável duas vezes ou do `read`, teto de 64 valores, `$(` sem par.
- CI: sem PR e sem check-run `bateria` para este sha (pedido sem PR por ordem do brief); suíte inteira fica para o CI do PR. Não cito `.verde` local.

## Revalidação por delta e25f079b..85043cc4 (E1.305)
Domínio lido por `forge-check parecer delta`: `hooks/conformidade.py`, `docs/hooks.md`, `docs/hooks-fixtures.md`, 20 fixtures `opaco-u4-*` e `opaco-semresto-u3-*`, `tests/test_hook_destino_opaco.py` (contagens 60 e 73) e as specs de mutantes `-7`, `-9` e `-16` (O99 a O104; O45 e O55 realinhados à assinatura nova). Mudança: `na_lista_positiva(corpo, linha)` recusa o comando que a linha redefine como função (U4, U3 e `$(pwd)`); `VARIAVEIS_DO_BASH` devolve None; O18 morto por fixture. O escopo do plano (A9, A10, D2b, U4) não mudou.
- Oráculo: prova de não edição refeita (commit 730843a9 ancestral; blob 535134e9 igual; log vazio); `python3 -m unittest tests.test_oraculo_v047`: 3 testes, OK, 29,8 s.
- Vermelho: `bin/forge-testes --vermelho e25f079b9834ba470ac8ccda65e5ad678a426aaa --modulos test_oraculo_v047,test_conformidade_opaco,test_hook_destino_opaco --prazo 1500`, rc=0: `vermelho: base=e25f079b9834 head=85043cc4008c`; `test_fixtures_opaco_u4 · H=ok · B=falha · prova (asserção)`; `contagem: não prova (passa na base)=8; prova (asserção)=1`. O `opaco_sem_resto` não prova na base: as contagens e a fixture do O18 só passam no HEAD, mas o O18 tem mutante que a cobre (abaixo); o resto é regressão.
- Mutação do delta: `bin/forge-mutante --processos 4 --base e25f079b9834ba470ac8ccda65e5ad678a426aaa tests/mutantes/v047-destino-opaco*.json`, cabeçalho `base=e25f079b9834… mb=e25f079b9834… rev=85043cc4008c`, 16 specs; nenhuma linha `sobreviveu` nem `sem veredito` (só `morreu`), incluindo O18 e O99 a O104.
- Cobertura: `bin/forge-mutante --cobertura --base f4b0c2aeb42b…` rc=0, `rev=85043cc4008c`; todas as condições `coberta` (as 3 novas: redefinição por função, `VARIAVEIS_DO_BASH`, guarda do `pwd`); 4 `isenta` com motivo lido (443, 596, 1326, 1340), aceitas como no parecer anterior.
- Fronteiras novas protegidas: `date`, `mktemp`, `pwd`, `true` redefinidos por função (bloqueia) e `date` redefinido com saída literal (libera); `REPLY`, `MAPFILE`, `BASH_REMATCH`, `OPTARG`, `OLDPWD` recusam; `HOME` e variável definida na linha liberam.
- CI: sem PR nem check-run `bateria` para este sha (pedido sem PR por ordem do brief); suíte inteira fica para o CI do PR. Não cito `.verde` local.

Parecer aprovado: nenhum achado aberto; o A1 da rodada anterior (mutante O18) morreu no 85043cc4 pela fixture `opaco-semresto-u3-mv-target-duas-vezes-bloqueia`; A1 resolvido, sem mutante sobrevivente, sem bug de produto (nada em `docs/qa/bugs/`).
