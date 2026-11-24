---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-fix
commit: 708c4bb09a6c74716b6897d37a2319575ae591b3
parecer: aprovado
escopo: incremental
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

## Delta E141.10: volta 2806ca57..1265fa11
Escopo: `repo new` como alias, REST decidido pelo nome do campo (colado, `=`, `--input`), GraphQL por `visibility` do input, endpoint com segmento vazio ou de ponto. `forge-check parecer delta` lista `hooks/conformidade.py`, `docs/hooks-fixtures.md`, o changelog e as fixtures novas; o plano (CA-n) não mudou.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `repo new` público ou sem visibilidade bloqueia | `trava-repo-new-*` | alias de `create` | passou |
| REST: campo decide (`-Fprivate=false`, `-fvisibility=public`, `--input`, maiúscula, `private=true` em outro campo) | `trava-api-criar-*`, `trava-api-patch-*` | campo colado, em outro campo, isca no input | passou |
| GraphQL: visibility do input, `<var>[visibility]`; descrição com a palavra não bloqueia | `trava-graphql-*` | string, ilegível falha fechado | passou |
| Endpoint com `//` ou `.` bloqueia | `trava-api-criar-endpoint-*` | segmento vazio e de ponto | passou |

- Fixtures novas: 34 no intervalo. `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_repo_publico` no head: OK. Vermelho: cópia do head com `hooks/conformidade.py` de 2806ca57, mesmo teste: `FAILED (failures=21)`, `AssertionError: 0 != 2`; as 21 que falham são todas do conjunto das 34 novas (o commit diz 18; a conta real é 21; as outras 13 são `libera` ou já bloqueadas na base). O teste prova.
- Mutação. `forge-mutante --base 216413c9` com as 6 specs `v0480-repo-publico-fix{,-2..-6}.json`, `--processos 3`, rc 0: cabeçalho `base=216413c917b81b185dcc2db857e32b708a1c7515 ... rev=1265fa11ec5e`; RP1 a RP46 `morreu`, 46 de 46, nenhum sobrevivente.
- Cobertura. `forge-mutante --cobertura --base 216413c9`, rc 0: nenhuma linha `não coberto`.
- Orçamento de CPU do hook: `test_muitos_heredocs_recusam_dentro_do_orcamento`, `test_linha_adversaria_de_crases_e_pastas_recusa_dentro_do_orcamento`, `test_tirar_heredocs_em_tempo_linear`, `test_orcamento_sai_numa_linha_de_formato_fixo` e o das fixtures: `Ran 5 tests in 19.3s, OK`; pior caso `HEREDOC-DONOS python3 - a{i} x3000: 0.88 s de CPU (limite 3 s)`.
- Fora do meu domínio: review (5f86c9a0) e segurança (1d160afd) reprovam o mesmo head por léxico do GraphQL (comentário); a volta é do autor. Não reabro; o QA do delta seguinte reconfere.
- Sem suíte local; a suíte inteira é do CI do PR.

## Delta E141.14: volta 1265fa11..708c4bb0
Escopo: léxico do GraphQL pela especificação (bloco `"""`, comentário até LF ou CR), falha fechada com CR, BOM e controle, `<var>[visibility]` só vale se a consulta usa a variável. `forge-check parecer delta` lista `hooks/conformidade.py`, 8 fixtures, `tests/test_hooks.py` (mínimo do lote 57 para 65), specs de mutantes 4, 6 e 7, índice e changelog; o plano (CA-n) não mudou.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Bloco `"""` só escapa `\"""`; `private` dentro do bloco com escape não libera | `trava-graphql-bloco-escape-bloqueia`, `-private-libera` | fim de bloco por escape | passou |
| Comentário fecha em LF ou CR; CR (também em arquivo) falha fechado | `trava-graphql-comentario-lf-bloqueia`, `-cr-bloqueia`, `-cr-arquivo-bloqueia` | `visibility` escondida depois do CR | passou |
| BOM na consulta falha fechado | `trava-graphql-bom-bloqueia` | controle fora do léxico | passou |
| `<var>[visibility]` com espaço ou sem uso na consulta não conta como privado | `trava-graphql-variavel-com-espaco-bloqueia`, `-variavel-nao-usada-bloqueia` | variável não referenciada | passou |

- Teste no head: `python3 -m unittest tests.test_hooks.Hooks.test_fixtures_do_repo_publico`: `Ran 1 test ... OK`.
- Vermelho: cópia do head com `hooks/conformidade.py` de 1265fa11, mesmo teste: `FAILED (failures=5)`, `AssertionError: 0 != 2`; caem `bloco-escape-bloqueia`, `bom-bloqueia`, `comentario-cr-arquivo-bloqueia`, `comentario-cr-bloqueia`, `variavel-nao-usada-bloqueia`. As outras 3 das 8 passam também na base: `comentario-lf-bloqueia` e `variavel-com-espaco-bloqueia` (guardas de regressão do que o 1265fa11 já recusava) e `bloco-escape-private-libera` (lado libera). O teste prova; a morte dessas guardas está nos mutantes.
- Mutação. `forge-mutante --base 1265fa11 tests/mutantes/v0480-repo-publico-fix-{4,6,7}.json --processos 3`, rc 0: cabeçalho `base=1265fa11ec5e75d16df8402d32664fd2d683538e mb=1265fa11ec5e75d16df8402d32664fd2d683538e rev=708c4bb09a6c74716b6897d37a2319575ae591b3`, `todos os mutantes entram`; 19 de 19 `morreu` (RP25 a RP32, RP41 a RP51, com RP30 e RP45 reancorados e RP47 a RP51 novos), nenhum sobrevivente.
- Cobertura. `forge-mutante --cobertura --base 1265fa11`, rc 0, zero `não coberto`; as linhas 3497, 3502, 3504 e 3505 saem cobertas por RP47, RP50, RP30, RP31 e RP51.
- Orçamento de CPU do hook: `Ran 13 tests in 20.0s OK` (os 4 de orçamento, o das fixtures e `test_orcamento_instrucao`); pior caso `HEREDOC-DONOS python3 - a{i} x3000: 0.88 s de CPU (limite 3 s)`. A regex nova do bloco `"""` não degrada o tempo.
- Review e segurança do head 708c4bb0 correm em paralelo e não são reabertos aqui.
- Sem suíte local; a suíte inteira é do CI do PR.
