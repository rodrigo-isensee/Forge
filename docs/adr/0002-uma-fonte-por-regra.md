# 0002 - Uma fonte por regra

Estado: vigente. Data: 2026-10-12.
Propósito: cada regra da fábrica tem um texto só, com ID, e todos os outros lugares citam o ID. Público: quem mantém o Forge. Revisão: 2026-10-12.

## Contexto
A mesma regra aparece com redações diferentes no Jarvis, no `tech-lead`, no modelo de `CLAUDE.md` do projeto e no `.claude/CLAUDE.md` do Forge ("a main é do usuário" está em pelo menos quatro lugares). Quando uma cópia muda e as outras não, os agentes recebem instruções contraditórias. Os `invariantes` de `tests/config.json` protegem frases espalhadas, o que reforça a duplicação, e o orçamento de linhas por agente sofre com isso.

## Decisão
1. **Pasta `docs/regras/`**, um arquivo por regra: `docs/regras/R-<ID>.md`, com frontmatter `id`, `titulo`, `verificada_por` (teste, hook, CI ou "revisão") e o texto completo da regra. `docs/regras/README.md` é o índice.
2. **IDs estáveis, nunca reaproveitados.** Lista inicial: `R-MAIN` (a main é do usuário); `R-FLUXO` (branches e promoção); `R-WIP` (1 cartão por agente e limites de coluna); `R-TETO` (agentes simultâneos, pesado um por vez, worktrees); `R-QA` (portão de QA); `R-REVIEW` (code review antes do QA); `R-DISCOVERY` (todo pedido começa com discovery); `R-CUSTO` (nada que custe dinheiro sem autorização); `R-NEUTRO` (neutralidade da fábrica); `R-COPIA` (não copiar agentes e skills para o projeto); `R-VERIFY` (nunca `--no-verify` nem `--force`). Novas regras ganham o próximo ID livre.
3. **Agentes e skills citam o ID** com o nome curto da regra (ex.: "`R-MAIN` a main é do usuário") e um link para o arquivo; o texto completo fica só na fonte. Mensagens dos hooks (ADR 0003) e do `forge-check` (ADR 0004) também citam o ID.
4. **Teste anti-duplicação:** compara sequências de 12 palavras normalizadas (minúsculas, sem pontuação) de cada `docs/regras/R-*.md` com `agents/`, `skills/`, `stacks/`, `templates/` e `docs/`. Qualquer coincidência fora da fonte falha. O nome curto da regra fica abaixo desse tamanho de propósito.
5. **`invariantes` apontam para a fonte:** os trechos protegidos passam a ser verificados em `docs/regras/R-*.md`; nos agentes, o invariante vira "cita o ID" (ex.: `agents/jarvis.md` precisa conter `R-MAIN`, `R-QA`, `R-TETO`). Mover um invariante para a fonte não é afrouxar a regra; mesmo assim, o PR da migração destaca isso no título, como pede o `.claude/CLAUDE.md`.

## Alternativas consideradas
| Opção | Prós | Contras |
|---|---|---|
| Um único `docs/regras.md` com âncoras | Um arquivo só para ler | Diffs e conflitos concentrados; frontmatter por regra fica impossível |
| Manter as cópias e só ampliar os `invariantes` | Nenhuma reorganização | Não resolve a divergência; cresce o custo de tokens |
| Injetar as regras no contexto por hook de início de sessão | O agente sempre "vê" a regra | Contradiz a ADR 0003 (hooks não injetam contexto) e paga tokens em toda sessão |

## Consequências
- Mais fácil: mudar uma regra é editar um arquivo; o teste mostra onde ela é citada; agentes ficam mais curtos.
- Mais difícil: o agente precisa ler o arquivo da regra quando precisar do detalhe. Mitigação: o nome curto basta para o caso comum, e as regras críticas também são garantidas por hook, teste ou CI.
- O `CLAUDE.md` do projeto não enxerga os arquivos do plugin; o modelo em `templates/projeto/` cita o ID e o nome curto, e o texto completo segue no Forge.
- Risco: o limite de 12 palavras pode dar falso positivo em frases genéricas; a lista de exceções do teste fica em `tests/config.json`, revisada no PR.
