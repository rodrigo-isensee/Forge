---
id: R-CONTRIB
titulo: Contribuição ao Forge - projeto abre PR, nunca mescla
verificada_por: hook parecer, rulesets e catraca do CI (ADR 0008)
---
# R-CONTRIB: Contribuição ao Forge - projeto abre PR, nunca mescla

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time, em qualquer projeto. Revisão: 2026-10-13. Decisão: `docs/adr/0008-governanca-de-contribuicoes.md`.

- **Quem trabalha em um projeto abre PR para a `develop` do Forge e nunca o mescla**; mesclar no Forge é da sessão que mantém o Forge — `tech-lead` ou Jarvis numa sessão cuja raiz é um clone do próprio Forge — e do usuário na `main`. Uma sessão de projeto nunca é essa sessão, mesmo com o mesmo login.
- **Nenhum portão tem exceção, nem para o dono:** checks, pareceres e rótulos valem para todos os autores.
- **Checklist de merge** (Jarvis e `tech-lead`): na `develop` e na `homolog`, mescle apenas com: todos os checks verdes (`gh pr checks`), pareceres válidos (`forge-check pr`) e, se a catraca exigir, o rótulo do dono; na `main`, nunca (`R-MAIN`). O hook `conformidade` libera o merge ao `jarvis` e ao `tech-lead` só quando o hook `parecer` aceita; a `main` fica barrada para todos.
- O PR é indicado pelo nome da branch, não só pelo número.
- O clone de contribuição (`~/.forge-contrib/<projeto>`) nasce com `core.hooksPath` ativado.
