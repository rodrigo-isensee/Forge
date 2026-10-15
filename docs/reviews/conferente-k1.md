---
tipo: review
contrato: 1
pedido: conferente-k1
branch: melhoria/conferente-k1
commit: 43a7c5a1f3091d50a8fbade2a251c765f3587a4b
parecer: reprovado
revisor: forge:tech-lead (independente)
data: 2026-10-15
---
# Re-review independente (volta 2): conferente confiável, fatia K1

Escopo: `git diff bad3edd...43a7c5a`, com foco na volta 2 (`git diff 28be2c9..43a7c5a`: `6d021b3`, `85ccb68` e `43a7c5a`; 6 arquivos, +16/−8). Conferi o diff contra o brief da volta 2 (`docs/briefs/conferente-k1-tech-lead-3.md`, Entregar 1–6), contra o pedido `conferente-k1` e contra as linhas C1, C3, C5, C6, C7, C8 e C10 (§3) e K1 (§6) da proposta. Não escrevi esta branch. O parecer anterior (`28be2c9`, sobre `5177b43`) é substituído por este.

## Parecer: **reprovado** (só invariantes; o texto das regras está certo)
O bloqueante anterior e os itens 1–5 do brief estão resolvidos no texto. O item 6 não está: dois dos quatro trechos novos de 1–4, entre eles a correção do bloqueante, não têm invariante que falhe se forem apagados. Os testes continuam verdes sem essas regras, e é exatamente essa regressão que o invariante deve impedir. Abaixo vai tudo de uma vez, para fechar numa volta só.

### Evidência (mutação)
Para cada trecho novo, apaguei-o de uma cópia do texto em memória e conferi quais regex de `invariantes` (`tests/config.json`) deixam de casar:

| Trecho apagado | Invariante que falha |
|---|---|
| `conferente.md:50`: ` e \`corte: etapa (ok)\`, que aparecem mas não reprovam` (item 1, o bloqueante) | nenhum (`corte: etapa \(ok\)` também casa na `:40`) |
| `conferente.md:65`: ` e o mesmo com a base da branch (\`origin/<Base>\`): o Base-sha precisa ser ancestral das duas; ...` (item 2) | nenhum (`Base-sha fora da branch` já existia em `28be2c9`) |
| `conferente.md:40`: `; etapa do papel do destino que falta no "Entregar" é corte` (item 3, 2ª parte) | nenhum |
| `conferente.md:40`: `(só a marca ou a citação ...)` (item 3, 1ª parte) | `só a marca ou a citação` |
| `conferente.md:62`: `Leia o brief do \`Arquivo:\` ...` (item 4) | `escopo: brief sem arquivo` |
| `jarvis.md:63`: ` \`Arquivo:\` (o caminho do brief em \`docs/briefs/\`),` na entrega (item 4) | nenhum (`docs/briefs/` casa no trecho do brief) |
| `conferente.md:64`: `, \`linhas>=N\`` (item 5) | `linhas>=N` |
| `R-DECISAO.md:15`: `; na entrega, \`pendente:\`` (item 5) | nenhum |

## Achados
| # | Arquivo:linha | Problema | Sugestão | Severidade |
|---|---|---|---|---|
| 1 | `tests/config.json` (`agents/conferente.md`) | Item 6 do brief incompleto: os trechos dos itens 1 e 2 (o bloqueante da volta 1 e o M1) não têm invariante efetivo (tabela acima). | Acrescentar, só por acréscimo: `"menos \`não verificável\` e \`corte: etapa \\(ok\\)\`"` e `"precisa ser ancestral das duas"`. | **bloqueia** |
| 2 | `tests/config.json` (`agents/conferente.md`, `agents/jarvis.md`) | Mesmo item 6, para os itens 3 (2ª parte) e 4 (lado do Jarvis): sem proteção. | `"etapa do papel do destino que falta"` em `conferente.md`; em `jarvis.md`, um trecho exclusivo da entrega, p. ex. `"\`Arquivo:\` \\(o caminho do brief"`. | **bloqueia** (mesmo item do brief; vai junto com o 1) |
| 3 | `tests/config.json` (`docs/regras/R-DECISAO.md`) | O `pendente:` da entrega, aceito como saída do item 5, não é protegido. | Acrescentar `"na entrega, \`pendente:\`"`. | recomendado |
| 4 | `agents/jarvis.md:60` | O prompt-padrão do Jarvis, que é quem escreve os PQs, ainda lista `espera: rc=0 \| contém \| igual \| linhas=N` sem `linhas>=N`. `R-PROVA` e o conferente já têm a forma. São três fontes do mesmo formato, e uma ficou para trás. | Acrescentar ` \| linhas>=N` na `:60` e atualizar o fragmento, se quiser. | recomendado |
| 5 | `agents/conferente.md:41` | Continua aberto (achado 3 da volta 1, fora do brief da volta 2): falta o rótulo de saída para "brief com commit sem PQ `sha`, `push` ou `arquivo`". | Ex.: `forma: sem PQ que o conferente confira`. | recomendado |
| 6 | `agents/conferente.md:64` | Continua aberto (achado 4 da volta 1): "`cmd` → compare só o que `espera:` diz" não diz que o comando roda. | "`cmd` → rode o comando (se for da lista acima) e compare só ...". | recomendado |
| 7 | `changelog.d/conferente-k1-texto-e-forma.md` | Continua aberto (achado 6 da volta 1): o nome foge de `<branch-sem-prefixo>.md`. | Renomear para `changelog.d/conferente-k1.md`. | recomendado |

