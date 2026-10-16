---
tipo: qa
contrato: 1
pedido: release-0.17.0
branch: melhoria/release-0.17.0
commit: a3a52d1aa1b223e79ee564f77cf4fef3288391f9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-16
---
# QA - versão 0.17.0 (K2 do conferente)

Sem UX nem API. Código testado: a3a52d1 (plugin.json 0.17.0, CHANGELOG fechado, fragmento removido) sobre a base 7cd4e42 (origin/develop); o HEAD (3e5baae) só acrescenta o parecer de review (`parecer: aprovado`, R-REVIEW antes de R-QA). Diff: 3 arquivos da fábrica, só texto e versão; sem teste novo de regra, então sem vermelho-antes-do-verde nem mutação.

## Obrigação -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| PQ-1 | Suíte verde | `python3 -m unittest discover -s tests -q` | n/a | 685 testes, OK (195 s) |
| PQ-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | "Validation passed" |
| PQ-3 | Sem fragmentos pendentes | `bin/forge-changelog conferir-release` | `changelog.d/` vazio | "ok: changelog.d/ sem fragmentos pendentes" |
| CI-1 | Versão/fragmento no PR para a develop | `bin/forge-changelog conferir --base origin/develop` | versão mudou | rc=0; base 0.16.0, PR 0.17.0 |
| CI-2 | Gate "main - release exige versão nova e changelog fechado" (script local com o Python do ci.yml, contra origin/main 4ccbd75, plugin 0.16.0) | 0.17.0 > 0.16.0; existe `## [0.17.0]`; `[Não publicado]` vazia; `conferir-release` | igualdade (a <= b reprova) | "gate-ok" |
| CF-1 | Notas extraíveis pelo caminho da publicação | awk do release.yml ("Tag e release") sobre o CHANGELOG.md | saída vazia | 3 linhas (cabeçalho `### Adicionado`, 1 item, linha em branco), não vazia |
| CF-2 | Texto da [0.17.0] traz o fragmento sem perda | cada linha do fragmento (de origin/develop) procurada literal (`grep -qxF`) nas notas | perda | 0 faltas |
| CF-3 | Nenhum fragmento sobra | `ls -A changelog.d`, `git ls-files changelog.d` | pasta vazia | vazio |

## Bugs
Nenhum.

## Observações
- Ruído do sandbox (bloqueio de rede para hosts externos) não afetou nenhum resultado.
- O gate real roda no PR homolog -> main; aqui foi reproduzido localmente contra origin/main.
