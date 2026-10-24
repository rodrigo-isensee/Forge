---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 96227be7a53d1f7c4448f19fa452bc5116714f9b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-leitura-hook (revalidação 10, opção B da revalidação 9)

Pedido RET-LEITURA-HOOK-REV10, E1.1. Sou revisor independente: não implementei a opção B da revalidação 9 nem escrevi os textos dela (`R-REVIEW`). O parecer anterior (revalidação 9, `reprovado`, A1 e A2 da classe "nível") está em `5ac6ab3`.

**Delta lido.** O `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` deu `3df051e..96227be`. O intervalo inclui o merge `c3d55d5`, que só traz a `develop` (`9c9014d`). O `git show --remerge-diff c3d55d5` sai vazio, então não houve resolução manual. Esses arquivos são da `develop` e ficam como "já lido" nos PRs deles. Li inteiro o delta da branch:
- `5ac6ab3..b42fd4b`, os 5 commits: `83c63b2` (o corpus vermelho), `53d0544` (`reduzida`), `aadb806` (o reconhecedor sem posição), `d73c373` (G1, a prova de G1 e a propriedade) e `b42fd4b` (o changelog). Os arquivos são `hooks/_comum.py:1757-1914`, `hooks/conformidade.py:660-670,854`, `hooks/parecer.py:358-383`, o corpus (`tests/fixtures/heredoc-volta-unica.json:210-236`), `tests/test_hooks.py:1897-2606` e `changelog.d/lote-leitura-hook.md:9`.
- `96227be`, os textos: a ADR 0011, linha 42; o desenho, linhas 280-282; e `docs/hooks.md:95`.

Fica como "já lido" o que vem antes de `3df051e` (revalidações 1 a 9).

**Critério.** Uso a frase de parada corrigida (proposta `lote-leitura-hook-caminho-rev9.md`, seção 2, no desenho, linha 282, e na ADR 0011, linha 42). O domínio é a linha Promete: a palavra que o bash recebe depois da remoção de aspas, em qualquer posição. O que está na linha "Não promete" é cartão. O fim é o critério verificável da seção 3B.

## Achados
- A1 (bloqueante) docs/hooks.md:95 · classe "texto", 1.ª volta: o parágrafo "Reavaliação pelo shell com ação crítica" descreve a regra da rev. 8 (5 shells, sem rbash; "por baixo dos lançadores que ele separa"; T9b sobre "mutações por nível") e não a do código (palavra reduzida em qualquer posição, rbash, G1)
- A2 (recomendado) docs/propostas/lote-leitura-hook-volta-unica.md:88 · a célula Promete da linha Leitor segue com a frase da rev. 8 (5 shells, por baixo dos lançadores); o rbash, que o código reconhece, não aparece no desenho, na ADR 0011 (linha 42: "um shell da lista") nem no docs/hooks.md
- A3 (recomendado) hooks/_comum.py:1915 · uma linha em branco só entre `reduzida` e `valor_do_split_string` (o resto do módulo usa duas); ajuste de formatação

## Parecer
**Reprovado**, por um bloqueante, o A1. É da classe "texto" (documentação que diverge do código), na 1.ª volta. Não é da classe "nível". Por isso não aciona a parada das duas voltas (decisão "A" de 2026-10-22): a volta vai direto a quem escreveu `96227be`.

O código da opção B está certo e cumpre o critério de fim da seção 3B nos itens 1 a 6, que medi:
- Não sobrou lista de posição: `reavaliacao_das_palavras` olha toda palavra do comando simples, e `reavaliacao` percorre todos os níveis de `palavras_do_texto`.
- A redução é uma função só, em `_comum`, usada pelos dois hooks.
- O `parecer` não usa mais a palavra do `shlex`.
- As sondas da revalidação 9 e mais 60 sondas novas saem 2 / 2.
- Num fuzz de 15.000 palavras, a redução bateu com o bash em todas. Num fuzz de 9.000 grafias de `eval`, shell e `-c`, o reconhecedor acertou todas.
- As três mutações ficam vermelhas, cada uma no lugar que a 3B diz.

O que falta é o texto. Os testes e o código mudaram, mas o parágrafo de `docs/hooks.md` que descreve o controle ainda descreve a versão anterior (A1).

