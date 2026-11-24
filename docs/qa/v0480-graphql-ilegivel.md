---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 5b04ce1ee7b0c85e591ea6ffb88816983e618dc3
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E168.15 (PR #854, delta 933539c5..5b04ce1e)

Obrigação testada: a chave antes do subcomando do `gh`, nele ou no endpoint recusa na dúvida (A7 da segurança, commit 5b04ce1e, E168.13; `R-CONFORMIDADE`, `R-MAIN`): `{api,graphql}`, `{-t,pr} api`, `-R {o/r,api} graphql`, `api {graphq,-Hx:}l`. Os marcadores `{owner}`, `{repo}`, `{branch}` e a chave sem vírgula seguem livres. Os pareceres anteriores (933539c5 e antes) valem para o que o delta não tocou.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Chave no valor de opção, no subcomando, no endpoint e em `graph{q..q}l` recusa | `test_gh_incerto_chave` (6 incertos), fixtures `trava-gh-chave-{antes,endpoint,endpoint-literal,subcomando,subcomando-opcao,subcomando-vazio}-bloqueia`, `parecer/v0480-gh-chave-{antes,endpoint,subcomando}-bloqueia` | `..` e `,`; subcomando vazio | passou |
| Marcador do gh, chave sem vírgula, chave em argumento depois do subcomando liberam | `test_gh_incerto_chave` (6 certos), `trava-gh-chave-marcador-libera` | `{owner}/{repo}`, `query{viewer{login,name}}`, `-H "Accept: {a,b}"` | passou |
| `CHAVES` numa fonte só (parecer) | mutantes GQ49 a GQ55; `test_expansao_por_palavra_chaves` segue verde | n/a | passou |

## Cenários e resultado real
Local, só os testes dos arquivos tocados; a suíte inteira fica para o check-run `bateria` do CI do PR.

Vermelho antes do verde. O `--vermelho` do módulo `test_hooks` inteiro estoura o prazo nesta máquina (sem veredito, como no parecer anterior), então a prova substituta foi à mão: cópia do head em `$TMPDIR` com `hooks/parecer.py` e `hooks/conformidade.py` de 5b0a3431 (antes do commit), `-k test_gh_incerto_chave -k test_fixtures_do_repo_publico`:
```
AssertionError: False is not true : ('gh', '-R', '{o/r,api}', 'graphql')
Ran 2 tests in 14.692s
FAILED (failures=10)
```
No head: `-k test_gh_incerto -k test_expansao_por_palavra_chaves -k test_analisar_pula` deu `Ran 4 tests in 4.359s · OK`.

Mutação. `bin/forge-mutante tests/mutantes/v0480-graphql-ilegivel-6.json tests/mutantes/v0480-graphql-ilegivel-9.json --processos 2` no head:
```
forge-mutante: pedido=v0480-graphql-ilegivel rev=5b04ce1ee7b0 spec=1bcf92b3… spec=99d3a1e1…
GQ28 a GQ35 · morreu (parecer.py 430, 425, 521, 463, 463, 468, 470, 617)
GQ49 · morreu · parecer.py:430   GQ50 · morreu · parecer.py:431   GQ51 · morreu · parecer.py:431
GQ52 · morreu · parecer.py:429   GQ53 · morreu · parecer.py:402   GQ54 · morreu · parecer.py:395
GQ55 · morreu · parecer.py:431
```
GQ49 a GQ55 morreram, nenhum sobrevivente nem equivalente.

Cobertura. `forge-mutante --cobertura --base 933539c5d2b6`: as condições mudadas em `hooks/parecer.py` (429, 430) saem `coberta` (GQ52; GQ28, GQ49, GQ50, GQ51, GQ55); `apagada` é linha removida da base. O único `não coberto` (`tests/pesos-d4.json`, rc 1) vem do merge da develop, fora do pedido. A troca em `conformidade.py:344` (`CHAVES = parecer.CHAVES`) é atribuição sem condição.

Não rodei sondas novas: fixtures e mutantes do autor cobrem as formas do delta.
