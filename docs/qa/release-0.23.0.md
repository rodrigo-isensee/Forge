---
tipo: qa
contrato: 1
pedido: release-0.23.0
branch: melhoria/release-0.23.0
commit: a0c2720fcff26b0a06021aaecadfd0cd1d937b58
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: release-0.23.0

Testado no HEAD 52e3e39 (descendente do commit alvo a0c2720; o diff entre os dois é só o parecer de review). Base do diff: 8833e1c.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: os dois plugin.json em 0.23.0 | grep version nos dois manifestos | n/a | passou |
| E1: versão maior que a da homolog e a da main | `git show origin/homolog` e `origin/main`: ambas 0.22.0 | 0.22.0 < 0.23.0 | passou |
| E1: fragmentos juntados e apagados | `bin/forge-changelog conferir-release` rc 0 ("sem fragmentos pendentes"); changelog.d/ sem fragmentos | pasta vazia | passou |
| E1: changelog e versão batem | `bin/forge-changelog conferir --base origin/develop` rc 0 (0.22.0 → 0.23.0) | versão mudou | passou |
| Suíte estrutural | `python3 -m unittest discover -s tests -q`: 876 testes, OK, 156 s | n/a | passou |
| Plugin válido | `scripts/validar-plugin.sh`: Validation passed (raiz e dev) | n/a | passou |

## Cenários e resultado real
- Antes da suíte, `pgrep` sem suítes concorrentes (R-TETO); uma suíte por vez.
- Diff 8833e1c..a0c2720: 9 arquivos (2 plugin.json, CHANGELOG.md com 10 linhas novas, 6 fragmentos apagados); nenhum código de produção.
- Sem mudança de comportamento, não há teste novo; vermelho antes do verde e mutação não se aplicam.
- Ruído do sandbox: tentativas de rede bloqueadas (api.anthropic.com, datadog) durante a validação; a validação passou mesmo assim.
- Sem bugs abertos.