**A1 (bloqueante).** `docs/hooks.md:95`, no trecho "**Reavaliação pelo shell com ação crítica** (opção B, RET-LEITURA-HOOK-B)", diz três coisas que o código já não faz:
- Que a recusa vale para "`eval` ou `bash`/`sh`/`zsh`/`dash`/`ksh` com opção curta que contém `c`, em qualquer nível que o hook lê (também por baixo de `env`, `command`, `nice`, `sudo` e dos outros lançadores que ele separa…)". É a regra posicional de `3df051e`. O código de `aadb806` vale em qualquer posição, sobre a palavra reduzida como o bash, e tem `rbash`.
- Que "o T9b roda no bash o que cada hook libera (corpus e mutações por nível…)". Desde `d73c373`, o T9b e a propriedade rodam sobre G1 (prefixos × grafias × reavaliadores × corpos), e `NIVEIS` só serve ao T8.
- Nada sobre a redução (`reduzida`), a prova de G1 no bash (`test_g1_esta_na_classe`) e o teste de diferença contra o bash (`test_reducao_da_palavra_como_o_bash`).

O `96227be` só acrescentou o FD14 no fim do parágrafo. O FD14 diz "em qualquer posição e grafia", então o mesmo parágrafo se contradiz: a frase do controle diz "por baixo dos lançadores" e o FD14 diz "em qualquer posição". É a divergência que o arquiteto apontou na nota do pedido.

`docs/hooks.md` é a referência do comportamento do hook para quem mantém a fábrica. A definição de pronto pede a documentação afetada atualizada na mesma entrega.

Sugestão: reescrever só esse trecho com a frase da linha Promete corrigida (desenho, linha 282) e citar `reduzida`, `rbash`, G1, `test_g1_esta_na_classe` e `test_reducao_da_palavra_como_o_bash`. Não muda código nem teste. A revalidação será pelo delta desse parágrafo.

**A2 (recomendado).** A frase de parada da linha 282 já corrige o domínio por referência ("na linha Leitor, a reavaliação prometida é…"), então a promessa vale. Mas a célula Promete (linha 88), que é o que se lê primeiro, ainda tem a frase antiga. O `rbash` está no código (`SHELLS_DA_REAVALIACAO`), no corpus (NR1) e no changelog ("rbash entra na lista dos shells"), mas em nenhum texto normativo. Como o código recusa mais do que o texto promete, não há furo. Sugestão: um `critério mudou:` curto na célula 88, apontando para a linha 282, e o `rbash` na lista.

**Os textos de `96227be` e o código.** A frase de parada é a mesma, palavra por palavra, na proposta (seção 2), no desenho (linha 282) e na ADR 0011 (linha 42). A frase antiga (linha 280) ficou marcada como "substituído pelo critério seguinte". O FD14 em `docs/hooks.md` bate com o corpus: FD14a sai 2 no `conformidade`, FD14b e FD14c saem 2 no `parecer`, e FD14d (o contorno) sai 0. A ADR só endurece e não tem rótulo `afrouxa-regra`, o que está certo. O que diverge está no A1 (`docs/hooks.md:95`) e no A2 (célula 88 e `rbash`).

### A1 e A2 da revalidação 9, contra os hooks reais
O runner é próprio (`$TMPDIR/tech-lead-lh10/sonda.py`). Ele usa `decisoes_dos_hooks` e `rodar_no_bash_do_t9b` de `tests/test_hooks.py`: os modelos do corpus, a SENTINELA do T9b no `{CORPO}`, `env -i`, `HOME` em `$TMPDIR/tech-lead-lh10/casa`, sem rede e com só o bash de programa real. Rodou sobre a worktree em `96227be`. Na tabela, "(s=2)" quer dizer que o hook também recusa a versão com a SENTINELA.

| Sonda | 3df051e conf / par | 96227be conf / par | Estado |
|---|---|---|---|
| CO1 `coproc bash -c '{CORPO}'` | 0 / 0, SENTINELA | 2 / 2 (s=2) | **A1 resolvido** |
| CO2 `coproc eval '{CORPO}'` | 0 / 0, SENTINELA | 2 / 2 (s=2) | resolvido |
| CO3 `coproc x { eval '{CORPO}'; }` | 2 / 0, SENTINELA | 2 / 2 (s=2) | resolvido |
| AN1 `bash -$'c' '{CORPO}'` | 2 / 0, SENTINELA | 2 / 2 (s=2) | **A2 resolvido** |
| AN2 `$'eval' '{CORPO}'` | 2 / 0, SENTINELA | 2 / 2 (s=2) | resolvido |
| AN3 `e$'val' '{CORPO}'` | 2 / 0, SENTINELA | 2 / 2 (s=2) | resolvido |
| AN4 `bash $'-c' '{CORPO}'` | 2 / 0, SENTINELA | 2 / 2 (s=2) | resolvido |
| AN5 `$'bash' -c '{CORPO}'` | 2 / 0, SENTINELA | 2 / 2 (s=2) | resolvido |
| CO4 `coproc {CORPO}` | 0 / 0, SENTINELA | 0 / 0, SENTINELA | não promete, cartão R5A-COPROC (no corpus com a marca) |
| CO5 `time {CORPO}` | 2 / 0, SENTINELA | 2 / 0, SENTINELA | não promete, cartão A6 (no corpus com a marca) |

