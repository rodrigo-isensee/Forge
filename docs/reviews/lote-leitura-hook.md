---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 182f9287110eaa9838c973aadef6757607e218a1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-leitura-hook (revalidação 11, opção C da revalidação 10)

Pedido RET-LEITURA-HOOK-E-REV, E1.1. Sou revisor independente: não implementei a opção C nem o bloco T (`R-REVIEW`). O parecer anterior (revalidação 10, `reprovado`, A1, A4 e A5 bloqueantes) está em `8d2b868`.

**Delta lido.** O `forge-check delta --parecer docs/reviews/lote-leitura-hook.md` deu `96227be..182f928`. O trecho `96227be..8d2b868` são só os pareceres da revalidação 10 (`docs/reviews/` e `docs/security/`). O merge `182f928` traz a `develop` `d150ec8`; o `git show --remerge-diff 182f928` sai vazio, então não houve resolução manual, e os arquivos da `develop` (`bin/forge-atualizar`, `bin/forge-changelog`, `bin/forge-check`, `agents/`, os pareceres e testes de LOTE-ATUALIZAR, RELEASE-DEV-VERSAO e CONF-BASE-DONO) ficam como "já lido" nos PRs deles. Li inteiro o delta da branch, `8d2b868..874965a`:
- `a49810f` (o corpus vermelho), `8333091` (bloco T), `f4163e6` (`INDECIDIVEL`), `7014072` e `00d83c2` (propriedade e par), `874965a` (textos);
- arquivos: `hooks/_comum.py`, `hooks/conformidade.py`, `hooks/parecer.py`, `tests/test_hooks.py`, `tests/fixtures/heredoc-volta-unica.json`, `docs/hooks.md:95-96`, o desenho (linhas 88 e 282), a ADR 0011 (linha 42) e `changelog.d/lote-leitura-hook.md`.

Fica como "já lido" o que vem antes de `96227be` (revalidações 1 a 10).

**Critério.** A proposta `lote-leitura-hook-caminho-rev10.md`, seções 2 (blocos T e X), 3C (o critério de fim da opção C) e 6 (os textos), com a decisão "C" do dono de 2026-10-24.

## Achados

## Parecer
**Aprovado.** Nenhum bloqueante. Os três bloqueantes da revalidação 10 fecham, e os critérios de fim de T e de C estão cumpridos e medidos.

**Contagem por classe** (decisão "A" de 2026-10-22): nesta volta não há achado em nenhuma classe. A classe "nível" (4.ª volta seguida na revalidação 10) fecha por construção; "orçamento de tempo" e "texto" fecham na 1.ª volta. Não há parada.

### Os achados da revalidação 10
| Achado | Estado | Evidência |
|---|---|---|
| A1 (bloqueante, texto) `docs/hooks.md:95` | **fecha** | o trecho da seção 6.1 está na linha 95, palavra por palavra, e a frase antiga do T9 ("corpus e mutações por nível") sumiu do arquivo |
| A2 (recomendado) célula Promete, linha 88, e `rbash` | **fecha** | o texto da 6.3 está na célula, com "Antes, pela opção B da revalidação 8:" e a data `2026-10-24` no lugar do marcador; `rbash` está na linha 88, na linha 282 e na ADR 0011, linha 42 |
| A3 (recomendado) `hooks/_comum.py:1915` | **fecha** | duas linhas em branco antes de `valor_do_split_string` (agora `hooks/_comum.py:1924-1925`) |
| A4 (bloqueante, nível) `\x{HH…}` | **fecha por construção** | `_ansi_c` e `ESCAPES_ANSI` saíram (o `grep` em `hooks/` não acha nenhum dos dois); AN34 a AN34g saem 2 / 2 no corpus |
| A5 (bloqueante, orçamento) a reavaliação quadrática | **fecha** | passada da direita para a esquerda; 50 mil palavras em menos de 1 s; OT1 e OT2 (20 mil palavras) saem 2 / 2 com o prazo de produção |

### Textos da seção 6
Conferi por script cada citação da seção 6 contra os arquivos (`grep -F` do texto inteiro): 6.1 (o trecho, os três itens de provas, a frase do T9, o acréscimo e o FD15 no FD14) e 6.2 estão literalmente em `docs/hooks.md`, e 6.4 está no desenho (linha 282) e na ADR 0011 (linha 42), com "um shell da lista (`bash`, `sh`, `zsh`, `dash`, `ksh`, `rbash`)". A 6.3 só difere pelo `<data da decisão>`, trocado por `2026-10-24`, que é o que a proposta pede. Os itens de provas da 6.1 entraram em linha, separados por ponto e vírgula, e não em sublista. O commit diz que foi para não partir o parágrafo, e o texto é o mesmo. Não sobrou "escapes ANSI-C" nos textos normativos. A ADR só endurece e não leva o rótulo `afrouxa-regra`, o que está certo.

