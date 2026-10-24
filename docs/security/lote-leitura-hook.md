---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 182f9287110eaa9838c973aadef6757607e218a1
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-leitura-hook (revalidação 11, opção C da revalidação 10)

Pedido RET-LEITURA-HOOK-E-REV, etapa E2.1. Escopo: a opção C da proposta `docs/propostas/lote-leitura-hook-caminho-rev10.md` (decisão "C" do dono, 2026-10-24).
- A implementação está em `a49810f` (corpus), `8333091` (bloco T), `f4163e6` (`INDECIDIVEL`), `7014072` e `00d83c2` (propriedade e par) e `874965a` (textos). A `develop` `d150ec8` foi trazida em `182f928`, um merge sem resolução (`git show --cc` vazio).
- O parecer anterior é a revalidação 10, sobre `96227be`. `forge-check delta --parecer` lista o intervalo `96227be..182f928`. Fora do lote, o intervalo só traz o que veio da `develop` pelo merge, que passou pelos gates dos próprios PRs.
- Reli inteiro o que é do lote no delta: `hooks/_comum.py:1665-1685` (tetos), `:1723-1840` (lançadores e reconhecedor), `:1855-1925` (`reduzida`), `:1980-1990` e `:2190-2262` (vigia de prazo e `executar`); `hooks/conformidade.py:644-680,742-745,1786`; `hooks/parecer.py:359-405,445`; o corpus; os testes novos de `tests/test_hooks.py` (propriedade do alfabeto, pares, tempo e vigia); `docs/hooks.md:95-96`; o desenho (linhas 88 e 282); a ADR 0011 (linha 42); e `tests/config.json`.

**critério mudou:** não. Vale a frase de parada do desenho `docs/propostas/lote-leitura-hook-volta-unica.md` (linha 282, lida com a linha 276), com o texto da opção C:
- **bloqueia** a sonda que um hook libera com o marcador, com efeito provado no bash, numa forma que a linha Promete cobre;
- a Promete cobre a reavaliação **em qualquer posição em que o bash rode o comando, inclusive depois de lançador**. `docs/hooks.md:95` diz, além disso, que "o `env -S` divide o valor em palavras, que se conferem de novo".

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: os hooks `conformidade` e `parecer`. O delta troca a redução ANSI-C pela recusa de toda palavra com `$'…'` ou `$"…"` e põe o orçamento de tempo nos dois hooks. Os hooks guardam R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA.

## Achados
- A1 (bloqueante) hooks/_comum.py:1764 · classe nova "lançador que divide texto" (env -S): o modelo do env -S difere do GNU env em 3 pontos (o -c depois do valor, a barra-sublinhado, a abreviação --split); env -S 'X=1 bash' -c '<linha>' sai 0 / 0 e o env roda a sentinela

## Detalhe dos achados
Há um bloqueante, nesta passada só. Sondei, contra os hooks reais da worktree em `182f928`:
- AN34 a AN34g, o `$"…"`, a sonda das 20 mil palavras e as grafias com escapes de todo o alfabeto;
- o tempo até o teto de caracteres e de palavras;
- os riscos que o autor declarou e o `env -S`.

Repeti as mesmas 822 sondas contra a `develop` `d150ec8` e as do `env -S` também contra `96227be`. As duas cópias saíram de `git archive` em `$TMPDIR` e rodaram com os testes de `182f928`.

Condições das sondas:
- cada hook roda **sempre**, com o vigia de produção (3 s), no modelo de fixture do corpus;
- a sentinela é a do T9b. Quando o hook libera, o texto roda no bash 5.3.9 do `rodar_no_bash_do_t9b`;
- o `env -S` roda fora do T9b, porque lá o `env` é um registrador. Ele roda com o `env` real (GNU `gnuenv` e uutils 0.8.0), com `git` e `gh` registradores, `env -i`, `HOME` e a pasta em `$TMPDIR/security-engineer-lote-leitura-hook/` e sem rede.

As células são conf / par. "SENT" quer dizer que o bash rodou a sentinela.