## Conferido e certo
- **Bloqueante da volta 1 (`conferente.md:50`):** resolvido. Agora diz "menos `não verificável` e `corte: etapa (ok)`, que aparecem mas não reprovam". Só falta o invariante (achado 1).
- **Item 2 (M1, `:65`):** o Base-sha precisa ser ancestral de `<b>` e de `origin/<Base>`, e "não contém" em qualquer um dos dois dá `escopo: Base-sha fora da branch`. Usa só `git merge-base`, que está na lista de comandos (`:19`, `:24`).
- **Item 3 (M2, `:40`):** a cobertura de `E<n>` vale "só a marca ou a citação `(E<n>)`; paráfrase não cobre". Etapa do papel do destino que falta no Entregar é corte. Isso é coerente com esta delegação: E1.1 é do tech-lead, que é o papel do destino, e foi cortada com a marca.
- **Item 4 (M3):** `Arquivo:` está na entrada do modo entrega (`conferente.md:57`) e no `jarvis.md:63`. O conferente lê o brief do arquivo (`:62`), e a falta ou a divergência reprova com rótulo `escopo:`, que é vocabulário do modo entrega. Não mistura com o `forma:` do brief.
- **Item 5:** `linhas>=N` está em `R-PROVA.md:11` e em `conferente.md:64`. **Saída do autor em `R-DECISAO.md:15`, aceita pelo Jarvis (decisão técnica registrada no pedido):** é coerente e eu não a contesto. O texto passa a dizer "no brief, `corte: sem marca`; na entrega, `pendente:`". Isso bate com `conferente.md:16` (vocabulário por modo), `:40` (brief) e `:66` (entrega: item do Entregar sem commit nem marca vira `pendente:`). O invariante `corte: sem marca` continua intacto, e trocá-lo exigiria decisão do dono (CLAUDE.md), por isso a saída é a certa. O objetivo do item (as duas fontes falarem a mesma língua por modo) foi cumprido.
- **Brief × entrega sem contradição:** `corte:` só aparece no brief (`:38-50`), e `pendente:`/`escopo:` só na entrega (`:52-79`). As regras de cada modo ficam na própria seção. O texto do `jarvis.md:63` descreve as duas entradas na mesma ordem dos blocos do conferente.
- **C1, C3, C5, C6, C7, C8, C10:** continuam como a proposta pede (detalhe no parecer da volta 1, `28be2c9`). A volta 2 só acrescenta e não desfaz nenhum.
- **Invariantes:** só acréscimos (`+5` em `conferente.md`, `+1` em `R-PROVA.md`). Nenhum item existente foi removido nem afrouxado. As linhas `-` do diff são a mesma entrada, que ganhou a vírgula.
- **Fragmento:** `changelog.d/conferente-k1-texto-e-forma.md` ganhou a linha da volta 2. O `CHANGELOG.md` e o `plugin.json` não foram tocados.
- **Correção `5177b43` (não mudou na volta 2):** só toca o ambiente dos testes. `maintenance.auto=false` e `gc.auto=0` vão por `GIT_CONFIG_COUNT/KEY/VALUE` em `ambiente_limpo()` (`tests/test_forge.py:402`), que só os processos filhos dos testes usam. `receive.autogc=false` é gravado no `remoto.git` temporário (`:663`). Nada é gravado no repositório real nem no `~/.gitconfig`. A causa está em `docs/briefs/conferente-k1-causa.md`, com a prova `repack disparado: 1` contra `0`.
- **`R-NEUTRO` / `R-CUSTO`:** ok. Não há nome de projeto, stack nem comando pago.

## Ferramentas (citadas, não refeitas)
- Suíte completa: não rodada aqui, porque a segurança roda em paralelo na mesma worktree. O autor a rodou. Rodei só as classes de texto no HEAD `43a7c5a`: `python3 -m unittest tests.test_forge.RegrasInviolaveis tests.test_forge.RegrasComId tests.test_forge.Agentes` → `Ran 9 tests in 0.031s` / `OK`.
- `scripts/validar-plugin.sh`: com o QA (`R-QA`).

## Para fechar (uma volta)
Acréscimos em `tests/config.json` (achados 1–3). Se quiser, os recomendados 4–7 entram no mesmo commit de texto. Depois, push. Basta isso para eu aprovar. O texto das regras não precisa mudar.
