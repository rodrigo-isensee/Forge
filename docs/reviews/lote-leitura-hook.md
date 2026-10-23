---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 3df051e400a7be84cba20a9da185f9e1ba86f3f7
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: lote-leitura-hook (revalidação 9, opção B)

Escopo: os commits da opção B, `b2c7d83..3df051e`. São eles: `403a3a0`, o corpus com as marcas `fecha: "B"`; `140256f`, o gatilho e o T9b (a parte A); `befe8d3`, o refactor que leva `separar_lancadores`, `LANCADORES` e `SHELLS` para `_comum`; `d6bd263`, a recusa da reavaliação nos dois hooks, a propriedade (5) e a troca do fixture FD13; e `3df051e`, as emendas e o changelog. Pedido RET-LEITURA-HOOK-REV9, E1.1. Sou revisor independente e não implementei (`R-REVIEW`). O parecer anterior (revalidação 8, `reprovado`, A1) está em `ed4416e`.

O `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` listou `b2c7d83..1648cd0`. O `1648cd0` é a cópia do parecer anterior nesta worktree. Li o delta inteiro:
- `hooks/_comum.py`: 1611-1622, 1659-1660 e 1712-1796;
- `hooks/conformidade.py`: 27-48, 232, 339, 369, 623, 721-727 e 853;
- `hooks/parecer.py`: 21-24, 342-349, 378-398;
- o corpus, linhas 193-210;
- os dois fixtures `contrib-remoto-nomeado-proprio-*`;
- `tests/test_hooks.py`: o T8 por nível, `NIVEIS`, o T9b e a propriedade;
- a ADR 0011, linha 41; `docs/hooks.md:94`; o desenho, linhas 88 e 280-281; e o fragmento do changelog.

Fica como "já lido" o que vem de antes de `b2c7d83` (revalidações 1 a 8). A segurança é do E2.1 e não foi refeita aqui.

**Critério:** vale o da seção 4B da proposta `docs/propostas/lote-leitura-hook-caminho-rev8.md`, que está no desenho, linha 280. Uma sonda bloqueia se os dois hooks, ou um deles, a liberarem com marcador e o T9b mostrar que o bash rodou a `SENTINELA`. Ficam de fora as formas da linha "Não promete": A4, X1 a X3 e a reavaliação por um programa que o hook não separa com o `<<` calculado. Apliquei esse critério sem mudança. A linha "Promete" (desenho, linha 88; ADR 0011, item 2(b)) diz que o `eval` e o `bash`/`sh`/`zsh`/`dash`/`ksh` com `-…c…` recusam "nos dois hooks, haja `<<` ou não". Leio `eval` e `-c` como a palavra que o shell recebe depois de tirar as aspas. É a mesma leitura da opção A (ADR 0011, item 2, (a): "como o programa a recebe").

## Achados
- A1 (bloqueante) hooks/_comum.py:1754 · classe "nível" (reconhecimento da reavaliação), 3.ª volta seguida: `reavaliacao` não pula `coproc`; `coproc bash -c '…'` e `coproc eval '…'` saem 0 / 0 e o bash roda a SENTINELA (CO1 a CO3).
- A2 (bloqueante) hooks/parecer.py:378 · mesma classe: o `parecer` reconhece a reavaliação nas palavras do `shlex`, que lê `$'eval'` como `$eval`; `$'eval'`, `e$'val'`, `bash -$'c'` e afins saem 2 / 0 e o bash roda a SENTINELA (AN1 a AN5).
- A3 (recomendado) tests/test_hooks.py:2081 · a propriedade (5) e o T9b só envolvem os textos em `NIVEIS`, a mesma lista que `reavaliacao` reconhece: ficam verdes com A1 e A2 abertos. Gerar os envoltórios com palavra reservada antes e com aspas no nome e na opção.
- A4 (recomendado) hooks/_comum.py:1760 · reavaliação sem `<<` fora da lista enumerada (`| bash`, `. <(…)`, `trap`, alias, `mapfile -C`, nome calculado, `$x eval`, `rbash -c`, `find -exec`): 0 com a SENTINELA rodada, como na `develop`; cartão N-HOOK1 (ver a nota de leitura do critério).
- A6 (recomendado) hooks/parecer.py:378 · leitor de base, fora do delta: `time gh pr merge …` sai 2 / 0 e `coproc git push … :main` sai 0 / 0, os dois com a SENTINELA rodada, como na `develop` (CO4, CO5); cartão ao `security-engineer` e ao N-HOOK1.
- A5 (recomendado) hooks/_comum.py:1497 · o A4 da revalidação 8 (opção do git que roda programa, R1) segue no cartão N-HOOK1, por decisão do dono.

