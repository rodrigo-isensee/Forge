---
tipo: qa
contrato: 1
pedido: release-0.30.7
branch: melhoria/release-0.30.7
commit: b1e11946c1e33df5f44823a27c10c28461c2d793
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: release 0.30.7 (REL-0307-REV, E3.1)

Escopo: o diff `2fdda20...b1e1194` só mexe em `plugin.json` e `dev/.claude-plugin/plugin.json` (0.30.6 para 0.30.7), na seção 0.30.7 do `CHANGELOG.md` e na remoção dos cinco fragmentos de `changelog.d/`. Não há código de produção, então não há mutantes nem vermelho-antes-do-verde. Por decisão técnica de 2026-10-29 16:52, a evidência é `tests.test_changelog`, os testes de versão e `scripts/validar-plugin.sh`, não a suíte completa.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão dos dois manifestos igual à última do CHANGELOG (0.30.7; exceção da decisão "C") | `tests.test_forge`, `tests.test_sessao_versao_carregada`, `tests.test_conferir_release` | n/a | passou |
| Seção 0.30.7 traz os cinco fragmentos da develop 2fdda20 | conferência por script: cada linha de fragmento removida aparece uma vez no CHANGELOG (1 Corrigido x3, 2 Alterado; 5/5, contagem 1 cada) | cinco de cinco, nenhum a mais | passou |
| Fragmentos consumidos | `tests.test_changelog`; `changelog.d/` sem os cinco arquivos | pasta sem fragmentos | passou |
| Validação do plugin | `scripts/validar-plugin.sh`: "Validation passed", rc=0 | n/a | passou |

## Resultado da execução
Worktree `~/.forge-contrib/wt/wt-qa-release-0.30.7` no head b1e1194. `unittest` de test_changelog, test_conferir_release, test_sessao_versao_carregada e test_forge: 511 testes, OK (1 skip: regra de nome de branch em HEAD destacado). O sandbox bloqueou a rede do validador (api.anthropic.com), sem efeito no resultado. Itens do PA-7 conferidos: sem segredo nem caminho pessoal, achados vazios.
