# Regras da fábrica

Propósito: índice das regras com ID; cada uma tem um texto só, na sua página. Público: todo o time e quem mantém o Forge. Revisão: 2026-10-12.

Decisão: `docs/adr/0002-uma-fonte-por-regra.md`. Agentes, skills e modelos citam o ID com o nome curto (ex.: "`R-MAIN` a main é do usuário"); o texto completo fica só aqui. IDs estáveis, nunca reaproveitados; regra nova ganha o próximo ID livre. O teste `AntiDuplicacao` falha se um trecho de 12 palavras de uma regra aparecer fora da sua página.

| ID | Regra | Verificada por |
|---|---|---|
| [`R-MAIN`](R-MAIN.md) | A main é do usuário | hook, teste, permissões |
| [`R-FLUXO`](R-FLUXO.md) | Branches e promoção | CI, hook |
| [`R-WIP`](R-WIP.md) | Um cartão por agente e limites de coluna | revisão |
| [`R-TETO`](R-TETO.md) | Teto de recursos da máquina | revisão |
| [`R-QA`](R-QA.md) | Portão de QA | revisão |
| [`R-REVIEW`](R-REVIEW.md) | Code review antes do QA | revisão |
| [`R-DISCOVERY`](R-DISCOVERY.md) | Todo pedido começa com discovery | revisão |
| [`R-CUSTO`](R-CUSTO.md) | Nada que custe dinheiro sem autorização | revisão |
| [`R-NEUTRO`](R-NEUTRO.md) | Neutralidade da fábrica | teste |
| [`R-COPIA`](R-COPIA.md) | Não copiar agentes e skills para o projeto | revisão |
| [`R-VERIFY`](R-VERIFY.md) | Nunca `--no-verify` nem `--force` | permissões, invariantes |