### Critério de fim do bloco T (seção 2), medido
1. **Por número de palavras:** `test_t_orcamento_por_numero_de_palavras` cobre 6 tipos × {1 mil, o teto = 5 mil, o teto + 1, o teto de caracteres} × 2 hooks. Recusa com 2 em menos de 3 s, com pior tempo de **0,57 s** na minha rodada. Na proposta, "5 mil" e "o teto" são o mesmo número.
2. **Linearidade:** `test_t_reconhecedor_da_reavaliacao_e_linear` roda 50 mil palavras em menos de 1 s, com o seu próprio alarme de 5 s. Fiz também um fuzz de equivalência entre a versão quadrática de `96227be` e a linear: 200 mil listas aleatórias de palavras de shell, `env`, `-S`, `--split-string`, lançadores, `-c` e `None`. Não houve nenhuma diferença em achar ou não achar (`$TMPDIR/tech-lead-rev-lote-leitura-hook/equiv.py`).
3. **Vigia:** `test_t_vigia_de_prazo_recusa_com_marcador_e_libera_sem` recusa com a regra do hook entre 2,5 e 10 s. Conferi à parte que o caso "sem marcador" passa mesmo pelo passo lento: `echo oi` com o passo lento leva **3,23 s** no `conformidade` e **3,18 s** no `parecer`, e sai 0. Sem o passo lento, leva 0,25 s. Então ele prova a liberação pelo vigia, e não um atalho. O `test_t_vigia_cobre_a_busca_do_proprio_marcador` cobre o próprio regex do marcador, com 20 mil `pr` e o `api` no fim.
4. **Mutações**, cada uma numa cópia limpa (`git archive 182f928`), só os testes do item (`$TMPDIR/tech-lead-rev-lote-leitura-hook/mut/`):

| Mutação | Resultado | Onde fica vermelho |
|---|---|---|
| `reavaliacao_das_palavras` volta à de `96227be` | `FAILED (failures=3)` | linearidade em `shell`, `env` e `env -S` |
| o vigia não arma (`vigia_de_prazo` sempre cede) | `FAILED (failures=5, errors=1)` | o vigia nos dois hooks, com e sem marcador, e a busca do marcador nos dois hooks |
| sem o teto no `parecer` | `FAILED (failures=18)` | só `hook='parecer'` (18 de 18), no teto, no teto + 1 e no teto de caracteres |

5. **A sonda de 20 mil palavras:** OT1 e OT2 saem 2 / 2 no corpus, que vale como o Claude Code, porque passar de 10 s libera.

### Critério de fim da opção C (seção 3C), medido
1. **Propriedade sobre o alfabeto:** o teste gera mais de 40 mil textos. Põe `$'` e `$"` em cada posição do nome e da opção, com `\` e cada caractere de 0x20 a 0x7E, a quebra de linha e as formas `\x{…}`, `\u{…}` e `\c\'`. Todos são reconhecidos por `reavaliacao`, o reconhecedor que os dois hooks usam. Uma amostra de 800 ou mais textos dá 2 nos dois hooks reais. A proposta pede os dois hooks reais para todo texto gerado, e o teste os roda só na amostra. Aceito a troca: os dois hooks chamam a mesma `reavaliacao(comando)` no nível 0, e a mutação "um hook só" mostra que a amostra separa os hooks (abaixo). Rodar 40 mil subprocessos levaria horas.
2. **Par exaustivo contra o bash:** 96 caracteres × 7 sufixos × 2 contextos, ou seja, 1.344 casos, dentro de `test_reducao_da_palavra_como_o_bash`, como o texto da 6.1 promete. A `reduzida` dá o valor do `printf '%s'` ou `None`, e nunca `INDECIDIVEL` para uma barra com um caractere.
3. AN34 a AN34g e AN35a a AN35d saem 2 / 2. Os FD15a, b, c, g e h saem 2 no `parecer`, e os contornos FD15d, e, f e i saem 0.
4. **Mutações:**

| Mutação | Resultado | Onde fica vermelho |
|---|---|---|
| `reduzida` sem o `INDECIDIVEL` do `$'` (só o do `$"`) | `FAILED (failures=1)` | a propriedade, já na parte do reconhecedor (o `fail` para no primeiro texto liberado) |
| o `parecer` não guarda o achado `INDECIDIVEL` | `FAILED (failures=455)` | só no `parecer` (455 de 455, nenhuma no `conformidade`): a propriedade separa os hooks |

