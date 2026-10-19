---
tipo: qa
contrato: 1
pedido: release-0.21.0
branch: melhoria/release-0.21.0-fragmento
commit: e65a7a88a80e1a16d41d18641178859be8a48e78
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# QA - release 0.21.0 (E5: junção dos fragmentos reconcilia-homolog-main e vv-2)

Links: `~/.forge-contrib/docs/pedidos/release-0.21.0.md` (E5.3), `docs/reviews/release-0.21.0.md` (review do E5, aprovado sobre `e65a7a8`). Não há UX nem API. Offline (`R-CUSTO`). Testado `e65a7a8`; o HEAD da worktree (`9d034a1`) soma só o parecer de review por cima (`git diff --name-only e65a7a8 HEAD`: `docs/reviews/release-0.21.0.md`). O QA anterior (`06b6a9e`, E1/E2.2) fica substituído por este.

## Escopo
Esta etapa cobre o que o E5 mudou: `CHANGELOG.md` (entrada `[0.21.0]`) e a remoção dos fragmentos `changelog.d/vv-2.md` e `changelog.d/reconcilia-homolog-main.md`. Versão e código não mudaram desde o `06b6a9e`; por isso a suíte e a validação do plugin rodam inteiras, e a instalação de ponta a ponta não foi repetida aqui (o CI a roda no `develop` e no `homolog`).

## Resultado

| Obrigação | Verificação | Resultado |
|---|---|---|
| Suíte inteira verde (R-QA) | `python3 -m unittest discover -s tests -v` na raiz da worktree, com `pgrep -f "unittest discover"` vazio antes | Ran 865 tests in 158.377s, OK, rc 0; 853 linhas `... ok` mais 12 `ok` isoladas (docstring), 0 FAIL/ERROR, 0 skipped |
| Plugin válido | `scripts/validar-plugin.sh` na raiz da worktree | rc 0; "Validation passed" no marketplace, no plugin e em `dev/`. Os avisos de rede são telemetria negada pelo sandbox |
| `conferir-release` (etapa que reprovou o #208) | `bin/forge-changelog conferir-release` | rc 0: `ok: changelog.d/ sem fragmentos pendentes` |
| Fragmentos consumidos | `ls changelog.d` (a pasta existe e está vazia) | 0 fragmentos; `vv-2.md` e `reconcilia-homolog-main.md` apagados |
| Linhas dos fragmentos na entrada `[0.21.0]` | para cada linha de conteúdo de `origin/develop:changelog.d/vv-2.md` e `reconcilia-homolog-main.md`, `grep -cxF` no `CHANGELOG.md` | 1 ocorrência cada (3 linhas de Adicionado/Alterado do vv-2 e 1 de Corrigido da reconciliação; as linhas de Adicionado e Corrigido ficam nas subseções já existentes e a de Alterado na subseção nova) |
| Nada além do previsto | `git diff --numstat origin/develop e65a7a8` | `CHANGELOG.md` com 5 inserções e 0 remoções; mais os dois fragmentos apagados. `git diff origin/develop e65a7a8 -- CHANGELOG.md` sem nenhuma linha removida |
| Versão e data | `grep -n '"version"' .claude-plugin/plugin.json dev/.claude-plugin/plugin.json` | `"version": "0.21.0"` nos dois; `## [0.21.0] - 2026-10-19` no CHANGELOG; `## [Não publicado]` vazio |
| Árvore limpa | `git status --short` antes de gravar este parecer | vazio |

## Achados
- Parecer aprovado: nenhum achado bloqueante ou recomendado.

Observações sem severidade: (1) a subseção `### Alterado` na `[0.21.0]` é nova no CHANGELOG; é a decisão técnica do Jarvis (Keep a Changelog põe Alterado antes de Corrigido) e o review a confere. (2) O sandbox nega a telemetria do CLI (`api.anthropic.com`, `datadoghq.com`); não afetou nenhum resultado.

## Riscos
Nenhum novo. A versão e o código são os de `06b6a9e`, já testados; a diferença do E5 é só changelog e fragmentos. O CI de `develop` e `homolog` repete a bateria completa sobre o conjunto. O commit deste parecer é `e65a7a8`; o HEAD da branch só ganha arquivos de `docs/reviews/` e `docs/qa/`, que a regra de pareceres aceita.
