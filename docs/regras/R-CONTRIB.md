---
id: R-CONTRIB
titulo: Contribuição ao Forge - projeto abre PR, nunca mescla
verificada_por: hook parecer, rulesets e catraca do CI (ADR 0008)
---
# R-CONTRIB: Contribuição ao Forge - projeto abre PR, nunca mescla

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time, em qualquer projeto. Revisão: 2026-10-13. Decisão: `docs/adr/0008-governanca-de-contribuicoes.md`.

- **Quem trabalha em um projeto abre PR para a `develop` do Forge e nunca o mescla**; mesclar no Forge é do `tech-lead` (e do usuário na `main`), a partir de um clone do próprio Forge.
- **Nenhum portão tem exceção, nem para o dono:** checks, pareceres e rótulos valem para todos os autores.
- **Checklist de merge** (Jarvis e `tech-lead`): na `develop` e na `homolog`, mescle apenas com: todos os checks verdes (`gh pr checks`), pareceres válidos (`forge-check pr`) e, se a catraca exigir, o rótulo do dono; na `main`, nunca (`R-MAIN`).
- O PR é indicado pelo nome da branch, não só pelo número.
- O clone de contribuição (`~/.forge-contrib/<projeto>`) nasce com `core.hooksPath` ativado.
