---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: c7a8ff72300365c64aa699e2301c2ca0c9e1b982
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.335, E1.339, E1.343)

## Rodada no 74b42c69 (E1.335, reprovado)
Revalidação por delta do head 74b42c69, a volta da E1.334 sobre a A13 e a A14 da segurança E1.332 (lote B). Revisou uma instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (rc 0), intervalo `e34924b4..74b42c69`, domínio de código e testes. Em `hooks/conformidade.py`, o delta muda duas guardas. A `corpos_conhecidos` (:556) passa a recusar também o corpo expandido de heredoc com `PADRAO_QUE_ATRIBUI` de qualquer nome (A13), e a `valores_da_variavel` (:688) devolve `None` quando a linha tem `${nome:=v}` ou `${nome=v}`, com ou sem índice, para o nome do destino (A14). O resto do delta: 8 fixtures `opaco-u4-*` (6 que recusam, com S42 e S43, e 2 que liberam: `${x:-y}` no corpo e `${x:-a}` na linha), o piso do `opaco-u4` sobe de 173 para 181, a spec nova `tests/mutantes/v047-destino-opaco-23.json` (O153 e O154), o `de` do O150 ajustado à linha nova, `docs/hooks.md` e o fragmento do changelog. Os commits de merge (`d7cc9bbd`, `85723cef`, `1b699d74`) só trazem pareceres.

Verificadores: `tests/test_hook_destino_opaco.py HookDestinoOpaco.test_fixtures_opaco_u4` dá OK no 74b42c69, com 181 fixtures. `bin/forge-mutante --processos 1 tests/mutantes/v047-destino-opaco-23.json`: O153 (:556) e O154 (:688) morreram. A `-22` rodou de novo pelo `de` que mudou: O149 a O152 morreram. A suíte completa fica com o CI do PR, que ainda não foi aberto.

