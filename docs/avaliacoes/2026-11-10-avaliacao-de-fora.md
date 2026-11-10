versao: 0.45.3

# Avaliação de fora 2026-11-10 (AQ)

Primeira avaliação de fora. Base: `origin/main` em `6aceb1a9` (release 0.45.3). Medido só com leitura: `forge-check metricas` (com `--raiz-pedidos ~/.forge-contrib --desde 2026-11-08`), `forge-check regras`, `forge-check transcricao custo`, `git log`, `gh run list` / `gh pr view` / `gh api` (rulesets) do repositório do Forge. Não li `agents/jarvis.md`, conversas nem pedidos em curso; o projeto piloto não foi medido (fora do escopo deste pedido). Referências externas (orkastery e a segunda referência, das ideias S1 a S8) entram como dado, pelos resumos do plano da 0.43.x; os resumos trazem ideias, não resultados medidos, então a comparação é só de mecanismo contra o resultado medido aqui.

## Medidas de base

| Medida | Valor | Fonte |
|---|---|---|
| Agentes do produto | 9 arquivos, 7.771 palavras (maior: `tech-lead` 1.297, `jarvis` 1.142, `conferente` 1.072) | `wc -w agents/*.md` |
| Skills | 19, 14.406 palavras (maiores: `kanban-scrum` 1.907, `qa-testing` 1.904) | `wc -w skills/*/SKILL.md` |
| Regras | 17 `R-*.md` + README, 4.615 palavras; 9 em dia, 8 com aviso "Medida sem número"; nenhuma vencida (revisar em 2027-01-07) | `forge-check regras` |
| Núcleo (jarvis + regras) | 35.793 caracteres de um teto de 37.511 (95%) | `docs/regras/orcamento.json` |
| Hooks | 11 arquivos, 8.371 linhas; `conformidade.py` 2.729 e `_comum.py` 2.753; 17 ganchos em 8 eventos | `wc -l hooks/*`, `hooks/hooks.json` |
| `bin/forge-check` | 10.128 linhas, 46 subcomandos | `grep add_parser` |
| Código de produto (bin, hooks, scripts) | 31.382 linhas | `wc -l` |
| Testes | 165 arquivos no topo, 3.888 `def test_`, 151.922 linhas (4,8 por linha de produto); 2.211 fixtures de hook (1.651 só do `conformidade`, 402 do `parecer`); 343 especificações de mutante | `find tests`, `grep -c` |
| Crescimento desde 08/11 | testes +34.885/−2.315 linhas; `conformidade.py`+`_comum.py` +912/−135; agentes, skills e regras +753/−674 | `git log --numstat` |
| CI no PR (06–10/11) | 55 execuções: 12 verdes, 30 vermelhas, 13 canceladas; verde leva mediana 20,0 min (p90 21,5) | `gh run list --json` |
| Main vermelha (desde 08/11) | 13 merges; CI no push concluído em 10: 4 verdes, 6 vermelhos (60%); Release falhou em 11 de 13. A 0.45.2 existiu só para tirar a main do vermelho; a 0.45.3 está vermelha agora (38+17 falhas em `test_pre_push_afetados` e `test_pre_push_parecer_curto`) | `gh run list --branch main` |
| PR juntado com check vermelho | #473, #475, #476, #480, #481, #483: todos com FAILURE no `statusCheckRollup` no merge | `gh pr view --json statusCheckRollup` |
| Proteção da main no servidor | ruleset `checks-obrigatorios-develop-main` exige `bateria`, `bateria (python 3.14)` e `catraca`, mas com bypass "always" para o papel admin; `mainRuleset` desativado | `gh api .../rulesets` |
| Lead time (desde 08/11) | até develop p50 55,5 h; fatias: autor 5,3%, portões 93,2%, dono 1,5%; até main: autor 14,8%, portões 81,1%, dono 4,1% | `forge-check metricas` |
| Voltas (desde 08/11) | 116 voltas para 15 prontos; 44 revalidações; 152 reprovações: escopo 44, decisão 41, citação 19, base 16, forma 12, etapa 10, implementação 4, prova 3 | `forge-check metricas` |
| Tokens de subagentes (172 sessões, sem corte por data) | 79,7 M; `conferente` 34,1 M (43%) em 676 mensagens; `tech-lead` 23,3 M; 9 lançamentos repetidos do conferente | `forge-check transcricao custo` |

