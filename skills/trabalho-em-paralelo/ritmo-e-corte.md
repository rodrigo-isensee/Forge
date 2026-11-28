# Ritmo diário, corte por arquivo e teto do time

Detalhe da skill `trabalho-em-paralelo` (diretriz 25: o Jarvis traz o resumo e manda ler este arquivo). Vale no Forge e em todo projeto.

## Ritmo diário (diretriz 32 do dono)
- O time desenvolve o máximo em paralelo, dia e noite, e junta cada item na `develop` assim que fica verde, em lotes de até 3 PRs sem arquivo em comum (`docs/fechamento-integrador.md`, diretriz 26).
- Nunca junta sem os testes verdes nem pela exceção do GitHub (bypass do ruleset).
- A versão fecha com 20 itens integrados na `develop`, sem corte diário (diretriz 34, abaixo). O que entra depois da marca vai para a versão seguinte.
- À noite o Jarvis não escreve ao dono, salvo algo grave que mude prazo ou risco. A mensagem da manhã traz a tabela pedido × entregue, o que precisa do dono e o `resumo:` do placar.
- Não é um PR só de desenvolvimento: cada item segue com revisão e testes próprios.

## Corte do trabalho por arquivo (diretriz 33 do dono)
- Cartões que mexem nos mesmos arquivos vão para o mesmo agente, na mesma branch, um depois do outro, nunca para agentes diferentes em paralelo (`forge-check sobreposicao` diz o arquivo em comum).
- Lote de desenvolvimento: de 3 a 5 cartões pequenos (ou um dia de trabalho), com uma revisão só.
- A junção na `develop` continua como na diretriz 26: até 3 PRs que não mexem nos mesmos arquivos.
- **Suíte verde sozinha (SIEG-G6):** no corte da versão e na integração (`R-FLUXO`), cada item deixa a suíte verde sozinho; o que depende de outro (uma interface e quem a usa) vai junto com ele, na mesma branch ou no mesmo lote.
- Lote por arquivo: itens decididos no mesmo arquivo vão numa branch, um commit por item com seus testes, portões uma vez e um PR que cita os itens; item com defeito sai por revert; item à espera do dono não entra; nenhum portão cai.

## Fila e conserto da integração (`R-FLUXO`; BP2, decisões do dono de 20/11)
- **Fila em série:** antes de cada merge, confira sobre qual topo da integração o CI do PR rodou. Se a base andou depois, o fechamento a traz pelo merge de sempre (sem forçar nem pular hook; no Forge, o passo 2b do `bin/forge-fechar <pedido> --ref <branch>`) e espera o CI de novo, mesmo sem arquivo em comum (D3). Check e parecer seguem: no Forge, a bateria completa roda no CI do PR, obrigatória para o merge, e o `tech-lead` mescla com tudo verde.
- **Develop só no fim (F3 do estudo de atrito, v0481 E30.1):** a branch não traz a `develop` durante as voltas; ela entra uma vez, no fechamento. O merge limpo (sem conflito nem resolução à mão: a árvore do `git merge-tree`) não reabre revisão nem pede parecer novo: o parecer aprovado no head revisado vale no head com a base (`forge-check pr --base`); byte à mão em código do domínio no merge o desatualiza, e o merge que descarta a base (o -s ours, o conflito resolvido com o lado da branch) também. Com conflito, o autor traz a base e o portão revalida só o que o `forge-check pr` aponta. Medida: commits de merge da `develop` por PR (meta: no máximo 1).
- **Base velha (PRONTO-BASE-VELHA, só aviso desde a v0481 E30.1):** a branch nascida antes da última marca de versão da `develop` não traz a base antes da entrega: o `forge-check pronto` avisa numa linha (`pronto: aviso: base velha: ...`) e roda as checagens contra o ponto de partida da branch; a marca é conferida na integração (o fechamento e o CI do PR). Reversão: se o CI do PR reprovar pela marca mais de uma vez por versão, o pronto volta a reprovar.
- **Lote** (diretriz 26) é exceção declarada (D4): já exige a integração verde antes, itens sem arquivo em comum e o CI acompanhado no fim; os itens dele não repetem o teste sobre o topo.
- **Onde mora a fila** (D1): no Forge, no `bin/forge-fechar <pedido> --ref <branch>` (até a I4, à mão; última linha), com o servidor como está; reabre quando o Forge for para uma organização (BP9). No projeto de organização, a fila nativa do GitHub (`docs/engineering/protecao-de-branch.md` do projeto); em conta pessoal, o passo à mão acima.
- **Conserto da integração vermelha** (D2): com o CI de `push` da integração vermelho, o PR que conserta entra só se todas valem; leitura que falha para o merge:
  1. o vermelho é o do topo, lido na hora, e terminou com falha (nem pendente nem cancelado); topo que andou, pare;
  2. pareceres da classe aprovados no head e a cadeia de sempre: nenhum portão é dispensado;
  3. merge preso ao head revisado (`--match-head-commit <head revisado>`); com a base trazida, o head novo só vale com pais (revisado, topo) e a árvore do `git merge-tree` dos dois, sem resolução nem edição à mão;
  4. cada teste que falhou no vermelho rodou e passou no PR: não vale pulado pelo id, pela classe (`setUpClass`, `tearDownClass`) ou pelo módulo (`setUpModule`, `tearDownModule`, `ModuleSkipped`), nem apagado; passo vermelho que não é teste (como o teto de pulados) fica verde no PR;
  5. o diff tem relação com o vermelho: toca o arquivo de um teste que falhou ou um arquivo mudado desde o último verde, ou reverte um merge desse intervalo;
  6. um conserto por vez; o CI do merge é acompanhado e, sem verde, a integração segue fechada para o resto;
  7. o `## Histórico` do pedido registra run, topo, PR e head.
