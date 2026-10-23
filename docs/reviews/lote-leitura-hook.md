---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: b2c7d83919b3c2d7e68dad82c4a1f37fde680146
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-23
---
# Review: lote-leitura-hook (revalidação 8, opção A)

Escopo: os commits da opção A, `02d1aaa..b2c7d83`. São eles: `8069653`, o merge da `develop` `7423c44` (#288); `e4189d9`, o corpus com as marcas `fecha: "A"`; `af335ca`, os itens 1 a 3; `171e3e1`, o T8 estendido e o T9; e `b2c7d83`, as emendas e o changelog. Pedido RET-LEITURA-HOOK-REV8, E1.1. Sou revisor independente e não implementei (`R-REVIEW`).

O `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` listou `02d1aaa..e03b3c6` (o `e03b3c6` é a cópia do parecer anterior nesta worktree). Li todo o delta da opção A: `hooks/_comum.py` 608-610, 733-734 e 1569-1655; `hooks/conformidade.py` 775-776; `hooks/parecer.py` 386-388; o corpus, linhas 163-193; `tests/test_hooks.py`, o T8 e o T9; `docs/hooks.md:94`; a ADR 0011, linha 40; o desenho, linhas 88 e 276-278; e o fragmento do changelog.

O que o merge trouxe (`.githooks/pre-push:242`, `tests/apoio_pathlib_312/`, os 2 fixtures `contrib-falha-fechada-*` e os pareceres `suite-local-verde`) é o #288, já revisado na `develop`. Ele não toca `hooks/`, então fica como "já lido". Também fica como "já lido" o que vem de antes (`960e71b..02d1aaa`, revalidações 6 e 7). A segurança é do E2.1 e não foi refeita aqui.

**Critério:** vale o da seção 2A de `docs/propostas/lote-leitura-hook-caminho-rev7.md`, que está no desenho, linha 278. Uma sonda só bloqueia se o hook a liberar com marcador e `<<` e o bash com registradores mostrar um programa ou um argv que a gramática não listou. A4/R1 e X1 a X3 são recomendação ou cartão N-HOOK1. FD9 a FD11 têm contorno e não bloqueiam.

Leio `<<` como o `<<` que o bash lê, que foi a leitura da própria proposta no BL1 (`<\⏎<`). Não é critério novo. Se o Jarvis ou o arquiteto lerem `<<` só como o literal do texto da chamada, o A1 vira cartão N-HOOK1.

## Achados
- A1 (bloqueante) hooks/_comum.py:1614 · classe "escopo da gramática (nível)", 2.ª volta seguida: o gatilho `"<<" in texto` não vê o `<<` partido por aspas ou `\` dentro de `eval`/`bash -c` (Q1 a Q4: 0 / 0, e o corpo roda no bash). Vai ao arquiteto e ao dono pela regra das duas voltas.
- A2 (recomendado) tests/test_hooks.py:2214 · o T9 só olha o que a gramática aceitou, e o T8 "por nível" só envolve o `<<` literal: nenhum vê o A1. O T9 fica verde ao reverter o item 1 ou o 2. Rodar o T9 também sobre o que os hooks liberam com marcador.
- A3 (recomendado) tests/fixtures/heredoc-volta-unica.json:182 · o BL1 recusa pelo leitor, não pelo gatilho: sem tirar o `\⏎` (M2t), corpus, T8 e T9 seguem verdes. Pôr caso que dependa só do gatilho ou anotar a cobertura.
- A4 (recomendado) hooks/_comum.py:1497 · outra classe, opção do git que roda programa (O2 `--receive-pack`, O3 `rebase -x`, R1): segue aberta, cartão N-HOOK1 por decisão do dono, na coluna "Não promete" do desenho (linha 88).

## Parecer
**Reprovado**, por um bloqueante, o A1. A opção A está implementada como a seção 2A pede. Os itens 1 a 3 estão em `af335ca`, com corpus vermelho antes (`e4189d9`, marcas `fecha: "A"`). O T8 cobre caractere, palavra, nível e corpo, e o T9 é um oráculo de bash com registradores, `env` mínimo e sem rede (`R-CUSTO`). A ADR 0011 só endurece, e o desenho tem o `critério mudou:` nas linhas 88 e 278. FD9 a FD11 estão no corpus e em `docs/hooks.md:94`, com contorno.

Os três bloqueantes da revalidação 7 estão fechados nas formas medidas. Mas a classe "nível" não acabou: o texto do nível 0 não contém os outros quando o `<<` do nível 1 nasce da remoção de aspas. A frase do item 2 da proposta ("o texto do nível 0 contém todos os outros") é falsa para `<''<`, `<""<` e `\<\<`. A correção de código é pequena, por exemplo um gatilho `<(?:['"\\]|\\\n)*<`, ou a gramática em todo nível que o hook segue. Mas é a 2.ª volta da mesma classe, então o caminho é do arquiteto e do dono, e não uma volta direta ao autor.

**A1.** Sem `<<` literal no texto do nível 0, a gramática não vale, e o nível 1, que o hook segue, volta ao leitor de `199d1d1`, como no B1. A ADR 0011 (linha 40) promete: "`bash -c '…'`, `sh -c` e `eval '…'` recusam ali". Não é regressão: Q1 a Q4 também saem 0 / 0 com os hooks da `develop` `7423c44`. Pela regra das duas voltas (decisão "A" de 2026-10-22), a entrega para: o `software-architect` propõe o caminho e o dono decide.

**A2.** Pela mutação, o T9 falha só quando se reverte o item 3 (tabela abaixo). Isso contradiz a divisão da seção 5 da proposta, que diz: "o T9 falha quando se reverte cada item 1 a 3". O item 1 fica de fora porque o T9 usa um git falso e o argv bate. O item 2 fica de fora porque o T9 pula o que não é `Gramatica`. Sugestão para o caminho do A1: o T9 falharia se um registrador recebe na entrada o corpo de um heredoc que a gramática não listou.

**A3.** Hoje isso só endurece, porque o leitor é mais estrito ali: ele lê o corpo do BL1 como comando (`R-MAIN`, `R-REVIEW`).

### Revalidação dos achados da revalidação 7, contra os hooks reais
As sondas rodaram com um runner próprio, que monta o fixture do corpus (`modelos` e `corpos`) para cada hook e chama `rodar` de `tests/test_hooks.py`. Rodei sobre a worktree em `b2c7d83`.

| Item | Sonda | conf / par | Estado |
|---|---|---|---|
| A1 (rev. 7) | G3 `git '-c' 'core.fsmonitor=…'` | 2 / 2 (`git -c` na chamada com heredoc) | **resolvido** |
| A1 | G3c (corpo `git push origin HEAD:main`) | 2 / – (célula do `parecer` não se aplica) | resolvido |
| A1 | G3d `git "-c"` em K3 | 2 / 2 | resolvido |
| A1 | G3p `git -'c'` (partida) | 2 / 2 | resolvido |
| A1 | G3e `'--config-env'=…`, G3x `'--exec-path'=…` | 2 / 2 | resolvido |
| A1 | G3s `git -ccore.fsmonitor=…` (colado) | 0 / 0 | controle: o git 2.53 recusa (`unknown option: -ccore.fsmonitor=…`) e não roda o fsmonitor |
| A2 (rev. 7) | B1 (`bash -c` com o Z1), B2 (`eval`) | 2 / 2 | **resolvido nas formas literais**; a classe reabre em A1 (Q1 a Q4) |
| A3 (rev. 7) | casos da lista do git no corpus | mutação: sem `-c`/`--config-env` em `GIT_FORA_DA_GRAMATICA`, 15 falhas no corpus; com `sh` em `PROGRAMAS_DA_GRAMATICA`, 2 falhas | **resolvido** |
| A4 (rev. 7) | O2, O3 | não medido de novo (fora do escopo) | **não resolvido**, cartão N-HOOK1 por decisão |
| BL1 | `PATH=/tmp/x$(( cat )) cat <\⏎<'EOF'…` | 2 / 2 (`R-MAIN` e `R-REVIEW`, não pela gramática) | resolvido (ver A3) |
| HC1, HC2, HC3 | `EOF)`, `EOF )` e `EOF x)` dentro de `$(` | 2 / 2 | **resolvido** (HC4 e HC5 no corpus verde) |
| Z1 | controle, nível 0 | 2 / 2 | segue |

### Sondas novas (A1)
O efeito foi medido no bash 5.3.9, com `env -i PATH=/usr/bin:/bin bash --noprofile --norc -c`, numa pasta de `$TMPDIR`. O `x0/cat` é falso (`exec bash -s`), e o `x0/gh` falso grava `prova`.

| ID | Sonda (`{CORPO}` é a linha crítica do hook) | b2c7d83 conf / par | develop conf / par | Bash |
|---|---|---|---|---|
| Q1 | `eval 'PATH=/tmp/x$(( cat )) cat <''<"EOF"⏎{CORPO}⏎EOF'` | **0 / 0** | 0 / 0 | `RODOU gh pr merge feature/x --merge` |
| Q2 | o mesmo com `bash -c` | **0 / 0** | 0 / 0 | `RODOU gh pr merge …` |
| Q3 | `bash -c "PATH=/tmp/x\$(( cat )) cat <""<'EOF'⏎{CORPO}⏎EOF"` | **0 / 0** | 0 / 0 | mesma leitura (não rodado) |
| Q4 | `eval PATH=/tmp/x\$\(\(\ cat\ \)\) cat \<\<\'EOF\'"⏎{CORPO}⏎EOF"` | **0 / 0** | 0 / 0 | `RODOU gh pr merge …` |
| Q5 | `bash -c '… cat <\⏎<"EOF"…'` | 2 / 2 | | controle: o gatilho tira `\⏎` |
| Q6 | `bash -c '… cat <""<"EOF"…'` (aspas duplas dentro das simples) | 2 / **0** | 2 / 0 | mesma leitura de Q1 |

Ao fim, o `x0/cat` é o mesmo cenário do Z1 e do B1 (`PATH` trocado pela aritmética): o bash roda o corpo do heredoc como comando.

### O T8 e o T9 provam o critério de fim da seção 2A?
Em parte. (1) O T8 e o T9 passam: `CorpusHeredocVoltaUnica`, numa cópia limpa (`git archive b2c7d83`), deu `Ran 6 tests in 39.949s OK`. (2) G, B, BL1, HC e as sondas das voltas 1 a 6 dão 2 nas células com marcador, pelo corpus verde e pelas sondas acima. (3) O critério não está provado: Q1 a Q4 escapam, e o T9, por construção, só olha o que a gramática aceitou.

Para conferir, reverti cada item numa cópia limpa e rodei só o T8, o T9 e o corpus, um de cada vez (`R-TETO`):

| Mutação | T8 | T9 | corpus |
|---|---|---|---|
| M1: sem `sem_aspas` em `comando_fora_da_gramatica` (item 1) | falha | **verde** | 13 falhas |
| M2: volta `if not achados: return None` (item 2) | falha | **verde** | 5 falhas |
| M3: sem a recusa da linha que começa pelo delimitador, na gramática e em `heredocs` (item 3) | falha | 9 falhas | 11 falhas |
| M3g: o item 3 só na gramática | falha | verde | verde (o `duvidar` de `heredocs` cobre o `$(`; fora dele o bash não fecha em `EOF)`, só recusa a mais, FD10) |
| M2t: o gatilho sem tirar `\⏎` | verde | verde | verde (A3) |

A suposição de "linha que começa pelo delimitador" está certa no bash 5.3.9: ` EOF)` e `⇥EOF)` não fecham; `EOF)` e `EOF⇥)` fecham.

### Fora do bloco
- A suíte completa não rodou, porque o dono limitou a memória e o pedido manda rodar só o corpus e as sondas. O implementador registrou `suíte 1608 OK` no histórico do RET-LEITURA-HOOK-A. `scripts/validar-plugin.sh` também não rodou, porque o delta não toca o manifesto nem a estrutura do plugin.
- Código: `sem_aspas` é exata porque `simples_da_gramatica` só monta palavra com aspas fechadas e literais. `Gramatica` dá ao T9 a lista que ele compara, sem duplicar a leitura. Os nomes e as docstrings dizem o que fazem.
- Os commits estão em Conventional Commits em português, na ordem da seção 5: corpus vermelho, depois a regra, depois os testes e as emendas. Não tocam `tests/config.json`. O Forge não tem `docs/engineering/praticas.md`, então não há regra de ferramenta nem de leitura a citar.
- Segurança: o A1 é um furo no controle (`R-SEGURANCA`, `R-MAIN` via `git push` no corpo, `R-REVIEW` via `gh pr merge`). O `security-engineer` o recebe por este parecer (sondas Q1 a Q6), sem cartão à parte.