Os outros recomendados da revalidação 9:
- **A3** (propriedade só sobre `NIVEIS`): resolvido por G1, com 4.000 textos ou mais na propriedade e 1.500 ou mais na prova no bash.
- **A4** (formas sem reavaliação literal): estão no corpus com a marca `nao_promete` (CN1 a CN3, VA2, PE1, ST1 a ST3), cartão N-HOOK1. NR1, NR2, NR3 e VA1 passaram à linha Promete e saem 2 / 2.
- **A5** (opções do git): segue no cartão N-HOOK1.
- **A6**: segue nos cartões R5A-COPROC e A6.

### Sondas novas sobre a frase corrigida (todas 2 / 2, s=2)
- **Posição:**
  - prefixos: `exec -a nome bash -c`, `command -p eval`, `builtin eval`, `X=1 eval`, `time -p eval`, `! eval`, `{ eval …; }`, `( eval … )`;
  - separadores e compostos: `true && eval`, `true;eval`, `true|eval`, `eval … & wait`, `case … in x) eval …;; esac`, `f() { eval …; }; f`, `for … do eval …; done`, `while eval …`, a segunda linha física (`true`⏎`eval …`);
  - lançadores: `env -S "bash -c '…'"`, `echo x | xargs bash -c`, `sudo -u root bash -c`, `nice -n 1`, `timeout 5`, `nohup`, `find -exec $'bash' -$'c'`.
- **Nível:**
  - `$(…)` em vários contextos: `${x:-$(eval …)}`, com e sem aspas duplas e com `$'eval'` dentro; `$(( $(eval …) + 1 ))`; `(( $($'eval' …) ))`; `x[$($'eval' …)]=1`; `a=( "$($'eval' …)" )`; `case $($'eval' …) in`; o alvo de redireção `> "$($'eval' …)"`; o `<<< "$($'eval' …)"`; `$(echo $(echo $($'eval' …)))`;
  - `$((eval …) )`, que o bash roda como substituição;
  - substituição de processo: `cat <(eval …)`, `cat x<(eval …)`, `> >(eval …)`;
  - crase simples e entre aspas, e a crase aninhada com `` \` `` (`` x=`echo \`eval …\`` `` e com `$'eval'`);
  - heredoc sem aspas com `$(eval …)` ou crase no corpo, e `cat <<'X' && eval …`.
