---
tipo: qa
contrato: 1
pedido: release-0.25.0
branch: melhoria/release-0.25.0
commit: 630d200aff68570aa1a184be41b645ecb8d60ab8
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA: fechamento da release 0.25.0

Ambiente: worktree da branch em d477e1e (HEAD; sobre 630d200 só entram os pareceres de devops e segurança, e o commit do fechamento é o 630d200). Sem rede e sem custo (R-CUSTO). O diff do fechamento (71ac7fc..630d200) é só versão (dois `plugin.json`), entrada `[0.25.0]` no CHANGELOG e remoção de 6 fragmentos; as mudanças de código já passaram por QA nos PRs de origem. Antes da suíte, `.githooks/pre-push --status`: "nenhuma suíte do Forge rodando", rc 1.

## Critério, teste, resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Suíte completa verde | `python3 -m unittest discover -s tests -q` | n/a | 985 testes em 198 s, OK; nenhuma falha intermitente |
| Plugin válido | `scripts/validar-plugin.sh` | manifesto raiz e `dev/` | "Validation passed" nos dois, rc 0 |
| Changelog fechado | `bin/forge-changelog conferir-release` | `changelog.d/` sem fragmentos | rc 0; `ls -A changelog.d` vazio |
| Versão e changelog batem | `bin/forge-changelog conferir --base origin/develop` | 0.24.0 para 0.25.0 | rc 0 |
| Versão maior que homolog e main | `git show origin/homolog:...` e `origin/main:...` | versão igual ou menor | ambas 0.24.0; 0.25.0 é maior |
| Raiz e `dev/` na mesma versão | `grep version` nos dois `plugin.json` | divergência | ambos 0.25.0 |
| DV-4 na promoção para a homolog | `scripts/conferir-release.py --base <homolog> --so-se-versao-mudou` num repositório em `$TMPDIR` com merge `--no-ff` da branch sobre `origin/homolog` | versão sobe: a checagem roda | merge sem conflito; "versão base: 0.24.0 \| versão da release: 0.25.0", "ok: changelog.d/ sem fragmentos pendentes", rc 0 |
| DV-4 na promoção para a main | mesmo script sem a flag, merge sobre `origin/main` | versão sobe, entrada e fragmentos | merge sem conflito; mesma saída, rc 0 |

## Observações
- Vermelho antes do verde e mutação: não se aplicam; o fechamento não traz teste nem regra nova (os testes da DV-4 e da leva foram vistos nos PRs de origem).
- A primeira simulação do merge (clone do worktree) não enxergava `origin/homolog`; foi descartada e refeita com `git fetch` das refs remotas da worktree para um repositório novo. Só a segunda vale e é a descrita acima.
- `actionlint`, `zizmor` e `shellcheck` não estão no PATH local; rodam no job `bateria` do CI.

## Achados
