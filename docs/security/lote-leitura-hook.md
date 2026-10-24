---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 96227be7a53d1f7c4448f19fa452bc5116714f9b
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-leitura-hook (revalidação 10, opção B da revalidação 9)

Pedido RET-LEITURA-HOOK-REV10, etapa E2.1. Escopo: a opção B da proposta `docs/propostas/lote-leitura-hook-caminho-rev9.md` (seções 2, 3B e 5).
- A implementação está em `83c63b2`, `53d0544`, `aadb806`, `d73c373` e `b42fd4b`. A `develop` foi trazida em `c3d55d5`, que é um merge limpo: `git show --cc` não mostra resolução. Os textos estão em `96227be`.
- O parecer anterior é a revalidação 9, sobre `3df051e`, commitado em `eb3da15`.
- `forge-check delta --parecer` sobre ele lista o intervalo `3df051e..96227be`. O intervalo inclui o que veio da `develop` pelo merge, que passou pelos gates dos próprios PRs.
- Reli inteiro o que é do lote: `hooks/_comum.py:1757-1915`, `hooks/conformidade.py:660-670,854-857`, `hooks/parecer.py:358-385`, o corpus, `tests/test_hooks.py` (G1, a prova de G1 no bash, a redução contra o bash e a propriedade), a ADR 0011 (linha 41), `docs/hooks.md:95` e o desenho (linha 280).

**critério mudou:** não. Vale a frase de parada corrigida (RET-LEITURA-HOOK-CAMINHO4, desenho `docs/propostas/lote-leitura-hook-volta-unica.md`, linha 280 e seguintes), lida com a linha 276.
- **Bloqueia** a sonda que um hook libera com marcador, com efeito provado no bash, numa forma que a linha Promete cobre.
- **A reavaliação prometida** é a palavra que o bash recebe depois da remoção de aspas, inclusive `$'…'` com os escapes ANSI-C, em qualquer posição.
- **O orçamento de tempo** também é promessa escrita. O desenho, na linha 45, diz que "o orçamento de tempo da regra 3.1 continua valendo". `docs/hooks.md:96` diz que "o hook decide antes do timeout de 10 s, que o Claude Code trata como liberado".
- **Fica fora da Promete, e é cartão:** a palavra com expansão, o shell que lê o texto por outra via, os programas que não são shell (X1, X3) e o `coproc {CORPO}` (R5A-COPROC).

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: os hooks `conformidade` e `parecer`. A mudança tira a posição do reconhecimento da reavaliação pelo shell e o faz sobre a palavra reduzida como o bash. Os hooks guardam R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA.

## Achados
- A1 (bloqueante) hooks/_comum.py:1852 · classe "nível" (grafia, redução de `$'…'`): a redução não trata o escape `\x{HH…}` do bash 5.3; `$'\x{65}'val '<gh pr merge …>'` e `bash -$'\x{63}' '…'` saem 0 no parecer e o bash roda a sentinela
- A2 (bloqueante) hooks/_comum.py:1777 · classe nova "orçamento de tempo": `reavaliacao_das_palavras` é quadrática; `: bash bash … (20 mil) ; git push origin X:main` (100 KB) estoura o timeout de 10 s nos dois hooks (liberado) e o bash roda a linha crítica; em 3df051e e na develop, 0,2 a 0,4 s e rc 2

## Detalhe dos achados
Os dois bloqueantes estão aqui, numa passada só. Sondei as famílias CO, AN, VA, CN, ST e NR, as grafias do marcador e os falsos positivos contra os hooks reais da worktree em `96227be`, e as sondas de comparação contra `3df051e` e contra a `develop` `40d8707` (`git archive` em `$TMPDIR`, com os testes de `96227be`). A redução passou por um teste de diferença aleatório contra o `printf` do bash: 9 mil palavras, em duas sementes.

Condições das sondas:
- cada hook rodou **sempre**, sem o atalho do `CRITICO` que o `decisoes_dos_hooks` usa;
- o modelo de fixture é o do corpus;
- a sentinela é a do T9b;
- o bash é o 5.3.9 do `rodar_no_bash_do_t9b`, com `env -i`, registradores no `PATH`, `HOME` e a pasta em `$TMPDIR/security-engineer-lh10/` e sem rede.

