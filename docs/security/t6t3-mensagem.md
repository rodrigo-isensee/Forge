---
tipo: revisao-seguranca
contrato: 1
pedido: t6t3-mensagem
branch: melhoria/t6t3-mensagem
commit: 0c2ef9ca9453736aecefad78a48c284dc599025e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: t6t3-mensagem

Lote E1, E2, E4 e E5 do T6T3-MENSAGEM (pedido T6T3-MENSAGEM-REV, E2.1). Diff `d14a713...0c2ef9c`.

## Gatilhos
`R-SEGURANCA`: controle do Forge (`bin/forge-check`, `agents/conferente.md`, `agents/jarvis.md`). Sem `hooks/`, workflow nem segredo.

## Achados
- A1 (recomendado) bin/forge-check:4609 · `--entrega` não confere o `Pedido:` do cabeçalho do brief com `--pedido`: o `Desde:` pode vir de outro pedido e a mensagem sai sem aviso
- A2 (recomendado) bin/forge-check:4604 · cabeçalho do brief com `Etapa:` ou `Branch:` repetido: vale a primeira linha, sem recusa; o conferente pode ler outra
- A3 (recomendado) bin/forge-check:4669 · `--entrega` não passa pelo `forge-check brief` (só a forma do cabeçalho): brief reprovado também gera mensagem; o conferente cobre, mas é lacuna

## Detalhe dos achados
Verificado e sem defeito: (1) hash: `Brief-sha256` sai do mesmo buffer lido uma vez, medido (teto 256 KiB) e impresso (`bin/forge-check:4619`, `4672`); não há segunda leitura, então não passa hash diferente do arquivo. (2) Etapa: vem da linha `Etapa:` do cabeçalho; `--etapa` diferente é recusado antes de imprimir (`4665-4668`, sondado: rc=2 com a etapa certa); sem `Etapa:` no brief o `--entrega` recusa. (3) Leitura: o `--entrega` lê só o brief (via `caminho_de_brief`, restrito a `docs/briefs/`) e o pedido; a worktree só passa por `isabs` e `isdir`, nunca é lida; `--anterior`, `--ref` e `--parecer` são recusados. (4) Injeção: campos de linha passam por `recusa_do_campo` e o texto do brief por `recusa_do_texto` (delimitador, controle, Cf, Zl, Zp) antes de qualquer saída; Branch, Base, Base-sha e Etapa vêm desse texto já limpo. (5) Testes do item: 5 verdes. PA-7 conferido (AR-1 a AR-9): sem recorrência (nenhum `python` sem `-I` novo, nem hook, nem lista negativa de ambiente).

A1: sondei brief do pedido `p` com `--pedido outro`: rc=0 e `Desde:` do outro pedido. Caminho: erro do Jarvis (não de atacante) leva o conferente a medir o delta contra a base errada e a gerar `não cumpriu` sem mérito. Severidade baixa. Correção mínima: recusar quando o `Pedido:` do cabeçalho existe e o stem difere. Esforço P. Dono: tech-lead. Informativo: `caminho_do_pedido` aceita qualquer arquivo existente em `--pedido` (comportamento anterior; só linhas `conferida <sha40>` saem, sem vazamento).

A2: sondei cabeçalho com `Etapa: codigo` e depois `Etapa: pr`: a mensagem sai com `codigo`. Quem escreve o brief é o Jarvis, sem fronteira de confiança cruzada; severidade baixa. Correção mínima: recusar a segunda ocorrência no cabeçalho. Esforço P. Dono: tech-lead.

A3: o `--entrega` diz no docstring que não reconfere; a defesa é o conferente. Severidade informativa. Correção mínima: aceitar e documentar, ou chamar `avaliar_brief`. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, `zizmor` e `semgrep` não estão no PATH (lacuna; o diff não toca workflow nem segredo). Análise manual e sondas locais com `python3 -I` em raiz sintética.
