---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ci-changelog-base
commit: b5d501257b67e9be2bce4051c26a7555d3d3f02f
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 · E1.52 (passo do changelog no CI usa HEAD^1)

Head revisado: 136cf316 (branch `melhoria/v047-ci-changelog-base`, base 028ac55b). Pedido de correção, sem especificação de UX: as obrigações vêm do pedido (E1.52) e da regra CI-CHANGELOG-BASE.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| O passo usa `BASE=$(git rev-parse HEAD^1)` e não o `base.sha` do evento | `MatrizNeedsEAgregadorTest.test_changelog_compara_com_o_pai_do_commit_de_juncao_e_nao_com_a_base_do_evento` (roda o `run` real do passo num repo temporário com a develop adiantada) | base velha do evento (`BASE` do env diferente de `HEAD^1`) | passou |
| M1 morto | `bin/forge-mutante tests/mutantes/v047-ci-changelog-base.json` | única linha de guarda mudada | passou (morreu) |
| Passo ainda barra PR sem fragmento | cenário manual com o `bin/forge-changelog` real e `BASE=$(git rev-parse HEAD^1)` | PR que muda `agents/` sem fragmento | passou (rc=1) |
| Fragmento de outro PR já na develop não é atribuído ao PR | mesmo cenário (outro.md na develop adiantada) | base velha | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_ci_local`: 66 testes, OK.
- Vermelho antes do verde, feito à mão (`forge-testes --vermelho 028ac55b` não deu veredito no prazo, então não vale como vermelho): com o `ci.yml` da base 028ac55b e o teste do head, o teste novo falha (`FAILED (failures=1)`); com o `ci.yml` do head, passa.
- Mutação: `M1 · morreu · .github/workflows/ci.yml:521`. Há um mutante para a única linha de guarda mudada no diff (a origem de BASE).
- Sem caminho para pular a checagem: o `if:` do passo (pull_request e base develop) não mudou; o `run` continua chamando `conferir`; o checkout do job tem `fetch-depth: 0` e, em `pull_request`, o HEAD é o commit de junção, então `HEAD^1` existe. Se `HEAD^1` falhasse, o `run` do GitHub (`bash -e`) pararia o passo com erro, não passaria em silêncio.
- Cenário manual, repo temporário: develop adiantada com fragmento alheio, PR sem fragmento: `Registre a mudança num fragmento novo...` rc=1; PR com fragmento: `ok: 1 fragmento(s) novo(s)` rc=0.
- Prova de CI: sem PR aberto, o check-run `bateria` não foi consultado.
- Limite: o commit de junção real do Actions não foi exercitado, só simulado em repositório temporário.

## Revalidação por delta (E1.68) até b5d50125
- `forge-check parecer delta` lista no domínio só `tests/test_ci_local.py`: uma linha em `MatrizNeedsEAgregadorTest`, em que o `git` do teste passa a usar `env=sem_manutencao(env)` (helper já importado e usado no mesmo arquivo com env próprio, linha 760). Nenhum `CA-n` nem guarda mudou; o mutante M1 e a tabela acima seguem valendo.
- `python3 -m unittest tests.test_ci_local tests.test_ambiente_git`: 86 testes, OK.
- Parecer: aprovado, sem achados bloqueantes nem recomendados.