## Parecer
**Reprovado**, por dois bloqueantes: A1 e A2. A opção B está implementada como a seção 4B pede, e o caminho dela está certo:
- a ordem dos commits é a pedida (o corpus vermelho, depois a regra, depois os testes e as emendas);
- o gatilho de A está em `HEREDOC_QUE_O_BASH_FORMA`;
- a recusa da reavaliação vem depois das regras específicas nos dois hooks;
- o T9b roda o que cada hook libera;
- a ADR 0011 só endurece;
- o desenho tem o `critério mudou:` nas linhas 88 e 280.

Q1 a Q6, QC1 e QC2 saem 2 / 2.

Mas a frase "fecha a classe nível por construção" só vale se o reconhecimento da reavaliação estiver completo, e ele é de novo uma leitura de texto que deixa formas de fora. Em A1, o `bash -c` está escrito, só que depois de uma palavra reservada que o hook não pula. Em A2, a palavra é `eval` ou `-c` depois da remoção de aspas que o `shlex` não faz. Nos dois casos, um dos hooks libera com marcador e o bash roda a SENTINELA. São formas da linha "Promete" e não estão na linha "Não promete". Não é regressão: a `develop` também libera.

Pela regra das duas voltas (decisão "A" de 2026-10-22), esta é a 3.ª volta seguida da classe "nível". Por isso a entrega para: o `software-architect` propõe o caminho e o dono decide. Não é uma volta direta ao autor.

**A1.** O CO4 (`coproc {CORPO}`, a linha crítica direta) também sai 0 / 0. Então o furo de origem está no leitor de base, e a segurança o leva como cartão próprio (R5a do parecer dela). Mantenho o A1 como bloqueante porque CO1 e CO2 são as formas que a promessa da opção B nomeia (`bash -c`, `eval`, "haja `<<` ou não"). Se o arquiteto puser o `coproc` no leitor de base, o A1 cai junto. A correção pontual é pôr `coproc` (com o nome opcional e o `{`) na lista que `reavaliacao` pula. Mas o achado mostra o mesmo padrão das voltas 7 e 8: a lista do hook e a lista do teste são a mesma (A3).

**A2.** O `conformidade` dá 2 nessas formas porque já recusa o `$` com marcador. O `parecer` não recusa. Duas saídas possíveis: tirar as aspas como o bash antes de chamar `reavaliacao`, ou recusar com o marcador a palavra de comando que o `leituras` não lê literal.

**Nota de leitura do critério (A4).** A frase de parada isenta "a reavaliação por um programa que o hook não separa **com o `<<` calculado**". Lida ao pé da letra, a mesma reavaliação **sem** `<<` não está isenta: está nas formas de A4. Eu as classifiquei como cartão por dois motivos. A linha "Promete" enumera os nomes (`eval`, os cinco shells com `-c`). E o desenho, linha 90, diz que o que nenhuma linha "Promete" cobre é cartão. Parte delas (`find -exec`, alias, `$CMD`) também já está em `docs/hooks.md:92` como "[B] barrado em regra, não garantido". Se o arquiteto ou o Jarvis lerem a frase ao pé da letra, A4 vira bloqueante da mesma classe, nesta mesma passada. O `| bash` sem `<<` merece atenção: o QP1 fecha só a forma com `<''<`.

### Revalidação dos achados da revalidação 8, contra os hooks reais
As sondas rodaram com um runner próprio. Ele usa `decisoes_dos_hooks` e `rodar_no_bash_do_t9b` de `tests/test_hooks.py` (os modelos do corpus, a SENTINELA do T9b no `{CORPO}`, `HOME` e as pastas em `$TMPDIR`) e roda sobre a worktree em `3df051e`. A `develop` e `b2c7d83` rodaram com os `hooks/` de cada commit (`git archive`), sob o mesmo runner.

