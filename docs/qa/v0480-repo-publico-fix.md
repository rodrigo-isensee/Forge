---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: 2806ca57ea41a48ea3e5ecaf1bda785b3f8c8dcb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0478 · E141.5 · PR #829 (CONFORMIDADE-REPO-CREATE-PUBLICO)

Obrigações: A1 (`gh repo create` só com visibilidade privada explícita) e A2 (`gh api` REST e GraphQL que cria ou edita repositório sem privado explícito; valor ilegível falha fechado), de `docs/security/v0480-repo-publico-diag.md`. Diff 216413c9..2806ca57: `hooks/conformidade.py` (+44), 23 fixtures, `tests/test_hooks.py` (+7), 2 specs de mutantes, doc e changelog.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1: `repo create` sem `--private`/`--internal`, ou com `--public`, bloqueia | fixtures `trava-repo-create-*` (public, sem-visibilidade, public-clone, source-push, template-public, source-igual, private-e-public) via `test_fixtures_do_repo_publico` | opção com valor (`-s`, `-p`) não confundida com bandeira; `--public` junto de `--private` | passou |
| A1: `--private` e `--internal` liberam | `trava-repo-create-private-libera`, `-internal-libera` | caminho feliz, sem falso positivo | passou |
| A2 REST: criar (`user/repos`, `orgs/<o>/repos`, `generate`) sem `private=true`/`visibility=private\|internal` bloqueia | `trava-api-criar-*-sem-campo-bloqueia` | campo ausente | passou |
| A2 REST: criar com privado libera; PATCH de descrição libera | `trava-api-criar-*-private-libera`, `trava-api-patch-descricao-libera` | sem falso positivo na edição | passou |
| A2: `campo=@arq` e variável lidos; ilegível falha fechado | `trava-api-private-de-arquivo-*`, `trava-api-visibility-de-arquivo-bloqueia`, `trava-api-private-de-variavel-bloqueia` | valor que o hook não lê | passou |
| A2 GraphQL: criar sem `PRIVATE`/`INTERNAL` literal, `$v`, ou update com visibilidade não privada bloqueia; criar privado e update sem visibilidade liberam | `trava-graphql-*` (5) | variável, ausência, update neutro | passou |
| Orçamento de instrução não estoura | `tests.test_orcamento_instrucao` | limite de tamanho | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_repo_publico tests.test_orcamento_instrucao` no head, da raiz, sem `-I`: `Ran 9 tests ... OK`.
- Vermelho antes do verde. `forge-testes --vermelho 216413c9 --modulos test_hooks`: `test_hooks H 600.0 s, B 600.0 s; 1201 s no total`, `base=216413c917b8 head=2806ca57ea41`, reverteu à base `changelog.d/...`, `docs/hooks-fixtures.md`, `hooks/conformidade.py`; `test_hooks · sem veredito (prazo, sinal ou executor sem registro em H,B)`, `sem veredito=1`. O módulo inteiro estoura o prazo de 600 s por cópia (o mesmo vale para a intermitência de `pesado/mesma-sessao-libera`, que é da develop e não deste item), então a ferramenta não deu veredito. Prova manual equivalente: cópia do head com só `hooks/conformidade.py` da base, `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_repo_publico` → `AssertionError: 0 != 2`, `FAILED (failures=15)`. Os 15 casos de bloqueio caem na base; o teste prova.
- Mutação. `forge-mutante --base 216413c9 tests/mutantes/v0480-repo-publico-fix.json tests/mutantes/v0480-repo-publico-fix-2.json --processos 2`: cabeçalho `base=216413c917b81b185dcc2db857e32b708a1c7515 mb=216413c9... rev=2806ca57ea41a48ea3e5ecaf1bda785b3f8c8dcb`, `todos os mutantes entram`; RP1 a RP16 `morreu`, nenhum sobrevivente.
- Cobertura. `forge-mutante --cobertura --base 216413c9`, rc 0: toda condição mudada em `hooks/conformidade.py` (linhas 3392 a 3429) tem mutante declarado e provado; nenhuma `não coberto`.
- Sem suíte local; a suíte inteira é do CI do PR.

## Limites
O vermelho pela ferramenta fica sem veredito por prazo do módulo (`test_hooks` grande); a prova manual acima cobre o teste novo. Não é defeito do item.
