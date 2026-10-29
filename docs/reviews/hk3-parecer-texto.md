---
tipo: review
contrato: 1
pedido: hk3-parecer-texto
branch: melhoria/hk3-parecer-texto
commit: cf6bf0adc637685b8f4773e5f9ea2f59c373cbf1
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: o hook parecer não recusa a chamada em que merge, pull ou gh pr só aparece no texto (HK3-PARECER, PR B, E2)

## Escopo
Revalidação por delta (volta 1) do parecer `a85dcfa`, sobre o head `cf6bf0a`.

**Delta lido:** `7b2a225..cf6bf0a`. Nele estão:
- os commits da volta `0c48474`, `2a2cc43`, `f3705f6` e `9663747`:
  - `hooks/parecer.py`, com +26 e -3 linhas;
  - 10 fixtures `texto-*` novas;
  - a spec nova `tests/mutantes/hk3-parecer-texto-4.json` (V1 a V12);
  - T4 e T13 reapontados na spec `hk3-parecer-texto.json`;
  - a linha de `docs/hooks.md`;
- o merge da `develop` `f3f63f9` (T6T3-MENSAGEM, #367). Ele não muda `hooks/`, `docs/hooks.md` nem `tests/hooks/`: `git diff --stat 9663747 cf6bf0a -- hooks/ docs/hooks.md tests/hooks/` sai vazio, e o `f3f63f9` já está na `origin/develop`.

**Já lido** no parecer `a85dcfa`: o resto do diff `d14a713...7b2a225`, isto é, `MERGE`, `SO_CAT`, `so_le_ou_espera`, as 57 fixtures da primeira entrega e as specs `-2` e `-3`. Nada mudou nesse trecho.

## Requisitos da volta (decisões de 2026-10-29 12:34 e 13:44; review a85dcfa A1; segurança 7b2a225 A1 e A3)
- **A1 do review, sh -c com shell que lê o stdin ou com `BASH_ENV=`.** Resolvido. O `e_shell_c_de_texto` devolve `False` em dois casos:
  - com `BASH_ENV=` no texto (`hooks/parecer.py:117`);
  - com qualquer palavra de shell que não seja a reavaliação `-c` (`:123`).

  Nas sondas, `sh -c 'echo git merge …' | sh`, `| dash`, `| zsh`, `| bash -s` e `BASH_ENV=e.sh bash -c 'sleep 1'` passaram a recusar (rc 2), como a base. Fixtures que cobrem: `texto-barra-sh-c-com-bash-env` e `texto-barra-sh-c-com-texto-enviado-a-shell-por-pipe`. Mutantes: V7 e V8. O que sobra está no A2, que é recomendado.
- **Isenção do cat só com o corte que o bash também faz (`heredocs_simples`, `:97`).** Esse era o A1 de segurança, e está resolvido. Todo `<<` tem de ser `HEREDOC_SIMPLES`, e as linhas de comando não podem ter `\` nem `$`. A fila de terminadores segue a ordem do bash, e o `<<-` tira só tabulação.

  Nas sondas, todas as formas do A1 de segurança recusam: `<<$'EOF'`, `<<$"EOF"`, `<<$'E\x4fF'`, `<<EOF\` com quebra de linha, `<<\` com quebra de linha, `<<-EOF` com `\` no corpo e `<<<`. Também recusam a continuação depois do delimitador (`cat <<EOF \` seguido de `; git merge`), `cat \` com `<<EOF` na linha seguinte, as misturas `<<A <<$'B'` e `<<'A' <<B\`, e `<< EOF`, `3<<EOF`, `<<1` e `<<ÉOF`, todos seguidos de um merge real.

  Seguem passando, e o bash confirma que é só texto: `cat <<EOF`/`<<"EOF"`/`<<'EOF'` com o merge no corpo, `<<A <<B` com os terminadores em ordem trocada, o terminador `EOF\r` e `<<- EOF` com espaço antes do terminador.

  Fixtures: sete `texto-barra-heredoc-*` novas e `texto-passa-heredoc-so-lido-com-cifrao-no-corpo`. Mutantes: V1, V5, V6 e V11.
- **`SED_LE` ancorado no início da palavra (`:41`).** Esse era o A3 de segurança, e está resolvido. `xsed -n 1p f` e `/x/sed -n 1p f` não viram mais `cat`. O `sed -n 1p f` seguido de `cat <<'EOF'` continua passando.
- **docs/hooks.md, limitação [B].** A linha registra três coisas:
  - a forma nova da isenção do cat;
  - o `sem shell que leia o stdin nem BASH_ENV=` do `sh -c`;
  - a limitação de `env`/`nice`/`timeout`/`xargs` antes do merge (A2 de segurança) e do `echo … | sh`, iguais à base.
- **Spec `-4` e os equivalentes declarados V2, V3, V4, V10 e V12.** A justificativa de cada um é que as outras condições, ou o `SO_CAT` sobre o texto já cortado, recusam o mesmo caso. Não refiz a mutação, que é do autor (V2). Conferi a afirmação por sonda: apliquei cada `de`→`para` numa cópia de `hooks/` e rodei 19 comandos (as formas do A1 de segurança, continuações, mistura de delimitadores, `xsed`, `$` na linha e os casos que passam). Nenhum mudou de veredito contra o original (`casos que diferem: 0`). V2, V3 e V4 são camadas redundantes de propósito, e a spec diz isso.

## Ferramentas (citadas, não refeitas)
- **Teto M14.** `git diff --numstat --no-renames origin/develop...cf6bf0a` dá 87 linhas de código e teste: `hooks/parecer.py` 70+8 e `tests/test_hooks_parecer_pasta.py` 9. Fica abaixo de 150. É um comportamento só, uma classe em `hooks/`, com corpus próprio. Os arquivos do T6T3 vieram pelo merge e já estão na `develop`.
- **Item do teste.** `python3 -m unittest tests.test_hooks_parecer_pasta` deu `Ran 2 tests in 7.335s OK`, com a carga de 1 minuto em 2,67. O corpus `texto-*` tem 68 fixtures, 14 delas de passa.
- **Changelog.** O fragmento `changelog.d/hk3-parecer-texto.md` segue presente. O `CHANGELOG.md` não foi tocado.

## Sondas
Comparei o hook da base `d14a713` com o de `cf6bf0a` num repositório temporário na `develop`, com `melhoria/x`. Cada forma que roda o merge foi conferida no bash real, com `echo` no lugar do merge.

Passam agora, onde a base recusava, e o bash executa o arquivo que o `sh -c` ou o `printf` gravou:
- `BASH_ENV+=e.sh bash -c 'sleep 1'`;
- `printf -v BASH_ENV e.sh; export BASH_ENV; bash -c …`;
- `export BASH_ENV+=e.sh; bash -c …`;
- `sh -c 'echo git merge …' > f; . ./f`, e o mesmo com `source f`.

O hook recusa `read`, `mapfile` e `declare -x BASH_ENV=`.

As cinco formas acima são a classe do A1 da rodada anterior. A base já deixa passar, com rc 0, as formas equivalentes sem o `sh -c`: `echo git merge … > f; . ./f`, `printf … > e.sh; sh e.sh`, `echo … | sh` e `BASH_ENV+=e.sh bash e.sh`. Por isso não há capacidade nova contra a base, e o achado fica como recomendado (A2), com o mesmo critério do A1.

A decisão de 13:44 pede `BASH_ENV=`, e o código cumpre o texto dela. Pela limitação [B] do ADR 0009, o hook barra em regra e não garante.

## Achados
- A2 (recomendado) hooks/parecer.py:117 · `BASH_ENV+=`, `printf -v BASH_ENV` + `export` e `export BASH_ENV+=` escapam do teste `"BASH_ENV=" in texto`. `. ./f` e `source f` depois de `sh -c '…' > f` não contam como shell (`:123`, `SHELLS_DA_REAVALIACAO`). As cinco formas rodam o merge e passam onde a base recusava. A base já deixa passar a forma sem o `sh -c`, então não há capacidade nova. Sugestão: tirar a isenção quando `BASH_ENV` aparece como palavra (`\bBASH_ENV\b`) e quando há `.` ou `source` na linha. Outra saída é registrar `source` e `+=` na limitação [B] de docs/hooks.md. Classe AR-10.

## AR (PA-7)
Conferi cada linha do `docs/engineering/achados-recorrentes.md`:
- AR-3 (lista negativa) não se aplica: as listas da isenção são positivas.
- AR-5 (python sem -I) não se aplica: não há python novo em caminho que decide.
- AR-6 (máscara do shell) não se aplica ao delta.
- AR-7 (`pasta-do-git-diferente-do-bash`) se repete no A1 de segurança de `7b2a225`, em que o hook cortava o terminador do heredoc diferente do bash. Atualizei a linha para vezes 3, última `hooks/parecer.py:587`.
- AR-10 (`texto-isento-executado-por-outro-caminho`) é linha nova. O texto que a isenção dá por inofensivo chega a um shell por outro caminho (pipe, `BASH_ENV`, `source`). É a classe do A1 de `a85dcfa`, que volta no A2 deste pedido.

## Parecer
**Aprovado.** A volta resolve o A1 do review e os achados A1 e A3 de segurança:
- a isenção do cat só vale quando o hook e o bash cortam o corpo no mesmo ponto;
- o `sh -c` deixa de ser isento com um shell que lê o stdin ou com `BASH_ENV=`;
- o `sed -n` só vira `cat` no início de uma palavra.

O merge da `develop` não toca `hooks/`. As regras R-NEUTRO, R-CUSTO, R-VERIFY e M14 estão cumpridas. O único achado é recomendado (A2), sem capacidade nova contra a base, e não devolve a entrega. Segurança e QA rodam em paralelo, cada um com o seu parecer.
