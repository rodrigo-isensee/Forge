---
tipo: qa
contrato: 1
pedido: release-0.26.0
branch: melhoria/release-0.26.0
commit: 998fdd5115212ef7ad892c0874574d859f60703c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA - release 0.26.0

Sem UX nem API. Código testado em 998fdd5; o HEAD (552f4cc) só acrescenta `docs/reviews/`, `docs/devops/` e `docs/security/`. Obrigações: E1 e E2 do pedido, `R-QA`, `R-TETO` (`.githooks/pre-push --status` rc=1, "nenhuma suíte do Forge rodando", antes da suíte; load 0,05). Os pareceres de review, devops e segurança estão `aprovado` com `## Achados` vazio.

## Critério -> teste -> resultado
| ID | Obrigação | Teste (comando real) | Fronteira protegida | Resultado |
|---|---|---|---|---|
| Q-1 | Suíte completa | `python3 -m unittest discover -s tests -q` | n/a | `Ran 1082 tests in 213.541s` / `OK` |
| Q-2 | Plugin válido | `scripts/validar-plugin.sh` | n/a | `Validation passed` (manifesto e plugin) |
| Q-3 | E1: changelog fechado, sem fragmentos | `bin/forge-changelog conferir-release` | pasta `changelog.d/` vazia | rc=0 `changelog.d/ sem fragmentos pendentes`; `ls changelog.d` vazio |
| Q-4 | E1: entrada coerente com a versão | `bin/forge-changelog conferir --base origin/develop` | versão do PR maior que a da base | rc=0 `versão base: 0.25.0 \| versão do PR: 0.26.0` |
| Q-5 | 0.26.0 maior que homolog e main | `git show origin/homolog:.claude-plugin/plugin.json`, idem main; `plugin.json` e `marketplace.json` locais | versão igual (não sobe) | homolog 0.25.0, main 0.25.0, release 0.26.0 nos dois manifestos |
| Q-6 | Merge --no-ff do head sobre a homolog passa na conferência | clone em `$TMPDIR`, `git merge --no-ff` de `origin/melhoria/release-0.26.0` sobre `origin/homolog` (8d34b13); `python3 scripts/conferir-release.py --base origin/homolog --so-se-versao-mudou` | conflito de merge; versão não mudou | merge sem conflito; rc=0 `versão base: 0.25.0 \| versão da release: 0.26.0` |
| Q-7 | Idem sobre a main | o mesmo sobre `origin/main` (aa5dc1c), sem `--so-se-versao-mudou` | idem | merge sem conflito; rc=0, mesma saída |
| Q-8 | Conteúdo da [0.26.0] = as quatro entregas | leitura de `CHANGELOG.md` | n/a | 3 itens em Alterado (CATRACA-ENDURECER, CONF-CORRECAO, S-16) e 1 em Corrigido (FECHAR-ESTAVEL); sem FORGE-CHECK-LOTE |

## Vermelho antes do verde
Não se aplica: a release não traz teste novo; os testes das quatro entregas foram vistos falhando nos pareceres de QA de cada uma (`docs/qa/catraca-endurecer.md`, `docs/qa/conf-correcao.md`, `docs/qa/fechar-estavel.md`) e aqui só se confere a suíte inteira sobre o conjunto.

## Instáveis
Nenhum teste falhou e passou de novo sem mudança (a suíte rodou uma vez, verde).

## Bugs
Nenhum.

## Achados
