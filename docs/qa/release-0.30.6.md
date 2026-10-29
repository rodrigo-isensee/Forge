---
tipo: qa
contrato: 1
pedido: release-0.30.6
branch: melhoria/release-0.30.6
commit: b2ea01b3d50283a65a1d4a7f87c1a4097ef78401
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: release 0.30.6 (REL-0306-REV, E3.1)

Escopo: o diff `49a45f2...b2ea01b` só mexe em `plugin.json` e `dev/.claude-plugin/plugin.json` (0.30.5 para 0.30.6), na seção 0.30.6 do `CHANGELOG.md` e na remoção dos oito fragmentos de `changelog.d/`. Não há código de produção, então não há mutantes nem vermelho-antes-do-verde. Por decisão técnica de 2026-10-29 09:28, a evidência é `tests.test_changelog`, os testes de versão e `scripts/validar-plugin.sh`, não a suíte completa.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Versão do `plugin.json` igual à última do CHANGELOG (0.30.6; SemVer com a exceção da decisão "C") | `tests.test_forge` (`test_plugin_json` e a conferência de versão) | n/a | passou |
| Seção 0.30.6 traz os oito fragmentos da develop 49a45f2 | conferência por script: cada linha de fragmento aparece uma vez no CHANGELOG, sob o tipo certo (1 Adicionado, 3 Alterado, 4 Corrigido) | oito de oito, nenhum a mais | passou (8/8, contagem 1 cada) |
| Fragmentos consumidos pela release | `tests.test_changelog`: 46 testes, OK (1 skip: a regra do nome de branch não vale em HEAD destacado) | `changelog.d/` sem os oito arquivos | passou |
| Release e versão dos dois manifestos | `tests.test_conferir_release` e `tests.test_sessao_versao_carregada`: 15 testes, OK; `plugin.json` e `dev/.claude-plugin/plugin.json` em 0.30.6 | n/a | passou |
| Validação do plugin | `scripts/validar-plugin.sh`: "Validation passed", rc=0 | n/a | passou |

## Resultado da execução
Worktree `~/.forge-contrib/wt/wt-qa-release-0.30.6` no head b2ea01b. O sandbox bloqueou a rede do validador (api.anthropic.com e telemetria), sem efeito no resultado. Itens do PA-7 conferidos: sem ID de regra copiado em frase, achados vazios, sem segredo nem caminho pessoal.
