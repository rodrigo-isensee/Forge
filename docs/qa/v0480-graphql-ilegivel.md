---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 7afc147aec89b1efe69e77e63f9e0cc303c42f53
parecer: reprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E168.7 (PR #854, delta 433c3782..7afc147a)

Obrigação testada: E168.5 (A1, A2 e A3 da segurança do #854): `gh` com opção antes do subcomando, entrada padrão por caminho e arquivo que não é regular, curinga fora de aspas num `gh api graphql` (`R-CONFORMIDADE`, `R-MAIN`). O parecer anterior (433c3782, aprovado) segue valendo para o que o delta não tocou.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 opção antes do subcomando passa pelas travas (`-X PUT api`, `-R o/r pr merge`, alias, opção longa, opção sem valor) | fixtures `trava-gh-opcao-antes-{alias,graphql,merge-rest,mutacao-literal}-bloqueia`, `trava-gh-opcao-longa-antes-bloqueia`, `trava-gh-opcao-sem-valor-antes-bloqueia`, `trava-gh-repo-antes-pr-merge-admin-bloqueia`; `test_ordem_do_gh` | `--` encerra; opção de 2 letras leva valor; `api`/`pr` como valor | passou |
| A1 leitura com opção antes libera | `trava-gh-opcao-antes-leitura-libera` | falso positivo | passou |
| A2 `/dev/stdin`, `/proc/self/fd/0` e FIFO são consulta ilegível | `trava-graphql-stdin-caminho-bloqueia`, `-stdin-input-…`, `-stdin-proc-…` (sessão do Forge); `test_graphql_arquivo_que_nao_e_regular_e_ilegivel` | não regular; `/dev` e `/proc` | passou |
| A3 curinga fora de aspas recusa; entre aspas libera | `trava-graphql-curinga-bloqueia`, `-curinga-colado-bloqueia`, `-curinga-entre-aspas-libera` | `[ID!]` entre aspas | passou |
| Orçamento de CPU do hook | `test_hooks -k orcamento` (3 testes) | linha adversária, 3000 heredocs | passou: pior caso 1,03 s de CPU (limite 3 s) |

## Cenários e resultado real
Local, só o que o diff toca (sem suíte; a bateria fica para o check-run `bateria` do CI do PR).

Vermelho antes do verde. Cópia do head em `$TMPDIR` com `hooks/conformidade.py` e `hooks/parecer.py` de 433c3782; `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_fixtures_do_repo_publico`:
```
FAILED (failures=11)   # as 11 fixtures novas de recusa, nenhuma de libera
```
A 12ª (`trava-gh-repo-antes-pr-merge-admin-bloqueia`) passa na base: `gh -R … pr merge --admin` já recusava por outra trava (a fixture guarda a regressão, não prova a correção). No head: `Ran 1 test … OK`.

Mutação. `bin/forge-mutante tests/mutantes/v0480-graphql-ilegivel-4.json tests/mutantes/v0480-graphql-ilegivel-5.json --processos 2` no head:
```
forge-mutante: pedido=v0480-graphql-ilegivel rev=7afc147aec89 spec=746b3ce1… spec=7c1e7dff…
GQ17 a GQ27 · morreu (11 de 11; GQ21 por erro do teste declarado sob o mutante, com controle verde)
rc=0
```
`forge-mutante --cobertura --base 433c3782` lista como `coberta` as condições mudadas (conformidade.py 369, 3214, 3217, 3496; parecer.py 398 a 406). A cobertura só olha condição; as quatro linhas que passam a chamar `ordem_do_gh` não são condição e ficaram sem mutante (A1).

Mutação à mão nessas quatro chamadas (cópia descartável do head, o conserto trocado por identidade):

| Linha | Mutação | Fixtures do item | Testes `-k gh -k alias -k graphql -k ordem_do` |
|---|---|---|---|
| parecer.py `analisar` | `ordem_do_gh(sem)` → `sem` | morreu (6 fixtures) | n/a |
| conformidade.py ~3339 (`gh_rotulo`) | sem `ordem_do_gh` | sobreviveu | sobreviveu (11 testes) |
| conformidade.py ~3737 (`gh`) | sem `ordem_do_gh` | sobreviveu | sobreviveu (11 testes) |
| parecer.py `alias_do_gh` | sem `ordem_do_gh` | sobreviveu | sobreviveu (11 testes) |

Sonda extra no rótulo (`gh -R o/r pr edit 1 --add-label afrouxa-regra`, na sessão de outro projeto): recusa no head e nos três mutantes, ou seja, outra trava já cobre essa forma, e nenhum teste distingue a chamada nova. Não rodei a suíte inteira nos mutantes (módulo inteiro estoura meu prazo); os 3 sobreviventes valem contra as fixtures e esses 11 testes.

## Achados
- A1 (bloqueante) hooks/conformidade.py:3339 · `ordem_do_gh` chamada em gh_rotulo, gh (conformidade.py) e alias_do_gh (parecer.py): sem mutante, e trocada por identidade nada cai. Falta teste ou a linha é redundante: declare mutante com teste que o mate, ou equivalente justificado.
