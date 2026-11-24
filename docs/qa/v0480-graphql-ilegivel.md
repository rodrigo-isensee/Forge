---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 933539c5d2b6083c6112425624040e63a9bdcedd
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E168.11 (PR #854, delta 7afc147a..933539c5)

Obrigação testada: fechar o A1 do QA anterior (as chamadas de `ordem_do_gh` sem mutante) e as mudanças da 2ª volta (commit 6042b096, E168.9): `gh_incerto` recusa na dúvida do subcomando nos dois hooks, `analisar` pula a opção com valor entre `pr` e o subcomando, chave com `,` ou `..` fora de aspas recusa na consulta GraphQL (`R-CONFORMIDADE`, `R-MAIN`). O parecer anterior (7afc147a) segue valendo para o que o delta não tocou. O merge da develop (933539c5) não toca o domínio do QA.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 fechado: cada `ordem_do_gh` tem teste que a mata (`gh_rotulo`, `gh`, `alias_do_gh`, `analisar`) | mutantes GQ35, GQ36, GQ37 + `test_alias_do_gh_com_opcao_antes_do_nome`, fixtures `rotulo-so-dono-*-opcao-antes-outra-conta`, `trava-gh-opcao-antes-api-no-forge` | chamada trocada por identidade | passou (todos morreram) |
| Dúvida do subcomando recusa (expansão antes; `api`/`pr` como valor de opção) | `test_gh_incerto` (5 incertos, 7 certos), fixtures `trava-gh-duvida-*` (3), `rotulo-so-dono-duvida-outra-conta`, `parecer/v0480-gh-duvida-valor-api-merge` | `--help api`, `-X PUT api $E` e `pr merge -b api` seguem certos; `gh` vazio | passou |
| Opção entre `pr` e o subcomando é pulada como o gh pula | `test_analisar_pula_a_opcao_entre_pr_e_o_subcomando`, fixture `trava-gh-opcao-valor-antes-pr-merge-…-bloqueia` | `--` para; `-Ro/r`; `--repo=` | passou |
| Chave fora de aspas com `,` ou `..` recusa; entre aspas, escapada ou sem vírgula libera | `test_expansao_por_palavra_chaves` (11 casos), `trava-graphql-chaves-{bloqueia,sequencia-bloqueia,entre-aspas-libera}` | `'{a,b}'`, `\{a,b}`, `{a.b}`, `{` com espaço | passou |
| Consulta GraphQL ilegível recusa também sem campo à vista | mutante GQ45 (conformidade.py:3785) | método não mutante + endpoint graphql | passou |
| Fixtures da sessão do Forge e a de prazo com campos entre aspas | `trava-graphql-stdin-{input,proc}-sessao-do-forge-bloqueia`, `trava-graphql-comentario-grande-prazo-libera` | prazo do hook | passou |

## Cenários e resultado real
Local, só o que o diff toca (sem suíte; a bateria fica para o check-run `bateria` do CI do PR).

Vermelho antes do verde. `forge-testes --vermelho 7afc147aec89b1efe69e77e63f9e0cc303c42f53 --modulos tests.test_hooks --prazo 1200`, duas vezes (prazo padrão de 600 s e depois 1200 s):
```
vermelho: base=7afc147aec89 head=933539c5d2b6 módulos=test_hooks (restrito por --modulos)
test_hooks · sem veredito (prazo, sinal ou executor sem registro em H,B)
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.
rc=2   # H 1200.0 s, B 1200.0 s: o módulo test_hooks inteiro estoura o prazo nesta máquina
```
O `--vermelho` não deu veredito (o módulo inteiro não cabe no prazo; `-k` não combina com ele), então não conta como vermelho. Prova substituta, à mão: cópia do head em `$TMPDIR` com `hooks/conformidade.py` e `hooks/parecer.py` de 7afc147a, `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_gh_incerto -k test_analisar_pula -k test_expansao_por_palavra_chaves -k test_alias_do_gh_com_opcao -k test_ordem_do_gh -k test_fixtures_do_repo_publico`:
```
Ran 6 tests in 23.843s
FAILED (failures=12, errors=1)   # test_gh_incerto (erro), test_analisar_pula…, test_expansao_por_palavra_chaves, test_ordem_do_gh e 9 fixtures novas de recusa em test_fixtures_do_repo_publico
```
`test_alias_do_gh_com_opcao_antes_do_nome` passa na base de propósito: guarda a chamada que já existia (é o teste que mata GQ35). No head, os 5 testes unitários: `Ran 5 tests … OK`.

Mutação. `bin/forge-mutante tests/mutantes/v0480-graphql-ilegivel-6.json tests/mutantes/v0480-graphql-ilegivel-7.json tests/mutantes/v0480-graphql-ilegivel-8.json --processos 2` no head:
```
forge-mutante: pedido=v0480-graphql-ilegivel rev=933539c5d2b6 spec=5df06c96… spec=374a289f… spec=02909570…
GQ28 a GQ48 · morreu (21 de 21)
rc=0
```
Cada linha saiu `morreu`, nenhum sobrevivente nem equivalente: GQ28 a GQ35 em parecer.py (416, 414, 506, 448 ×2, 453, 455, 602), GQ36 a GQ39 em conformidade.py (3745, 3345, 3347, 3747), GQ40 a GQ43, GQ46 e GQ47 (363, 372, 385, 386), GQ44 (3504), GQ45 (3785), GQ48 (parecer.py:398).

Cobertura. `forge-mutante --cobertura --base 7afc147aec89b1efe69e77e63f9e0cc303c42f53`: toda condição mudada em `hooks/` sai `coberta` (conformidade.py 363, 372, 386, 3345, 3504, 3745, 3785; parecer.py 398, 406, 414, 416, 448, 453, 455, 506); as `apagada` são linhas removidas da base; `não coberto: bin/forge-fechar` vem do merge da develop, fora do pedido. As chamadas de `ordem_do_gh` que o A1 apontou têm mutante (GQ35 a GQ37), e o A1 está fechado.

Não rodei sondas novas: as fixtures e os mutantes do autor cobrem as formas do delta.
