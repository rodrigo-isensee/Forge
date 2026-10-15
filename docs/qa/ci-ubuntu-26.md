---
tipo: qa
contrato: 1
pedido: ci-ubuntu-26
branch: melhoria/ci-ubuntu-26
commit: bbc658f13b9d57fd551f73e17b57975799146fd7
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-15
---
# QA: CI fixado em ubuntu-24.04

Mudança: troca de rótulo `runs-on: ubuntu-latest` para `ubuntu-24.04` em ci.yml (9 jobs), catraca.yml (2) e release.yml (1), mais entrada no CHANGELOG. Sem código de produção. HEAD da branch no teste: 2f0b85c (só docs depois de bbc658f).

## Verificações
| ID | Obrigação | Verificação | Resultado |
|---|---|---|---|
| CT-01 | Nenhum `ubuntu-latest` em `.github/workflows` | `grep -rn ubuntu-latest .github/workflows` | sem ocorrências (rc=1) |
| CT-02 | Diff só troca rótulo, 12 jobs, sem matriz | `git diff develop..HEAD -- .github` | 12 trocas, 12 linhas por 12; sem outra linha alterada |
| CT-03 | YAML válido e todos os jobs em 24.04 | `yaml.safe_load` nos 3 arquivos | válidos; 12 de 12 jobs em `ubuntu-24.04` |
| CT-04 | Suíte verde | `env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests` | 561 testes, OK (182 s) |
| CT-05 | Plugin válido | `scripts/validar-plugin.sh` | passou |
| CT-06 | Portão do PR | `python3 bin/forge-check pr ci-ubuntu-26 --base develop` | antes do parecer: `sem parecer para o pedido ci-ubuntu-26 (R-QA)`, rc=1; com o parecer commitado: sem saída, rc=0 |

## Lacunas
- `actionlint` e `shellcheck` não estão instalados aqui; o job `workflows` do CI roda actionlint e zizmor. A validação de YAML foi só de sintaxe.
- Não há runner 24.04 aqui: nada prova o comportamento no GitHub. É troca de rótulo, mas só o CI do PR confirma.
- O risco de quebra na 26.04 (Python 3.14, shellcheck 0.11) é hipótese do devops e fica para a migração em cartão próprio.
- Rótulo `afrouxa-regra` (altera `.github/`) é do dono; não verificável localmente.
- A variável `FORGE_ABERTURA_FEITA` da sessão foi removida na suíte (problema de ambiente conhecido, correção em outra branch).

## Resultado
Aprovado, sem bugs abertos. Carga da máquina antes da suíte: 1,24 (abaixo do teto).
