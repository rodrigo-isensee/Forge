---
tipo: revisao-seguranca
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 3df051e400a7be84cba20a9da185f9e1ba86f3f7
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: lote-leitura-hook (revalidação 9, opção B)

Pedido RET-LEITURA-HOOK-REV9, etapa E2.1. Escopo: a opção B escolhida pelo dono para as sondas Q1 a Q4 da revalidação 8 (`docs/propostas/lote-leitura-hook-caminho-rev8.md`, seções 3, 4A e 4B), nos commits `403a3a0`, `140256f`, `befe8d3`, `d6bd263` e `3df051e`. O parecer anterior é a revalidação 8, em `b2c7d83` (commit `14c9eeb`). `forge-check delta --parecer` sobre ele lista:
- `hooks/_comum.py:1611-1622,1659-1660,1712-1796`;
- `hooks/conformidade.py` (imports, `:623`, `:721-727`, `:853`);
- `hooks/parecer.py:21-24,342-349,378-398`;
- o corpus, dois fixtures do `conformidade` e `tests/test_hooks.py` (T9b e a propriedade);
- a ADR 0011 (linha 41), `docs/hooks.md:94`, o desenho (linhas 88 e 280-281) e o fragmento do changelog.

É controle do Forge e foi relido inteiro. Conferi também que o `befe8d3` só move código: as linhas tiradas de `hooks/conformidade.py` e as postas em `hooks/_comum.py` são as mesmas, salvo o import e um comentário.

**critério mudou:** não. Vale a frase de parada da opção B (desenho, `docs/propostas/lote-leitura-hook-volta-unica.md:280`), lida com a linha 276 e a regra A4 do mesmo desenho. A sonda bloqueia se cair na linha **Promete** do Leitor, se um dos hooks a liberar com marcador e se o T9b mostrar que o bash rodou a `SENTINELA`. Pela A4, a pertença se decide pela tabela. A linha Promete da opção B nomeia:
- `eval` e `bash`/`sh`/`zsh`/`dash`/`ksh` com `-…c…`, na forma direta ou por baixo dos lançadores que o hook separa;
- o `<<` que o bash pode formar.

O que essa linha não cobre é cartão (linha 276), mesmo que o bash rode a sentinela. FD12 e FD13 têm contorno em `docs/hooks.md` e não bloqueiam.

## Gatilhos
`R-SEGURANCA`, gatilho controles do Forge: os hooks `conformidade` e `parecer`. A mudança é a gramática positiva da chamada com `<<` e ação crítica e a recusa da reavaliação pelo shell. Os hooks guardam R-MAIN, R-VERIFY, R-CONTRIB, R-CONFORMIDADE e R-REVIEW/R-QA.

## Achados

## Detalhe dos achados
Nenhum bloqueante. As sondas novas acharam uma classe aberta, a do reavaliador ou comando que o hook não reconhece (R5 e R5a abaixo). Ela fica fora da linha Promete, não depende de `<<` e dá o mesmo código na `develop` `7423c44`. Por isso não é da classe "nível" e não bloqueia. Vai a cartão, com severidade alta.

### Revalidação dos achados da revalidação 8
Hooks reais da worktree em `3df051e`. Cada sonda passou pelo `decisoes_dos_hooks` e pelo `rodar_no_bash_do_t9b` do próprio T9b:
- o modelo do corpus, com a sentinela do hook no `{CORPO}`;
- o `bash 5.3.9` com `env -i` e registradores no `PATH`;
- `HOME` e a pasta em `$TMPDIR`, sem rede.

As células são conf / par.
- **R0 (Q1 a Q4 e Q6): resolvido.** No corpus, Q1 a Q6 saem **2 / 2**, e rodei Q1 e Q4 de novo no T9b: 2 / 2. Variantes que a proposta não pôs no corpus também saem 2 / 2:
  - `<'\''<` (QN3);
  - `$""` entre os dois `<` (QN2);
  - `$(echo $(true))` aninhado entre os dois `<` (QN1).

  A regex `HEREDOC_QUE_O_BASH_FORMA` (`hooks/_comum.py:1614`) não casa o QN1 por causa do `[^()]*`, mas a recusa da reavaliação fecha o caso antes.
