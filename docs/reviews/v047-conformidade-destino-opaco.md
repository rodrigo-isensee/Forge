---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: c3cde09fdec39e3d8bed6b8d0e0113216189a7ca
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.335, E1.339)

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

Pareceres irmãos no remoto, lidos antes do veredito: segurança e QA ainda no 74b42c69 (A15 e A16 bloqueantes, a mesma classe que este delta fecha; A11 e A5 recomendados, fora do delta). A revalidação deles no c3cde09f corre em paralelo; não os refaço.

A1 (A15 da segurança, A16 do QA): fechado em 384d16ef, com fixtures e mutantes O155 e O156 em 0378772f; S1 e S2 abaixo davam rc 0 no 74b42c69 e dão rc 2 no c3cde09f.

Achado da rodada no 74b42c69, agora fechado: A1 (bloqueante) hooks/conformidade.py:693 · A A14 fechou só a busca de :688; a do prefixo nascido na linha ainda pula `${d:=v}` (S1: `: ${d:=.gi}; cp x "$d"t`, S2: `: ${d:=.gi}; cp -rT ev "$d"t`, rc 0). Fechado acima.

## Achados

## Sondas

## Parecer
Aprovado no c3cde09f (R-REVIEW). A volta fecha a A15 (e o A1 deste parecer) na busca do prefixo, com função única para o nome e o prefixo, fixtures dos dois ramos, mutante por guarda que morre e cobertura sem lacuna. Nenhum achado aberto no delta; a suíte inteira fica com o CI do PR.
