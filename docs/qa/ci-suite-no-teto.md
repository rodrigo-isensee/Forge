---
tipo: qa
contrato: 1
pedido: ci-suite-no-teto
branch: melhoria/ci-suite-no-teto
commit: 1effb9e26ca8dc9956f29a1426717ef9ebae115f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-03
---
# QA: ci-suite-no-teto

Diff `1b6f418...1effb9e`: três `timeout-minutes` do `.github/workflows/ci.yml` (20 na checagem rápida, 25 na bateria python 3.14 e na bateria), fragmento de changelog e a asserção em `Workflows` de `tests/test_catraca.py`. Sem especificação de UX nem contrato de API; a obrigação é o escopo E2 do pedido (só os três tempos, sem afrouxar portão, sem custo, R-CUSTO).

## Achados
- A1 (recomendado) tests/test_pesos_teto.py:15 · limite antigo no texto (AR-9): TETO_DO_JOB_S e a docstring ainda dizem 15 min do job bateria, agora 25; o limite de 225 s por módulo fica mais apertado que o teto real. Não quebra nada.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E2: rápida 20, 3.14 25, bateria 25 | `Workflows.test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore` (`re.findall` == ["20","25","25"]) | valor exato e ordem dos três jobs | passou |
| E2: mesmos jobs da base, portão intacto | leitura do YAML (PyYAML) base x head | jobs `rapida`, `bateria-python-tres-quatorze`, `bateria` nos dois | passou |
| Sem custo (R-CUSTO) / sem afrouxar | diff: só números de tempo, nenhum `if`, `needs` ou passo mudou | n/a | passou |

## Cenários e resultado real
- Carga antes da suíte: load 3,55 e MemAvailable 13,5 GB.
- `python3 -m unittest tests.test_catraca` sobre 1effb9e: `Ran 267 tests in 74.219s`, `OK`.
- ci.yml carregado com yaml: `{'rapida': 20, 'bateria-python-tres-quatorze': 25, 'bateria': 25}`; jobs da base: `['rapida', 'bateria-python-tres-quatorze', 'bateria']` (iguais).
- Vermelho antes do verde: `forge-testes --vermelho 1b6f418b11dbb69f4a9d6731f448165fc9d50cad --modulos test_catraca` (a forma `tests.test_catraca` do brief é recusada com rc=2: o `--modulos` pede `test_<nome>`):
  - `vermelho: base=1b6f418b11db head=1effb9e26ca8 módulos=test_catraca (restrito por --modulos)`
  - `revertidos à base: .github/workflows/ci.yml, changelog.d/ci-suite-no-teto.md`
  - `tests.test_catraca.Workflows.test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore · H=ok · B=falha · prova (asserção)`
  - `contagem: não prova (passa na base)=266; prova (asserção)=1`, `rc=0`.
- `scripts/verificar-contribuicao.sh origin/develop`: `ok: nenhum segredo nem caminho pessoal no diff contra origin/develop.` rc=0.
- Mutação: não se aplica (diff não toca `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`).
- A suíte completa não foi rodada: o diff só muda números de tempo em YAML e uma asserção; o módulo que lê o YAML passou inteiro e o CI roda a bateria no PR.
- Lista PA-7 (achados recorrentes) conferida: AR-9 gerou o A1; `release.yml` (20) e `catraca.yml` (10) fora do escopo e intactos.