- **QC1 e QC2 (o `<<` calculado com `$(printf '\x3c\x3c')` dentro de `eval` e de `bash -c`): resolvidos.** No corpus e no T9b, os dois saem 2 / 2. Rodei também `command sh -ec` (QC3sh) e `env -i PATH=… nice -n 1 bash -lc` (QC4env): 2 / 2. A recusa entra em `hooks/conformidade.py:723` e em `hooks/parecer.py:393`, depois das regras específicas. O reconhecimento está em `reavaliacao` (`hooks/_comum.py:1760`).
- **R1 (`~` no alfabeto fora de aspas): não resolvido.** `hooks/_comum.py:507` não mudou. `git push origin feature/x ~ && git commit -F - <<'EOF'⏎msg⏎EOF` sai 0 / 0 (TIL), e o bash roda o `git` com o caminho da casa no argv. Continua recomendação de severidade baixa, sem caminho de ataque, como na revalidação 8.
- **R3 (limites do T9): não resolvido, e o T9b tem um limite do mesmo tipo.** O T9 não mudou. O T9b só põe shell de verdade para `bash`, `sh`, `dash`, `zsh` e `ksh` (`SHELLS_DO_T9B`, `tests/test_hooks.py:2283`). Os outros programas são registradores. Um reavaliador fora dessa lista (`rbash -c`, `find -exec bash -c`, `flock f bash -c`) fica só gravado e nunca roda a sentinela. Nas minhas sondas R1rb, R3fi e R49fl (parecer), o T9b dá "sentinela não rodou", e isso é artefato do oráculo, não prova. Recomendação abaixo (R6).

### Outra forma de esconder a ação crítica do nível 0, com a recusa da reavaliação em vigor
Procurei pelo reconhecimento da reavaliação, que é a única entrada da opção B:
- o nome do programa;
- a opção `-c`;
- a palavra antes do comando;
- o shell que lê a entrada sem `-c`.

Sondei cada forma sem `<<` e com o `<<` calculado.

| ID | texto (o `{CORPO}` é a sentinela do hook) | 3df051e | develop `7423c44` | sentinela no bash |
|---|---|---|---|---|
| R5ce, R6cq | `$(echo eval) '{CORPO}'`, `"$(printf eval)" '{CORPO}'` | 0 / 0 | 0 / 0 | rodou |
| R50cm | `$(printf bash) -c '{CORPO}'` | 0 / 0 | 0 / 0 | rodou |
| R1pe | `/proc/self/exe -c '{CORPO}'` (o próprio bash) | 0 / 0 | 0 / 0 | rodou |
| R7pi | `echo '{CORPO}' \| bash` | 0 / 0 | 0 / 0 | rodou |
| R9so | `. <(echo '{CORPO}')` | 0 / 0 | 0 / 0 | rodou |
| R23tr | `trap '{CORPO}' EXIT` | 0 / 0 | 0 / 0 | rodou |
| R26B | `"$BASH" -c '{CORPO}'` | 2 / 0 | 2 / 0 | rodou (parecer) |
| CO1, CO3 | `coproc bash -c '{CORPO}'`, `coproc eval '{CORPO}'` | 0 / 0 | 0 / 0 | rodou |
| CO4 | `coproc {CORPO}` (a linha crítica direta, sem reavaliação) | 0 / 0 | 0 / 0 | rodou |
| CO2 | `coproc x { bash -c '{CORPO}'; }` | 2 / 0 | 2 / 0 | rodou (parecer) |
| QCco, QCce, QPc | `coproc bash -c`, `$(echo eval)` e `printf … \| bash` com o `<<` calculado em vez do `{CORPO}` direto | 0 / 0 | — | rodou |
| controles | `bash -c`, `'bash' -'c'`, `bash "-c"`, `(…)`, `f() {…}; f`, `case`, `exec`, `time -p`, `!`, `{ …; }`, `bash <<<` | 2 / 2 | o `parecer` libera quase todos | — |

Leitura: com a opção B, o `eval` e os cinco shells com `-c` que o hook reconhece recusam nos dois hooks, em todas as formas que tentei. O que passa tem uma de três causas:
- O nome do programa é calculado ou não está na lista: `$(echo eval)`, `/proc/self/exe` e, no `parecer`, `"$BASH"`.
- O shell lê o texto por outra via que não o `-c`: `| bash`, `. <(…)`, `trap`.
- A palavra reservada `coproc` vem antes do comando, e o hook não a pula (`CORPO_DE_LACO`, `hooks/_comum.py:1754`).