## Propostas (em ordem de impacto)

### 1. REMOVER o bypass do admin e, no lugar, aposentar a prova de suíte feita no cliente

- **Problema observado:** a main ficou vermelha em 6 de 10 CI concluídos desde 08/11, e seis PRs foram juntados com check vermelho. O servidor já exige `bateria` e `catraca`, mas o papel admin passa por cima sempre. Ao mesmo tempo, a prova feita no cliente (`.githooks/pre-push`, prova `.verde`, carimbo K6, envio curto e dirigido, `hooks/pesado.py`) cresce a cada versão: 25 itens do `CHANGELOG.md` da 0.43.0 à 0.45.3 mexem no `conformidade`. E as falhas de hoje na main estão justamente nos testes dessa maquinaria (`test_pre_push_*`). A barreira cara (cliente) não segurou o dano. A barreira barata (servidor) foi desligada por quem tinha o poder.
- **Proposta:** (a) tirar o bypass "always" do ruleset, ou trocá-lo por "pull_request" só com aprovação explícita do dono registrada no PR (decisão do dono, `R-MAIN`). (b) Com o check do servidor de fato obrigatório, remover do pre-push a prova `.verde`, o carimbo K6 e o modo "envio dirigido", deixando o pre-push como atalho opcional (afetados), não como portão. (c) Os testes e fixtures dessa maquinaria saem junto.
- **Por que o existente não basta:** o existente basta (o ruleset). Ele só não está valendo.
- **Esforço:** P para (a), M para (b) e (c).
- **Risco:** com (a), um CI instável trava o merge. Mitigação: o dono mantém o poder de desligar a regra por um PR, com registro.
- **Como medir:** % de pushes na main com CI vermelho. Linha de base 60% (10 CI, desde 08/11). Sucesso: 0% em 10 merges seguidos. Reversão: 2 merges travados por check instável sem defeito.
- **Afrouxa o processo?** (a) não, aperta. (b) sim: troca a prova de suíte do cliente (`R-TETO`, `R-FLUXO`) pelo check do servidor.
- **Custo de eficiência:** cada main vermelha custa uma versão de correção (0.45.2: ~1 PR, ~20 min de CI, mais o trabalho do autor). Ganho estimado de 3 a 6 versões de correção a cada 13 merges. O pre-push sem portão deixa de rodar a suíte local (minutos por envio; a mediana local não foi medida aqui).
- **Fonte:** `docs/melhoria-continua.md` (resultado antes de processo); skill `software-architecture` (controle no ponto de menor custo).

### 2. REMOVER o conferente agente do modo entrega e deixar só a ferramenta

- **Problema observado:** o `conferente` gastou 34,1 M de 79,7 M tokens de subagentes (43%) em 676 mensagens, mais 9 lançamentos repetidos. A medida do próprio `R-PROVA` mostra que só 34 de 905 entregas reprovadas (3,8%) caíram por implementação. Desde 08/11, só 4 de 152 reprovações (2,6%) são de implementação; o resto é forma, citação, base, etapa, escopo ou decisão, que a ferramenta (`forge-check entrega`, `forge-check brief selar`) confere de forma determinística. No `R-BRIEF`, o conferente já é opcional.
- **Proposta:** tirar o modo entrega do `agents/conferente.md` e dos textos que o pedem. A conferência da entrega fica só no `forge-check entrega`. O agente fica para dúvida de conteúdo, chamado pelo dono ou pelo coach. O texto do conferente desce para o teto-alvo de 5.000 caracteres que já está no `orcamento.json`.
- **Por que o existente não basta:** não é mecanismo novo; é retirada.
- **Esforço:** P.
- **Risco:** perder a conferência de escopo semântico (o que a ferramenta não lê). Mitigação: o review (`R-REVIEW`) já lê o diff contra o pedido.
- **Como medir:** tokens do conferente por versão (`forge-check transcricao custo --desde`) e escapes de entrega achados no review. Linha de base: 43% dos tokens de subagentes e 4 reprovações por implementação em 152. Sucesso: conferente abaixo de 10% dos tokens, sem aumento de escapes no review em 5 versões. Reversão: 2 escapes de escopo que o conferente pegaria.
- **Afrouxa o processo?** Sim, `R-PROVA` (a parte "conferente agente").
- **Custo de eficiência:** de 10 a 30 M tokens por janela parecida (média ~20 M; base: 34,1 M em 172 sessões, estimando que de metade a 90% vêm do modo entrega), mais uma rodada do Jarvis por entrega.
- **Fonte:** `docs/economia-de-tokens.md`; `docs/praticas-agentes-pesquisa.md` (verificação determinística antes de juiz-modelo).