- No Forge, o `bin/forge-fechar <pedido> --ref <branch>` passa a conferir o conserto e a fila (BP2 I1 e I4); até lá, e no projeto, o `tech-lead` confere à mão.

## CI pago (`R-CUSTO`, E3.43)
Em projeto privado, cada push e cada `gh run rerun` custa um run de CI (num projeto de origem, 163 rodadas de push contra 33 de PR num dia esgotaram a cota grátis).
- Junte os commits e envie uma vez, com a entrega pronta e o comando local verde; push de cada commit ou de trabalho pela metade é run gasto.
- `gh run rerun` pede motivo escrito: falha de infraestrutura comprovada no log (runner, rede, serviço fora do ar). Teste vermelho não se repete: volta ao autor no brief de volta.
- Vale para o autor, os portões e o Jarvis; o comando local é o pronto do `CLAUDE.md` (no Forge, o PQ do brief).

## Teto do time (decisão do dono, H6)
- Até 20 agentes ao mesmo tempo, dentro do `R-TETO`, e no máximo 12 branches com trabalho aberto.
- Agente livre termina o que está aberto (revisão, conserto, teste vermelho, CI vermelho) antes de abrir item novo; branch nova só quando uma entra na `develop`.
- A regra de tocar o máximo de itens ao mesmo tempo continua: o máximo vale dentro desses tetos.
- Instância extra de um papel, uma por item independente, trabalha numa cópia própria, um clone: `forge-copia clone --instalar`, em `~/.forge-contrib/wt/<item>` no Forge e `.forge/wt/<item>` no projeto (o sandbox não libera `.git/worktrees`).
- Fim do item (PR mesclado, PR fechado sem merge ou `vazio: sim`), no Forge e nos projetos: o tech-lead apaga a cópia com `forge-copia limpar <cópia>`, que confere o fim e só apaga a cópia limpa, sem stash e com tudo na origem; a branch fica. No Forge, o `forge-fechar <pedido> --ref <branch> --limpar` já passa as cópias a ele (LIMPEZA-AO-FIM-DO-ITEM).

## Versão com 20 itens (diretriz 34 do dono)
- A versão fecha com 20 itens integrados na `develop` (`forge-contador`: `<versão>: N de 20`): o tech-lead marca, promove à `homolog` e abre o PR `homolog` → `main`; sem versão por dia nem versão parcial (ordem do dono de 26/11).
- O PR `homolog` → `main` continua mesclado pelo dono (`R-MAIN`); o Jarvis avisa o dono numa linha quando ele fica verde.
- O time usa o teto de agentes cheio, com os cartões em lotes por arquivo (diretriz 33).
- No Forge, antes do `bin/forge-changelog release <versão> <data>`, o tech-lead roda `scripts/placar-mutacao.py --desde <tag anterior> --versao <versão>` e o bench (BENCH-POR-RELEASE), medidas, não portão, e `forge-check decisoes --sem-cartao`, e leva tudo ao Jarvis; na mesma marca, regera `tests/pesos-d4.json` com `python3 -I scripts/pesos-do-ci.py --repo <dono/repo> --saida tests/pesos-d4.json` e o commita (PR-VERDE C1).
