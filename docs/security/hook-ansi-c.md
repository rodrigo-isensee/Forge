---
tipo: revisao-seguranca
contrato: 1
pedido: hook-ansi-c
branch: melhoria/hook-ansi-c
commit: f3d1fd092979c2bb8eb0af09db16e33909f94154
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-27
---
# Review de segurança: hook-ansi-c

Escopo: a volta 1, revalidada por delta sobre o parecer anterior (`2fe8e1c`, head `3707e28`). O `forge-check delta` lista `3707e28..f3d1fd0`: `hooks/_comum.py:963-965,983-997,1092-1093`, `tests/test_hook_ansi_c.py`, `tests/mutantes/hook-ansi-c.json:58-90`, `bin/forge-testes:71,101`, `tests/test_testes_tocados.py:61` e `changelog.d/hook-ansi-c.md:2`. O delta toca um controle do Forge (o leitor comum dos hooks), então reli a função nova inteira e o ponto em que ela é chamada. Método: sondas diferenciais com o hook real em três pontas (base `770c19a`, head anterior `3707e28` e head `f3d1fd0`), com o bash real como oráculo numa pasta temporária com `.env` falso (`$TMPDIR/security-engineer-hook-ansi-c/saida-5.txt` e `saida-6.txt`), mais `tests.test_hook_ansi_c` (9 testes OK).

## Gatilhos
Controle do Forge (`hooks/`): o leitor comum (`palavras_do_texto` e `leituras`), lido pelos hooks `conformidade`, `parecer` e `pesado`.

## Achados

## Detalhe dos achados
**A1 do parecer anterior: fechado, pela opção (b).** `_ansi_com_aspa_escapada` (`hooks/_comum.py:983`) lê o conteúdo do `\$'…'` como o bash lê `$'…'`: o `\` consome o caractere seguinte, e a função para no primeiro `'` sem escape. Ela é chamada só fora de aspas, em `hooks/_comum.py:1092`, e por isso cobre o texto interno que o `aninhado` relê (o valor do `shlex` mantém o `\$` entre aspas duplas). Resultado das sondas, na ordem base/3707e28/f3d1fd0:
- Saíam 0/0 e agora saem 2: `bash -c "echo \$'it\\'s'; cat .env \\'"` (o bash lê o `.env`), a mesma linha com `rm -rf .git` (o bash apaga o `.git`), `sh -c` e `eval` com o mesmo texto, `bash -lc`, `bash -e -c`, `env GH_REPO=x bash -c`, as linhas com `true &&` antes e `&& true` depois, `x=\$'a\\'b'`, a quebra de linha no lugar do `;`, o aninhamento duplo (`bash -c "bash -c \"…\""`, `eval "bash -c \"…\""`, `bash -c "eval \"…\""`) e `echo $(bash -c "…")`. O papel `security-engineer` dá o mesmo resultado.
- Seguem 2: as grafias que a volta anterior já fechava (aspas simples, `$'…'` no argumento e `$'` cru dentro de aspas duplas).
- O `parecer` já recusava a variante com `gh pr merge` por `bash -c` e por `eval` (2/2/2).
- O `pesado` não muda (0/0/0). É o A2, abaixo.

Controles legítimos, iguais nas três pontas (0/0/0): `bash -c "echo \$HOME"`, `bash -c "echo \$'a\\nb'"`, `bash -c "echo \$'a\\\\'"`, `eval "echo \$'\\x41'"`, `bash -c "git status"`, `bash -c "echo \$'a'; echo \"it's\""`, `grep -n "\$'" README.md`, `echo \$'a'`, `bash -c 'echo $HOME'`, `echo $'a\nb'`, `git status`, `cat README.md`, `gh pr view 1`. `bash -c "echo \$'it\\'s'"`, sem segundo comando, já saía 2 na base. Os testes `test_o_nivel_aninhado_entre_aspas_duplas_sai_2` (as quatro variantes) e `test_controles_do_nivel_aninhado_saem_0` levam a dimensão nova da matriz (argumento de `bash -c`/`sh -c`/`eval` entre aspas duplas). Os mutantes A6 (detecção desligada), A7 (qualquer barra vale) e A8 (sem pular o caractere escapado) guardam a função e o ponto de chamada. A recusa a mais existe, mas é estreita: só `\$'…'` fora de aspas com `\'` antes do fecho, grafia em que o hook e o shell de dentro discordam.

**A2 do parecer anterior (`hooks/pesado.py:90`): no cartão.** Está no `KANBAN.md` como `PESADO-ANSI-C` (dono `forge:tech-lead`, depois do HOOK-ANSI-C), pela DECISÃO TÉCNICA de 2026-10-27 17:56. É risco de recurso (`R-TETO`), não de segurança, e a ADR 0013 aceita liberar na dúvida. A sonda aninhada do `pesado` dá 0 nas três pontas.

**Recomendação nova R3 (fora da classe, já existia na base): aspas duplas dentro de `"$( … )"`.** Evidência: `hooks/conformidade.py:893-897`. A palavra `"$(bash -c "cat .env")"` chega como o valor do `shlex`, `$(bash -c cat .env)`, e as aspas internas se perdem. O `bash -c` relido recebe só `cat`, e o `.env` vira argumento posicional. Sondas: `echo "$(bash -c "cat .env")"` sai 0 na base e na head, e o bash lê o `.env`. A grafia com aspas simples (`"$(bash -c 'cat .env')"`) sai 2. A variante ANSI-C dentro dela também sai 0/0/0, mas só porque herda essa falha, já que o `cat .env` puro passa. Caminho de ataque: um agente de papel `dev`, por erro ou por instrução injetada num arquivo que leu, lê os segredos do `.env`. Severidade: alta. Não é desta classe nem deste arquivo (`hooks/conformidade.py` está com o HOOK-CD), e a regra é uma classe de comportamento por PR em `hooks/`. Proposta: um cartão depois do HOOK-CD, em que o nível `so_substituicoes` relê o texto cru da substituição em vez do valor do `shlex`, ou falha fechado com aspas duplas dentro de `$(` entre aspas duplas. Esforço: P/M. Dono: `tech-lead`.

**Recomendação nova R4 (fora da classe, já existia na base): o nome do alvo montado por variável.** Evidência: `hooks/conformidade.py:100` (`ARQUIVO_ENV` casa o nome literal). `D=e; cat .${D}nv` e `D=.env; bash -c "cat $D"` saem 0 na base e na head. Mesmo caminho de ataque e mesma severidade (alta). É uma classe própria (expansão de variável no alvo), e não a citação ANSI-C. Proposta: um cartão para recusar `$`/`${` em palavra que vira alvo de leitura, ou para expandir as atribuições da própria linha. Esforço: M. Dono: `tech-lead`. As duas recomendações vão ao Jarvis para virar cartões. Elas não devolvem esta entrega: nenhuma é regressão, e a base sai igual.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: só leitura e sondas locais com Python e bash, sem rede. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` não estão no PATH (lacuna registrada). O delta não toca dependência, workflow nem segredo. Em `bin/`, muda só a lista do mapa de testes. PA-7 (`docs/engineering/achados-recorrentes.md`): sem itens.