### 3. SIMPLIFICAR o `hooks/conformidade.py`: trocar a análise de shell por uma lista do que pode, por papel

- **Problema observado:** `conformidade.py` e `_comum.py` somam 5.482 linhas, e o `conformidade` tem 1.651 fixtures. Desde 08/11 entraram +912 linhas e pelo menos 25 itens de changelog de "mais uma forma" de escrever o mesmo comando: `--all` e `--al`, `-C`, `GIT_DIR`, alias do gh em quatro pastas, curinga, heredoc, `tee`, `sed -i`. É uma corrida contra o próprio agente, sem fim, porque o bash tem formas infinitas de escrever a mesma coisa. Enquanto isso, o dano real (main vermelha, proposta 1) passou pelo servidor. O `R-CONFORMIDADE` diz "Medida: sem medida".
- **Proposta:** congelar a lista de recusas. Para os papéis só de leitura (AQ, conferente), já existe a lista do que pode em `so_leitura.comandos_por_papel`: estendê-la aos outros papéis para as ações críticas (push, merge, gh api de escrita) e recusar o resto, em vez de reconhecer cada variante perigosa. As fixtures de variante (`trava`, `heredoc`, `gh`, `git`: ~390) viram casos de uma tabela única.
- **Por que o existente não basta:** a lista do que pode existe só para dois papéis. O resto vive de lista do que não pode, que cresce a cada versão.
- **Esforço:** G.
- **Risco:** a lista do que pode recusa comando legítimo. Mitigação: o registro do `vigia` mostra quais comandos foram recusados, e cada inclusão na lista é uma linha.
- **Como medir:** linhas de `conformidade.py` + `_comum.py`, fixtures do `conformidade` e itens de changelog do hook por versão. Linha de base: 5.482 linhas, 1.651 fixtures, ~2 itens por versão. Sucesso: menos 40% de linhas e zero item de "variante nova" em 5 versões. Reversão: uma ação crítica que passe em produção.
- **Afrouxa o processo?** Não no efeito, porque a lista do que pode é mais estrita. Muda a forma do `R-CONFORMIDADE`.
- **Custo de eficiência:** a parte `conformidade` do `test_hooks` (citado em 13 min no plano de 09/11), menos de 30 a 60% nos minutos de CI desse módulo; e ~1 item de trabalho por versão que hoje vai para variantes.
- **Fonte:** skill `software-architecture`; `docs/praticas-agentes-pesquisa.md` (lista do que pode em ferramentas de agente).

### 4. SIMPLIFICAR os portões no caminho até a develop (93% do lead time)

- **Problema observado:** desde 08/11, os portões são 93,2% do lead time até a develop (p50 55,5 h), contra 5,3% do autor. Houve 44 revalidações para 15 prontos, e o `R-REVIEW` mede 89% de revalidações sem achado. O `test_hooks` do parecer tem 402 fixtures e o `hooks/parecer.py` 790 linhas para controlar arquivos de parecer presos a sha.
- **Proposta:** (a) para a classe T e N só de texto, um parecer único do `tech-lead` (review e QA juntos), sem arquivo separado de QA; (b) a revalidação só roda quando o `forge-check parecer delta` mostra código no domínio, e nunca por commit só de texto ou de changelog (hoje é a regra, mas 89% sem achado indica que ainda dispara demais: medir o disparo); (c) contar a fatia por portão no `forge-check metricas` antes de cortar mais.
- **Por que o existente não basta:** a classe T já tem um review só; o grosso do tempo está na N, que roda review e QA em paralelo e com revalidação.
- **Esforço:** M.
- **Risco:** escape de QA na N. Mitigação: o CI do servidor (proposta 1) cobre a regressão.
- **Como medir:** fatia "portões" do `forge-check metricas` e revalidações por pronto. Linha de base: 93,2% e 2,9 por pronto. Sucesso: abaixo de 70% e de 1 por pronto em 5 versões. Reversão: 2 escapes de QA na classe N.
- **Afrouxa o processo?** Sim, `R-REVIEW` e `R-QA` na classe N só de texto.
- **Custo de eficiência:** de 10 a 30 h de lead time por item (média ~20 h; base p50 55,5 h × 93%) e uma rodada de subagente por revalidação evitada (~40 em 4 dias).
- **Fonte:** `docs/melhoria-continua.md` (gargalo primeiro); skill `kanban-scrum` (tempo por coluna).

