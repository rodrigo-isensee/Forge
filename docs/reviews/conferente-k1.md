---
tipo: review
contrato: 1
pedido: conferente-k1
branch: melhoria/conferente-k1
commit: 5177b4316baddcfd3610e10ec015f99ba7090002
parecer: reprovado
revisor: forge:tech-lead (independente)
data: 2026-10-15
---
# Review independente: conferente confiável, fatia K1 (texto e forma)

Escopo: `git diff bad3edd...5177b43`, 6 commits e 8 arquivos. Conferi o texto contra as linhas C1, C3, C5, C6, C7, C8 e C10 da §3 e a linha K1 da §6 da proposta `conferente-confiavel.md`, e contra o pedido `conferente-k1`. Não escrevi esta branch.

## Parecer: **reprovado** (um ajuste de uma linha)
Os sete itens estão implementados como a proposta pede, e os invariantes só acrescentam. Há um problema: a regra do veredito do modo brief continua literal ("qualquer campo diferente de `ok`"). Por essa regra, a linha nova `corte: etapa (ok)` reprova o brief. Isso traz de volta o vai e volta que a K1 quer acabar.

| # | Arquivo:linha | Problema | Sugestão | Severidade |
|---|---|---|---|---|
| 1 | `agents/conferente.md:50` (com a `:40`) | A `:40` define a saída `corte: etapa (ok)` para etapa de outro papel. A `:50` diz que "qualquer campo diferente de `ok` (menos `não verificável` ...) dá `veredito-brief: reprovado`". O valor `etapa (ok)` não é `ok`. Lido ao pé da letra, e o haiku lê assim, todo brief que põe uma etapa de outro papel no "Fora do escopo" sai reprovado. É o mesmo caso do pós-release 0.15.0 que motivou o C1. | Na `:50`: "Qualquer campo diferente de `ok` (menos `não verificável` e `corte: etapa (ok)`, que aparecem mas não reprovam sozinhos) dá ...". Se der, acrescente na `:40` que, havendo vários itens, a linha `corte:` lista cada um e só `sem marca` reprova. Convém um invariante para o trecho novo da `:50`. | **bloqueia** |
| 2 | `docs/regras/R-PROVA.md:11`, `agents/conferente.md:51`, `agents/jarvis.md:63` | O vocabulário de `espera:` é `rc=0 \| contém \| igual \| linhas=N`, sem limite mínimo. A própria proposta (§6, K1, PQ-2, PQ-4 e PQ-5) usa "linhas ≥ 1" e "≥ 1 linha". Quando o brief tiver um PQ assim, o conferente da entrega não terá a regra para compará-lo, e o do brief pode marcá-lo como forma inválida. | Incluir `linhas>=N` no formato das três fontes, ou deixar escrito que `linhas=N` é exato e mandar reescrever esses PQs. | recomendado |
| 3 | `agents/conferente.md:41` | "Brief com commit precisa de ao menos um PQ `sha`, `push` ou `arquivo`" (C6) não diz qual linha de saída sai quando falta esse PQ. O haiku vai inventar um rótulo. | Ex.: "Falta: `forma: sem PQ que o conferente confira`". | recomendado |
| 4 | `agents/conferente.md:51` | O texto antigo dizia "`cmd` → rode o comando se for da lista acima". O novo só diz "compare só o que `espera:` diz". Que o comando roda ficou implícito. | "`cmd` → rode o comando (se for da lista acima) e compare só o que `espera:` diz ...". | recomendado |
| 5 | `docs/regras/R-DECISAO.md:15` | A regra ainda diz que, em "decisão, brief ou entrega", o conferente reprova com `corte: sem marca`. Pelo C10, no modo entrega o rótulo agora é `pendente:`. As fontes divergem no rótulo, não no efeito. | Trocar para "(`corte: sem marca` no brief; `pendente:` na entrega)". O arquivo fica fora dos 8 do diff e o texto é protegido, por isso a decisão é do autor: nesta fatia ou num cartão. | recomendado |
| 6 | `changelog.d/conferente-k1-texto-e-forma.md` | O nome não segue `changelog.d/<branch-sem-prefixo>.md`, que daria `conferente-k1.md` (`bin/forge-changelog:4` e `:67`). O CI não barra, mas a convenção existe para evitar colisão e para dar rastreio. | Renomear para `changelog.d/conferente-k1.md`. | recomendado |