5. A busca de `$'` e `$"` nos fixtures `-libera` do `parecer` está registrada no `a49810f`, e nenhum fixture muda de código.

**Sonda própria da classe "nível"** (`fuzz_eval.py`, só o bash). Gerei 10 mil textos `: <miolo> eval SENT`. O miolo junta pedaços de `$'`, `$"`, aspas, barras, `\x{65}`, separadores, quebra de linha, `#`, `bash` e `-c`. Rodei cada texto no bash com `eval` e `bash … -c` trocados por funções sentinela. Destes, **623** rodam a sentinela no bash, e o reconhecedor libera **0**. A confusão do leitor sobre onde termina um `$'…'` fica sempre na mesma palavra que tem o `$'`, e por isso essa palavra cai em `INDECIDIVEL`.

### A invariante `def conteudos_de_crase` em `tests/config.json`
**Não é afrouxamento.** A troca vem do `f34a329` (CRASE-ASPA-HOOK), de pedido anterior do lote, e não deste delta. A função saiu de `hooks/conformidade.py` e foi para `hooks/_comum.py:346`. A invariante da definição foi junto: a chave nova `"hooks/_comum.py": ["def conteudos_de_crase"]` segue protegendo a definição, agora no lugar onde ela está. Em `hooks/conformidade.py`, a entrada passou a `conteudos_de_crase\(`, que protege o uso: as chamadas nas linhas 723 e 1355. A linha do `import` não casa, porque não tem o parêntese. Proteger o uso no hook é tão forte quanto proteger a definição, e a definição continua protegida. O PR não precisa do destaque de afrouxamento.

### Recomendação, fora do bloco (não bloqueia)
A mensagem do prazo vencido (`hooks/_comum.py:2235`) usa o contorno do teto ("divida a chamada em comandos menores…"). Quando o que passou dos 3 s foi um `git` lento, e não o texto, esse contorno não ajuda. A medida tem folga: um `git push origin melhoria/sonda` legítimo, num clone de sonda do Forge, levou de 0,12 a 0,24 s com o prazo de produção (o `gh pr create` levou de 0,12 a 0,18 s). Sugestão para um cartão: dizer também "ou tente de novo; o motivo está em `.forge/run/erros.log`".

### Fora do bloco
- **Testes que rodei**, na worktree em `182f928`, com `HOME` em `$TMPDIR/tech-lead-rev-lote-leitura-hook/casa`: `python3 -m unittest tests.test_hooks` deu `Ran 66 tests in 482.958s OK`. A suíte completa não rodou, porque o brief limita a execução aos testes do lote, e o pre-push do envio roda a suíte. `scripts/validar-plugin.sh` também não rodou: o delta não toca o manifesto nem a estrutura do plugin.
- **Código:**
  - `reduzida` ficou menor e só tem a remoção de aspas do POSIX.
  - `_resto_com_ansi` é conservador depois de `$(`, `${` e crase. No máximo recusa um `$'` que estava entre aspas.
  - O vigia desarma em `bloquear` e no `finally`.
  - `PrazoVencido` deriva de `BaseException`, então nenhum `except Exception` a engole.
  - O caminho depois do vigia (`registrar_erro` e `sessao_vigiada`) só lê o sistema de arquivos e não roda `git`, então não come o resto dos 10 s.
  - Sem `SIGALRM` (Windows nativo), valem só os tetos, e isso está no comentário e no changelog.
- **Commits:** em Conventional Commits em português e na ordem da seção 5 da proposta. O passo 4 saiu em dois commits (`7014072` e `00d83c2`). É o desvio de forma que o Jarvis já aceitou no pedido, e não pede retrabalho. O delta não toca `tests/config.json`.
- O Forge não tem `docs/engineering/praticas.md`, então não há regra de ferramenta nem de leitura a citar. O `docs/engineering/achados-recorrentes.md` (PA-7) não tem linha, e nada nele se aplica.
- **Segurança:** é do E2.1 e não foi refeita aqui. O parecer dela (`a143cf4`, `reprovado`) entrou na branch antes do meu envio, e o A1 dela é da classe nova "lançador que divide texto" (`env -S`). Conferi só se é regressão deste delta, e não é: `env -S 'X=1 bash' -c '…'` dá `None` em `reavaliacao` tanto em `182f928` como em `96227be`. O `-c` depois do valor é lido como opção do `env` pelos dois modelos, e o fuzz de equivalência acima também não mostra diferença. O achado é anterior ao delta e fica com a segurança. Ele não muda o meu veredito sobre o código da opção C e do bloco T, mas o lote não vai ao PR enquanto o parecer dela estiver reprovado.
