---
tipo: review
contrato: 1
pedido: hk3-parecer-texto
branch: melhoria/hk3-parecer-texto
commit: 7b2a225fb476be9c09c3b1a2b41792b7fcaec6ad
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: o hook parecer não recusa a chamada em que merge, pull ou gh pr só aparece no texto (HK3-PARECER, PR B, E2)

## Escopo
Primeira rodada do PR B: o diff `d14a713...7b2a225`, com os commits `1046a5d` e `7b2a225`. Os arquivos são:
- `hooks/parecer.py`, com +47 e -8 linhas;
- `tests/test_hooks_parecer_pasta.py`, com +9 linhas;
- 57 fixtures `texto-*` em `tests/hooks/parecer/`;
- as três specs `tests/mutantes/hk3-parecer-texto{,-2,-3}.json`;
- uma linha em `docs/hooks.md`;
- o fragmento `changelog.d/hk3-parecer-texto.md`.

## Requisitos (decisões de 2026-10-28 10:40 e de 2026-10-29 10:39, 12:06, 12:12 e 12:34)
- **merge-base.** `MERGE = r"merge(?!-base\b)"` tira o `git merge-base` do `PREFILTRO` e do `CRITICO`. Fixtures que cobrem: `texto-passa-merge-base-*` e `texto-barra-merge-base-e-merge`.
- **Heredoc isento só quando a chamada inteira é de cat.** O `SO_CAT.fullmatch` roda sobre a linha sem os corpos. Ele aceita só linhas `cat [>|>>] <arquivo>…`, sem aspa, `$`, `#`, `;`, `&`, `|` nem parêntese, e só ele tira a gramática positiva D. O `corpo_so_lido` e o M3 ficam como estavam.
- **`sed -n <N[,M]>p <arquivos>` vira `cat`.** A troca vale só com números, sem opção depois dos arquivos e com um terminador logo depois. Ela tira o par de aspas em volta de `Np`, e esse par é idêntico e cerca um texto sem caractere especial, então tirá-lo não muda o estado das aspas do resto da linha. Fixtures que cobrem: `sed-i`, `sed-com-comando-e`, `sed-com-e-colado`, `opcao-depois`, `opcao-no-lugar-do-arquivo` e `metacaractere`.
- **sh -c só de leitores e espera.** O `e_shell_c_de_texto` percorre os mesmos comandos simples e chama a mesma `reavaliacao_das_palavras` que a `reavaliacao`. Com isso, toda reavaliação da linha tem de ser `<shell> -c <script literal>` cujo script só usa `grep`, `cat`, `sleep` e `echo`, com laços e condições, sem crase nem `$(`. O `eval`, o `env -S`, o lançador com opção e o `$'…'` continuam devolvendo `False`.
- **O M3 continua valendo para python3, git, gh e forge-check.** Fixtures que cobrem: `texto-barra-heredoc-gravado-roda-{python3,git,gh,forge-check,sh}`.
- **Pull em heredoc e pull ou gh pr em eval seguem barrados.** Esse era o mérito parcial da conferência das 12:12. Fixtures que cobrem: `texto-barra-heredoc-bash-executa-pull`, `texto-barra-eval-executa-{pull,gh-pr,merge}`.
- **Corpus.** O PR traz 57 fixtures novas, 44 `texto-barra` e 13 `texto-passa`; o glob `texto-*` do teste também pega a `texto-no-corpo-do-pr-nao-confunde`, que já existia. O teste novo exige pelo menos 30 fixtures e pelo menos 10 do lado que passa, o que cumpre o item 11 do checklist (o mínimo de itens).
- **Specs.** As três specs somam 39 mutantes (T1 a T39). Elas cobrem cada guarda nova: a leitura ilegível, o `all`, o índice do shell, as quatro condições do `resto`, `corpos or`, `SO_CAT`, `MERGE`, as partes do `SED_LE` e cada item de `LE_O_TEXTO`, `SO_ESPERA` e `CONTROLE`. Não refiz a mutação: ela é do autor (V2), e a entrega `7b2a225` foi conferida às 12:26.