## O que foi conferido e está certo
- **C1:** o `_modelo.md` do pedido ganhou `E1.` e `## Etapas` com `E1.1 (<agente>)` e `E1.2 (dono)`. No `jarvis.md`, o passo 1 traz IDs e Etapas, e o item 3 do prompt-padrão pede `(E2)` e etapa sem a marca. No conferente, o item 3 pareia por ID, devolve `corte: não verificável (pedido sem IDs)` sem reprovar (é a mitigação da proposta) e exige que o trecho exista literalmente em `## Etapas`. Esta delegação de review serve de exemplo: E1.1 é do mesmo papel do destino (tech-lead) e por isso foi cortada com a marca, como o texto exige.
- **C3:** o brief vai para `docs/briefs/<pedido>-<destino>-<n>.md` em `R-BRIEF`, no `jarvis.md:63` e na entrada do modo brief (`Arquivo:`, `test -e`, `cat`, cópia igual ao arquivo). O `forge-check brief --prompt-igual` é da K2, e o `forge-check docs` não varre `docs/briefs/`. Até a K2, quem compara a cópia com o arquivo é a leitura do haiku. É um risco conhecido, com mitigação já planejada, e não conta como achado.
- **C5 (só texto):** o formato está em `R-PROVA`, no item 1 do modo entrega e no prompt-padrão. O texto diz que o rc ≠ 0 não reprova quando a espera é de saída, e que "saída de X" vale como `contém` na transição. `forma: PQ-n sem espera` fica no brief.
- **C6:** a linha `PQ-n do autor | <comando> → conferido pelo QA (R-QA) e pelo lastro` está lá. Ela não reprova (`:67`) e não conta como `não verificável`. `R-PROVA` diz o mesmo.
- **C7:** `Base-sha:` está na entrada do modo entrega e no `jarvis.md`. Antes do diff, o conferente roda `git merge-base --is-ancestor` (forma já liberada em `conferente.md:24`). O diff usa o sha, não a base local.
- **C8:** o anexo implícito só vale por acréscimo, conferido com `git diff --numstat`. A saída `escopo: anexo com remoção` reprova. O "mover cartão" vai no Entregar, pelo `jarvis.md`.
- **C10:** os modos estão separados no topo (uma linha por modo, `a691f24`). `corte:` aparece só no brief e `pendente:` só na entrega, tanto no item 3 da entrega quanto no exemplo de saída e no veredito (`:67`). Não achei contradição entre os dois modos. A única inconsistência é a de dentro do modo brief (item 1). O começo do modo brief "por `forge-check brief`" é da K2, como manda a §6.
- **Invariantes (`tests/config.json`):** só há acréscimos. As cinco linhas `-` do diff são a mesma entrada com a vírgula nova. São 8 trechos novos em `conferente.md`, 3 em `jarvis.md`, 2 no `_modelo.md`, 2 em `R-PROVA` e 1 em `R-BRIEF`, e eles cobrem os trechos que viraram regra. Nenhum item existente foi afrouxado.
- **Correção `5177b43`:** `ambiente_limpo()` acrescenta `maintenance.auto=false` e `gc.auto=0` por `GIT_CONFIG_COUNT/KEY/VALUE`. Isso vale só para o processo filho, não grava nada e não persiste. O `HookPrePush.setUp` grava `receive.autogc=false` só no `remoto.git` temporário (`self.tmp`). O helper `git()` (`tests/test_forge.py:407`) é o único que usa esse env. Nada toca o repositório real nem o `~/.gitconfig`. A causa está documentada em `docs/briefs/conferente-k1-causa.md`, com a prova `repack disparado: 1` contra `0`, e bate com o git local (2.55.0).
- **Changelog:** o fragmento existe e está no formato certo (`### Adicionado` + linha). O nome é o item 6.
- **Regras invioláveis:** `R-NEUTRO` ok, porque não há nome de projeto nem stack. `R-CUSTO` ok, porque não há comando pago. O `plugin.json` e o `CHANGELOG.md` não foram tocados.

## Ferramentas (citadas, não refeitas)
- Suíte completa: rodada pelo autor e não refeita aqui, porque a segurança roda em paralelo. Rodei só as classes que este diff toca, no HEAD `5177b43`: `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.RegrasComId tests.test_forge.Agentes tests.test_forge.HookPrePush tests.test_forge.IsolamentoDoGit`, com saída `Ran 19 tests in 1.652s` / `OK`.
- `scripts/validar-plugin.sh`: não rodado. Fica com o QA (`R-QA`).

## Para o security-engineer (aponto, não decido)
- O C3 muda a entrada do conferente: o brief passa a ser lido do disco com `cat`. Um brief gravado em disco pode trazer instrução ao conferente, como antes, e a regra de `conferente.md:10` continua valendo. Não há comando novo na lista do `so_leitura`.

## Pendências fora desta fatia
- PQ-6 da linha K1 (um brief real gravado em `docs/briefs/` e conferido, com a saída colada no PR): é prova de PR, na E3.2.
