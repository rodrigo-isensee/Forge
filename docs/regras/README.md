# Regras da fábrica

Propósito: índice das regras com ID (como cada uma é verificada fica no frontmatter dela). Público: todo o time e quem mantém o Forge.

Decisão: `docs/adr/0002-uma-fonte-por-regra.md`. Agentes, skills e modelos citam o ID com o nome curto; o texto fica só aqui (o teste `AntiDuplicacao` reprova trecho de 12 palavras copiado; exceções em `anti_duplicacao.excecoes` de `tests/config.json`). IDs nunca se reaproveitam.

**Validade e medida (decisão do dono, 2026-11-08):** toda regra traz `Revisar em:` e `Medida:` (o número que a justifica, ou "sem medida"); `forge-check regras` aponta as vencidas. Regra nova só com medida (`R-DECISAO`).

| ID | Regra |
|---|---|
| [`R-MAIN`](R-MAIN.md) | A main é do usuário |
| [`R-FLUXO`](R-FLUXO.md) | Branches, integração contínua e promoção |
| [`R-WIP`](R-WIP.md) | Um cartão por agente e limites de coluna |
| [`R-TETO`](R-TETO.md) | Teto de recursos da máquina |
| [`R-QA`](R-QA.md) | Portão de QA |
| [`R-REVIEW`](R-REVIEW.md) | Code review em toda entrega, numa passada |
| [`R-DISCOVERY`](R-DISCOVERY.md) | Todo pedido começa com discovery |
| [`R-CUSTO`](R-CUSTO.md) | Nada que custe dinheiro sem autorização |
| [`R-NEUTRO`](R-NEUTRO.md) | Neutralidade da fábrica |
| [`R-COPIA`](R-COPIA.md) | Não copiar agentes e skills para o projeto |
| [`R-VERIFY`](R-VERIFY.md) | Nunca `--no-verify` nem `--force` |
| [`R-DECISAO`](R-DECISAO.md) | Decisões do dono uma a uma, com opções e recomendação, sem prazo que decida |
| [`R-CONFORMIDADE`](R-CONFORMIDADE.md) | Controles não se contornam; o que está em vigor é do usuário |
| [`R-CONTRIB`](R-CONTRIB.md) | Contribuição ao Forge: projeto abre PR, nunca mescla |
| [`R-SEGURANCA`](R-SEGURANCA.md) | Parecer de segurança quando há gatilho |
| [`R-PROVA`](R-PROVA.md) | Afirmação com prova |
| [`R-BRIEF`](R-BRIEF.md) | Brief selado pela ferramenta antes da delegação |
