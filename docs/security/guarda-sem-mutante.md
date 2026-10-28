---
tipo: revisao-seguranca
contrato: 1
pedido: guarda-sem-mutante
branch: melhoria/guarda-sem-mutante
commit: 7c86f530cb491355a40f2699215ebd45f3d2c5d4
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-28
---
# Review de segurança: guarda-sem-mutante (PR 1, `forge-mutante --cobertura`, núcleo Python)

Diff revisado: `991cd092b42c88d86a16912ff8ddc1b72b8da026...7c86f530cb491355a40f2699215ebd45f3d2c5d4` (`bin/forge-mutante`, 6 specs em `tests/mutantes/`, `tests/test_forge_mutante.py`, `agents/qa-engineer.md`, `skills/qa-testing/SKILL.md`, fragmento do changelog). Referências: o modelo de ameaças `docs/security/guarda-sem-mutante-ameacas.md` (T1, T3 a T7) e a ata `docs/alinhamentos/2026-10-28-revisao-desenho-guarda-sem-mutante.md` (decisões 1 a 5 e o plano de PRs, com shell, `isentas` e os tetos restantes de T7 no PR 2). Sondas em clone descartável em `$TMPDIR/security-engineer-guarda-sem-mutante/`; nada escrito no `~/Forge`.

## Gatilhos
`controles do Forge` (`R-SEGURANCA`): a entrega cria uma checagem que decide, por rc, se a condição mudada tem mutante declarado. É um controle que analisa entrada (o diff e as specs), revisado pela matriz de dimensões da família.

## Achados
- A1 (bloqueante) bin/forge-mutante:324 · passagem silenciosa: `.gitattributes` com `-diff`, `binary` ou `diff=<driver>` com textconv faz o `git diff -U0` sair sem hunk; a condição nova não cruza linha mudada e o rc é 0 (sondas P1c, P1d, textconv); correção: `--text --no-textconv`
- A2 (bloqueante) bin/forge-mutante:375 · passagem silenciosa: com `\r` solto (arquivo só com CR, ou `\r` dentro de string tripla), o `ast` numera linhas que o `git diff` não numera; a condição nova cai fora de `linhas` e o rc é 0 (sondas P3b, P3e); correção: rc 2 para `\r` fora de `\r\n`
- A3 (recomendado) bin/forge-mutante:375 · troca de condições entre si (multiconjunto igual, ex. `a > 1` e `b > 2` trocados de ramo) sai com rc 0 (sonda P2); efeito da decisão 1 da ata; aceitar como risco ou contar condição cuja linha mudou mesmo com contagem igual
- A4 (recomendado) bin/forge-mutante:433 · nome de arquivo com quebra de linha sai cru na saída e parte a linha (sonda P4); o rc não muda, mas a leitura humana pode ser enganada; imprimir o caminho escapado (`repr` ou `\n` literal)

## Detalhe dos achados
**A1, passagem silenciosa por atributo do git (média).** Evidência: `bin/forge-mutante:324-327` roda `git diff -U0 --no-renames --no-color --no-ext-diff` sem `--text`; com o arquivo marcado como binário o corpo é só `Binary files ... differ`, `HUNK.findall` não acha nada, `linhas` fica vazio e `bin/forge-mutante:375` pula toda condição nova. A apagada (por contagem) ainda reprova uma condição editada (sonda P1), mas a condição **adicionada** passa. Sondas, todas com `if b == 7:` novo em `bin/sonda.py` e nenhum mutante:
- P1c: `.gitattributes` `bin/sonda.py -diff` no mesmo diff: saída só `não coberto: .gitattributes`, rc 0.
- P1d: o mesmo atributo já na base (`bin/*.py -diff`), só a condição no diff: saída vazia, rc 0.
- `bin/sonda.py diff=x` versionado e `diff.x.textconv` na configuração local: rc 0 (sem a configuração, rc 1).
- Controle da correção: o mesmo diff com `--text --no-textconv` devolve `@@ -7,0 +8,2 @@`. O `git show <sha>:<arq>` de `ler_no_commit` não aplica textconv (conferido), então só o `git diff` precisa da mudança.

Caminho: o autor (ou um projeto que já marca código gerado como `-diff` ou `binary`) versiona o atributo; ele vale também na rodada do conferente e do QA, que leem o mesmo commit. É a classe que o pedido quer fechar (rc 0 sem cobrir) e a dimensão "mecanismo" da matriz (o que altera a saída do diff lido) não estava coberta. Correção mínima: em `bin/forge-mutante:324`, acrescentar `--text` e `--no-textconv` ao `git diff -U0`; os atributos que a correção precisa neutralizar são, inteiros: `-diff`, `binary` (macro de `-diff -merge -text`), `diff=<driver>` com `diff.<driver>.textconv` e `diff=<driver>` com `diff.<driver>.binary=true`. Teste: um caso por atributo dessa lista com condição nova sem mutante, esperando rc 1. Esforço P. Dono: `tech-lead` (autor da E1.2).

