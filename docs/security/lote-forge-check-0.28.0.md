---
tipo: revisao-seguranca
contrato: 1
pedido: lote-forge-check-0.28.0
branch: melhoria/lote-forge-check-0.28.0
commit: 1d001b1348dc915917f314eb99881e21dd1a4989
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: lote-forge-check-0.28.0

Entrega revisada: `ad6d96ce6b19663f7695d361d61f59c7545bdca6..1d001b1348dc915917f314eb99881e21dd1a4989`. Revalidação por delta sobre o parecer anterior (`389096e`, reprovado por A1 e A2): as voltas 1 e 2 (`c190356`, `56ae496`, `f49fd41`), o merge da develop (`24754c9`) e a ampliação da isenção de QA (`1d001b1`). Leitura estática e os módulos de teste do delta rodados na worktree (`test_isencoes`, `test_testes_tocados`, `test_anotar`, `test_citacao`: 56 testes, OK). Sem achado bloqueante.

## Achados

## Revalidação
- A1 anterior (`anotar` grava em qualquer arquivo), metade do `forge-check`: corrigida em `56ae496`. `cmd_anotar` (`bin/forge-check:1641-1644`) resolve o alvo por `pedido_para_anotar` e recusa o que está fora de `docs/pedidos/`, ausente ou link simbólico. A metade do hook `conformidade` (o `anotar` e o `brief gerar --gravar` tratados como escrita em pasta do jarvis) fica para a volta 3, com revalidação própria, como o pedido define; este parecer não a cobre.
- A2 anterior (`--citar .env:1`): corrigida em `c190356`. `linhas_da_fonte` (`bin/forge-check:3734` e `:3745`) só aceita documento `.md` cujo nome não é de `.env`, conferido no nome pedido e no nome real depois do `realpath` (um `.md` que é link para o `.env` não passa).
- Merge da develop (`24754c9`): toda linha que a develop acrescentou em `bin/forge-check` desde a base comum está no HEAD (conferido linha a linha); `cmd_fila` (P9) é idêntica à da develop e segue só leitura, sem rede; o `executar` mantém `anotar`, `fila` e o `brief gerar` com os argumentos novos. Em `bin/forge-testes`, `FORGE_CHECK` é a união das duas listas (19 módulos), sem perder `test_hooks`, `test_catraca` nem `test_guarda_*`; o pre-push dirigido não deixa de rodar teste de portão. `tests/test_testes_tocados.py` confere a união. A MODELOS-NO-FORGE (`test_modelos_citados` em `CONTEUDO`) está preservada.
- Isenção de QA (`1d001b1`): `MD_DE_CONTROLE` (`bin/forge-check:513`) passa a incluir `stacks/*/seguranca.md`, `stacks/*/pronto.md`, `templates/projeto/` e qualquer `CLAUDE.md`, conforme a decisão do dono de 2026-10-21 14:03; só reduz o que é isento (endurece), e a lista de arquivos segue `--no-renames`, então renomear um arquivo de controle para fora dele não escapa. A recomendação R3 do parecer anterior foi atendida.

## Gatilhos
- Controles do Forge: `docs/regras/R-BRIEF.md` e `tests/config.json` no diff (gatilho do `forge-check pr`).
- Portões: `hooks/parecer.py` (isenção do M13) e `bin/forge-check` (`pr`, `brief`, conferência do conferente), marcados no pedido.
- Leitura de caminho vindo de texto (P3, conferência de citação e `--citar`) e escrita nova em pastas de outro papel (P4 `anotar`, P6 `--gravar`).
- Rede: `gh pr view` no `brief gerar` (P5), gratuito (`R-CUSTO`).

## Item a item
- M16 (`5f3ae67`, `f49fd41`): aprovado. A correção do review (o item citado não cobre a etapa do papel do destino) só aperta a conferência.
- P2 (`84db057`), M4 (`9921db8`), M5 e P2 tabela (`3101c0d`), P5 (`158af43`), testes (`389096e`): aprovados no parecer anterior, sem mudança no delta.
- M13 (`8ccff9f`, `1d001b1`): aprovado; falha fechada com diff vazio ou base ausente, lista de controle ampliada pela decisão do dono.
- P6 (`bfed7d5`, `9ffd14c`): aprovado no que entrega; a escrita por papel que não é o jarvis fica com a metade do hook (volta 3).
- P4 (`c23ea30`, `56ae496`): aprovado na metade do `forge-check`.
- P3 (`8f8fa3c`, `c190356`): aprovado.

**Recomendações (não bloqueiam):**
- R1. `gh pr view` no `brief gerar`: passe `--` antes da branch (uma branch que começa com `-` vira opção do `gh`). Baixa.
- R2. P6: o `0444` do brief aprovado não é trava (a ferramenta Write sobrescreve); abra o cartão da P6b (hook `conformidade`, com parecer de segurança) e não o cite como proteção até lá.
- R4. `CONTROLES_DO_FORGE` não inclui `hooks/`, `bin/forge-check` nem `agents/`: o gatilho de segurança deste lote veio da marcação no pedido, não do diff. Anterior ao lote; vale um cartão.
- R5. `cmd_anotar` reescreve o pedido inteiro depois de checar o link simbólico; prefira arquivo temporário e renomear, para não truncar o pedido numa falha.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `shellcheck` não estão no PATH deste ambiente (lacuna registrada; nada foi instalado). O delta não toca workflow, dependência nem contêiner. Nenhum segredo real foi lido nem exibido.