### Os achados da revalidação 10
- **A1 (`\x{…}`): resolvido.** Saem 2 / 2:
  - AN34 a AN34g;
  - `$'\x65'val`, `$'\145'val` e `$'\u0065'val`;
  - AN35a a AN35d, no teste do corpus.

  As 36 posições do grupo AN saem 2 / 2, salvo uma forma que o bash não roda (abaixo). As 11 do grupo `$"…"` saem todas 2 / 2, entre elas `$"eval"`, `e$"val"`, `bash -$"c"`, `$"bash" -c`, `coproc $"eval"` e `$"ev$x"`. As posições cobrem `coproc`, `time`, `if`, `$(…)`, crase, `"$(…)"`, `<(…)`, redireção e atribuição antes, `command`, `sudo`, `find -exec`, função, `case`, `for`, depois de `&&`, `|`, `&` e quebra de linha, o heredoc rodado e `eval "$(cat <<'E' …)"`.
  - A exceção é `env -S "$'\x{65}'val '…'"`, que sai 2 / 0. O GNU env recusa o `$'` ("only ${VARNAME} expansion is supported") e não roda nada.
  - Com a opção C, o hook não lê mais o escape. Por isso a mesma recusa vale para qualquer versão do bash.
- **Alfabeto inteiro: 2 / 2.** São 576 sondas: `\` com cada caractere de 0x20 a 0x7E e a quebra de linha, no nome (`$'\c'eval`), dentro da opção (`bash -c$'\c'`) e como argumento da linha crítica, nos dois hooks. O teste de pares do autor compara `reduzida` com o `printf` do bash em 1.330 pares, e a propriedade cobre mais de 40 mil textos.
- **A2 (orçamento): resolvido.** `: bash ×20000; <linha crítica>` sai 2 / 2 em 0,33 s e 0,20 s, pelo teto de 5 mil palavras. Na revalidação 10, o hook estourava os 10 s. `env ×20000` dá o mesmo.

  Até o teto, todos os tipos que sondei decidem em menos de 1 s nos dois hooks, também com o vigia desligado (prazo de 60 s):
  - 4.990 palavras de shell;
  - `env -u env` ×2.499, que é quadrático no reconhecedor, mas o teto o corta;
  - uma palavra de 149 mil caracteres e um `$'\x41…'` de 149 mil;
  - 2.400 comandos, `$(x)`, `"$(x)"` e crase;
  - 4.900 `${x:-y}` e `a'b'c`;
  - 60 `$(` aninhados e 2.400 redireções;
  - um heredoc de 2 MB, um heredoc rodado de 1 MB e 2.400 heredocs;
  - 1.600 `env -S 'env -S x'`.

  O pior foi 0,95 s, numa palavra de 149 mil caracteres.

### A1: o modelo do `env -S` (bloqueante, classe nova "lançador que divide texto")
- **Evidência.** `opcoes_do_lancador` (`hooks/_comum.py:1750-1767`) divide o valor do `-S` com `shlex.split` (`:1764`). `reavaliacao_das_palavras` (`:1832-1838`) e `separar_lancadores` (`:1783`) usam o resultado. O GNU env age diferente em três pontos:
  1. **As opções depois do valor.** O env põe as palavras divididas antes do resto do argv e volta a ler opções a partir delas, então para na primeira palavra que não é opção. O hook segue lendo como opção do `env` o `-c` que vem depois do valor. Em `env -S 'X=1 bash' -c '<linha>'`, o `-c` some, e o shell dividido fica sem opção depois dele (`opcao_a_partir[depois]` é falso).
  2. **A barra-sublinhado.** No `-S`, o `\_` separa palavras (GNU, e uutils na forma colada `-S'…'`). O `shlex` o lê como `_`, então `env -S 'bash\_-c' '<linha>'` vira a palavra única `bash_-c`.
  3. **A abreviação da opção longa.** O `getopt_long` aceita `--split`, `--spl=…` e as demais formas sem ambiguidade. `valor_do_split_string` (`:1926-1940`) só reconhece `--split-string`.
- **Sondas: 17 formas saem 0 / 0 nos dois hooks.** Rodei 16 delas com o `env` real, e o bash rodou `git push origin SENTINELA:main` (ou `gh pr merge SENTINELA --merge`):
  - `env -S 'X=1 bash' -c '…'`, `env -S 'timeout 5 bash' -c '…'`, `env -u X -S 'timeout 5 bash' -c '…'`, `env -S 'timeout 5 sh' -ec '…'`, `env -S 'nice bash' -c '…'`, `env -S 'bash -e' -c '…'`, `env -S 'timeout 5 bash' -lc '…'`, `env -S 'timeout 5 bash -e' -c '…'` e `env -S 'env -S "timeout 5 bash"' -c '…'`;
  - `env --split-string='timeout 5 bash' -c '…'`, `env -iS 'timeout 5 bash' -c '…'` e `env -S'timeout 5 bash' -c '…'`. A última também roda no uutils;
  - `env -S 'bash\_-c' '…'` e `env -S 'X=1\_bash' -c '…'`;
  - `env --split 'bash -c' '…'` e `env --spl='bash -c' '…'`.

  A 17.ª, `sudo env -S 'timeout 5 bash' -c '…'`, segue o mesmo mecanismo; não a rodei, porque não há `sudo` no sandbox.

  O uutils 0.8.0 desta máquina não divide `-S 'x y'` em palavra separada: dá "No such file or directory" e não roda nada. Na forma colada (`-S'…'`), ele roda a sentinela.

  Quando o shell e o `-c` estão os dois dentro do valor, o hook acerta e sai 2 / 2, inclusive no `env -S 'timeout bash -c …'` que o autor declarou: `env -S 'timeout 5 bash -c' '…'`, `-S"timeout 5 env -S 'bash -c'"`, `--split-string='…'`, `-iS`, `timeout 5 env -S 'bash -c'`, `-s KILL`, `nice -n 5`, `X=1 timeout …`, `--foreground` e `env -S 'timeout 5' bash -c`.
- **Por que é Promete, e não cartão.**
  - A palavra que roda é `bash -c`, lançada pelo `env`. A frase de parada cobre a reavaliação "em qualquer posição em que o bash rode o comando (… de lançador …)".
  - `docs/hooks.md:95` promete que "o `env -S` divide o valor em palavras, que se conferem de novo", e o código diz o mesmo (`:1806`).
  - Se o dono ler essa forma como fora da Promete, a linha de `docs/hooks.md:95` passa a prometer o que o hook não faz e tem de mudar no mesmo PR. Ela não pode seguir como está.
- **Comparação.** Não é regressão: as formas saem 0 / 0 também na `develop` `d150ec8` e em `96227be`. O piso da M5 se mantém. As formas não estavam no corpus nem no G1: o G1 só põe o `env` como `env X=1 {R}`, sem `-S`. Eu também não as sondei na revalidação 10, onde só testei o `-c` dentro do valor.
- **Caminho de ataque.** Um agente, por engano ou por injeção de prompt, escreve `env -S 'X=1 bash' -c 'git push origin HEAD:main'` ou `env -S 'bash\_-c' 'gh pr merge 12 --merge'`. Os dois hooks liberam. O push vai à `main` sem o R-MAIN do hook, ou o PR é mesclado sem parecer (R-REVIEW, R-QA). Restam a proteção de branch e o `pre-push`.
- **Severidade:** alta, a mesma do A1 da revalidação 10.
- **Correção mínima,** esforço P. Proponho a mesma lógica da opção C: com o marcador crítico, o `env` com split-string recusa sem que o hook tente dividir o valor, como o `INDECIDIVEL`.
  - Conta como split-string: qualquer grupo curto em que o `S` venha antes de outra letra que leve valor (`-S`, `-iS`, `-S'…'`) e qualquer prefixo de `--split-string`, com ou sem `=`.
  - Assim o hook não depende do `\_`, do `${VAR}`, do `\c`, das diferenças entre GNU, uutils e BSD, nem de onde o `env` para de ler opções.
  - Quem quer manter a divisão tem de imitar o env nos três pontos: parar as opções depois do valor e reler a partir das palavras divididas, tratar o `\_` e aceitar as abreviações. São três mecanismos a provar, contra uma regra só.
  - Em qualquer dos caminhos: as 17 formas acima no corpus, com 2 / 2, e uma dimensão nova na matriz do gerador, "lançador que divide texto", com grafia da opção × separador × lado do `-c` em relação ao valor.
  - Falso positivo novo, só na solução por recusa: `env -S` junto com ação crítica, raro em chamada de agente. O contorno é o comando direto.
- **Dono:** `tech-lead`. Se a correção for a recusa, o `software-architect` redige o texto de `docs/hooks.md:95`.
- **Contagem de voltas.** A classe é nova. A revalidação 10 teve "nível" e "orçamento", então não é a 2.ª volta seguida da mesma classe (decisão "A" de 2026-10-22). Quem escolhe entre a recusa e a imitação é o Jarvis, com o arquiteto.

### Os riscos que o autor declarou
- **O vigia de 3 s conta a espera do git.** É falha fechada:
  - com o marcador, o git lento (até `GIT_TIMEOUT_S = 5`) faz o hook recusar, e não liberar;
  - sem o marcador, nada muda;
  - o `subprocess.run` mata o filho quando o `PrazoVencido` sobe;
  - nenhum `except:` nem `except BaseException` nos hooks engole o `PrazoVencido` (`grep` em `hooks/` e `bin/forge-check`).

  O custo é falso positivo sob carga, no sentido seguro. Não é achado. Recomendo citar o caso em `docs/hooks.md:96`, que hoje só diz "em qualquer ponto".
- **O `INDECIDIVEL` depois de `$(`, `${` ou crase** (`_resto_com_ansi`, `hooks/_comum.py:1872`). Ele só recusa a mais, quando o `$'` estava entre aspas dentro da substituição. A substituição em si é lida como nível próprio por `palavras_do_texto`, então a palavra interna também é conferida. Pelo lado da segurança, não há caminho para liberar menos.
- **Sem `SIGALRM` no Windows.** Até os tetos, o pior tempo que medi com o vigia desligado foi 0,95 s. O que sobra é a espera de rede ou do git, que já era assim na `develop`. É informativo.
- **O `env -S 'timeout bash -c …'`.** Com tudo dentro do valor, sai 2 / 2. A forma com o `-c` fora do valor é o A1.

### A invariante `def conteudos_de_crase` (`tests/config.json`)
Não afrouxa:
- a definição mudou de lugar e continua protegida, agora em `hooks/_comum.py` (`def conteudos_de_crase`);
- em `hooks/conformidade.py`, a invariante virou `conteudos_de_crase\(`. O teste a lê como regex (`tests/test_forge.py:379`), e ela casa só com a chamada (`:723` e `:1355`), não com o import;
- na base `9c9014d`, a invariante só exigia a definição no `conformidade`.

Agora a definição e o uso estão os dois protegidos.

### Piso por classe contra a `develop` (decisão M5)
Nenhuma das 822 sondas que a `develop` `d150ec8` recusa sai liberada na branch. As sondas cobrem os grupos AN, `$"…"`, alfabeto, tempo, `env -S` e falsos positivos.
- **Grupos que endurecem:**
  - no `parecer`, 32 sondas do grupo AN, 10 do `$"…"` e 2 do alfabeto passam de 0 SENT a 2;
  - mais 188 do alfabeto, 13 do `env -S` e 2 de tempo passam de 0 a 2.
- **Grupos iguais:** o `conformidade` já recusava qualquer `$'` com o marcador.
- **Falsos positivos:** os do `conformidade`, como `git commit -m "… $'x' …" && git push`, já existiam na `develop`. O FD15 está aceito pelo dono, com o contorno no corpus (FD15d, e, f e i dão 0).

### Outra forma de esconder a ação crítica
- **X3 (marcador ofuscado).** Continua no cartão C8, igual à `develop`: `git $'\x70'ush` sem marcador e `gh pr $'\x6d'erge` no `parecer`.
- **Expansão.** `$@eval`, `"${x}"eval` e afins seguem no N-HOOK1, como a Promete diz.

### Recomendações da revalidação 10
- **R7 e R8:** superadas, porque a tabela ANSI-C saiu e o `$"…"` recusa.
- **R9 (`docs/hooks.md:95`):** resolvida, porque o parágrafo não fala mais em "por baixo dos lançadores".
- **FD14 com `docker exec … bash -lc`:** já citado em `docs/hooks.md:95`.
- **X3 / C8:** continua no cartão.

## Riscos aceitos e ferramentas
Nenhum risco aceito.

Ferramentas usadas:
- `forge-check delta --parecer` e `git show --cc 182f928`;
- `python3 -m unittest tests.test_hooks.CorpusHeredocVoltaUnica`: `Ran 15 tests in 384.191s`, `OK`;
- as sondas, por um script próprio que usa `Fixture`, `rodar` e `rodar_no_bash_do_t9b` do próprio teste: 822 por árvore, mais 26 do `env -S`;
- o `env` real (GNU `gnuenv` e uutils 0.8.0) com registradores;
- a comparação contra a `develop` `d150ec8` e contra `96227be` em cópias em `$TMPDIR`;
- o bash 5.3.9, com `HOME` em `$TMPDIR/security-engineer-lote-leitura-hook/casa`, sem rede e sem custo (`R-CUSTO`).

Lacunas:
- Não há BSD env nem macOS na máquina. O `-S` do BSD tem outra sintaxe, o que é mais uma razão para a correção por recusa.
- Não há `sudo` no sandbox.
- Não rodei o Claude Code. O "timeout = liberado" vem de `docs/hooks.md:96`.
- A suíte inteira não rodou fora do pre-push (`R-TETO`).
- `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH e não se aplicam ao delta do lote, que não tem segredo, workflow nem dependência.

Nada foi instalado e nada saiu da máquina. Além deste parecer, só gravei em `$TMPDIR`. Uma ressalva: na sonda `env -iS`, o `env` limpa o `PATH` e roda o `git` real, que falhou com "not a git repository", numa pasta de `$TMPDIR` sem rede.