- **Grafia:**
  - escapes ANSI-C e afins: `$'\145val'`, `$'eval'`, `$"eval"`, `$'eval\0x'`;
  - barra e aspas parciais: `e\val`, `'e'"v"$'a'l`, `"e"val`;
  - continuação de linha: `e\`⏎`val` e `bash -\`⏎`c`;
  - nome do shell: `/bin/bash`, `$'/bin/bash'`, `$'rbash'`, `` k''sh -$'c' ``, `zsh "-c"`, `\dash`;
  - opções: `-O extglob -c`, `--norc -c`, `-x -c`, `-ce` e `+x -c`.
- **Controle:** `"\eval"` sai 0 / 0 e o bash não roda a SENTINELA. O bash recebe `\eval`, que não é `eval`, e por isso a liberação está certa.
- **Falso positivo:** o corpo de heredoc com as palavras `eval` e `bash -c` não recusa no `parecer`: no `--body "$(cat <<'EOF'…)"` sai 0, e no `git commit -F - <<'EOF'` com `git push` também sai 0. O 2 do `conformidade` no `gh pr create` é do papel `dev` do modelo, e não da reavaliação. `git commit -m 'eval' && git push` sai 2: é o FD14, documentado.

**Fuzz da redução e do reconhecedor** (`fuzz.py` e `fuzz2.py`, só o bash):
- `fuzz.py`: 5 sementes × 3.000 palavras aleatórias, montadas com `\`, `'…'`, `"…"`, `$"…"` e `$'…'`, com os escapes `\xHH`, `\nnn`, `\0nnn`, `\uHHHH`, `\UHHHHHHHH`, `\cX`, `\c\\`, `\0` e os incompletos. `reduzida` deu o mesmo valor que o `printf '%s'` do bash em todas: 0 diferenças em 15.000.
- `fuzz2.py`: 3 sementes × 3.000 grafias aleatórias de `eval`, `bash`, `sh`, `rbash` e `zsh` com `-c`, `-ec`, `-lc` e `-xc`, cortadas em pedaços com aspas diferentes. `reavaliacao` reconheceu todas: 0 falhas em 9.000.

### Critério de fim da 3B
1. **Corpus** (item 1): CO1 a CO3, AN1 a AN5, NR1 a NR3 e VA1 saem 2 / 2. FD14a a FD14d têm a célula do hook com marcador, e FD14d, o contorno, sai 0. Nenhuma marca `fecha` sobra.
2. **Propriedade sobre G1** (item 2) e **redução contra o bash** (item 4): verdes no `tests.test_hooks` abaixo.
3. **G1 está na classe** (item 3): `test_g1_esta_na_classe` está verde. Fiz uma mutação do oráculo, numa cópia limpa: a grafia "simples" passou a gerar `'eval '`, com um espaço, que o bash não roda como `eval`. A prova no bash ficou vermelha, `FAILED (failures=216)`. Um gerador que não produz reavaliação de verdade fica vermelho, como a 3B pede.
4. **Mutações** (item 5): cada uma numa cópia limpa (`git archive 96227be`), uma de cada vez, rodando a propriedade, o corpus e o T9b (`$TMPDIR/tech-lead-lh10/mutacoes.sh`):

| Mutação | Resultado | Onde fica vermelho |
|---|---|---|
| posição: a regra de `3df051e` (pula `CORPO_DE_LACO` e os lançadores, olha só a 1.ª palavra), sobre as palavras já reduzidas | `FAILED (failures=1806)` | propriedade em `G1 coproc / … / eval` e `… / bash -c` nos dois hooks; corpus em CO1, CO2 (os dois hooks), CO3, NR2, NR3, VA1, FD14a a c, CN1, CN3 |
| shlex: o `parecer` volta às palavras do `shlex` (com o reconhecedor novo, sem posição) | `FAILED (failures=1325)` | só no `parecer` (894 falhas da propriedade, todas `hook='parecer'`); corpus em `parecer/AN1` a `AN5` e `parecer/CN3` |
| um hook: sem a recusa só no `parecer` | `FAILED (failures=3539)` | a propriedade separa os hooks: 2.384 falhas, todas `hook='parecer'`, nenhuma no `conformidade` |

5. **Não promete** (item 6): CO4, CO5, CN1 a CN3, VA2, PE1 e ST1 a ST3 estão no corpus com `nao_promete` e com o código de hoje. Quando o hook libera, o T9b afirma que a SENTINELA roda, então o conserto futuro aparece como mudança de teste.
6. **Frase de parada** (item 7): é a da seção 2, nos três textos.

### Fora do bloco
- **Testes que rodei**, na worktree em `96227be`, com `HOME` em `$TMPDIR/tech-lead-lh10/casa`:
  - `python3 -m unittest tests.test_hooks`: `Ran 61 tests in 227.313s OK`.
  - `test_g1_esta_na_classe` e `test_reducao_da_palavra_como_o_bash`, à parte: `Ran 2 tests in 11.566s OK`.

  A suíte completa não rodou: o pedido limita a execução a estes testes, e o pre-push do envio roda a suíte. `scripts/validar-plugin.sh` também não rodou, porque o delta não toca o manifesto nem a estrutura do plugin.
- **Código:**
  - `reavaliacao_das_palavras` é curta e não tem lista de prefixos.
  - A tabela de `reduzida` está escrita no comentário e coberta por teste contra o bash.
  - O `so_substituicoes` pula só a palavra `"$(…)"`, que o nível de fora já leu. As sondas `"${x:-$($'eval' …)}"`, `"$($'eval' …)"` e a crase aninhada confirmam isso.
  - Os commits estão em Conventional Commits em português e na ordem da 3B: o corpus vermelho, a redução, o reconhecedor, depois G1. Não tocam `tests/config.json`: as 3 linhas do intervalo vêm da `develop`.
  - O Forge não tem `docs/engineering/praticas.md`, então não há regra de ferramenta nem de leitura a citar.
- **Segurança:** é do E2.1 e não foi refeita aqui. Não achei furo novo no controle. As sondas e os fuzz estão nos scripts em `$TMPDIR/tech-lead-lh10/`, para o `security-engineer`.
