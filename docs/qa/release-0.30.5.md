---
tipo: qa
contrato: 1
pedido: release-0.30.5
branch: melhoria/release-0.30.5
commit: d7e0c9f030ecbe9adefacad7884e3d58c715ef2a
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: release-0.30.5

Release 0.30.5 (REL-0305-REV, E3.1): commit de release sobre a develop a83de9e, sem código de produção novo (diff: manifestos, `CHANGELOG.md`, seis fragmentos apagados). Plano antecipado não se aplica (sem especificação nova); o escopo do pedido (E1) vira os critérios abaixo.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1: versão 0.30.5 nos dois manifestos | `plugin.json` e `dev/.claude-plugin/plugin.json` lidos por script (0.30.5 e 0.30.5); `tests.test_forge` Manifestos, ManifestoDoPlugin, PluginDeDesenvolvimento (inclui versão igual à do Forge) | manifesto de dev divergente | passou |
| E1: seção 0.30.5 do CHANGELOG confere com os seis fragmentos da develop a83de9e | script: cada linha `- ` de cada fragmento em `git show a83de9e:changelog.d/*` está na seção (6 de 6; 6 itens na seção, nenhum a mais) | fragmento perdido ou extra | passou |
| E1: fragmentos apagados, `[Não publicado]` vazio | diff e `ls changelog.d` (pasta inexistente no head) | n/a | passou |
| E1: formato do changelog | `tests.test_changelog`: 46 testes, OK (1 skip do próprio módulo) | n/a | passou |
| Release/versão carregada | `tests.test_conferir_release`, `tests.test_sessao_versao_carregada`: 15 OK | n/a | passou |
| Plugin válido | `scripts/validar-plugin.sh`: rc=0, "Validation passed" | n/a | passou |

## Cenários e resultado real
- Worktree `~/.forge-contrib/wt/wt-qa-release-0.30.5` em d7e0c9f, árvore limpa antes do parecer.
- Suíte completa não rodada por mim (brief: só os testes do item; a completa roda no pre-push). Vermelho antes do verde e mutação não se aplicam: nenhum teste novo, nenhum `bin/`, `hooks/` ou `.githooks/` alterado no diff.
- Os avisos de rede negada (api.anthropic.com, datadog) vêm do sandbox e não alteraram o resultado do validador.
- Checklist PA-7 (`docs/engineering/achados-recorrentes.md`): sem código de autor no diff; nada a conferir além do formato do parecer.
- Observação: o texto do CHANGELOG diz "forge-mutante --cobertura" etc. conforme os fragmentos; conferido literalmente, sem divergência.
