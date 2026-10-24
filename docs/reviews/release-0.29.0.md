---
tipo: review
contrato: 1
pedido: release-0.29.0
branch: melhoria/release-0.29.0
commit: 49cf5c32cb55cb944c3d103b632321bb6b5a4016
parecer: aprovado
revisor: forge:tech-lead (REL-029-REV, E1.1)
data: 2026-10-23
---
# Review: release 0.29.0

Escopo: `git diff db55859...49cf5c3` (23 arquivos, 40 inserções, 63 remoções): só versão, changelog e fragmentos. Conferência só com `git show`/`git diff`.

Veredito sobre `49cf5c3`: **APROVADO**, sem achados.

## Achados

## O que foi conferido
1. **Versão.** `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` passam de 0.28.0 para 0.29.0 e o título da seção nova é `## [0.29.0] - 2026-10-23`: as três batem. Minor (melhoria compatível, SemVer do `CLAUDE.md`).
2. **Changelog (ADR 0006).** Os 20 fragmentos apagados de `changelog.d/` (lidos em `db55859`) têm todas as linhas de texto presentes, byte a byte, na seção 0.29.0 e sob o cabeçalho certo (Adicionado, Alterado, Corrigido), incluindo os de mais de uma linha e de mais de uma classe (`impl-d4-textos-dono2`, `impl-n-fechar-b2`, `lote-forge-check-0.28.0`, `suite-paralela-d4`). A seção fica logo abaixo de `## [Não publicado]`, que segue vazia; a pasta `changelog.d/` fica sem fragmentos.
3. **Nada além.** `git diff --stat`: dois `plugin.json` (1 linha cada), `CHANGELOG.md` (+38) e os 20 fragmentos (-63). Nenhum outro arquivo mudou; `tests/config.json` intocado.
4. **Regras.** R-NEUTRO, R-CUSTO, R-VERIFY: nada de código, projeto ou serviço pago neste commit.

## Recomendações (não bloqueiam)
- R1 · Várias linhas não terminam em ponto final, herdado dos fragmentos; cosmético.
- R2 · Segurança e QA desta release são de outros papéis e não foram refeitos aqui.
