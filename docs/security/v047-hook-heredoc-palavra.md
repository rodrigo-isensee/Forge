---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v047-hook-heredoc-palavra
commit: 76b50dc775c366408d0064efd172eec658b0a7a3
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v0474 (E2.38, melhoria/v047-hook-heredoc-palavra, HOOK-HEREDOC-PALAVRA-FP)

Revalidação por delta da rodada E2.15 (head 7185b64c, reprovado pelo A3; texto no git). Delta lido (`forge-check parecer delta`, 7185b64c..76b50dc7): no domínio, `hooks/parecer.py:268,281` (filtro `*?[{`), a emenda v047 da ADR 0011 (cita a chave) e 3 fixtures `heredoc-dado-alvo-com-chave-*-bloqueia`; fora do domínio, o spec de mutantes (M9 reapontado, M12 novo) e `docs/hooks-fixtures.md`, lidos por serem a guarda do controle. Já lido e não tocado: o resto de `corpos_de_dado` e `hooks/_comum.py`. Estado dos achados anteriores: A3 (bloqueante) resolvido; A2 (recomendado) sem mudança.

## Gatilhos
Gatilhos: controle do Forge (`hooks/parecer.py`, guarda do `R-REVIEW`), afrouxamento de veredito do hook (4 recusas viram libera).

## Achados
- A2 (recomendado) hooks/parecer.py:283 · sem mudança: o arquivo gravado que outro processo roda depois segue fora da promessa da emenda (mesma capacidade do Write).
- A4 (recomendado) hooks/parecer.py:281 · com extglob ligado no shell do Bash, bin/@(ls) e bin/+(ls) gravam bin/ls se ele já existe e o hook libera (S1, S2); depende de estado anterior (item 3 da ADR 0011). Correção: `(` no filtro.
- A5 (recomendado) hooks/parecer.py:283 · em sistema de arquivos sem caixa (APFS padrão do macOS) bin/LS é bin/ls; o cruzamento `alvos & nomes` diferencia caixa e libera (S3). Não provado aqui (Linux). Correção: comparar com casefold().

## Sondas
- S1 · fixture do hook com o comando cat > bin/@(ls) <<'FIM' / #!/bin/sh / gh pr merge 12 --squash / FIM / ls (idem bin/+(ls)) · espera: código 2 · obtido: código 0
- S2 · bash -O extglob c.sh, com bin/ls existente no PATH e c.sh = cat > bin/@(ls) <<'FIM' / #!/bin/sh / echo CORPO-RODOU / FIM / ls · espera: o ls não roda o corpo · obtido: CORPO-RODOU (sem extglob: erro de sintaxe, rc 2)
- S3 · fixture do hook com cat > bin/LS (e bin/Ls) <<'FIM' / … / FIM / ls · espera: código 2 em sistema sem caixa · obtido: código 0

## Detalhe dos achados
**A3: resolvido.** Sondas no head (fixture do hook, corpo com `gh pr merge 12`), todas código 2: `bin/l{s..s}`, `bin/{l..l}s`, `>> bin/l{s..s}`, `2> bin/l{s..s}`, `g{r..r}ep` com `grep`, `w{c..c}` com `wc`, `ca{t..t}` com `cat`, `{a,b}`, `{ls,}`, `l{s,s}`, aninhadas (`{{l..l}s}`, `l{{s..s},}`, `{l..l}{s..s}`), com incremento (`l{s..s..1}`), com espaço (`l{s.. s}`, `"bin/l {s..s}"`), entre aspas (`"bin/l{s..s}"`, `'bin/l{s..s}'`, conservador), escapada (`l\{s..s}`), chave na pasta (`b{i..i}n/ls`), chave no alvo do `ls` e na redireção depois do `<<`, e `cat > bin/l{s..s} < x; ls`. `$'bin/ls'`, `bin/$'l's`, `~/bin/ls`, `~+/ls`, `~-/ls`, `~root/bin/ls`: código 2. Refeitas as do alvo das rodadas anteriores (literal, aspas partidas, `./ls`, `bin//ls`, `bin/ls/`, `bin/ls/.`, `[`, `?`, `*`, `?(…)`, `*(…)`, `!(…)`, `$( )`, crase em 4 posições, `\`, `\` com quebra de linha, `>(sh)`, `''`, `&>`, `>|`, `1>`, redireção antes do programa, `{fd}>`, `/usr/local/bin/ls` com `/bin/ls`, `sh x`): todas código 2. Legítimos (7: `ls`, `wc -l`, `head` com pasta entre aspas com espaço, `mkdir -p … && … head`, `>>` com `tail`, `2>/dev/null`, `<<"FIM"` com `wc`): código 0. Mutantes M9 a M12 morrem; o teste do corpus heredoc passa.

**Outras expansões do bash que mudam o nome gravado (pergunta do brief).** A chave de um só elemento só aceita letra e dígito (sondei os 94 caracteres imprimíveis: `{/../}` fica literal), então não move a `/` e não troca o último componente; a chave na pasta deixa o nome cruzável (`b{i..i}n/ls` recusa). O til só expande no início e dá pasta (`~`, `~+`, `~-`, `~usuario`): não forma o nome do programa. Parâmetro, aritmética, `$'…'` e `$"…"` têm `$` (recusa); crase, `$( )` e `<( )`/`>( )` recusam; o alvo da redireção não passa por divisão de palavra (vira redireção ambígua); `nocaseglob`, `globstar`, `nullglob` e `failglob` só agem com `*?[`, já filtrados. Sobra o curinga estendido (A4): com `extglob` ligado, `@(…)` e `+(…)` não têm `*?[` e casam com o arquivo existente. O snapshot do shell do Claude Code grava o `shopt` da sessão interativa do usuário (aqui `shopt -u extglob`); o `bash-completion` liga o `extglob` nas sessões interativas, então ele vem ligado em muitas máquinas. Fica recomendado pelo item 3 da ADR 0011: só casa com `bin/ls` já gravado, e quem o grava antes (Write) já tem a capacidade (A2). Fora do bash, o A5: o sistema de arquivos sem caixa grava `bin/LS` como `bin/ls` e o `PATH` acha `ls`, sem estado anterior; sem sistema assim no ambiente, fica recomendado. Ambas as correções custam uma linha, sem tocar os legítimos acima: `"*?[{("` em `:281` e `alvos` e `nomes` comparados com `casefold()` em `:283`, com uma fixture `-bloqueia` para cada e a emenda da ADR citando o parêntese e a caixa. Esforço: P. Dono: autor da branch (`tech-lead` revisa); pode ir nesta branch ou em cartão.

**Afrouxa-regra e a emenda.** O texto emendado bate com o código (chave citada). O rótulo `afrouxa-regra` segue do dono (`R-LIMITES`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados no clone em 76b50dc7: `tests.test_hooks_parecer_pasta.PastaDoGit.test_corpus_heredoc_dado_libera_e_bloqueia` (OK), `bin/forge-mutante tests/mutantes/v047-hook-heredoc-palavra-2.json` (M9, M10, M11, M12 morreram) e 82 sondas do hook (script em `$TMPDIR`). A suíte inteira roda no CI do PR, ainda não aberto. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint; o delta não toca workflow nem traz segredo.
