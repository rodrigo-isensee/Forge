# Regras da fábrica

Propósito: índice das regras com ID; cada uma tem um texto só, na sua página. Público: todo o time e quem mantém o Forge. Revisão: 2026-10-14.

Decisão: `docs/adr/0002-uma-fonte-por-regra.md`. Agentes, skills e modelos citam o ID com o nome curto (ex.: "`R-MAIN` a main é do usuário"); o texto completo fica só aqui. IDs estáveis, nunca reaproveitados; regra nova ganha o próximo ID livre. O teste `AntiDuplicacao` falha se um trecho de 12 palavras de uma regra aparecer fora da sua página; exceções (falso positivo em frase genérica) ficam em `anti_duplicacao.excecoes` de `tests/config.json`, revisadas no PR.

| ID | Regra | Verificada por |
|---|---|---|
| [`R-MAIN`](R-MAIN.md) | A main é do usuário | hook, teste, permissões |
| [`R-FLUXO`](R-FLUXO.md) | Branches e promoção | CI, hook |
| [`R-WIP`](R-WIP.md) | Um cartão por agente e limites de coluna | revisão, hook |
| [`R-TETO`](R-TETO.md) | Teto de recursos da máquina | revisão, hook |
| [`R-QA`](R-QA.md) | Portão de QA | revisão, hook |
| [`R-REVIEW`](R-REVIEW.md) | Code review antes do QA | revisão, hook |
| [`R-DISCOVERY`](R-DISCOVERY.md) | Todo pedido começa com discovery | revisão |
| [`R-CUSTO`](R-CUSTO.md) | Nada que custe dinheiro sem autorização | revisão |
| [`R-NEUTRO`](R-NEUTRO.md) | Neutralidade da fábrica | teste |
| [`R-COPIA`](R-COPIA.md) | Não copiar agentes e skills para o projeto | revisão |
| [`R-VERIFY`](R-VERIFY.md) | Nunca `--no-verify` nem `--force` | permissões, invariantes |
| [`R-DECISAO`](R-DECISAO.md) | Uma decisão por vez, com opções e recomendação | conferente (corte de escopo), revisão |
| [`R-CONFORMIDADE`](R-CONFORMIDADE.md) | Controles não se contornam; o que está em vigor é do usuário | hook, sandbox, permissões, vigia |
| [`R-CONTRIB`](R-CONTRIB.md) | Contribuição ao Forge: projeto abre PR, nunca mescla | hook, rulesets, CI |
| [`R-SEGURANCA`](R-SEGURANCA.md) | Parecer de segurança quando há gatilho | revisão, hook |
| [`R-PROVA`](R-PROVA.md) | Afirmação com prova | conferente, revisão |
| [`R-BRIEF`](R-BRIEF.md) | Brief conferido antes da delegação | conferente, revisão |