## Ferramentas (citadas, não refeitas)
- **Teto M14.** `git diff --numstat --no-renames origin/develop...HEAD` dá 64 linhas de código e teste: `hooks/parecer.py` 47+8 e `tests/test_hooks_parecer_pasta.py` 9. Fixtures, specs, `.md` e o fragmento ficam fora da conta. É um comportamento só, uma classe em `hooks/`, com corpus próprio.
- **Item do teste.** `python3 -m unittest tests.test_hooks_parecer_pasta` deu `Ran 2 tests ... OK`, rodado com a carga de 1 minuto em 3,27.
- **Caminho pessoal.** O padrão `/home/<nome>/` do `scripts/verificar-contribuicao.sh:22` não aparece no diff. As fixtures usam `home/wtx` relativo, o caso do CI do PR #360.
- **Changelog.** O fragmento `changelog.d/hk3-parecer-texto.md` está presente. O `CHANGELOG.md` não foi tocado.

## Sondas (o hook da base `d14a713` contra o da branch, repositório temporário na `develop` com `melhoria/x`)
**Continuam barrados nos dois:**
- `git merge` direto;
- o `<<-` com o delimitador tabulado seguido de merge;
- `( sh -c 'sleep 1' ); bash -c 'git merge …'`;
- `PS4='$(git merge …)' bash -xc`, `x='$(…)' bash -c 'echo ${x@P}'` e o índice aritmético `${a[x]}`, com prefixo, `export` e `env`;
- os delimitadores `E"O"F`, `\EOF` e `''`;
- o `sed -n 1p` sem arquivo seguido de merge;
- `bash <<'EOF'` com `sed` e merge;
- o heredoc gravado seguido de `sed -n 1p f | sh`, de `sh f`, de `bash --rcfile f -ic` ou de `sh -c 'cat f'`.

**Passam agora, e o bash confirma que é só texto:** `cat <<'EOF'` com merge no corpo, ` EOF` com espaço antes, dois heredocs na mesma linha, `cat 3<<'EOF'`, o CRLF e a espera `timeout 900 sh -c 'until grep …'` com `merge-base`.

**Passam agora, mas a base recusava:** `sh -c 'echo git merge …' | sh` e `BASH_ENV=e.sh bash -c 'sleep 1'` depois de `printf … > e.sh`. Os dois rodam o merge. São a mesma classe de `echo 'git merge …' | sh` e de `printf … > e.sh; sh e.sh`, e essas formas já passam na base (rc 0 nas duas). Não abrem uma capacidade nova contra a base, por isso o achado fica como recomendado (A1). Pela limitação [B] do ADR 0009, o hook barra em regra e não garante.

## Achados
- A1 (recomendado) hooks/parecer.py:95 · `sh -c 'echo git merge …' | sh` e `BASH_ENV=f bash -c 'sleep 1'` passam onde a base recusava. A base já deixa passar `echo … | sh` e `printf … > f; sh f`, então não há capacidade nova. Sugestão: pôr "texto enviado por pipe a um shell" na limitação [B] de docs/hooks.md, ou não isentar o `sh -c` cuja linha tem um shell que lê o stdin.

## Parecer
**Aprovado.** O PR B faz o que o E2 pede, dentro do limite que as decisões de 12:06 e 12:34 fixaram:
- a palavra crítica deixa de contar no `merge-base`, no corpo de heredoc numa chamada só de `cat` (com o `sed -n` numérico) e no `sh -c` que só lê ou espera;
- executar merge, pull ou gh pr em heredoc rodado por um shell, em `sh -c` com outro comando e em `eval` continua barrado;
- o M3 continua valendo para python3, git, gh e forge-check.

O código é curto e reaproveita os leitores existentes (`palavras_do_texto`, `reavaliacao_das_palavras`, `leituras`), então a isenção e a recusa leem a linha do mesmo jeito. As regras R-NEUTRO, R-CUSTO, R-VERIFY e M14 estão cumpridas. O único achado é recomendado (A1) e não devolve a entrega. Nenhuma classe se repetiu neste pedido, por isso não gravei linha AR. Segurança e QA rodam em paralelo, cada um com o seu parecer.