A A13 fecha, e a A14 fecha na forma direta. A correção segue a mínima que a segurança propôs: reusa a `PADRAO_QUE_ATRIBUI` no corpo, sem duplicar a busca. Pela mesma máquina do `tests/test_hooks.py`, sondei 12 entradas. Recusam com rc 2: `$\`+quebra+`{d:=…}` na linha e no corpo, `"${d:=…}"` entre aspas, `${x:-${d:=…}}` aninhado, `<<-E` com tab, `cp x "$d"` depois do corpo, heredoc dentro de `x=$(…)`, `&&` no lugar de `;` e `${d:=.g""it}` com resto `/config`. Liberam com rc 0: `echo a > "$d"` sem atribuição (variável do ambiente, como antes), `cat <<E⏎${HOME}⏎E` com `"$(mktemp)"` e `: ${x:-a}; echo a > "$x"`. O falso positivo novo (corpo de heredoc sem aspas com `${x:=v}` junto de um destino opaco) falha fechado e está em `docs/hooks.md`.

Antes do envio, o remoto trouxe a revalidação da segurança E1.336 no mesmo 74b42c69 (merge só de parecer, código igual), com a A15: a busca do prefixo nascido na linha (:693), na mesma função da A14, não conta `${d:=v}`. Refiz a S44 na mesma máquina e ela dá rc 0; `d=.gi; cp x "$d"t` dá rc 2. A A14 fechou só na forma direta; o achado A1 cita a A15 sem refazê-la.

## Revalidação por delta 74b42c69..c3cde09f (E1.339, volta da A15; instância que não fez a entrega)
Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (rc 0), intervalo `74b42c69..c3cde09f`, domínio de código e testes: `hooks/conformidade.py`, `docs/hooks.md`, 7 fixtures `opaco-u4-*` novas, `tests/test_hook_destino_opaco.py` (piso 181 para 188) e a spec `tests/mutantes/v047-destino-opaco-23.json` (O154 reescrito, O155 e O156 novos).

A correção é a mínima que a segurança propôs: a regex da A14 vira a função `atribui_por_expansao` (:680), usada pelo nome (:693) e por cada prefixo (:698), sem duplicar a busca. Só acrescenta recusa (R-CONFORMIDADE). Fixtures do ramo de falha: S44 a S47 da segurança, `cp x` simples e `${d[0]:=…}`; do ramo livre, `: ${d:-docs}; echo a > "$d"`. `docs/hooks.md` acompanha (A15 citada pelo ID).

Varri as outras buscas por nome com `(?<![\w${{])` (A15, "varra também"): `textos_do_valor` (:1401-1402) e `corpo_positivo` (:1470-1471) também pulam `${d:=`, mas nelas a omissão só deixa de liberar (o U4 em `valores_da_variavel` recusa depois); sem achado.

Verificadores: `bin/forge-mutante --processos 1 tests/mutantes/v047-destino-opaco-23.json`, `rev=c3cde09fdec3`: O153 (:556), O154 (:693), O155 (:698) e O156 (:682) `morreu`, rc 0. `bin/forge-mutante --cobertura --base 74b42c69…`: as condições 682, 693 e 698 `coberta`, nenhuma sem mutante. A suíte completa fica com o CI do PR, que ainda não existe (brief sem PR).

Sondas (aspas simples; hook real pela máquina do `tests/test_hooks.py`, fixture `opaco-u4-prefixo-dois-pontos-igual-cp-simples-bloqueia` com o comando trocado): recusam com rc 2 `: ${d:=.gi}; cp x "$d"t`, `: ${d=.gi}; echo a > "$d"t`, `: ${d[0]=.gi}; echo a > "$d"t`, `: "${d:=.gi}"; echo a > "$d"t`, `: ${d:=.g}; echo a > "$d"it`, `: ${do:=.gi}; echo a > "$do"t`, `: ${d:=.gi}; echo a > "${d}t"`, `: ${d:=.gi} ${e:=t}; echo a > "$d$e"` e `true ${d:=.gi} && cp -rT ev "$d"t`. Liberam com rc 0, sem atribuir: `: ${d:-docs}; echo a > "$d"t`, `: ${d:+.gi}; …`, `: ${d:?.gi}; …` e `echo a > "$HOME"t`.

Pareceres irmãos no remoto, lidos antes do veredito (a primeira tentativa de envio voltou com o remoto à frente): segurança E1.340 (915fa1a7) e QA E1.341 (c0266d0f), os dois no c3cde09f e reprovados. A15 e A16 do QA anterior fechados; abrem a A16 da segurança e o A17 do QA, a mesma falha: o prefixo colado que o próprio bash grava (`"$_"t` lido `$_t`) não passa por `VARIAVEIS_DO_BASH` no laço de :698. Refiz na mesma máquina: `: .gi; cp x "$_"t` e `: .gi; cp -rT ev "$_"t` dão rc 0 no c3cde09f. Minha varredura de sondas não testou variável do bash como prefixo; o achado A2 cita a A16 sem refazer a análise. A11 e A5 da segurança seguem recomendados e fora do delta.

A1 (A15 da segurança, A16 do QA): fechado em 384d16ef, com fixtures e mutantes O155 e O156 em 0378772f; S1 e S2 abaixo davam rc 0 no 74b42c69 e dão rc 2 no c3cde09f.

Achado da rodada no 74b42c69, agora fechado: A1 (bloqueante) hooks/conformidade.py:693 · A A14 fechou só a busca de :688; a do prefixo nascido na linha ainda pula `${d:=v}` (S1: `: ${d:=.gi}; cp x "$d"t`, S2: `: ${d:=.gi}; cp -rT ev "$d"t`, rc 0). Fechado acima.

Achado e sondas da rodada no c3cde09f (fechados na E1.343, abaixo):
A2 (bloqueante, fechado) hooks/conformidade.py:698 · O laço de prefixos não confere `VARIAVEIS_DO_BASH`: `: .gi; cp x "$_"t` dá rc 0 (`$_t`, prefixo `_` gravado pelo bash). Recuse o prefixo da lista, com fixture e mutante (A16 da segurança E1.340, A17 do QA; R-CONFORMIDADE)

S3 (da rodada) · : .gi; cp x "$_"t · espera: 2 · obtido: 0
S4 (da rodada) · : .gi; cp -rT ev "$_"t · espera: 2 · obtido: 0

Veredito da rodada: reprovado no c3cde09f (R-REVIEW). A volta fecha a A15 (e o A1 deste parecer) na busca do prefixo, com função única para o nome e o prefixo, fixtures dos dois ramos, mutante por guarda que morre e cobertura sem lacuna. Mas o mesmo laço de :698 deixa passar o prefixo que o bash grava (A2, a A16 da segurança). A volta aplica ao prefixo a recusa de `VARIAVEIS_DO_BASH` que :690 já aplica ao nome inteiro (o `GIT_` não precisa: prefixo com `GIT_` faz o nome inteiro começar com `GIT_`), com fixtures S48 a S51 da segurança e mutante.

## Revalidação por delta c3cde09f..c22624c5 (E1.343, volta da A16; instância que não fez a entrega)
Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (rc 0), intervalo `c3cde09f..c22624c5`, domínio de código e testes: `hooks/conformidade.py`, 5 fixtures `opaco-u4-*` novas (S48 a S51 da segurança, que recusam, e `"$HOME"t`, que libera), `tests/test_hook_destino_opaco.py` (piso 188 para 193), a spec `-23` (`de` do O154 e do O155 ajustados) e a spec nova `-24` (O157 e O158). Os merges `0d8c4051`, `c626bb21` e `0012f436` e o `491fb745` só trazem pareceres.

A correção é a mínima que o A2 pediu e reusa o existente: as três recusas do nome inteiro (lista do bash, `GIT_` ou nome solto na linha, `${nome:=v}`) viram a função `nasce_fora_do_ambiente` (:685), chamada pelo nome (:699) e por cada prefixo (:704); o prefixo atribuído (`d=`) segue numa busca própria. Só acrescenta recusa (R-CONFORMIDADE): a lookahead do prefixo passa de `(?![\w])` para `(?![\w=])` com a busca `(?<![\w$])d=` ao lado, o que cobre o mesmo conjunto e mais `${d=`.

Verificadores: `tests/test_hook_destino_opaco.py HookDestinoOpaco.test_fixtures_opaco_u4` OK (193 fixtures, 15 s). `bin/forge-mutante --processos 1`: na `-24`, O157 (:699) e O158 (:704) `morreu`; na `-23`, O153 (:556), O154 (:692), O155 (:704) e O156 (:682) `morreu`. `bin/forge-mutante --cobertura --base c3cde09f`: 699 e 704 `coberta`, nenhuma sem mutante; rc 0. A suíte completa fica com o CI do PR, que ainda não existe (brief sem PR).

Sondas (aspas simples; hook real pela máquina do `tests/test_hooks.py`, fixture S51 com o comando trocado). As da A16 e do A17 do QA recusam com rc 2: `': .gi; cp x "$_"t'`, `': .gi; cp -rT ev "$_"t'`, `': .gi; echo a > "$_"t'`. Formas rebuscadas da mesma família também recusam: `"$_"'t'`, `"$_""t"`, `"$_"\t`, `"${_}"t`, `"$_${e:-t}"`, `e=t; … "$_$e"`, `': .g; cp x "$_"i"t"'`, `"$_"$'t'`, `` "$_"`echo t` ``, `"$_"t/../.git/config`, `read <<< .gi; cp x "$REPLY"t`, `[[ .gi =~ .* ]]; cp x "$BASH_REMATCH"t`, `set -- .gi; cp x "$1"t`, `x=(.gi); cp x "${x[0]}"t`, e as da A15 (`: ${d:=.gi}; cp x "$d"t`, `d=.gi; cp x "$d"t`). Sem regressão no lado livre, rc 0: `echo a > "$HOME"t`, `echo a > "$HOME"`, `echo a > "$TMPDIR"/x`, `cp x "$PWD"/y`.

Pareceres irmãos no remoto, lidos antes do veredito (dois envios voltaram com o remoto à frente): QA E1.345 (50725bfd) aprovado no c22624c5, Achados vazio; segurança E1.344 (d1febc7d) aprovada no c22624c5, A16 fechada. A A17 do QA e a A16 da segurança são este A2. Os recomendados da segurança (A5, A11, A17 a A19) já estão na develop f4b0c2ae e viram cartão, fora do delta (ordem do dono de 15/11).

A2 (A16 da segurança, A17 do QA): fechado em c22624c5; S3 e S4 davam rc 0 no c3cde09f e dão rc 2 agora. Achados das rodadas anteriores deste parecer (A1, A2) todos fechados; nenhuma fuga nova achada.

## Revalidação por delta c22624c5..081473ac (E2.129, junção do lote B com a develop bf475209; instância que não fez a entrega)
Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (rc 0), intervalo `c22624c5..081473ac`, sem o que veio da base; no domínio só os dois arquivos em conflito, `bin/forge-testes` e `tests/test_testes_tocados.py`.

Resolução conferida por `git show --remerge-diff 081473ac`: em `bin/forge-testes` o conflito era só a tupla `REAPROVEITAM_O_LOTE`, e o resultado é a união dos dois lados (`test_hook_destino_opaco` da branch, `test_hook_erro_libera` da develop). `git diff bf475209 081473ac` nos dois arquivos é exatamente o diff do lado da branch sobre a base comum f4b0c2ae: `FORGE_CHECK` e a regra `hooks/.*` ganham os dois módulos da A9, `REAPROVEITAM_O_LOTE` ganha `test_hook_destino_opaco`, e o teste ganha `sem_oraculos` e a contagem. Nenhuma linha de `--texto`, `TESTES_DE_TEXTO` ou guarda da develop foi alterada; não há guarda nova no delta, então não há mutante a declarar.

Contagem: `FORGE_CHECK` tem 76 nomes na base, 79 na develop e 81 na junção, sem repetição. O `planejar(["bin/forge-check"])` dá 84 no bf475209 e 86 no 081473ac, sem oráculos. A develop asserta 83 e está vermelha nesse teste (CI 43771793322: `AssertionError: 84 != 83`); a junção asserta 86, o valor certo. `tests.test_testes_tocados` inteiro no 081473ac, com ambiente limpo: 151 testes, OK (skipped=1). A suíte completa fica com o CI do PR.

Conclusão: a resolução não muda comportamento além da soma dos dois lados; a contagem 86 corrige de quebra o vermelho da develop.

## Revalidação por delta 081473ac..81c50342 (E2.504, junção com a develop 86ac0fcb; instância que não fez a entrega)
Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (rc 0), intervalo `081473ac..81c50342`, sem o que veio da base; no domínio `bin/forge-testes`, `tests/test_testes_tocados.py`, `hooks/conformidade.py`, `docs/hooks.md`, `docs/hooks-fixtures.md` e `docs/engineering/achados-recorrentes.md`.

`git show --remerge-diff 81c50342` sai vazio: a junção não teve conflito nem edição à mão. O diff de `hooks/conformidade.py` contra a develop 86ac0fcb, antes (081473ac) e agora, difere só no trecho `CITA_A_MARCA` que o revert do #576 trouxe na develop; as linhas da A9 e da A10 são as mesmas já aprovadas. Sem mudança de comportamento da branch.

Verificador: `python3 -m unittest tests.test_testes_tocados` no 81c50342: 161 testes, OK (skipped=1, o `/proc` de outro namespace). `forge-check docs` rc 0. A suíte completa fica com o CI do PR.

## Revalidação por delta 81c50342..c7a8ff72 (E2.612, junção com a develop e oráculo ajustado; instância que não fez a entrega)
Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (rc 0), intervalo `81c50342..c7a8ff72`, sem o que veio da base; no domínio `bin/forge-testes`, `tests/test_oraculo_v047.py` e `tests/test_testes_tocados.py`. Os mutantes G12 a G14 e G20 (`v046-conformidade-caminho-git-2` e `-4`) são teste do QA aprovado e ficam dispensados; não os alterei.

Condição do dono (17/11): `git diff 730843a9 HEAD -- tests/test_oraculo_v047.py` tem 3 mudanças, 7 linhas a mais e 4 a menos. (1) `from ambiente_git import sem_manutencao` com o `sys.path.insert`; (2) `git()` e `bases_do_git()` passam o `env` por `sem_manutencao(...)`, o padrão de ambiente do git; (3) a chave do arquivo de exemplo `README.md` vira `LEIAME.md` em `ARQUIVOS` (a única ocorrência no arquivo). Asserções: 15 linhas de `assert*`, `fail`, `subTest` e `def test_` em 730843a9 e 15 no HEAD; só `assert*`, 10 e 10. Nenhuma checagem saiu, nenhum limite (`TETO_DE_EXECUCOES`, `PRAZO_LARGO_S`) mudou e nenhum teste foi pulado. Conclusão: o oráculo só mudou no padrão de ambiente do git e no nome do arquivo de exemplo, e nada ficou mais fraco.

`bin/forge-testes`: o delta só soma `test_pre_push_patch` ao mapa `hooks/.*` e a regra do patch; os quatro testes que a resolução do conflito devia manter seguem na tupla (`test_hook_destino_opaco`, `test_conformidade_opaco`, `test_pr_hook_rapido` e o novo). `tests/test_testes_tocados.py`: `AMBIENTE` sem o `GIT_*` herdado e um teste novo do mapa.

Verificador: `python3 -m unittest tests.test_oraculo_v047 tests.test_testes_tocados` (sem `-I`) no c7a8ff72: 165 testes, OK (skipped=1, o `/proc` de outro namespace). A suíte completa fica com o CI.

## Achados

## Sondas

## Parecer
Aprovado no 81c50342 (R-REVIEW), por delta: junção limpa com a develop 86ac0fcb, código da branch igual. Antes: aprovado no 081473ac. A junção com a develop bf475209 resolve os conflitos de `bin/forge-testes` e `tests/test_testes_tocados.py` pela união dos dois lados, sem mudar comportamento; a contagem 86 confere com o plano real. Aprovação anterior no c22624c5 mantida; a suíte completa fica com o CI do PR.

Revalidado no c7a8ff72 (R-REVIEW), por delta: aprovado. Oráculo da v047 conferido contra o 730843a9 (condição do dono): só ambiente do git e nome do arquivo de exemplo, mesmas asserções. Sem código de `hooks/` no delta; QA e segurança não precisam revalidar (o delta não toca código que eles aprovaram).
