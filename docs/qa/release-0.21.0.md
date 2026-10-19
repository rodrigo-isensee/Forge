---
tipo: qa
contrato: 1
pedido: release-0.21.0
branch: melhoria/release-0.21.0
commit: 06b6a9e0959474fb787a58cc60725cc65a837b60
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# QA - release 0.21.0

Links: `~/.forge-contrib/docs/pedidos/release-0.21.0.md` (E1, E2.2), `docs/reviews/release-0.21.0.md` (aprovado). Não há UX nem API. Offline (`R-CUSTO`). Testado `06b6a9e`; o HEAD da worktree (`1d50b11`) só soma o parecer de review por cima (`git diff --stat 06b6a9e HEAD`: 1 arquivo, `docs/reviews/release-0.21.0.md`).

## Escopo
A release só move a versão e o texto do changelog (E1); o código das quatro melhorias (T-1, CONF-ANEXO-PARECERES, S-18, BP-1) já passou por QA próprio. Aqui: suíte inteira, validação do plugin, instalação de ponta a ponta, versões e changelog.

## Resultado

| Obrigação | Verificação | Resultado |
|---|---|---|
| Suíte inteira verde (R-QA) | `python3 -m unittest discover -s tests` na raiz da worktree (nenhuma outra suíte rodando, conferido com `pgrep -af "unittest discover"`) | Ran 813 tests in 163.239s, OK |
| Plugin válido | `scripts/validar-plugin.sh` | "Validation passed" nos manifestos do marketplace, do plugin e de `dev/` |
| Instalação de ponta a ponta (como o CI) | `git archive 06b6a9e` extraído em `$TMPDIR` e `bash tests/e2e-instalacao.sh` | `e2e-instalacao: ok (plugin instalado, 8 agentes, 9 skills, projeto inicializado)`, rc 0 (CLI 2.1.303; o CI fixa 2.1.296) |
| Versão 0.21.0 nos dois manifestos | `grep -n version .claude-plugin/plugin.json dev/.claude-plugin/plugin.json` | `"version": "0.21.0"` nos dois (linha 3) |
| Entrada no CHANGELOG | `sed -n '/^## \[0.21.0\]/,/^## \[0.20/p' CHANGELOG.md` | `## [0.21.0] - 2026-10-19` com S-18, T-1 (Adicionado) e BP-1, CONF-ANEXO-PARECERES (Corrigido) |
| Fragmentos consumidos | `ls changelog.d \| grep -E '^(t-1\|conf-anexo-pareceres\|s-18\|bp-1)\.md$'` | nenhum (0) |
| Árvore limpa após a bateria | `git status --short` | vazio |

## Achados
Crítico 0, alto 0, médio 0, baixo 0. Sem bug aberto; `aceite_usuario` não se aplica.

Observações sem severidade: (1) as saídas dos comandos mostram negações de rede para `api.anthropic.com` e `datadoghq.com` do sandbox (telemetria do CLI); não afetaram nenhum resultado. (2) `docs/qa/_modelo.md` não existe na raiz do Forge (só em `templates/projeto/docs/qa/`); o formato seguiu o parecer `docs/qa/bp-1.md`. (3) Vermelho antes do verde e mutação não se aplicam: a release não traz teste nem código de produção novos.

## Riscos
Nenhum novo; o CI de `homolog` repete a bateria completa sobre o conjunto.
