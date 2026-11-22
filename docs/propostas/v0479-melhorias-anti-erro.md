# MELHORIAS-ANTI-ERRO: desenho das AE1 e AE3 a AE8 (pedido v0478, E54.3)

Propósito: desenho, antes do código, dos cartões AE1 e AE3 a AE8 do pedido MELHORIAS-ANTI-ERRO (pasta de controle,
`docs/pedidos/melhorias-anti-erro.md`). Público: `tech-lead`, o backend da stack, `devops-engineer`, `security-engineer`,
`qa-engineer` e o dono. Estado: proposta. Sem código.

- Neutro (`R-NEUTRO`, ADR 0001): vale para o Forge e para os projetos. "Pasta de controle" é onde moram o quadro, o
  histórico, os pedidos e as retrospectivas: no Forge, `~/.forge-contrib`; no projeto, a raiz do próprio repositório.
- O AE2 (o quadro anda com os PRs) e o contador da versão têm desenho próprio (E54.1, branch `melhoria/v0479-ae2-contador`).
  Aqui só aparecem as dependências.
- Nada custa dinheiro (`R-CUSTO`). Do GitHub só se lê (`gh` com a conta já autenticada), além do git local. A única
  escrita remota é o push da pasta de controle (D3), feito na sessão num marco, nunca pelo relógio (condição do dono no D7).
- Afrouxa? Não. Todo item aperta ou mede. Nenhum texto de `docs/regras/`, item de `tests/config.json` ou controle sai ou é
  trocado. O AE8 tira um bypass, e quem tira é o dono (`R-CONFORMIDADE`).
- Pronto do pedido: a auditoria diária (AE6) dá zero divergências por 3 dias seguidos, contados depois que o AE6.3 entrar
  com todas as checagens ligadas (ver D8).

## 1. Problema medido

