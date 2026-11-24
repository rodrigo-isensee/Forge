# BP11: as 4 métricas DORA no placar (desenho)

Pedido v0478, etapa E155.1 (cartão BP11-DORA-NO-PLACAR, origem `docs/propostas/boas-praticas-1911.md`, linha BP11). Só desenho: nenhum script, hook, teste, CI nem o `forge-check` foi alterado; a ligação no `forge-check` fica para depois. Público: o dono e o time. Revisão: 2026-12-24. Base lida: develop e15c8566. Medidas só do processo, nunca de pessoa ou agente.

Ideia: o `forge-placar` passa a mostrar as 4 métricas DORA ao lado das do processo, lendo o que o `bin/forge_dora.py` já calcula, sem escrever em nada. Hoje elas existem no `forge-check dora`, mas o placar (a visão do `comparar` e das propostas) não as vê, então nenhuma melhoria pode prometer ganho em DORA.

## 1. O que já existe

| Peça | Evidência | O que cobre |
|---|---|---|
| Frequência de entrega | `bin/forge_dora.py:29-40` (`releases`), `:133-151` (`calcular`) | tags `vX.Y.Z` por semana ISO; brutos sempre, média só com 20 ou mais |
| Lead time de mudança | `bin/forge_dora.py:42-51` (`esperas_da_mudanca`) | horas do commit sem merge até a tag que o publicou; p50 e p90 só com 20 ou mais |
| Taxa de falha de mudança | `bin/forge_dora.py:98-116` (`falhas`) | releases com ao menos um escape (`docs/kanban/escapes.md`) sobre as releases |
| Tempo para restaurar | `bin/forge_dora.py:98-116` | horas do escape até a release seguinte; `abertas` conta os sem release depois |
| Develop vermelha | `bin/forge-placar:757-780` (`paradas_do_ci`), usada por `fases` | minutos entre o `failure` e o `success` seguinte do CI da develop, pelo `--ci` gerado fora |
| Saída do placar | `bin/forge-placar:449-471` (`cmd_placar`) | só as 6 `METRICAS` (`:99`), janela de `--dias` contra a anterior; `comparar` e `propostas` só conhecem essas 6 |
| Quadro movido pelo PR | `docs/propostas/ae2-quadro-anda-com-pr.md` | o merge move o cartão dentro do `forge-fechar`; é a fonte do "registro do processo" que a BP11 pede |

Medido hoje, em `bin/forge-check dora --desde 2026-10-25` na cópia de trabalho (sem a pasta de controle): `frequencia n=39 media_por_semana=9.75`; `espera_da_mudanca_h n=1585 p50=19.92 p90=44.66`; `taxa_de_falha entregas=39 com_falha=0 taxa_pct=0.0`; `recuperacao_h n=0`; `vazao n=0`. Comando e janela citados: `medido`; o 0 de falha não é medido (item 2, F1).

## 2. O que falta

- **F1, ausência vira zero.** Com `escapes.md` ausente, `falhas` lê `""` e `taxa_de_falha` sai `com_falha=0 taxa_pct=0.0`, e `vazao` sem histórico sai `n=0`. Isso viola `R-DECISAO` (dado ausente nunca vira zero): a taxa 0,0% acima é "não medido", não "sem falha". O placar não pode herdar isso.
- **F2, as 4 não estão no placar.** O `cmd_placar` e o `--json` não as trazem; `comparar` não as compara; `propostas` não aceita `taxa_de_falha` como métrica.
- **F3, restaurar a develop tem duas fontes.** O `forge_dora` mede "escape até a release seguinte" (cai no conceito de produção); a BP11 pede "restaurar a **develop**", que é o `paradas_do_ci` (CI vermelha). São medidas diferentes e a escolha é do dono (seção 5, D2).
- **F4, o quadro descolado.** A vazão e o lead por cartão dependem do `historico.md` estar em dia; hoje depende de movimento manual. É a promessa do AE2, não desta proposta.

## 3. O desenho

