---
tipo: review
contrato: 1
pedido: f1-lote5-verificacao
branch: melhoria/f1-lote5-verificacao
commit: 54c9b7b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Parecer de autor: lote 5 da fonte F1 (regras por ferramenta ou leitura)

Escopo: seção "Regras e quem as decide" em `templates/projeto/docs/engineering/praticas.md`, parágrafo no checklist da skill `engineering-practices`, frase no item 3 do `tech-lead`, invariantes em `tests/config.json` (só acrescentam) e linha em `[Não publicado]`.

Conferido: 310 testes verdes; `scripts/validar-plugin.sh` passa. Comandos como marcadores genéricos, sem stack (`R-NEUTRO`); sem custo (`R-CUSTO`). `hooks/conformidade.json` intocado de propósito: "tech-lead não grava fora de `docs/reviews/`" fica como recomendação para PR futuro (no CHANGELOG). Migração: o `forge-upgrade` não migra, pois o `praticas.md` é do projeto; ajuste manual opcional, registrado no CHANGELOG.

Parecer de autor, feito pelo mesmo agente que escreveu a mudança; o review independente fica a cargo do `tech-lead` no PR.
