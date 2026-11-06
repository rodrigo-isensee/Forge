---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/catraca-fork
commit: 838803f4c8da680b589f47f022aebe9c2e81e25b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: catraca-fork

Mudança: em `--modo pareceres` a catraca recusa o PR cujo head vem de outro repositório, que herdaria os pareceres de uma branch homônima já mesclada (o campo `branch:` liga o parecer ao nome da branch, que o autor do fork escolhe). O workflow passa `HEAD_REPO` e `BASE_REPO` por env; fork, `head.repo` nulo e, em CI (`GITHUB_ACTIONS`), `BASE_REPO` vazio falham fechado. Empilhada em catraca-ramo-cmd-pr (088a1e1). HEAD de código: 838803f (5ad6373 e 838803f); os commits seguintes só tocam `docs/` (o head da branch na hora do parecer é 8b621aa). QA local: a confirmação em runner real fica para o primeiro run do PR, e a correção só vale no CI depois de estar na base, porque a catraca roda da base.

## Achados
- A1 (recomendado) tests/catraca.py:1114 · o texto da recusa não tem teste da ordem "vem de X, não de Y": trocar `HEAD_REPO` por `BASE_REPO` no `_main` sobrevive (a comparação é simétrica; muda só a mensagem)
- A2 (recomendado) tests/catraca.py:1109 · a comparação é sensível a caixa (`Dono/Forge` x `dono/Forge` recusa); o `full_name` e o `github.repository` vêm canônicos do GitHub, então só afeta a execução manual com env

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PR de fork com o nome de branch de um parecer aprovado não herda o parecer | `test_fork_com_o_nome_de_branch_ja_mesclada_nao_herda_o_parecer`, S2 | fork e `head.repo` vazio | passou |
| A recusa vale sem arquivo sensível e nas promoções | `test_fork_recusa_ate_sem_arquivo_sensivel_e_nas_promocoes`, S9 e S10 | `pr`/develop, develop/homolog, homolog/main | passou |
| Em CI com `BASE_REPO` vazio falha fechado; fora do CI libera | `test_em_ci_sem_base_repo_falha_fechado_e_fora_do_ci_libera`, S4 a S7 | os dois vazios, um vazio, `GITHUB_ACTIONS` ligado e desligado | passou |
| Mesmo repositório ou sem env não muda o resultado | `test_mesmo_repositorio_ou_sem_env_nao_muda_o_resultado`, S1 e S8 | igualdade e vazio | passou |
| O workflow entrega `HEAD_REPO` e `BASE_REPO` ao passo e não os interpola no `run` | `test_workflow_declara_head_repo_e_base_repo_no_passo_de_pareceres` | env do passo sem `${{` no script | passou |
| A CLI lê os dois por env e devolve rc 1 para fork | `test_cli_le_o_repositorio_do_head_por_env_e_recusa_o_fork` | env, não opção (opção desconhecida daria rc 2 na catraca da base) | passou |

## Cenários e resultado real
| ID | Obrigação | Verificação | Resultado |
|---|---|---|---|
| CT-01 | Vermelho antes do verde | base 5ad6373~1 extraída em cópia, com o `test_catraca.py` do head, nos 9 testes novos (`-k fork -k base_repo -k head_repo -k mesmo_repositorio -k repositorio_do_head`) | 9 testes: 2 falhas e 10 erros (subtestes incluídos); nenhum passa |
| CT-02 | Verde no head | os mesmos 9 testes no head | 9 testes, OK |
| CT-03 | Suíte do módulo | `python3 -m unittest discover -s tests -p test_catraca.py` (3 min 15 s, carga entre 7 e 11) | OK |
| CT-04 | Ponta a ponta, CLI real, repositório descartável (base `develop`, branch `pr` com `hooks/novo.py` e parecer `review` aprovado com `branch: pr`) | `python3 tests/catraca.py --modo pareceres --raiz . --base base --ramo pr --base-ref develop`, com `env -i` e as variáveis de cada cenário | veja a tabela abaixo |
| CT-05 | Mutação no código do diff | 6 mutantes em cópia do head | 4 mortos (guarda de CI, igualdade, chamada removida, `BASE_REPO` fora do yml); 2 sobrevivem: texto da mensagem (A1) e `repositório desconhecido` renomeado (só rótulo, equivalente) |

Cenários de ponta a ponta (rc do head 838803f; entre parênteses, o rc da catraca de 088a1e1, antes da correção):

| Cenário | HEAD_REPO / BASE_REPO / GITHUB_ACTIONS | rc |
|---|---|---|
| S1 mesmo repositório, em CI | dono/Forge / dono/Forge / true | 0 (0) |
| S2 fork com branch homônima, em CI | fulano/Forge / dono/Forge / true | 1 (0) |
| S3 `head.repo` nulo, em CI | vazio / dono/Forge / true | 1 (0) |
| S4 CI, `BASE_REPO` vazio | dono/Forge / vazio / true | 1 (0) |
| S5 CI, os dois vazios | vazio / vazio / true | 1 (0) |
| S6 CI, sem nenhum env | sem env / sem env / true | 1 (0) |
| S7 local, sem env | sem env / sem env / sem | 0 (0) |
| S8 local, mesmo repositório | dono/Forge / dono/Forge / sem | 0 (0) |
| S9 fork na promoção develop para homolog | fulano/Forge / dono/Forge / true | 1 (0) |
| S10 fork na promoção homolog para main | fulano/Forge / dono/Forge / true | 1 (0) |
| S11 fork, execução local | fulano/Forge / dono/Forge / sem | 1 (0) |
| S12 caixa diferente | Dono/Forge / dono/Forge / true | 1 (0) |

A coluna de 088a1e1 reproduz o defeito: o fork (S2) passa com rc 0 e herda o parecer. As mensagens de S2 a S6 citam `R-REVIEW` com a origem do head.

## Lacunas
- Sem runner aqui: a confirmação em runner real fica para o primeiro run do PR. A catraca roda da base; a recusa só vale no CI depois de a correção estar na base (o changelog diz isso).
- Sem PyYAML aqui; o env do passo foi conferido pelo teste do próprio módulo (leitura do `ci.yml` por texto) e pela remoção do `BASE_REPO` no mutante M5.
- A contagem de testes do módulo inteiro não ficou registrada (a saída foi cortada); o veredito é OK.
- `forge-mutante` não foi usado: não há spec declarada em `tests/mutantes/` para este pedido, então a lista de 6 mutantes é minha, escolhida sobre as 4 guardas do diff.

## Resultado
Aprovado, sem bugs abertos.