1. **Um subcomando de leitura, `forge-placar dora`**, que importa `forge_dora.calcular` (o mesmo `modulo_do_bin` que o `forge-check` usa) e imprime as 4 linhas mais a vazão, com o mesmo `--dias`/`--ate` do placar (janela atual e anterior) e `--json`. Não reimplementa a conta: uma só fonte, o `forge_dora.py`. Não escreve em arquivo algum.
2. **Linhas no placar comum.** O `cmd_placar` ganha uma linha por medida, depois de `pronto_ate_develop`, no formato `dora_<nome>: atual X · anterior Y`, e a chave `dora` no `--json`. Antes das metas de proposta, entram fora de `METRICAS`: nenhuma conta do `comparar` muda.
3. **Ausência é `-`, nunca 0 (corrige F1).** O `forge_dora` passa a devolver `None` (e o placar mostra `-`) quando `escapes.md` ou `historico.md` não existe; arquivo existente e vazio continua 0 de verdade. Abaixo de `MINIMO_PARA_RESUMO` (20) o placar mostra os brutos e nenhuma taxa, como o `forge-check dora` já faz.
4. **Estabilidade com velocidade.** A saída põe frequência e lead juntos de falha e restauração, na mesma ordem da skill `kanban-metricas`; velocidade que sobe com estabilidade em queda é dito na linha `resumo:`, que ganha uma frase DORA em linguagem simples (ex.: "entregamos 9 vezes por semana, e nenhuma release teve defeito escapado" só com falha medida).
5. **Métricas candidatas a proposta, em etapa posterior.** Só depois de 2 semanas de leitura estável (item 4, "Como medir") `taxa_de_falha` e `restaurar_h` entram em `METRICAS` e nas `GUARDADAS`/`propostas`, por decisão do dono (D3), porque aí passam a poder reprovar uma mudança.
6. **Fora desta proposta:** o hook de PR que move o quadro (AE2), a ligação `forge-check` ↔ placar e qualquer gravação.

## 4. Como medir

| Medida | Como | Meta |
|---|---|---|
| As 4 linhas no placar | `bin/forge-placar --ate <data>` mostra `dora_frequencia`, `dora_lead_h`, `dora_falha`, `dora_restaurar_h` | 4 de 4 linhas |
| Nada de zero inventado | teste: sem `escapes.md` a linha sai `-`; com o arquivo vazio, 0 | 0 casos de ausência virando zero |
| Mesma conta do `forge-check dora` | para a mesma janela, os números das duas saídas são iguais | diferença 0 |
| Só leitura | o placar roda com a raiz em modo somente leitura e `git status` limpo depois | 0 arquivos alterados |
| Efeito | `forge-placar comparar --antes <data> --depois <data> --metrica taxa_de_falha` depois de 2 semanas | rc 0 ou 3, não rc 1 |

Critério de reversão: se a taxa de falha ou a taxa de escape piorar além da tolerância do `comparar` nas 2 semanas seguintes ao início, ou se as linhas DORA divergirem do `forge-check dora`, reverte-se a mudança inteira.

## 5. Decisões do dono

| ID | Decisão | Recomendação |
|---|---|---|
| D1 | Aprovar a mudança (sim ou não) e a versão em que entra (`versão:` nomeada, `R-DECISAO`) | Aprovar, como `minor`, no pedido de código seguinte; a BP11 é a última da ordem "segurança e medida" |
| D2 | "Restaurar a develop" = (a) escape até a release seguinte (o que o `forge_dora` já mede) ou (b) CI vermelha da develop (`paradas_do_ci`) | Mostrar as duas com nomes distintos (`restaurar_release_h` e `develop_vermelha_min`); só (a) vale como DORA de produção, e (b) responde à BP11 literal. Começar sem escolher entre elas |
| D3 | Depois de 2 semanas, promover `taxa_de_falha` a métrica do `comparar` e das `GUARDADAS` (pode reprovar uma proposta) | Sim, mas só então; antes, só leitura |
| D4 | A BP11 pede o quadro movido pelos hooks de PR; aceitar que isso é do AE2 e não deste cartão | Aceitar: sem o AE2 em dia a vazão fica `-` e o placar não a inventa |

## 6. Riscos e limites

- **Poucos dados:** 39 releases em 4 semanas dão frequência, mas falha e restauração dependem de `escapes.md` com linhas reais; com poucas linhas a saída fica em brutos.
- **Escape registrado tarde subestima a falha:** quem acha o bug depois do parecer final roda `forge-check escape registrar`; sem isso a taxa fica baixa sem estar certa. Aviso na saída com o número de escapes lidos.
- **Custo:** nenhum (`R-CUSTO`): git, arquivos locais e biblioteca padrão.
- **Neutralidade (`R-NEUTRO`):** nada de projeto no texto; a fonte do projeto é o git e a pasta `docs/kanban` dele.
