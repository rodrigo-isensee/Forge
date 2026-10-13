---
id: R-NEUTRO
titulo: Neutralidade da fábrica
verificada_por: teste Neutralidade e lista termos_proibidos_hash (tests/config.json); revisão
---
# R-NEUTRO: Neutralidade da fábrica

Propósito: texto único desta regra; os outros arquivos citam o ID. Público: todo o time. Revisão: 2026-10-12.

- O Forge serve N projetos: nada específico de um projeto entra em agentes, skills, docs ou modelos. Isso inclui nomes, regras de negócio, stack fixa, dados pessoais e trechos de código do projeto de origem.
- O que é do sistema fica no projeto: código, regras de negócio, ADRs, `CLAUDE.md` e exceções locais.
- PR vindo de um projeto descreve a situação sem dados dele (se o repositório for público, o PR é público).
- O teste `Neutralidade` e a lista `termos_proibidos_hash` de `tests/config.json` são o mínimo garantido; o `tech-lead` confere o resto no review.