As células são conf / par. "SENT" quer dizer que o bash rodou a sentinela; "-" quer dizer que não rodou.

### Resposta por classe: a reavaliação com ação crítica recusa em qualquer posição e grafia?
- **CO (posição): sim.** As 66 sondas saem 2 / 2. Elas cobrem:
  - `coproc` (com e sem nome, com `{ …; }`), `time`, `time -p`, `!` (antes e depois de `time`), `if`, `while`, `until`, `{ }`, `( )`, função (`f()` e `function`), `case` (também com `;;&`), `for` e `select`;
  - redireção antes (`>/dev/null eval`, `2>&1 eval`), atribuição antes, `exec`, `exec -a`, `command -p`, `builtin`, `nohup`, `sudo -u`, `timeout`, `nice`, `setsid`, `stdbuf`, `env --`, `env -S` (as duas grafias), `xargs`, `find -exec`, `flock`, `busybox sh` e um programa desconhecido;
  - depois de `&&`, `||`, `|`, `&`, de quebra de linha e de comentário;
  - dentro de `$(…)`, crase, `"$(…)"`, `<(…)`, `>(…)`, `${x:-$(…)}` (com e sem aspas), `$(( ))`, `(( ))`, `$[ ]`, `a[$(…)]=1`, `a=( … )`, `[[ ]]`, `[ ]`, `case $(…) in` e `<<< "$(…)"`;
  - no corpo de heredoc rodado (`bash <<'E'`, `cat <<'E' | bash`, `eval "$(cat <<'E' …)"`);
  - `ev\`⏎`al`.

  CO1 a CO3, NR1 a NR3 e VA1 do corpus saem 2 / 2.
- **AN (grafia): não, no `parecer`.** 44 das 47 grafias saem 2 / 2:
  - `'…'`, `"…"`, `\`, `$'…'` com `\xHH`, `\nnn`, `\uHHHH` e `\UHHHHHHHH`;
  - `\0` que corta o resto, `$"…"`, `''eval`, `$''eval`, `eval$''`;
  - `"ev"\`⏎`al`, `/bin/b''ash`, `./bash`, `ba$'\x73'h -c`, `bash -$'\x63'`, `bash -"c"` e `bash -\c`.

  Três grafias corretamente não são `eval` e o bash não roda a sentinela: `"eva\l"`, `e"\v"al` e `$'\0145val'`. A exceção é o **A1**: o `$'\x{HH…}'`.
- **VA (variável): sim, dentro da Promete.** `$x eval`, `$empty bash -c`, `x=1 bash -c` e `declare …; eval` saem 2 / 2. As formas em que a palavra do programa é calculada saem 2 / 0 SENT e são cartão N-HOOK1 (expansão): `"$BASH" -c`, `x=eval; $x`, `${x:-eval}` e `"${x}"eval`.
- **CN (nome calculado): fora da Promete, cartão N-HOOK1.** Saem 0 / 0 SENT: `$(printf bash) -c`, `ev?l` e `~/../../bin/bash` no `parecer`. Saem 2 / 2, porque a palavra `eval` ou `bash` aparece dentro da substituição: `$(echo eval)`, `"$(printf eval)"` e `` `echo eval` ``.
- **ST (outra via): fora da Promete, cartão N-HOOK1.** `| bash`, `. <(…)` e `trap` saem 0 / 0 SENT, como no corpus (ST1 a ST3, marca "não promete"). `bash <<<`, `bash -s <<<`, `source /dev/stdin <<<` e `x='a[$(…)]'; (( x ))` saem 2 / 2.
- **NR (reavaliador fora da lista): fora da Promete, cartão N-HOOK1.** Saem 0 / 0: `ash -c`, `mksh -c`, `su x -c`, `script -qc` (2 / 0) e `ssh host '…'`. No T9b, esses programas são registradores, então o "-" não é prova. Eles não estão na lista de shells da frase.

### A1: o escape `\x{…}` do `$'…'` (bloqueante, classe "nível": grafia)
- **Evidência.** `_ansi_c` (`hooks/_comum.py:1852`) só lê `\x` seguido de 1 ou 2 dígitos. O bash 5.3.9 também lê `\x{HH…}`, com qualquer número de dígitos e até sem a chave de fecho: `$'\x{65}val'`, `$'\x{0000065}val'` e `$'\x{65'` dão `e…`. A redução do hook devolve o texto com a barra. Resultado:
  - `$'\x{65}'val`, `$'\x{65}\x{76}\x{61}\x{6c}'`, `bash -$'\x{63}'`, `$'\x{62}'ash -c`, `coproc $'\x{65}'val` e `$'\x{0000065}'val` saem **2 / 0, e o bash roda `gh pr merge SENTINELA --merge`** (AN34 a AN34f);
  - o `conformidade` dá 2 por outra regra, a recusa do `$` com marcador;
  - a `develop` dá o mesmo código, mas a pertença não depende da comparação (proposta, seção 2, motivo 3). A forma é `$'…'` com escape ANSI-C e se reduz a literal: está na Promete.
- **Teste de diferença.**
  - Na semente com `\x{`, 523 de 4 mil palavras divergem do bash. As 30 listadas divergem todas por `\x{`.
  - Na semente sem os elementos `\x{`, 459 de 5 mil divergem. Nas listadas, as que formam letras vêm de `\x` seguido de `{`, e as demais não formam letras (R7).
- **Por que o oráculo não viu.** O `test_reducao_da_palavra_como_o_bash` compara só as grafias de G1, e G1 não tem `\x{`. É o mesmo recorte por amostra que o critério de fim queria evitar, agora na tabela da redução.
- **Caminho de ataque.** Um agente, por engano ou por injeção de prompt, escreve `$'\x{65}'val 'gh pr merge 12 --merge'`. O `parecer` libera, e o `gh pr merge` roda sem parecer de review e de QA (R-REVIEW, R-QA). Restam a proteção de branch e o `pre-push`.
- **Severidade e correção.** Severidade alta. Correção mínima, esforço P:
  - no `_ansi_c`, ler `\x{` como o bash: dígitos hexadecimais até `}`, e o que o bash faz sem a chave;
  - pôr `\x{…}` na tabela de grafias de G1 e no teste de diferença;
  - tornar o teste de diferença gerativo sobre a tabela inteira de escapes, e não só sobre G1;
  - pôr AN34 a AN34f no corpus.
- **Dono:** `tech-lead`.
- **Contagem de voltas.** É a classe "nível" de novo, dentro da frase corrigida. Pela seção 5 da proposta e pela decisão "A" de 2026-10-22, a entrega para e volta ao `software-architect`. A falha está na redução, que a proposta tinha apontado como o único ponto restante da opção B.

### A2: orçamento de tempo do reconhecedor sem posição (bloqueante, classe nova "orçamento")
- **Evidência.** `reavaliacao_das_palavras` (`hooks/_comum.py:1763-1789`) varre `palavras[k + 1:]` para cada palavra de nome de shell (`:1776-1777`), e faz a mesma coisa com `separar_lancadores` para cada `env`. O custo é quadrático no número de palavras do comando simples. A chamada fica dentro de `conferir_linha`, depois da conferência do prazo:
  - no `conformidade` (`hooks/conformidade.py:670`), o prazo de 3 s e o teto de 150 mil caracteres só se conferem na entrada de `bash()`;
  - no `parecer` (`hooks/parecer.py:365`), não há orçamento.
- **Medidas** (`reavaliacao` sozinha): 2 mil palavras em 0,27 s, 5 mil em 2,2 s, 10 mil em 8,3 s e 20 mil em 32 s.
- **De ponta a ponta,** com o hook real e o prazo de produção (`hooks/hooks.json`: 10 s), sobre `: bash bash … ; <sentinela>`:

  | palavras | tamanho | `96227be` | `3df051e` e `develop` `40d8707` | sentinela no bash |
  |---|---|---|---|---|
  | 12 mil | 60 KB | 10,9 s / 10,3 s (rc 2, no prazo largo do teste) | 0,3 s | — |
  | 20 mil | 100 KB, abaixo do teto de 150 mil | **estoura o timeout de 10 s nos dois hooks** | rc 2 em 0,2 a 0,4 s | roda (SENT) |

  Pelo `docs/hooks.md:96` e pelo comentário de `hooks/conformidade.py` (`bash()`), o Claude Code trata o timeout como liberado.
- **Por que os testes não viram.** Os testes de tempo do lote passaram (`tests.test_hooks`: 61 testes, OK) porque nenhum deles usa um comando simples com muitas palavras.
- **Caminho de ataque.** Um agente, por injeção de prompt, manda uma linha longa de palavras inertes seguida de `git push origin HEAD:main` ou de `gh pr merge`. Os dois hooks estouram o prazo, e a ação crítica direta roda sem R-MAIN e sem R-REVIEW. Não é preciso reavaliação nem grafia. Numa máquina carregada, basta menos.
- **Natureza e severidade.** É regressão deste delta. A posição fixa de `3df051e` era linear. Severidade alta, porque exige uma linha deliberada e restam a proteção de branch e o `pre-push`.
- **Correção mínima,** esforço P:
  - tornar o reconhecimento linear: uma passada da direita para a esquerda, com um marcador "há opção com `c` depois";
  - o mesmo para o `env`;
  - conferir o prazo da linha dentro de `conferir_linha` nos dois hooks (o `parecer` com um prazo próprio), recusando ao estourar;
  - um teste de tempo com um comando simples de 20 mil palavras com marcador, que tem de recusar abaixo de 3 s.
- **Dono:** `tech-lead`. Proponho a classe "orçamento" como dimensão nova da matriz (tamanho por número de palavras, não só por caracteres).

### Outra forma de esconder a ação crítica do nível 0
Dentro da Promete, as únicas formas que achei são A1 e A2. As outras que testei ficam fora da Promete.

**Marcador ofuscado (X3, cartão C8 da ADR 0011).**
- **As formas.** O `CRITICO` do `conformidade` é `\b(git|gh)\b[^\n]*\b(push|…)`. Ele não atravessa a quebra de linha e lê o texto cru. Por isso escapam do marcador, nos dois níveis:
  - `git \`⏎`push origin SENTINELA:main` direto (M9), que sai 0 e roda o push;
  - `eval 'git \`⏎`push …'` (M1), `bash -c 'git \`⏎`push …'` (M4) e `coproc eval 'git \`⏎`push …'` (M10);
  - `eval $'git \x70ush …'` (M5).

  Todas saem 0 SENT no `conformidade`. A `develop` dá o mesmo (M1, M9).
- **Por que é cartão.** Sem marcador, a recusa da reavaliação não liga. O que falha é o marcador, que está na "Não promete" (X3), e não a reavaliação.
- **No `parecer`.** O `CRITICO` dele tem `re.S`, e as formas com `\`⏎ dão 2 (M7, M8).
- **Pedido.** Peço ao Jarvis que junte o `\`⏎ e o `$'\x..'` ao cartão C8. A correção que a ADR já escreve para o C8 (rodar o `CRITICO` sobre as palavras reduzidas) cobre os dois, e agora a `reduzida` existe. Severidade alta, porque o push direto passa no hook. Dono: `tech-lead`.

### Falsos positivos além do FD14?
Não achei falso positivo fora da família do FD14 (a palavra `eval`, ou um shell seguido de opção com `c`, como argumento). Comparei com `3df051e`. Os novos são todos FD14:
- `grep -rn eval … && git push`;
- `echo "eval" && git push`;
- `git log -S eval && git pull`;
- `grep -c eval && git pull`;
- `shfmt -ln bash -ci … && git push`;
- `docker exec c bash -lc 'make test' && git push`;
- `echo usa bash -c` com marcador.

Ficaram iguais, sem falso positivo:
- os corpos de heredoc dentro de `"$(cat <<'EOF' …)"` como valor de `-m` e `--body`, mesmo com `eval` ou `bash -c` numa linha (`reavaliacao` devolve None);
- `--body 'Fecha bash -c e eval'`;
- `python3 -c 'print(eval("1"))'`;
- `git commit -F - <<'EOF'`;
- o comentário `# roda bash -c`.

O mais provável em projeto é o `docker exec … bash -lc` (ou `ssh host bash -c`) junto com o push. Recomendo citá-lo no FD14 de `docs/hooks.md:95` (dono: `software-architect`).

### Revalidação das recomendações da revalidação 9
- **R6 (oráculos sobre o domínio do reconhecedor): resolvido** para o que se reduz a literal, salvo o recorte da redução (A1).
  - G1 é gerado por produto, e a verdade vem da construção.
  - `test_g1_esta_na_classe` roda G1 nativo no bash.
  - `rbash` entrou como shell do T9b, e `find`, `flock`, `sudo`, `nice`, `nohup` e `timeout` entraram como repassadores.
- **R3 (limites do T9/T9b): parcial.** Os programas da NR acima seguem como registradores.
- **R5:** segue no N-HOOK1. As formas estão no corpus com a marca "não promete" (CN1 a CN3, VA2, PE1, ST1 a ST3).
- **R5a:** segue no R5A-COPROC (CO4, e CO5 no A6).
- **R1 (`~`):** fora do delta, como estava.

### Recomendações (não bloqueiam)
- **R7. Divergências da redução que não formam letras** (`hooks/_comum.py:1857`, `:1852`). Três casos:
  - `$'\c\''`: o hook fecha a aspa no `\'`, devolve None e pula a palavra;
  - `\c` seguido de caractere fora do ASCII: o hook usa o caractere, e o bash usa o primeiro byte;
  - `\U` acima de 10FFFF: o hook não gera nada, e o bash gera 4 bytes.

  Nenhum dos três forma `eval`, nome de shell ou `-c`, porque o resultado tem byte de controle ou byte fora do ASCII. Não há caminho de ataque. Corrigir junto com o A1 e cobrir pelo teste de diferença. Dono: `tech-lead`.
- **R8. `$"…"` com catálogo de mensagens** [inferência, não sondado]. Com `TEXTDOMAIN`, `TEXTDOMAINDIR`, um locale que traduz e um `.mo` gravado antes, o bash traduz a palavra, e ela deixa de ser literal. A redução a trata como `"…"`. É preciso preparar o arquivo deliberadamente e pôr as atribuições noutra linha. Cartão N-HOOK1.
- **R9. `docs/hooks.md:95`, parágrafo "Reavaliação pelo shell com ação crítica".** Ele ainda diz "em qualquer nível que o hook lê (também por baixo de `env`, `command`, …, dos lançadores que ele separa)", que é a regra de posição de `3df051e`. A nota do arquiteto no pedido já aponta isso. Dono: `software-architect`.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas:
- `forge-check delta --parecer`;
- `git show --cc c3d55d5`;
- `python3 -m unittest tests.test_hooks.CorpusHeredocVoltaUnica -v`: `Ran 10 tests in 209.470s`, `OK`;
- `python3 -m unittest tests.test_hooks`: `Ran 61 tests in 235.339s`, `OK`;
- as sondas por um script próprio, que usa `Fixture`, `rodar` e `rodar_no_bash_do_t9b` do próprio teste;
- o teste de diferença aleatório da `reduzida` contra o `printf` do bash;
- a medida de tempo com o prazo de produção (10 s);
- a comparação contra `3df051e` e a `develop` `40d8707` em cópias em `$TMPDIR`;
- o bash 5.3.9, com `HOME` em `$TMPDIR/security-engineer-lh10/casa`, sem rede e sem custo (`R-CUSTO`).

Lacunas:
- Só o bash 5.3 está na máquina, e o `\x{` pode variar entre versões.
- O "timeout = liberado" vem do próprio projeto (`docs/hooks.md:96`); não rodei o Claude Code.
- `ash`, `mksh`, `su`, `script` e `ssh` só foram gravados.
- A suíte inteira não rodou fora do pre-push (`R-TETO`).
- `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH e não se aplicam ao delta do lote, que não tem segredo, workflow nem dependência. O workflow trazido da `develop` passou pelo gate do PR dele.

Nada foi instalado e nada saiu da máquina. Além deste parecer, só gravei em `$TMPDIR`.