| AE | Fato (fonte) | Medida |
|---|---|---|
| AE1 | A A3 foi dada como "feita" sem PR: a branch estava 23 commits à frente e 64 atrás da develop, sem PR (retro v0478, 3.5). O #705 foi dado como "na main", mas só tinha ido à homolog (retro v0478, 3.3). | 2 afirmações de estado erradas em 2 dias. Cerca de 24 min com o estado errado no #705. 22 cartões entregues ainda abertos (Histórico v0478, 19/11 22:01). |
| AE3 | `~/.forge-contrib` ficou sem commit de 14/11 17:08 a 16/11 07:3x: 469 arquivos (ERRO-JARVIS 16/11, cartão QUADRO-E-RETRO-NO-GIT). Em 20/11 08:30, 65 alterações sem commit (ordem do dono). | 3 ordens do dono para "commit agora": 16/11, 19/11 21:46 e 20/11 08:30. |
| AE4 | v0478 tem 20 linhas ORDEM DO DONO (retro v0478, seção 1). O `forge-check decisoes --sem-cartao` só lê DECISÃO DO DONO (`bin/forge-check:7771`). | Ordens sem cartão: `não medido` (nenhuma ferramenta conta). O AE4.1 tira a primeira medida. |
| AE5 | As retros de v047, v0474, v0477 e v0478 só saíram por ordem do dono, em 20/11. Antes disso, 4 versões chegaram à main (19/11 08:08 a 20/11 07:19) sem retro. A avaliação de 16/11 contou 4 pedidos sem retro versionada. | 4 versões na main sem retro em até 24 h. |
| AE6 | E11.2 (19/11 21:46): 22 cartões entregues seguiam abertos, 8 colunas divergiam do histórico e 90 cartões não tinham linha. Em 20/11 07:55, havia 1.339 cópias em `wt/`. A branch da A3 ficou sem PR e ninguém viu. | Cada uma só apareceu quando o dono perguntou. |
| AE7 | "Só aperta?" foi remontado à mão 6 vezes (E1.17, E1.19, E1.23, E3.32, E3.34 e E3.38; cartão HOOK-COMPARA-BASE). 2 dos 10 rótulos do v0478 afrouxavam (#690 e #687; retro v0478, 3.2). O E50 teve um afrouxamento autorizado que precisa ser medido de novo (decisão do dono 20/11 10:59). | 20% dos rótulos estavam errados. 0 de 10 foram medidos por ferramenta. |
| AE8 | O ruleset da develop tem bypass "always" (Histórico do quadro, 15/11 20:51, AV1-BYPASS-RULESET). O dono mesclou 7 PRs direto na develop: #680, #695, #697, #700, #701, #703 e #715. O #680 entrou antes do CI e quebrou a develop. O #701 entrou com a S1 vermelha. | 7 merges de fora do fluxo em 3 dias, 2 deles com a develop quebrada. O passo a passo (`docs/protecao-de-branch.md`) já pede a lista de bypass vazia, mas nada confere. |

Causa comum: o estado é afirmado de memória ou por texto, em vez de ser lido de uma fonte por ferramenta. É a mesma causa
nova da retro v0478 (EV-V0478-ESTADO-COM-PROVA, absorvida no AE1).

## 2. Por que o existente não basta

| Existe | Para quê | Por que não basta (evidência) |
|---|---|---|
| `forge-check movimento` | grava o movimento com a hora | Aceita `--para Pronto` sem prova. Os 22 cartões "entregues e abertos" e a A3 "feita" passaram por ele ou por edição à mão. |
| `forge-check rodar` (S5) | grava a execução em `.forge/run/<slug>/run.json` | Grava a prova, mas nada exige que ela exista para mover o cartão. |
| `hooks/quadro.py` + `forge-check kanban` | formato e WIP do quadro | Não cruza o quadro com o git nem com o GitHub. Os 8 desvios de coluna passaram por ele. |
| `forge-check decisoes --sem-cartao` | decisão sem cartão | Só lê as linhas DECISÃO (`linhas_de_decisao`). As ordens ficam de fora. |
| `forge-check retro` | métricas e gatilhos de um pedido | Só roda quando alguém chama. Não cobra prazo depois do merge na main. |
| `hooks/doutor.py` | diagnóstico uma vez por dia | Só local, sem `gh` (por desenho, ADR 0003). Roda só no Stop de uma sessão ativa. Não vê PR nem ruleset. |
| `forge-check afrouxamentos` | rótulo sobre o diff, pela catraca | É estático: diz se o texto de uma regra mudou, não se o comportamento passou a aceitar mais. Por isso não pegou o #690 nem o #687. |
| `docs/protecao-de-branch.md` | passo a passo do ruleset | O texto pede bypass vazio, mas o ruleset real tem bypass "always" e nenhuma ferramenta confere. |
| Cartões DOCS-COMMIT-AUTO, QUADRO-VERSIONADO, QUADRO-E-RETRO-NO-GIT | commit do controle | Estão abertos desde 0.28 a 0.47.8 e nunca entraram. O AE3 os absorve (D4). |

## 3. Opções e recomendação

### AE1: feito só com prova da ferramenta
- (a) Recomendada: prova lida por ferramenta no próprio movimento. `forge-check onde <versão|PR|cartão|branch>` lê, só
  leitura:
  - a presença em `develop`, `homolog` e `main` (`git merge-base --is-ancestor`);
  - o PR (`gh pr view`: `state`, `baseRefName`, `mergedAt`, `mergedBy`).

  `movimento --para Pronto|Fechado*` só grava com `--prova <tipo>:<ref>`, que a ferramenta confere e escreve na linha.
  Tipos de prova:
  - `pr:#N` (mesclado na base certa);
  - `commit:<sha>` (ancestral da develop);
  - `rodar:<slug>` (run.json com rc 0);
  - `ruleset:<branch>` (AE8);
  - `juntado:<ID>` (cartão destino existe e está ativo).

  A ação do dono entra pelo mesmo caminho. O merge feito pelo dono aparece em `mergedBy`. O patch aplicado pelo dono
  depende do PP1-APLICADO-PELO-DONO. A configuração do sandbox é provada por um `rodar` que tenta gravar e é recusado.
- (b) Uma linha "prova:" escrita pelo Jarvis. Recusada: é declaração, e o problema é justamente esse.
- (c) Só a auditoria diária (AE6). Recusada sozinha: acha o erro até 24 h depois. Fica como rede de segurança.

### AE3: commit automático da pasta de controle
- (a) Recomendada: `forge-check controle salvar --marco <nome>` faz commit só dos caminhos de controle conhecidos (quadro,
  histórico, pedidos, briefs, retros, pareceres do controle), nunca `add -A`. Ele roda:
  - ao fim dos comandos que são marco (`movimento`, `anotar`, `brief selar`, `conferencia registrar` e a marca de versão);
  - no relógio (D7), quando o último commit tiver mais de 30 min e a árvore estiver suja; aqui só o commit local, sem push.

  O push (D3) sai só nos marcos, rodado na sessão, dentro do sandbox e sob o hook `conformidade`, e leva junto os commits
  do relógio. O relógio só lê o GitHub e só grava na pasta de controle (condição do dono no D7).

  No projeto, o commit vai para a branch própria `controle`, nunca para `develop` (`R-FLUXO`, `R-MAIN`); ver D3.
- (b) Hook de PostToolUse em toda escrita. Recusada: um commit por edição, ruído, e corrida entre sessões.
- (c) Só o texto do Jarvis ("commit a cada marco"). Recusada: já existe como ordem e falhou 3 vezes.

### AE4: toda ordem aponta para um cartão
- (a) Recomendada:
  - `forge-check ordens [--pedido] [--desde]` lista `sem-cartao:` e `sem-id:` das linhas ORDEM DO DONO. Reusa o
    `linhas_sem_cartao` das decisões; não é lógica nova.
  - `anotar --tipo ordem` passa a exigir `--cartao <ID|E<n>>`, conferido contra o KANBAN ou as etapas do pedido, e grava
    `· cartão: <ID>` na linha.
- (b) Só a listagem. Recusada: acha depois, não evita.

### AE5: retrospectiva cobrada 24 h depois da main
- (a) Recomendada: `forge-check retro --pendentes` lista as tags `vX.Y.Z` da `main` com mais de 24 h que nenhuma retro
  cobre. A retro declara `Cobre: vX.Y.Z, ...` no cabeçalho, então uma retro de pedido pode cobrir várias versões. A
  cobrança é uma linha da auditoria (AE6) e do recibo das 8h.
- (b) Uma retro por versão. Recusada: com corte a cada cerca de 6 h, seriam 4 retros por dia.

### AE6: auditoria diária às 8h
- (a) Recomendada: `forge-check auditoria [--gravar] [--serie N]` em módulo próprio (`bin/forge_auditoria.py`), só
  leitura. Cada checagem imprime `divergencia: <classe> | <alvo> | <fato>`. Classes:
  - `pronto-sem-merge`;
  - `andamento-sem-branch`;
  - `pr-sem-cartao`;
  - `branch-mesclada-viva`;
  - `branch-orfa` (sem PR e sem cartão ativo há mais de 48 h);
  - `copia-de-item-fechado`;
  - `versao-divergente` (tag × `plugin.json` × CHANGELOG × ordem `main ≤ homolog ≤ develop`);
  - `retro-pendente` (AE5);
  - `ordem-sem-cartao` (AE4);
  - `controle-sem-commit` (AE3);
  - `ruleset-com-bypass` (AE8).

  `--gravar` escreve `docs/kanban/auditoria/<data>.md` na pasta de controle. `--serie 3` sai rc 0 só com 3 dias seguidos
  em zero: é o critério de pronto do pedido. O agendamento das 8h fica com o relógio (D7).
- (b) Ação do GitHub com agendamento. Recusada: não vê a pasta de controle nem as cópias locais, e em repositório privado
  gasta minutos (`R-CUSTO`).

### AE7: "só aperta" medido
- (a) Recomendada: `forge-check comparar <base> <head> [--alvo hooks|entrega]`.
  - Extrai `hooks/` (ou o `bin/forge-check`) dos dois shas para pastas temporárias, com `git archive`.
  - Roda o mesmo corpus contra os dois: os eventos de PreToolUse das fixtures e as famílias geradas.
  - Conta as transições `recusa → aceite`.
  - Saída: `so-aperta: medido base=<sha> head=<sha> corpus=<sha256> casos=<n> aceites-novos=<n>`, mais um caso por linha
    nas transições.
  - O corpus vem da base, somado aos casos novos do head. Assim, o autor não consegue tirar o caso que viraria.
- (b) Seguir com a declaração no parecer da segurança. Recusada: é o problema medido.
- Limite declarado: o corpus é finito. `aceites-novos=0` prova "nenhum caso conhecido passou a ser aceito", não "nada
  afrouxou". A segurança continua revisando, e a saída mostra a cobertura por família.

#### Emenda AE7.1: limite declarado por lista positiva de forma (E58.52, software-architect)
Motivo: cinco rodadas da segurança, cada uma com uma classe nova de porta (A1 a A14). A guarda cresceu por lista negativa;
cada forma não listada era porta. Decisão: o comparador só mede a árvore que cumpre uma **lista positiva** de forma, nos
dois lados, antes de extrair. Fora dela: `nao-verificavel` com o item que falhou. A lista é do código do comparador, nunca
da árvore medida.
- F1 modos: só blob `100644`, `100755` e pasta. Link `120000` (A11) e submódulo `160000` (A14) saem.
- F2 nomes, em qualquer pasta: nenhum `.gitattributes` (A2) nem `.gitmodules` (A14, também sem gitlink).
- F3 raiz: nenhum arquivo que o Claude Code lê por convenção além de `hooks/hooks.json` (`.mcp.json`, `.lsp.json`,
  `settings.json` e as pastas `monitors/` e `workflows/`, A18); o autor confere a lista na documentação de plugins e no
  binário da versão sondada e a cita no docstring (2.1.224: `themes/` não executa, `bin/` é limite declarado, o resto é
  F4, F5 ou F6).
- F4 `plugin.json`: só as chaves `name`, `version`, `description`, `author`, `repository`, `homepage`, `license`,
  `keywords`, `agents`, `skills`, `commands`. Qualquer outra (`hooks`, `mcpServers`, `lspServers`, `monitors`,
  `outputStyles`, chave futura) sai (A10, A16).
- F5 `marketplace.json`: só `$schema`, `name`, `owner`, `metadata` (só `description` e `version`; `pluginRoot` sai, A15) e
  `plugins` com uma entrada só, `source` `.` ou `./` (A12) e chaves da F4 menos `agents`, `skills`, `commands`.
- F6 cabeçalho de `.md`, forma simples, com toda quebra de linha (o `\r` sozinho também, A17): a 1ª linha de conteúdo na
  coluna 0; toda linha na coluna 0 que não é comentário é `chave:` com a chave em `[A-Za-z0-9_-]` (sem aspas, `?`, `&`,
  `*`, `!`, `{`, `[`, `%`, `<<`); a chave não é `hooks` nem `allowed-tools` (A16). Linha recuada é valor da chave de cima.
  Substitui o `CABECALHO_SUSPEITO` (A13 e o A14 do review deixam de ser lista de truques).
- F7 `hooks/hooks.json`: matcher na forma simples (A7), como hoje.

O que ele promete medir: o veredito dos hooks de `hooks/hooks.json` sobre o corpus, numa árvore que cumpre F1 a F7.
Fora do que ele promete (limite declarado, escrito no docstring e na ajuda, não reprova):
- liberação que não passa por hook (A16): código de `bin/` e `scripts/`, instrução de agente, permissão do projeto ou do
  usuário. `so-aperta: medido` fala dos hooks, não do plugin inteiro; o code review e a segurança seguem lendo o resto;
- o que o instalador ou o Claude Code passarem a ler depois da versão sondada (arquivo de convenção novo na raiz, campo
  novo fora dos manifestos). Campo novo nos manifestos já sai pela F4/F5;
- o `metadata.pluginRoot` (A15) não precisa de prova de leitura: sai pela F5 por não estar na lista;
- hook que detecta o ambiente sintético e o corpus finito (limite original acima).

Critério de parada das rodadas da segurança (vale para o AE7.1 e o AE7.2):
- bloqueante: árvore que cumpre F1 a F7, mede rc 0 ou 1, e o Claude Code instalado roda nela um hook, um argv, um ambiente
  ou um conteúdo diferente do que o comparador rodou. A prova é a sonda nessa árvore, com o item da lista que ela cumpre;
- bloqueante: item da lista implementado diferente do texto acima (teste que deveria dar rc 2 e dá rc 0);
- limite declarado (cartão, não reprova): porta que exige forma fora de F1 a F7 (já sai `nao-verificavel` por construção) e
  tudo da lista "fora do que ele promete". Quem achar caso nessa classe propõe item novo na lista por cartão.
- A revalidação lê o delta e a lista; achado novo cita o item F que a árvore da sonda cumpre, ou é limite declarado.

Efeito no Forge hoje (árvore do head 3fb6761c, lida neste clone): F2 e F3 cumprem (nenhum `.gitattributes`, `.gitmodules`,
`.mcp.json`, `.lsp.json` nem `settings.json`); F4 cumpre (`name`, `version`, `description`, `author`, `repository`,
`license`, `keywords`, `agents`, `skills`); F5 cumpre (`name`, `owner`, `metadata.description`, um plugin com `source` `.`,
`name`, `description`); F1 cumpre pelos pareceres (0 links no review, 0 gitlinks na segurança); `allowed-tools` em 0 `.md`.
F6 não foi provada sobre os 1535 cabeçalhos: o oráculo é o C0 (`forge-check comparar HEAD HEAD`, e o mesmo em
`origin/develop` e `origin/main`) dar rc 0. Se um `.md` do Forge cair na F6, corrige-se o `.md`, não a regra.

Afrouxa: não. Toda forma que hoje dá rc 2 continua dando; a lista só acrescenta saídas rc 2 (o corpo do `.md` já não
contava desde o A13). O critério de parada muda o que reprova na revisão da segurança, não uma regra de `docs/regras/`; se
o `security-engineer` divergir, vira ADR com as duas posições. Tamanho: F4 a F6 trocam código que existe
(`declara_hooks`, `plugin_fora_da_raiz`, `CABECALHO_SUSPEITO`); o teto já excedido (303 linhas) não deve crescer mais de 30.
Reversão: um afrouxamento real, num PR da `develop`, que passe F1 a F7 com rc 0 e só a revisão humana pegue reabre a
decisão (a lista positiva não fecha a classe e volta a lista de truques com sonda por rodada).

### AE8: ruleset da develop sem exceção
- (a) Recomendada, em duas partes:
  - Texto: o `devops-engineer` atualiza o passo a passo, no Forge e no modelo de projeto, para o estado real: achar o
    ruleset com bypass, tirar o ator e conferir. A emergência (develop vermelha) passa pelo modo conserto da BP2 no
    `bin/forge-fechar`, nunca por bypass.
  - Conferência: a auditoria lê `gh api repos/<dono>/<repo>/rulesets` e cada ruleset que atinge a develop. Diverge se
    `current_user_can_bypass` for diferente de `never` para a conta da máquina, que é a do dono (20/11 08:30). O primeiro
    passo do AE8.2 confirma o campo na API real; se ele não existir, o item volta como pergunta.
- (b) Só o texto. Recusada: o texto já pede bypass vazio desde 0.45.6, e o bypass segue lá.

## 4. Corte em itens (até 150 linhas de código e até 10 arquivos cada)

Linhas contam só código de produção. Teste, spec de mutante e fragmento de `changelog.d/` acompanham todo item e não
contam (regra do META85-ITEM-ATE-10-ARQUIVOS).

| Item | Papel | Arquivos | Linhas | Depende de | Casos de abuso que cabem ao item |
|---|---|---|---|---|---|
| AE1.1 `forge-check onde` | backend da stack | `bin/forge_onde.py`, `bin/forge-check` (subcomando), teste, spec de mutante, changelog | ~130 | — | ref com `..` ou opção (`-x`) vira argumento do git; `gh` lento (timeout 10 s, sai `nao-verificavel`, nunca `sim`); nome de branch com controle no texto da saída |
| AE1.2 movimento exige `--prova` | backend da stack | `bin/forge-check` (`cmd_movimento`), teste, spec, `skills/` do quadro (uso), changelog | ~110 | AE1.1 | prova de outro cartão (o PR não cita o ID: recusa); PR mesclado em outra base; `rodar:` com slug de outra raiz ou link simbólico; `juntado:` em cartão fechado ou nele mesmo |
| AE1.3 Pronto sem prova é violação do quadro | backend da stack | `bin/forge-check` (`cmd_kanban`), teste, spec, changelog | ~60 | AE1.2 | linha de prova escrita à mão no histórico (o formato leva o sha conferido; a auditoria confere de novo); edição direta do KANBAN.md sem movimento (o hook `quadro.py` já roda `cmd_kanban`) |
| AE1.4 medida da afirmação sem prova | tech-lead | `hooks/meta.py` (medida S6), `agents/jarvis.md` (colar a linha do `onde`), teste, changelog | ~50 | AE1.1 | mensagem que esconde "feito" em citação ou código (conta o texto fora dos dois e a lista de palavras é fixa); só mede, nunca bloqueia (ADR 0003) |
| AE3.1 `forge-check controle salvar` e marcos | backend da stack | `bin/forge_controle.py`, `bin/forge-check` (5 chamadas de marco), teste, spec, changelog | ~140 | — | caminho de controle com link para fora (recusa, O_NOFOLLOW); arquivo grande ou segredo (lista positiva de caminhos e teto de tamanho); hook ativo na pasta de controle que não seja da fábrica (`core.hooksPath` ou `.git/hooks`: confere antes do commit e recusa com `nao-verificavel`; nunca troca nem esvazia o `core.hooksPath`, `R-VERIFY`; sem `-c` vindo de fora); push no projeto só da branch `controle`, conferida, nunca da `develop`; dois commits ao mesmo tempo (trava) |
| AE3.2 relógio de 30 min e branch `controle` no projeto | devops-engineer | `scripts/forge-relogio`, atalho da BP3 (janela no tmux), `hooks/doutor.py` (aviso de relógio parado), modelo de projeto, teste, changelog | ~120 | AE3.1, BP3 S1 | relógio rodando o `forge-check` de uma cópia de trabalho (só o do plugin instalado, pelo caminho do plugin); relógio duplicado (pidfile com trava); relógio que faz push, escreve no GitHub ou grava fora da pasta de controle (lista positiva: o script só chama o `forge-check` do plugin instalado, e este só o `gh` de leitura e o git local da pasta de controle; o teste prova as três condições do D7) |
| AE4.1 `forge-check ordens` e `anotar --cartao` | backend da stack | `bin/forge-check` (`cmd_decisoes` generalizado, `cmd_anotar`), teste, spec, `agents/jarvis.md` (uso), changelog | ~90 | — | `--cartao` inventado (confere o KANBAN e as etapas do pedido); ID de cartão fechado sem entrega (vale só se a ordem for anterior ao fechamento); cartão de outro pedido (a coluna Pedido tem de ser o pedido anotado); KANBAN.md trocado no meio, FIFO ou grande demais (uma abertura com `O_NOFOLLOW` e `O_NONBLOCK`, só arquivo comum, com teto de bytes) |
| AE5.1 `retro --pendentes` e `Cobre:` | backend da stack | `bin/forge-check` (`cmd_retro`), modelo de retrospectiva (Forge e projeto), teste, spec, changelog | ~80 | — | `Cobre:` com versão que não existe (`aviso:` e não cobre); retro vazia só com o cabeçalho (exige as seções do modelo); tag fora da `main` |
| AE6.1 auditoria: núcleo, cartões, PRs, branches | backend da stack | `bin/forge_auditoria.py`, `bin/forge-check` (subcomando), teste, spec, changelog | ~150 | AE1.1; AE2 (formato da citação do cartão no PR) | resposta do `gh` com nome de branch hostil (sai por `sem_controle`); `gh` fora do ar (classe `nao-verificavel`: não conta como zero, ver D8) |
| AE6.2 auditoria: cópias, versões, retro, ordens, controle | backend da stack | `bin/forge_auditoria.py`, teste, spec, changelog | ~130 | AE6.1, AE4.1, AE5.1, AE3.1 | cópia em `wt/` que é link para fora (não segue); `plugin.json` ilegível (diverge, não cai) |
| AE6.3 gravação diária e série de 3 dias | backend da stack | `bin/forge_auditoria.py`, `scripts/forge-relogio` (chamada das 8h), teste, changelog | ~70 | AE6.2, AE3.2 | arquivo do dia reescrito à mão para zerar (a série relê os dias pelo commit do AE3, e o arquivo traz o sha256 do conteúdo); dia sem arquivo conta como não zero |
| AE7.1 comparador de hooks | tech-lead | `bin/forge_comparar.py`, `bin/forge-check` (subcomando), `tests/comparar/corpus.jsonl`, teste, spec, changelog | ~150 | — | head que remove casos do corpus (o corpus vem da base); hook do head que se comporta diferente quando detecta o comparador (roda com o mesmo ambiente e argv do Claude Code); `git archive` de sha fora do repositório |
| AE7.2 famílias geradas e alvo `entrega` com o caso do E50 | tech-lead | `tests/comparar/geradores.py`, `bin/forge_comparar.py` (alvo `entrega` com repositórios de fixture), teste, changelog | ~140 | AE7.1, E50 na develop | gerador com semente variável (semente fixa e registrada na saída); o caso do E50 (parecer commitado sozinho na volta) precisa aparecer como `aceite-novo` contra a base anterior ao E50 (prova de que o comparador vê o afrouxamento autorizado) |
| AE7.3 o rótulo "só aperta" exige a linha medida | tech-lead | `bin/forge-check` (`cmd_pr`), `tests/catraca.py` (leitura do parecer de segurança), `agents/security-engineer.md`, teste, spec, changelog | ~90 | AE7.1; PV-A (OK preso ao commit) | linha `so-aperta:` copiada de outro PR (base e head precisam ser os do PR; o corpus, o da base); linha com `aceites-novos>0` e rótulo sem OK do dono (recusa) |
| AE8.1 passo a passo do ruleset sem bypass | devops-engineer | `docs/protecao-de-branch.md`, `templates/projeto/docs/engineering/protecao-de-branch.md`, changelog | texto | — | o texto não pede token nem API de escrita a agente (`R-CONFORMIDADE`) |
| AE8.2 checagem de bypass na auditoria | devops-engineer | `bin/forge_auditoria.py`, teste, changelog | ~50 | AE6.1 | resposta sem o campo (diverge como `nao-verificavel`, nunca `never`); ruleset em modo Evaluate (diverge: não barra) |

Ordem e paralelismo. Uma trilha por arquivo, como manda a diretriz 33:
- Trilha `bin/forge-check`, em série: AE1.1 → AE1.2 → AE1.3 → AE4.1 → AE5.1 → AE6.1 (subcomando) → AE7.1 (subcomando)
  → AE7.3. Ela divide o arquivo com o AE2 e o contador (E54.1) e com o PV-A. O `tech-lead` decide a ordem entre os
  pedidos.
- Em paralelo com a trilha acima: AE3.1 e AE3.2 (módulo e script próprios); AE7.2 (testes e módulo próprio, depois do
  AE7.1); AE8.1 (texto, pode começar já); AE1.4 (`hooks/meta.py`).
- `bin/forge_auditoria.py` em série: AE6.1 → AE6.2 → AE8.2 → AE6.3.
- `qa-engineer` em cada item: escreve os testes a partir desta tabela, em paralelo ao autor (META42). Cada caso de abuso
  vira teste.

## 5. Critério de parada (AE7, AE1.2/AE1.3, AE6; PAR-P2)
- bloqueia: o movimento a Pronto ou Fechado sem prova conferida; o rótulo "só aperta" sem a linha medida do próprio
  PR; a auditoria que diz zero sem ter lido todas as fontes.
- prova-falsa · `--prova` cujo alvo não é o cartão, a base ou o sha · oráculo: `tests/test_forge_onde.py` e o teste do
  `cmd_movimento` com prova de outro cartão
- pronto-sem-prova · cartão em Pronto, depois do corte (D1), sem linha `prova:` · oráculo: teste do `cmd_kanban` com
  fixture de histórico
- aceite-novo · caso do corpus recusado na base e aceito no head · oráculo: `forge-check comparar` com o par de shas do
  E50 (AE7.2)
- linha-alheia · `so-aperta:` com base ou head diferente dos do PR · oráculo: teste do `cmd_pr` com a linha de outro PR
- zero-cego · auditoria rc 0 com uma fonte sem ler (`gh` fora do ar) · oráculo: teste do `forge_auditoria` com `gh`
  simulado em falha
- gatilho · oráculo: `python3 -m unittest tests.test_forge_onde tests.test_auditoria tests.test_comparar -v`
- O que não está nas classes acima vai para cartão, não para reprovação (o mesmo critério do lote da volta única).

## 6. Decisões que dependem do dono

1. **D1 (AE1) Corte por data.** A prova é exigida dos movimentos feitos depois do merge do AE1.2. Os cartões antigos em
   Pronto sem prova saem numa lista única da auditoria, e o `agile-coach` faz o backfill em 1 dia.
   Recomendo: sim.
2. **D2 (AE1) Ação do dono sem leitor por ferramenta** (por exemplo: "reabri a sessão", "configurei no site"):
   - (a) fica em "Aguardando o dono" até existir um leitor, e cada leitor que falta vira item;
   - (b) aceitar `prova: dono-disse <hora>`, contada à parte.

   Recomendo (a). Com (b), o "inclusive ação do dono" deixaria de valer.
3. **D3 (AE3) Destino do commit:**
   - no Forge: commit local a cada marco, mais push se a pasta de controle tiver remoto;
   - no projeto: branch própria `controle`.

   Recomendo: sim aos dois. O push protege contra perder a máquina (QUADRO-VERSIONADO).
   Quem faz o push: o `controle salvar` chamado num marco, na sessão; o relógio só faz o commit local (condição do D7).
4. **D4 (AE3) Absorver DOCS-COMMIT-AUTO, QUADRO-VERSIONADO e QUADRO-E-RETRO-NO-GIT no AE3,** fechando os três como
   "juntado em AE3". Recomendo: sim.
5. **D5 (AE4) O que conta como apontador:**
   - (a) cartão do KANBAN ou etapa `E<n>` do pedido; a ordem de execução imediata aponta para a etapa que a cumpriu;
   - (b) só cartão.

   Recomendo (a). Com (b), cada "faça o commit agora" vira um cartão.
6. **D6 (AE5) Unidade da cobrança:** cobrar por versão na main, com a retro agrupando versões pela linha `Cobre:`.
   Recomendo: sim.
7. **D7 (AE3, AE6) Relógio:**
   - (a) uma janela do tmux da BP3 roda `scripts/forge-relogio` (30 min e 8h), com o plugin instalado e fora da sessão,
     e o doutor avisa quando o relógio parar;
   - (b) o primeiro Stop depois das 8h (só com sessão ativa; o Stop fica lento com o `gh`);
   - (c) uma ação agendada do GitHub (não vê a pasta local; custa minutos em repositório privado).

   Recomendo (a).
   Condição do dono (20/11 13:51), parte do aceite: o relógio roda só o plugin instalado, só lê o GitHub e só grava na
   pasta de controle. A segurança aprova antes de ligar, e o teste do AE3.2 prova. Por isso o relógio não faz push (D3).
8. **D8 (AE6) Definição de zero:** toda linha `divergencia:` conta, e `nao-verificavel` também. A ferramenta não tem lista
   de isenção; ruído recorrente vira cartão e conserto. A contagem dos 3 dias começa no merge do AE6.3.
   Recomendo: sim.
9. **D9 (AE7) Uso da medida:**
   - o rótulo `afrouxa-regra` com o motivo "só aperta" só vale com `aceites-novos=0` no par base/head do PR;
   - com `aceites-novos>0`, volta a pergunta ao dono com a lista de casos, como foi feito no E3.32;
   - a confirmação escrita da segurança (condição de 19/11 08:54) passa a citar a linha.

   Recomendo: sim.
10. **D10 (AE8) Emergência sem bypass:** a develop vermelha só se conserta pelo modo conserto da BP2. O dono também
    espera a bateria (o texto atual já diz isso). O `main-do-dono` mantém o bypass "só por PR", que vale só para a regra
    de update da main. Recomendo: sim.

## 7. Riscos e reversão

| Risco | Mitigação | Reverte se (fato observável) |
|---|---|---|
| AE1.2 trava o fluxo quando o `gh` cai | `nao-verificavel` deixa o cartão em "Aguardando validação", não em Pronto; nada se perde | mais de 2 movimentos por dia presos por `nao-verificavel` durante 3 dias: o `pr:` passa a aceitar o `git merge-base` sozinho |
| AE3 faz commit de lixo ou de segredo | lista positiva de caminhos, teto de tamanho e parecer da segurança | um commit automático com caminho fora da lista: desliga o relógio e o commit volta a ser à mão até o conserto |
| Relógio (D7) roda código fora do sandbox | só o plugin instalado (versão da main), só leitura no GitHub, gravação só na pasta de controle | o relógio executa algo fora do plugin instalado (o teste do AE3.2 falha): tira a janela do atalho |
| AE6 com ruído alto não zera nunca | classes pequenas; ruído vira conserto, não isenção | 7 dias sem nenhum dia em zero e mais de 50% das linhas de uma só classe: a classe é revista em ADR com o dono |
| AE7 dá falsa segurança (corpus finito) | a saída mostra a cobertura; a segurança segue revisando; o corpus cresce a cada achado | um afrouxamento achado depois do merge com `aceites-novos=0`: o caso entra no corpus e o D9 volta a pedir a declaração junto com a medida |
| AE8 sem bypass prende o dono numa develop vermelha | modo conserto da BP2 | 2 episódios de develop vermelha por mais de 4 h sem saída pelo modo conserto: o dono decide de novo o bypass |
| Concorrência na trilha `bin/forge-check` com o AE2 e o PV-A | série única e subcomandos em módulos próprios | — (só ordem) |

Segurança (`R-SEGURANCA`): passam pelo `security-engineer` os itens AE1.2, AE1.3, AE3.1, AE3.2, AE6.1, AE6.3, AE7.1,
AE7.3 e AE8.2. São controles, `gh` com a conta de administrador, commit automático e código rodando fora do sandbox.

Leituras: pedido MELHORIAS-ANTI-ERRO; v0478 (Escopo, E50 e E54; decisões de 19/11 08:54, 20/11 09:43, 10:59 e 12:33);
retros v0474 e v0478; triagem E11.3; `docs/protecao-de-branch.md`; `bin/forge-check` (subcomandos, `cmd_decisoes`);
`bin/forge_corrigidos.py` (`cmd_afrouxamentos`); `hooks/hooks.json`, `doutor.py`, `meta.py`, `quadro.py`; ADR 0001,
0003, 0008 e 0018; `docs/engineering/achados-recorrentes.md`.