| Item (rev. 8) | Sonda | 3df051e conf / par | Estado |
|---|---|---|---|
| A1 (Q1 a Q4) | Q1 `eval '… cat <''<"EOF"⏎{CORPO}⏎EOF'` | 2 / 2 (develop 0 / 0) | **resolvido** |
| A1 | Q2, Q3, Q4, Q6 | 2 / 2 (corpus verde) | resolvido |
| A1 (X5 da proposta) | QC1 `eval "… $(printf '\x3c\x3c')EOF…"`, QC2 | 2 / 2 (develop 2 / 0) | resolvido |
| A2 (o T9 só olha a gramática) | mutações MA e MB, abaixo | o T9b fica vermelho | **resolvido**, com a ressalva do MBc |
| A3 (BL1 só pelo leitor) | mutação M2t | o corpus fica vermelho em `parecer/BL2` | **resolvido** (só no `parecer`) |
| A4 (opções do git) | não medido de novo | – | **não resolvido**, cartão N-HOOK1 (A5) |

### Sondas novas (A1 a A4)
Na coluna "develop", 0* quer dizer que o hook libera e a SENTINELA roda.

| ID | Sonda | 3df051e conf / par | develop conf / par |
|---|---|---|---|
| Z0 | `bash -c '{CORPO}'` (controle) | 2 / 2 | 2 / 0* |
| CO1 | `coproc bash -c '{CORPO}'` | **0 / 0**, SENTINELA | 0* / 0* |
| CO2 | `coproc eval '{CORPO}'` | **0 / 0**, SENTINELA | 0* / 0* |
| CO4 | `coproc {CORPO}` (sem reavaliação) | 0 / 0, SENTINELA (A1, A6) | 0* / 0* |
| CO5 | `time {CORPO}` (sem reavaliação) | 2 / **0**, SENTINELA (A6) | 2 / 0* |
| CO3 | `coproc x { eval '{CORPO}'; }` | 2 / **0**, SENTINELA | 2 / 0* |
| AN1 | `bash -$'c' '{CORPO}'` | 2 / **0**, SENTINELA | 2 / 0* |
| AN2 a AN5 | `$'eval'`, `e$'val'`, `bash $'-c'`, `$'bash' -c` | 2 / **0**, SENTINELA | 2 / 0* |
| QT1 a QT6 | `bash -'c'`, `-\c`, `ba''sh`, `e''val`, `\eval`, `"eval"` | 2 / 2 | 2 / 0* (QT3: 0, sem SENTINELA) |
| LA1 a LA8 | `env X=1`, `command`, `time`, `time -p`, `!`, `nohup`, `if`, `true \|` antes da reavaliação | 2 / 2 | 2 / 0* (LA5: 0, sem SENTINELA) |
| SB1 a SB3 | dentro de `"$(…)"`, `x=$(…)` e `<(…)` | 2 / 2 | 2 / 0* |
| VA1, VA2 | `$x eval '…'`, `"$BASH" -c '…'` | 2 / 0, SENTINELA (A4) | 2 / 0* |
| CN1, CN2 | `$(echo eval) '…'`, `$(printf bash) -c '…'` | 0 / 0, SENTINELA (A4) | 0* / 0* |
| ST1 a ST5 | `\| bash`, `. <(…)`, `trap`, alias, `mapfile -C` | 0 / 0, SENTINELA (A4) | 0* / 0* |
| NR1, NR2 | `rbash -c`, `find -exec bash -c` | 0 / 0 (A4) | 0 / 0 |

No NR1 e no NR2, o T9b troca `rbash` e `find` por registradores. Por isso o efeito foi medido à parte, com os binários reais, `gh` e `git` falsos e `env -i`: os dois gravaram a SENTINELA.

### O T9b e a propriedade (5) provam o critério de fim da 4B?
Sobre as formas que eles enumeram, sim. Sobre a promessa, não.

O que passa:
1. Numa cópia limpa (`git archive 3df051e`), a classe `CorpusHeredocVoltaUnica` inteira, com o T8, o T9, o T9b, a propriedade e o corpus, deu `Ran 8 tests in 72.688s OK`.
2. Q1 a Q4 e Q6 saem 2 / 2 e estão no corpus.
3. Nas mutações, o T9b e a propriedade ficam vermelhos (tabela abaixo).
4. O T9b inclui QC1 e QC2, que ficam verdes porque a chamada recusa.

