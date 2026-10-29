---
tipo: revisao-seguranca
contrato: 1
pedido: t6t3-mensagem
branch: melhoria/t6t3-mensagem
commit: e31bf9dc10c1eb8f5693c4b71f3beb44d010f264
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: t6t3-mensagem

Lote E1, E2, E4 e E5 do T6T3-MENSAGEM (pedido T6T3-MENSAGEM-REV, E2.1). Diff `d14a713...e31bf9d`; revalidação por delta `0c2ef9c..e31bf9d` (volta 1).

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

## Revalidação por delta (0c2ef9c..e31bf9d)
Delta em código: `bin/forge-check` (`mensagem_de_entrega`: `Desde:` passa a ser `bases_do_pedido(...)[-1]`, `bin/forge-check:4610-4616`), `agents/conferente.md` (reflow de parágrafos e o bloco de entrada em uma linha por campo) e testes. Sem hook, workflow nem segredo; os demais arquivos são pareceres e mutantes. A1 a A3 seguem como recomendação (a volta não os tocou; não bloqueiam).
Verificado: (1) hash e etapa: o trecho do hash (`4619`, `4672`) e a conferência de `--etapa` não mudaram, então não abre mensagem com hash diferente do arquivo nem etapa trocada. (2) Caractere de controle: a worktree segue só por `isabs` e `isdir` e o valor com controle é recusado sem ser impresso (teste novo `controle_no_worktree`, verde); o `Desde:` imprime só `sha40` casado por regex (`CONFERIDA`, `BASE_DO_DONO`). (3) O Desde novo só lê o `## Histórico` do pedido (`secoes_por(..., "Histórico")`, `bin/forge-check:814`); a linha de base do dono só vale com `DECISÃO DO DONO` no pedido (`816`), como no `entrega`. Informativo: o `Desde:` da mensagem não confere ancestralidade (quem a confere é o `desde_valido` do `forge-check entrega`, que o conferente roda); sha inexistente leva a recusa lá, não a delta errado. (4) Testes do item: 11 verdes (`tests.test_mensagem_conferente`). PA-7 reconferido: nenhum `python` sem `-I` novo, nem hook, nem lista negativa de ambiente. Carga conferida antes do teste (4,25).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, `zizmor` e `semgrep` não estão no PATH (lacuna; o diff não toca workflow nem segredo). Análise manual e sondas locais com `python3 -I` em raiz sintética.