Nenhuma dessas formas precisa de `<<`, e o `<<` calculado nelas não muda nada: o `{CORPO}` direto já roda. Todas dão o mesmo código na `develop`, e o `parecer` da `develop` libera ainda mais (linha dos controles). A opção B não abriu nenhuma delas e fechou as que estão na sua linha.

### O T9b e a propriedade (5) provam o critério de fim da 4B?
Pelo que a 4B escreve, sim. Para a classe, não: os dois oráculos quantificam sobre o corpus e as mutações do T8 por nível, e não sobre o domínio do reconhecedor.
- (1) `python3 -m unittest tests.test_hooks.CorpusHeredocVoltaUnica` em `3df051e` (corpus, T6, T7, T8, T9, T9b, propriedade e cobertura): `Ran 8 tests in 95.445s`, `OK`.
- (2) Q1 a Q6, QC1, QC2, BL2 e QP1 estão no corpus como 2 / 2 e passam.
- (6) QC1 e QC2 estão no T9b (corpus com `{CORPO}`) e passam porque a chamada recusa.
- (3) Mutações, cada uma numa cópia de `3df051e` em `$TMPDIR`, rodando o corpus, o T9b e a propriedade:
  - **m1**: o gatilho volta ao de `b2c7d83` (`"<<" in texto.replace("\\\n", "")`, em `tem_heredoc_no_texto`). Resultado: 6 falhas. O T9b falha em QP1 nos dois hooks, e o corpus falha em QP1, FD12 e FD12b. B1, B2 e Q1 a Q4 **ficam verdes**, porque a recusa da reavaliação os pega antes. A mutação da seção 3 ("T9b vermelho em B1, B2 e Q1 a Q4") não vale mais como foi escrita. Com a opção B, o gatilho novo só é provado pelo shell que lê a entrada (QP1) e pelo FD12. É uma consequência esperada de B, e não um furo: o gatilho deixou de ser a única barreira.
  - **m2**: a recusa da reavaliação sai dos dois hooks (`hooks/conformidade.py:723` e `hooks/parecer.py:393` com `if False:`). Resultado: 31 falhas.
    - O T9b falha em QC1 e QC2 no `parecer`: o bash rodou a sentinela.
    - A propriedade falha em todas as linhas diretas dentro de `eval`, `sh -c`, `bash -c`, `env X=1 bash -c` e `command eval`, nos dois hooks.
    - O corpus falha em QC1 e QC2 (parecer) e em FD13a a FD13e.

    No `conformidade`, QC1 e QC2 seguem 2 sem a regra nova: ele segue o `eval` e o `bash -c` até o nível 1, e o texto de lá não fecha.
  - **m3**: a recusa sai só do `parecer`. Resultado: 21 falhas, todas no `parecer`. O T9b falha em QC1 e QC2, a propriedade falha nas linhas diretas dentro dos sete níveis, e o corpus falha em QC1, QC2, FD13b, FD13d e FD13e. A propriedade e o T9b separam os dois hooks: cada um tem de recusar sozinho.
- (5) A propriedade usa uma leitura própria da reavaliação (`REAVALIACAO_DO_TESTE`, `tests/test_hooks.py:2398`). Ela casaria `coproc bash -c '…'`, mas esse texto não está entre as entradas. Por isso a propriedade prova a recusa para os textos que ela gera, e não para toda reavaliação que o regex dela reconhece. Pôr na entrada as formas da R5a que estão no alcance desse regex (`coproc bash -c`, `coproc eval`) mostraria a falha sem bash. Isso entra na R6.

