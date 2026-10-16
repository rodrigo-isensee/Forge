---
tipo: qa
contrato: 1
pedido: release-0.16.0
branch: melhoria/release-0.16.0
commit: 447276580098bf62a1a6a1912c45fe0f3ffbe6ca
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-16
---
# QA - versão 0.16.0 (K1 e processo)

Sem UX nem API. Código testado: 4472765 (plugin.json 0.16.0, CHANGELOG fechado, dois fragmentos removidos) sobre a base a7246d4 (origin/develop); o HEAD só acrescenta o parecer de review (`parecer: aprovado`, R-REVIEW antes de R-QA).

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 657 testes, OK (184 s) |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| PQ-3 | Changelog sem fragmentos pendentes | `bin/forge-changelog conferir-release` | `changelog.d/` vazio | "ok: changelog.d/ sem fragmentos pendentes" |
| CI-1 | Fragmento/versão no PR para a develop | `bin/forge-changelog conferir --base origin/develop` | versão mudou | rc=0; base 0.15.1, PR 0.16.0 |
| CI-2 | Gate "main - release exige versão nova e changelog fechado" (script local com o mesmo Python do ci.yml, contra origin/main 640884d, plugin 0.15.1) | versão 0.16.0 > 0.15.1; existe `## [0.16.0]`; `[Não publicado]` vazia; `conferir-release` | igualdade (a <= b reprova) | "gate ok" |
| CF-1 | Notas extraíveis pelo caminho da publicação | awk do release.yml (linhas 32-36) sobre o CHANGELOG.md da branch | saída vazia | 9 linhas, não vazia |
| CF-2 | Texto da [0.16.0] traz os dois fragmentos sem perda | cada linha dos fragmentos (de origin/develop) procurada literal (`grep -qxF`) nas notas | perda | 0 faltas; 2 + 4 itens = 6 itens nas notas |
| CF-3 | Nenhum fragmento sobra | `ls changelog.d`, `git ls-files changelog.d` | pasta vazia | vazio |

## Observações
- Vermelho antes do verde e mutação: não se aplicam (sem teste novo nem código de produção; só versão e texto).
- A seção 0.15.1 do CHANGELOG não mudou (diff só acrescenta a 0.16.0).
- O diff toca apenas `plugin.json`, `CHANGELOG.md`, os dois fragmentos (apagados) e o parecer de review.
- A checagem de rede do `claude plugin validate` bloqueada pelo sandbox (api.anthropic.com) não afetou o resultado: "Validation passed".

Parecer: **aprovado**, sem bugs.
