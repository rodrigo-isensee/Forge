---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/ci-comentario-rapida
commit: 8bcc469d7eb32f3a09accc59d242755474d54f57
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: ci-comentario-rapida

Mudança: o comentário do topo do `ci.yml` dizia que o push na develop roda "só a checagem rápida"; o job `rapida` roda a suíte inteira (`scripts/suite-paralela.py`, Python 3.12). Só texto de comentário e um teste novo; nenhuma linha executável do workflow muda. HEAD de código: 8bcc469 (empilhada na migração ao ubuntu-26.04); os commits seguintes só tocam `docs/`. QA local, sem runner: a confirmação em runner real fica para o primeiro run do PR.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| O comentário não chama a suíte da develop de "checagem rápida" e cita o script que o job `rapida` de fato roda | `test_comentario_do_topo_diz_que_a_rapida_roda_a_suite` | o comentário só vale se o job `rapida` ainda chamar o mesmo script (o teste lê os passos do job) | passou |

## Cenários e resultado real
| ID | Obrigação | Verificação | Resultado |
|---|---|---|---|
| CT-01 | Vermelho antes do verde | base 8bcc469~1 extraída em cópia, com o `test_ci_local.py` do head | 54 testes, 1 falha (`só a checagem rápida` ainda no topo) |
| CT-02 | Verde no head | `python3 -m unittest discover -s tests -p test_ci_local.py` | 54 testes, OK |
| CT-03 | Mutação: voltar só o `ci.yml` à base no head | cópia do arquivo da base e mesmo comando | 1 falha, o teste mata o mutante; arquivo restaurado, árvore limpa |
| CT-04 | A afirmação do comentário é verdadeira | leitura do job `rapida` | `setup-python` 3.12 e `python3 scripts/suite-paralela.py`, como o texto diz |
| CT-05 | O diff não mexe em linha executável | `git diff 1bba5fd HEAD -- .github` | só linhas de comentário (`#`); `runs-on: ubuntu-26.04` segue nos 5 jobs |

## Lacunas
- Sem PyYAML nem actionlint aqui; a conferência de sintaxe foi por leitura do diff, que só mexe em comentário.
- Confirmação em runner real fica para o primeiro run do PR.

## Resultado
Aprovado, sem bugs abertos.