### 5. REMOVER texto de regra que a ferramenta já cobre e as regras sem medida

- **Problema observado:** o núcleo está a 95% do teto (35.793 de 37.511 caracteres): a próxima regra estoura. Nove regras dizem "Medida: sem medida" (`R-COPIA`, `R-NEUTRO`, `R-DISCOVERY`, `R-CONFORMIDADE`, `R-MAIN`, `R-CONTRIB`, `R-CUSTO`, `R-WIP`, `R-VERIFY`), e várias valem só por permissão ou hook (`R-VERIFY`: "vale por permissão negada"; `R-WIP`: "o hook `quadro` barra"). O orkastery tirou do `.md` a regra que tem `verificada_por` executável (ideia 6, aprovada em 09/11); aqui o texto continua. Os testes cresceram 44 vezes mais que o texto desde 08/11 (+34.885 contra +79 líquidas).
- **Proposta:** juntar `R-VERIFY`, `R-MAIN`, `R-CUSTO`, `R-CONTRIB` e `R-COPIA` num `R-LIMITES` de uma tela, com o `verificada_por` de cada item. As regras só de hook (`R-WIP`) passam a uma linha no `docs/regras/README.md`, com a mensagem de recusa do hook como texto único. Cada regra sem medida ganha um número (do `vigia` ou do `recusas.log`) até 2027-01-07, ou sai.
- **Por que o existente não basta:** o `orcamento.json` só impede crescer; não tira nada.
- **Esforço:** P.
- **Risco:** perder contexto para quem lê pela primeira vez. Mitigação: a recusa do hook explica a regra.
- **Como medir:** caracteres do núcleo e marcadores normativos (`test_jarvis_nucleo`, `test_orcamento_instrucao`). Linha de base: 35.793 caracteres e 17 regras. Sucesso: abaixo de 30.000 e 12 regras, sem subir os erros por papel (`tests/evals/test_erros_por_papel.py`). Reversão: um erro repetido que o texto removido cobria.
- **Afrouxa o processo?** Não: o controle fica no hook ou na permissão; sai só o texto.
- **Custo de eficiência:** ~5.000 caracteres a menos no núcleo, ~1.300 tokens por carga do Jarvis e dos agentes que citam as regras (base: 35.793 caracteres a ~4 por token), vezes as cargas de cada sessão.
- **Fonte:** `docs/economia-de-tokens.md`; ideia 6 do orkastery e S1 da segunda referência (teto que só desce), como dado.

## Regras vencidas

Nenhuma: todas as 17 revisam em 2027-01-07, e o `orcamento.json` em 2026-12-08. As 8 com aviso de "Medida sem número" estão na proposta 5.

## O que falta

- **Métrica da main vermelha e do merge com check vermelho:** nenhum `forge-check` mede isso. Calculei à mão pelo `gh`. Deveria sair no `forge-check metricas --gh` por versão.
- **Métricas do Forge pelo padrão:** sem `--raiz-pedidos`, o `forge-check metricas` não acha nada; com ela, os itens da 0.44 em diante dão `lead_main_h=nao-medido` e `tokens=-`; e o `transcricao custo --desde 2026-11-09` não devolveu linha. Assim não há custo de tokens por versão para comparar antes e depois.
- **Fatia por portão:** "portões" é uma fatia só. Falta separar review, QA, segurança, CI e revalidação para saber qual cortar.
- **Uso dos subcomandos e das skills:** 46 subcomandos e 19 skills, sem contagem de uso. Sem esse número não dá para propor quais sair.
- **Resultado das referências:** os resumos do orkastery e da segunda referência (S1 a S8) trazem mecanismos, não resultados (main vermelha, lead time, tokens). A próxima avaliação deve pedir pelo menos um número deles, ou compará-los só como ideia.
- **Piloto:** não medido nesta avaliação. A próxima deve incluir o projeto piloto indicado pelo dono.

O dono aprova as remoções (propostas 1b, 2, 3, 4 e 5).
