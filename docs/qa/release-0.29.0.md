---
tipo: qa
contrato: 1
pedido: release-0.29.0
branch: melhoria/release-0.29.0
commit: 49cf5c32cb55cb944c3d103b632321bb6b5a4016
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-23
---
# QA: release-0.29.0

Código testado: 49cf5c3 (base db55859, develop com o #297). O diff toca só `.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md` e apaga 20 fragmentos de `changelog.d/`. Sem especificação de UX: critério de integração (R-QA). Pedido REL-029-REV.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão 0.29.0 nas duas cópias | `json.load` de `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 49cf5c3 | as duas batem | 0.29.0 e 0.29.0 |
| Versão subiu sobre a base | `git show db55859:.claude-plugin/plugin.json` | minor para melhoria compatível | 0.28.0 para 0.29.0 |
| CHANGELOG cobre todos os fragmentos | cada linha `- ` dos 20 fragmentos da base achada literal na entrada [0.29.0] (`grep -qxF`) | nenhum PR de fora, nenhuma linha perdida | 0 faltas |
| Fragmentos juntados e apagados | `git diff --diff-filter=D` em `changelog.d/` (20) contra os 20 da base; pasta ausente na árvore | nenhum fragmento sobra | passou |
| Testes que leem versão e changelog | `python3 -m unittest tests.test_changelog tests.test_conferir_release tests.test_sessao_versao_carregada tests.test_testes_tocados`: 109 testes, rc 0 (1 skip condicional: `test_fragmentos_novos_desta_branch_tem_o_nome_dela`, "branch 'HEAD' não é de melhoria", worktree destacada; não é skip de correção) | n/a | passou |
| Plugin válido e identificado como 0.29.0 | `scripts/validar-plugin.sh` rc 0 (Validation passed) e `claude plugin validate .` (Validation passed); versão lida do manifesto = 0.29.0 | n/a | passou |
| docs | `bin/forge-check docs` | n/a | sem erro |

## Notas
- `bin/forge-testes` com os caminhos do diff não aceita arquivos como argumento (só `--base`); com a base, o `dev/.claude-plugin/plugin.json` não tem mapa e cai na suíte completa (falha fechada), proibida fora do pre-push por este pedido; rodei os módulos que leem versão e changelog direto com unittest. A suíte completa roda no pre-push do envio.
- Vermelho antes do verde e mutação não se aplicam: sem teste novo e sem código de `bin/`, `hooks/` ou `.githooks/` no diff.
- Sem rede: CI e `gh` não consultados; as sondas de rede do validador foram negadas pelo sandbox, sem efeito no resultado.