**A2, linha física do git × linha lógica do `ast` (baixa).** Evidência: `linhas` vem dos hunks do git, que só contam `\n` (`bin/forge-mutante:327`); `condicoes` (`bin/forge-mutante:335`) usa o `lineno` do `ast`, que trata `\r` solto como quebra de linha. Com um `\r` solto antes da condição, o número do `ast` passa à frente do do git, e `linhas.isdisjoint(...)` em `bin/forge-mutante:375` pula a condição. Sondas: P3b, arquivo só com CR e `if b == 7:` novo: rc 0; P3e, arquivo LF com `X = """a\rb"""` na linha 1 e `return 0` trocado por `return b == 7`: rc 0. (Em string de aspas simples o `\r` quebra o parse e dá rc 2, o lado certo.) Caminho: menos provável que A1 (editor ou cópia que grava CR), mas a falha é aberta e silenciosa, na dimensão "linha física e lógica" da matriz. Correção mínima: em `ler_no_commit` ou `analisar`, o texto Python com `\r` que não faz parte de `\r\n` é `ValueError` (rc 2), igual a "arquivo que não faz parse"; ou calcular `linhas` em Python sobre `antes` e `depois` com a mesma quebra do `ast`. Teste: as duas sondas acima, esperando rc diferente de 0. Esforço P. Dono: `tech-lead`.

**A3 (baixa, recomendado).** Sonda P2: trocar `a > 1` e `b > 2` de lugar no `if`/`elif` mantém o multiconjunto e sai rc 0, embora a guarda de cada ramo tenha mudado. A decisão 1 da ata escolheu o multiconjunto para não contar código só movido; o T3 do modelo pedia que a linha removida que era condição contasse. Sem caminho barato de ataque além do erro do autor; fica como risco a aceitar no PR 2 ou como regra extra (condição nova cuja linha está num hunk conta, mesmo com contagem igual, quando o texto da linha da base no mesmo hunk era outra condição). Dono: `tech-lead`.

**A4 (informativa, recomendado).** Sonda P4: `bin/nl\nx.py` sai em duas linhas. O rc segue 1 e o `-z` protege a leitura; só a saída para quem lê pode ser forjada por nome de arquivo (ex. uma linha `coberta · ...` falsa). Correção: escapar o caminho ao imprimir. Dono: `tech-lead`.

**Conferido sem achado (sondas e leitura).**
- T1, mutante de fachada: `de` com menos de 8 caracteres não brancos não cobre (F1); troca fora do nó não cobre (F3); troca em comentário dentro de condição de várias linhas dá rc 2 por `ast.dump` igual (F2); `para` só com espaço não cobre (F7); `de`=`para` já é barrado por `validar_spec`; só specs que o diff adiciona ou edita contam; `testes` inexistente ainda "cobre", o que é o "declarado, não provado" aceito.
- T3: `return a > b`, `not`, `assert`, guarda de `match`, compreensão e condição em várias linhas entram pelo `ast` (`bin/forge-mutante:76-79`); arquivo `.py` removido e condição apagada saem com rc 1 (P9, P0); `.py` sem parse dá rc 2 (P7); nada é importado nem executado (só `ast.parse`).
- T4: `--base HEAD` e diff vazio dão rc 2 (P5); `--base` com `-` inicial não vira opção (`--end-of-options` em `resolver`, P5b); leitura por `git show`, não pela árvore; a primeira linha imprime `base= mb= rev=`. Configurações `color.ui=always`, `diff.noprefix`, `diff.mnemonicPrefix`, `diff.relative`, `core.quotePath`, `diff.algorithm=patience`, `diff.suppressBlankEmpty` e cwd em subpasta não mudam o resultado.
- T5: shebang Python sem extensão é analisado (P8); `.sh` em `hooks/` e arquivo sem extensão nem shebang saem como `não coberto` (P6, P8b), como a ata manda até o PR 2.
- T6: a checagem cobre a si mesma; sobre o próprio diff, `bin/forge-mutante --cobertura --base 991cd092b42c88d86a16912ff8ddc1b72b8da026` deu rc 0 com 24 condições `coberta · ... · declarado, não provado` em `bin/forge-mutante` (linhas 313 a 513), em 1,2 s. As tabelas `TESTES_DO_NO`, `FORA_DA_COBERTURA` e `SPEC_DO_DIFF` são dado sem condição: risco aceito do modelo de ameaças, e mudar nelas pede esta releitura (gatilho `controles do Forge`).
- T7: `-z`, `--literal-pathspecs`, `--` e lista de argumentos sem shell; nomes `-x.py`, com espaço e com quebra de linha são lidos certo (P4); teto de 300 arquivos, 1 MiB por arquivo e 64 KiB por spec; spec que não é objeto dá rc 2 (F6); `UnicodeDecodeError` e `RecursionError` caem nas classes capturadas (rc 2); exceção não prevista termina com rc 1, nunca 0. O orçamento de tempo fica fora da v1 pela ata.
- Para o `tech-lead`, fora de segurança: qualquer arquivo mudado fora de `TESTE`, `*.md` e `changelog.d/` é decodificado como UTF-8 antes de `eh_python` (`bin/forge-mutante:423-424`), então uma imagem ou um arquivo de mais de 1 MiB no diff dá rc 2. A falha é fechada, mas é falso positivo a medir contra o critério de reversão do dono.
- Segredos: nenhum no diff (leitura manual).

## Riscos aceitos e ferramentas
Seguem os riscos aceitos do modelo de ameaças: equivalência semântica e teste fraco (a morte é da rodada `forge-mutante SPEC` e do QA), dado sem condição, a checagem não é portão (nenhum hook nem CI a chama até o PQ do PR 2), e `hooks/` e workflows ficam como `não coberto`. Nenhum risco novo aceito por este parecer.

Ferramentas: sondas locais com `git` e `python3` 3.14.4; `shellcheck` presente, mas o diff não tem shell. Lacunas no PATH: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` (não instalados, `R-CUSTO`). O diff não toca workflow nem dependência.
