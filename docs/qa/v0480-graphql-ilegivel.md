---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-graphql-ilegivel
commit: 433c3782d067b58ac85f481f6bd13c085f9704e7
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E168.3 (PR #854, consulta GraphQL que o hook não lê)

Obrigação testada: E168.1 (`GRAPHQL-CONSULTA-EM-VARIAVEL`, `R-CONFORMIDADE`). `gh api graphql` com consulta que o hook não lê recusa em todo papel, também na sessão do Forge; a consulta literal e o valor entre aspas de outro campo ou opção seguem livres.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E168.1 expansão fora de aspas (`$Q`, `$(…)`, crase) em qualquer argumento recusa | fixtures `trava-graphql-consulta-variavel-nua`, `-valor-nu`, `-substituicao`, `-crase`, `-argumento-solto` (via `test_fixtures_do_repo_publico`) | palavra dividida pelo bash | passou |
| E168.1 entre aspas duplas: recusa no campo `query`, no nome de campo e no endpoint | `-variavel-aspas`, `-chave-variavel`, `-endpoint-crase` | chave `query` em qualquer caixa, chave com expansão | passou |
| E168.1 também na sessão do Forge | `-sessao-do-forge-bloqueia` | papel/sessão | passou |
| E168.1 consulta literal e valor entre aspas de outro campo ou opção liberam | `-aspas-duplas-libera`, `-cabecalho-libera`, `-escape-libera`, `-formas-libera`, `-mutacao-legivel-libera`, `-sessao-do-forge-libera`, `trava-gh-leitura-graphql-variavel-libera` (ajustada) | `\$` escapado, aspas simples, `-H`, `--jq`, `-F n="$N"` | passou |
| Orçamento de CPU do hook não piora | `test_hooks -k orcamento` (3 testes) | linha adversária, 3000 heredocs | passou, 0,94 s de CPU no pior caso (limite 3 s) |

## Cenários e resultado real
Local, só o que o diff toca: `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_fixtures_do_repo_publico` OK no head (11 s, 98 fixtures do item). A suíte inteira fica para o check-run `bateria` do CI do PR.

Vermelho antes do verde. `bin/forge-testes --vermelho 95b0978567ae…` sem `--modulos` abriu 116 módulos (teto de 139200 s) e foi interrompido; com `--modulos test_hooks` estourou meu prazo de 580 s (rc 124, sem veredito, não vale como vermelho). Recuo equivalente: cópia do head em `$TMPDIR` com só `hooks/conformidade.py` da base, mesmo comando acima. Resultado: `FAILED (failures=9)`, exatamente as 9 fixtures de recusa (`argumento-solto`, `chave-variavel`, `crase`, `endpoint-crase`, `sessao-do-forge`, `substituicao`, `valor-nu`, `variavel-aspas`, `variavel-nua`), todas `0 != 2`. No head: `OK`.

Mutação, `forge-mutante --cobertura --base 95b0978567ae…`: toda condição Python mudada tem mutante declarado (`coberta`, linhas 360-375, 3481-3496, 3765; sem `não coberto`). Rodada dos 3 specs (`--processos 2`), 24 mutantes:
```
forge-mutante: pedido=v0480-graphql-ilegivel rev=433c3782d067 spec=dae61075… spec=f54ecd1e… spec=f64fee6b…
GQ1 a GQ24 · morreu (24 de 24; nenhum sobrevivente, nenhum equivalente, nenhum sem veredito)
rc=0
```

Sondagem de abuso (fora das fixtures do autor, em cópia descartável; a cópia foi apagada): 18 formas, entre elas `-f query=$Q`, `-f 'query'="$Q"`, `--field=query="$Q"`, `-X POST` antes do endpoint, `Query` maiúsculo, `$'…'`, `${Q}` com atribuição, `-- "$Q"`, chave por variável e endpoint `"$EP"`, `graphql$X`. Todas as formas que o hook não lê recusam (a regra nova ou R-CONTRIB, pelo endpoint com variável); as que devem liberar (`--jq ".. $F"`, `-f "n=$N"`, `-f v='$Q'`) liberam. Sem bypass encontrado.

Atenção ao revisor: o parecer de segurança do mesmo head (021ec802) está reprovado; os achados dele ficam no domínio dele e não os revalidei aqui.
