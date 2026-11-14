---
tipo: review
contrato: 1
pedido: release-0.47.0
branch: melhoria/release-0.47.0-b
commit: 0867f7157f37ca5ea76ef31824cbb159c215086f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: release-0.47.0

Marca refeita da 0.47.0 no head 0867f715 (E2.21): os PRs 541, 544, 542 e 543 entraram na develop depois da release e seus quatro fragmentos foram para a entrada 0.47.0.

## Achados

## Sondas

## Parecer
Aprovado. O commit 0867f715 só toca `CHANGELOG.md` (4 linhas) e apaga os quatro fragmentos de `changelog.d/` (mp1311-worktree-jarvis, v047-ci-serie, v047-jarvis-parte2, v047-caminho-runner). Cada fragmento aparece uma vez na entrada 0.47.0, na seção do seu tipo (três em Alterado, um em Corrigido), com o texto idêntico ao do fragmento.

Versão: `plugin.json` e `dev/.claude-plugin/plugin.json` seguem em 0.47.0 e batem com o título da entrada; `[Não publicado]` fica vazio e `changelog.d/` só traz o README (`forge-changelog conferir-release`: ok). `tests/test_changelog.py`: 74 testes, OK. `forge-check docs`: sem erro. O CI do PR não existe (branch sem PR), por isso só os testes leves.

Domínio contra a main: o diff é a release inteira (202 arquivos, de `bin/`, `hooks/`, `agents/`, `skills/`, `stacks/` e `.github/`), revisada nos PRs de origem; o delta deste head é só changelog, sem código novo. Sem achado bloqueante nem recomendado.