### Recomendações (não bloqueiam; cartão N-HOOK1 ou cartão próprio)
- **R5. Reavaliador ou comando que o hook não reconhece (classe nova, nem "nível" nem X1 a X3; já na `develop`)** (`hooks/_comum.py:1760-1777`; `hooks/conformidade.py:853`; `hooks/parecer.py:378`).
  - Formas, na tabela acima: nome calculado (`$(echo eval)`, `$(printf bash) -c`), o bash por outro nome (`/proc/self/exe` e, no `parecer`, `"$BASH"`) e o shell que lê a entrada (`| bash`, `. <(…)`, `trap '…' EXIT`).
  - Caminho de ataque: um agente, por engano ou por injeção de prompt, contorna no hook o R-MAIN e o R-REVIEW com efeito medido. Restam como camada o `pre-push` e a proteção de branch, como na R0 da revalidação 8.
  - Severidade **alta**. Não é regressão: a `develop` dá o mesmo código.
  - Correção mínima, esforço M. Precisa de decisão do dono, porque recusa mais e tem falso positivo. Três peças:
    - com o marcador crítico na chamada, recusar o programa cujo nome não é literal (palavra de comando com `$(`, crase ou `$`);
    - pôr `trap`, o `source`/`.` de `<(…)` ou de `/dev/stdin` e o shell que recebe a entrada por pipe ou por `<(…)` na mesma regra de B;
    - pôr `/proc/self/exe` e `rbash` na lista dos shells.
  - Dono: o `software-architect` propõe, e o caminho vai ao dono (`R-DECISAO`) pelo cartão N-HOOK1.
- **R5a. `coproc` antes do comando (já na `develop`; cartão próprio, que peço ao Jarvis)** (`hooks/_comum.py:1754`, `CORPO_DE_LACO`).
  - O CO4 é `coproc git push origin SENTINELA:main` (no `parecer`, `coproc gh pr merge SENTINELA --merge`). Ele sai 0 / 0, e o bash roda a linha crítica **direta**, sem reavaliação nenhuma. A mesma linha sem o `coproc` sai 2 / 2 (Zdir). O furo está no leitor de base, e não na opção B.
  - Severidade **alta**.
  - Correção mínima, esforço P: pular `coproc` e `coproc NOME` antes de `{` nos dois hooks (`CORPO_DE_LACO` e o `segmento`/`analisar`) e pôr CO1 a CO4 no corpus.
  - Dono: `tech-lead`.
- **R6. Oráculos sobre o domínio do reconhecedor** (`tests/test_hooks.py:2283,2398`).
  - O problema: no T9b, os reavaliadores fora de `SHELLS_DO_T9B` são registradores, então o T9b não vê a sentinela que eles rodariam (R3). E a propriedade (5) só olha os textos que ela gera.
  - Esforço P: pôr na entrada da propriedade as formas da R5 e da R5a que o regex dela reconhece. As outras entram no corpus com a marca "Não promete", para o conserto futuro aparecer como mudança de teste.
  - Dono: `tech-lead`.
- **R1 (`~`) e R3 (limites do T9)** da revalidação 8 seguem como estavam (acima). O mesmo vale para a R2 (`cd -`, cartão R2-CD-MENOS) e a R4 (o N-HOOK1 com as opções do `git`/`gh`, `remote.<r>.receivepack` e a classe X).
- **FD13 num fixture `-libera`.** `tests/hooks/conformidade/contrib-remoto-nomeado-proprio-libera.json:25` perdeu o `bash -c`. A linha antiga foi para `contrib-remoto-nomeado-proprio-bash-c-bloqueia.json`, que espera 2. Isso endurece a regra e tem contorno (o `gh pr merge` direto). O R-CONTRIB continua coberto pelo `-libera` com a linha direta. A proposta dizia que não havia fixture assim, e essa é a única divergência com ela. Não bloqueia.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas usadas:
- `forge-check delta --parecer`;
- a leitura do diff `b2c7d83..3df051e` e a conferência do move do `befe8d3`;
- a classe `CorpusHeredocVoltaUnica`;
- as sondas pelo `decisoes_dos_hooks` e pelo `rodar_no_bash_do_t9b` do próprio T9b, contra os hooks reais da worktree e contra os hooks da `develop` `7423c44` (`git archive` em `$TMPDIR`, com os testes de `3df051e`);
- as mutações m1 a m3 em cópias em `$TMPDIR`;
- o `bash 5.3.9`, com `HOME` numa pasta de `$TMPDIR`, sem rede e sem custo (`R-CUSTO`).

Lacunas:
- Só o bash 5.3 está na máquina.
- `rbash` e `dash` existem, mas o oráculo não roda o `rbash` de verdade (R6). `find`, `flock` e `rbash` só foram gravados.
- A suíte inteira não rodou fora do pre-push (`R-TETO`).
- `gitleaks`, `zizmor`, `actionlint` e `semgrep` não estão no PATH e não se aplicam: o delta não tem segredo, workflow nem dependência.

Nada foi instalado e nada saiu da máquina. Além deste parecer, só gravei em `$TMPDIR`.
