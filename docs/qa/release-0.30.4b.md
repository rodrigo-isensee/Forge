---
tipo: qa
contrato: 1
pedido: release-0.30.4b
branch: melhoria/release-0.30.4b
commit: b0f0e7a60a0479959e98261758feb33f175f6b18
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-27
---
# QA: release-0.30.4b

Commit de release da 0.30.4 sobre a develop `1f7bd7f` (diff `1f7bd7f...b0f0e7a`: CHANGELOG.md, 18 fragmentos de changelog.d apagados e os dois plugin.json). Sem código de produção; sem `bin/`, `hooks/`, `.githooks/` ou `tests/catraca.py` no diff, então não há mutantes a declarar nem teste novo (vermelho antes do verde não se aplica).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` passam de 0.30.3 para 0.30.4 e batem com a seção `[0.30.4]` | conferência do diff dos dois manifestos; `tests.test_changelog` | os dois manifestos iguais | passou (única mudança de cada manifesto é a linha `version`) |
| Cada fragmento apagado aparece na seção `[0.30.4]` | script: cada linha de conteúdo dos 18 fragmentos de `1f7bd7f` buscada por texto exato em `CHANGELOG.md` (flaky-ctrlc-troca, prop-tempo-cpu, metade-k6, lote-tx1, lote-fechar2, lote-leitura-hook e os demais) | 18 de 18 fragmentos, 0 linhas faltando (leitura-hook 14 linhas, fechar2 4, mutante 3) | passou |
| `changelog.d/` sem fragmento residual | `ls changelog.d` na raiz da worktree: a pasta não existe (todos os arquivos foram apagados) | pasta vazia | passou |
| `[Não publicado]` fica vazio e `[0.30.4]` tem data | leitura do diff do CHANGELOG.md (`## [0.30.4] - 2026-10-27`) | cabeçalho e data | passou |
| Testes de changelog e de versão carregada | `python3 -m unittest tests.test_changelog tests.test_sessao_versao_carregada`: 51 testes, OK (1 skipped, do próprio teste, não adicionado por esta entrega) | n/a | passou |
| Validação do plugin | `scripts/validar-plugin.sh` na raiz da worktree: "Validation passed" (só o aviso ICON_MISSING do perfil directory, que não muda o resultado) | n/a | passou |

## Cenários e resultado real
- Rodei só os testes do item (suíte completa fica no pre-push e no CI, por decisão do dono).
- A sonda de rede do validador (api.anthropic.com e datadog) foi negada pelo sandbox; o resultado "Validation passed" não depende dela.
- Fora do escopo: o conteúdo técnico das entradas (já revisado nos PRs de origem).