O que falta: os dois testes amostram só os envoltórios de `NIVEIS`. Por isso não veem A1 nem A2, que fazem o hook liberar e o bash rodar a SENTINELA na mesma máquina do T9b (A3).

Cada mutação rodou numa cópia limpa, uma de cada vez (`R-TETO`), com só o T9b, a propriedade e o corpus:

| Mutação | T9b | propriedade | corpus |
|---|---|---|---|
| MB: sem a recusa da reavaliação nos dois hooks | vermelho (QC1, QC2 no `parecer`) | 21 falhas | 5 falhas (QC1, QC2, FD13b, FD13d, FD13e no `parecer`) |
| MBc: só no `conformidade` | **verde** (o QC já recusa por outra regra) | 7 falhas | 3 falhas (FD13a, FD13c, FD13d) |
| MBp: só no `parecer` | vermelho (QC1, QC2) | 14 falhas | 5 falhas |
| MA: o gatilho de `b2c7d83` (`"<<" in texto`) | vermelho (QP1, nos dois hooks) | verde | 4 falhas (QP1, FD12, FD12b) |
| M2t: o gatilho sem `\⏎` | verde | verde | 1 falha (`parecer/BL2`) |

Sem mutação, os mesmos 3 testes deram `Ran 3 tests in 102.896s OK`. No `conformidade`, quem prova a opção B é a propriedade, e não o T9b. Com B, o MA não deixa o T9b vermelho em B1, B2 e Q1 a Q4, o que é esperado: a recusa da reavaliação os cobre antes do gatilho.

### Fixture FD13 e refactor `befe8d3`
- **FD13.** O `contrib-remoto-nomeado-proprio-libera` mantém o que ele prova, que é o R-CONTRIB com o remoto `forge` e o `GH_REPO=acme/proj`. Agora o `gh pr merge 3` é direto, sem `bash -c`. A linha antiga foi para `contrib-remoto-nomeado-proprio-bash-c-bloqueia`, que espera 2 com `R-CONFORMIDADE: \`bash -c\` na chamada com ação crítica`. A troca está certa. A proposta dizia que nenhum fixture `-libera` usava `bash -c` (seção 1, [EXE]), e isso estava errado: o histórico do RET-LEITURA-HOOK-B registra o achado. O custo de uso do FD13 continua com o contorno de uma linha.
- **`befe8d3`.** Só move código. Comparei as linhas removidas com as acrescentadas, ordenadas. Só duas diferem: o `import` de `_comum` no `conformidade` e o comentário de `LANCADORES`. No `conformidade` não sobrou referência a `valor_do_split_string` nem a `ENV_COM_VALOR_CURTA`.

### Fora do bloco
- A suíte completa não rodou. O pedido limita a memória e manda rodar só o corpus e as sondas, e o pre-push do envio roda a suíte. O implementador registrou `suíte 1610 OK` no histórico do RET-LEITURA-HOOK-B. `scripts/validar-plugin.sh` também não rodou, porque o delta não toca o manifesto nem a estrutura do plugin.
- Código: `reavaliacao` é curta e diz o que faz. `CONTORNO_DA_REAVALIACAO` é uma fonte única para as duas mensagens. O `env -S` ilegível como reavaliação fecha na dúvida. Há um falso positivo menor que não chega a achado: `OPCAO_DE_REAVALIACAO` olha todas as palavras depois do shell, então `bash x.sh -c` com marcador recusa.
- Os commits estão em Conventional Commits em português e não tocam `tests/config.json`. O Forge não tem `docs/engineering/praticas.md`, então não há regra de ferramenta nem de leitura a citar.
- Segurança: A1 e A2 são furos no controle, com efeito no bash (`R-REVIEW` via `gh pr merge`, `R-MAIN` via `git push … :main`). A4 é o mesmo efeito em formas que a promessa não enumera. O `security-engineer` os recebe por este parecer (sondas CO, AN, VA, CN, ST e NR), sem cartão à parte. O parecer dele, `eb3da15`, aprova a revalidação 9 e leva o `coproc` como cartão (R5a). A divergência sobre CO1 e CO2 está no A1 e é para o arquiteto decidir. O AN1 a AN5 e o CO5 não aparecem nas sondas dele.
