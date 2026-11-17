---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-hook-heredoc-palavra
commit: 7185b64c57835ab876cc98df59112fd0a05bfe04
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 (E2.15, melhoria/v047-hook-heredoc-palavra, HOOK-HEREDOC-PALAVRA-FP)

Revalidação por delta da rodada E2.7 (head 730261a5, reprovado; texto no git). Delta lido (`forge-check parecer delta`, 730261a5..7185b64c): no domínio, `hooks/parecer.py` (`corpos_de_dado`, `:264-283`), a emenda v047 da ADR 0011 e 5 fixtures `heredoc-dado-*-bloqueia` novas; fora do domínio, os 2 specs de mutantes (M5 reapontado, M10 e M11), `docs/hooks-fixtures.md` e o fragmento do changelog, lidos por serem a guarda do controle. Já lido na rodada anterior e não tocado: o resto do hook e `hooks/_comum.py`.

## Gatilhos
Gatilhos: controle do Forge (`hooks/parecer.py`, guarda do `R-REVIEW`), afrouxamento de veredito do hook (4 recusas viram libera).

## Achados
- A3 (bloqueante) hooks/parecer.py:281 · alvo com chave de sequência (cat > bin/l{s..s}, bin/{l..l}s, g{r..r}ep) tem valor literal com a chave, o nome lido (l{s..s}) não cruza com os programas; o bash expande para bin/ls e o ls da mesma chamada roda o corpo (S1, S2). Mesma família do A1.
- A2 (recomendado) hooks/parecer.py:283 · o corpo gravado num arquivo que outro processo roda depois (.git/hooks/pre-commit, ~/.bashrc) passa como dado; a emenda v047 da ADR 0011 o põe fora da promessa (mesma capacidade do Write). Informativa, sem mudança.

## Sondas
- S1 · fixture do hook com o comando cat > bin/l{s..s} <<'FIM' / #!/bin/sh / gh pr merge 12 --squash / FIM / ls (quebras de linha como /) · espera: código 2 (R-CONTRIB ou R-REVIEW) · obtido: código 0, sem stderr
- S2 · bash c.sh, com bin/ls executável no PATH e c.sh = cat > bin/l{s..s} <<'FIM' / #!/bin/sh / echo CORPO-RODOU / FIM / ls · espera: o ls não roda o corpo · obtido: CORPO-RODOU

## Detalhe dos achados
**A1 da E2.7 (crase no alvo): resolvido.** `corpos_de_dado` devolve False com crase na linha fora dos corpos (`:272`) e com alvo sem valor literal, None ou vazio (`:277`). Refeitas as sondas da crase e as que dependem do alvo (50, hook do head, fixtures de `tests/test_hooks.Fixture`): as 4 formas do A1 (`` `echo bin/ls` ``, `` bin/`echo l`s ``, `` `cat n` ``, `` `head -1 n` ``) e as variantes `` `echo bin/ls`x ``, `` "`echo bin/ls`" ``, `''`, `""`, crase com `>>`, `&>`, `>|`, `1>`, colada, redireção antes do programa, `>&`, `{fd}>`, `3>`, crase no argumento do `ls`, do `echo` e do `cd`, e crase como o próprio programa, todas código 2; S1 e S2 da E2.7 dão código 2. Alvo literal segue recusando com nome de programa (`bin/ls`, `'bin/ls'`, `bin/'l's`, `bin/l''s`, `bin/l""s`, `"bin/"ls`, `~/bin/ls`, `./ls`, `~+/ls`, curinga `[`, `?`, `*`, `$( )`, `\`, `$'…'`, `>(sh)`, segunda redireção depois do `<<`). Legítimos seguem liberando: crase dentro do corpo de `<<'FIM'`, `<<"FIM"` com `wc`, `2>/dev/null`, alvo com espaço entre aspas, `mkdir -p` com `head`, `>>` com `tail`. Mutantes M9, M10 e M11 morrem (`bin/forge-mutante`), e o teste do corpus heredoc passa.

**A3 (bloqueante, alta para o controle).** Evidência: `hooks/parecer.py:281` filtra só `*?[` no nome do alvo; a chave fica no `valor` do leitor (o alvo `bin/l{s..s}` vira o nome `l{s..s}`), e o bash aplica a expansão de chaves ao alvo da redireção: a sequência de um elemento (`{s..s}`, `{l..l}`, `{r..r}`) dá uma palavra só, sem o erro de redireção ambígua que barra `bin/{ls,}`. Sondas no head, corpo com `gh pr merge 12`: `bin/l{s..s}`, `bin/{l..l}s`, `>> bin/l{s..s}` (com `ls`) e `g{r..r}ep` (com `grep`) dão código 0; o corpo com `git merge` também. S2 prova no bash real o mesmo cenário do S2 da E2.7. Não bloqueiam (sem efeito): `bin/l{s}` (o bash grava o nome literal), `ls{,}` (redireção ambígua), `{bin/ls..bin/ls}` (sequência inválida, nome literal). Caminho: o agente troca o nome literal do alvo pela chave de sequência e passa a ação crítica pela guarda do `R-REVIEW`; cai no critério de reversão da própria emenda ("um programa da mesma chamada que o hook libera como dado roda o corpo") e no item 3 (ii) da ADR 0011. Correção mínima: em `corpos_de_dado`, incluir `{` no filtro do nome (`"*?[{"`, `:281`), o que também recusa a chave entre aspas, conservador e sem custo para os legítimos acima; uma fixture `heredoc-dado-*-bloqueia` para `bin/l{s..s}` com `ls` e para `g{r..r}ep` com `grep`, e um mutante que guarde a nova condição (o M9, se a linha mudar, precisa do `de` novo). Esforço: P. Dono: autor da branch (`tech-lead` revisa). A emenda diz "todo alvo de redireção de valor literal, sem curinga (`*?[`)"; com a correção, citar também a chave. Este achado era da varredura da E2.7 e me escapou: lá sondei só a chave com vírgula (`bin/{ls,}`), que o bash recusa; a sequência entra como dimensão nova da matriz (expansão de chaves de um elemento no alvo).

**A2 (recomendado, sem mudança de estado).** A emenda o registra como fora da promessa e com o sandbox e o pre-push; nada a fazer nesta branch.

**Afrouxa-regra e a emenda.** O afrouxamento das 4 fixtures antigas (`texto-passa-heredoc-lido-e-ls`, `heredoc-parecer-cat-e-wc-libera`, `-echo-com-redirecao-libera`, `-echo-em-segundo-plano-libera`) está coberto pela emenda v047 da ADR 0011: nomeia as 4, dá o motivo (texto que só cita a ação crítica, sem nada rodar; mesma capacidade do Write), os limites e o critério de reversão, e marca "Afrouxa; rótulo `afrouxa-regra`". Falta só que os limites escritos batam com o código (A3). O rótulo segue do dono (`R-LIMITES`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados no clone em 7185b64c: `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_heredoc_dado_libera_e_bloqueia` (OK), `bin/forge-mutante tests/mutantes/v047-hook-heredoc-palavra-2.json` (M9, M10, M11 morreram) e as 60 sondas (script em `$TMPDIR`). A suíte inteira roda no CI do PR, ainda não aberto. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint; o delta não toca workflow nem traz segredo.
