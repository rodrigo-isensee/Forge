---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/ci-ubuntu-26
commit: fd3a3e1536b9b353e1f51e696f04412a5d994f05
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: ci-ubuntu-26-migracao

Mudança: os 5 jobs (`ci.yml` 3, `catraca.yml` 1, `release.yml` 1) passam de `ubuntu-24.04` para `ubuntu-26.04`, mais teste em `tests/test_ci_local.py`. HEAD de código: fd3a3e1; os commits seguintes só tocam `docs/`. QA local: não há runner 26.04 aqui; a confirmação em runner real fica para o primeiro run do PR.

## Achados
- A1 (recomendado) .github/workflows/catraca.yml:20 · sem runner 26.04 aqui, o `python3` do sistema (3.12 para 3.14) e o shellcheck 0.11 só se provam no primeiro run do PR

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Todo job de todo workflow roda em `ubuntu-26.04`, sem `-latest` | `test_todo_job_roda_no_ubuntu_26_04` | workflow novo ou job novo em outro runner (o teste afirma lista não vazia de `runs-on`) | passou |

## Cenários e resultado real
| ID | Obrigação | Verificação | Resultado |
|---|---|---|---|
| CT-01 | Vermelho antes do verde | base fd3a3e1~1 (árvore extraída em cópia) com o `test_ci_local.py` do head | 53 testes, 3 falhas (uma subTest por workflow: `ubuntu-24.04` no lugar de `ubuntu-26.04`) |
| CT-02 | Verde no head | `python3 -m unittest discover -s tests -p test_ci_local.py` | 53 testes, OK |
| CT-03 | Diff só troca o rótulo | `git diff fd3a3e1~1 fd3a3e1 -- .github` | 5 linhas `-` e 5 `+`, todas `runs-on`; contagem por arquivo: ci 3, catraca 1, release 1 |
| CT-04 | Sintaxe dos workflows | o módulo `yaml` não existe aqui; conferi por `grep` que nenhum `ubuntu-24.04` ou `-latest` sobra e que o diff é só de `runs-on` | sem ocorrências |

## Lacunas
- Sem PyYAML, sem actionlint e sem runner 26.04 aqui: confirmação em runner real fica para o primeiro run do PR.
- `forge-testes --vermelho` roda a suíte inteira e passou do prazo; usei a cópia da base com o teste do head, que dá o mesmo veredito por teste.

## Resultado
Aprovado, sem bugs abertos.
