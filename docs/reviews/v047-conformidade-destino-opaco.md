---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 74b42c69d7c1fd98980986104f7e3733dbbbdd5b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.335)

Revalidação por delta do head 74b42c69, a volta da E1.334 sobre a A13 e a A14 da segurança E1.332 (lote B). Revisou uma instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (rc 0), intervalo `e34924b4..74b42c69`, domínio de código e testes. Em `hooks/conformidade.py`, o delta muda duas guardas. A `corpos_conhecidos` (:556) passa a recusar também o corpo expandido de heredoc com `PADRAO_QUE_ATRIBUI` de qualquer nome (A13), e a `valores_da_variavel` (:688) devolve `None` quando a linha tem `${nome:=v}` ou `${nome=v}`, com ou sem índice, para o nome do destino (A14). O resto do delta: 8 fixtures `opaco-u4-*` (6 que recusam, com S42 e S43, e 2 que liberam: `${x:-y}` no corpo e `${x:-a}` na linha), o piso do `opaco-u4` sobe de 173 para 181, a spec nova `tests/mutantes/v047-destino-opaco-23.json` (O153 e O154), o `de` do O150 ajustado à linha nova, `docs/hooks.md` e o fragmento do changelog. Os commits de merge (`d7cc9bbd`, `85723cef`, `1b699d74`) só trazem pareceres.

Verificadores: `tests/test_hook_destino_opaco.py HookDestinoOpaco.test_fixtures_opaco_u4` dá OK no 74b42c69, com 181 fixtures. `bin/forge-mutante --processos 1 tests/mutantes/v047-destino-opaco-23.json`: O153 (:556) e O154 (:688) morreram. A `-22` rodou de novo pelo `de` que mudou: O149 a O152 morreram. A suíte completa fica com o CI do PR, que ainda não foi aberto.

A A13 fecha, e a A14 fecha na forma direta. A correção segue a mínima que a segurança propôs: reusa a `PADRAO_QUE_ATRIBUI` no corpo, sem duplicar a busca. Pela mesma máquina do `tests/test_hooks.py`, sondei 12 entradas. Recusam com rc 2: `$\`+quebra+`{d:=…}` na linha e no corpo, `"${d:=…}"` entre aspas, `${x:-${d:=…}}` aninhado, `<<-E` com tab, `cp x "$d"` depois do corpo, heredoc dentro de `x=$(…)`, `&&` no lugar de `;` e `${d:=.g""it}` com resto `/config`. Liberam com rc 0: `echo a > "$d"` sem atribuição (variável do ambiente, como antes), `cat <<E⏎${HOME}⏎E` com `"$(mktemp)"` e `: ${x:-a}; echo a > "$x"`. O falso positivo novo (corpo de heredoc sem aspas com `${x:=v}` junto de um destino opaco) falha fechado e está em `docs/hooks.md`.

Antes do envio, o remoto trouxe a revalidação da segurança E1.336 no mesmo 74b42c69 (merge só de parecer, código igual), com a A15: a busca do prefixo nascido na linha (:693), na mesma função da A14, não conta `${d:=v}`. Refiz a S44 na mesma máquina e ela dá rc 0; `d=.gi; cp x "$d"t` dá rc 2. A A14 fechou só na forma direta; o achado A1 cita a A15 sem refazê-la.

## Achados
- A1 (bloqueante) hooks/conformidade.py:693 · A A14 fechou só a busca de :688; a do prefixo nascido na linha ainda pula `${d:=v}`, e `: ${d:=.gi}; cp x "$d"t` dá rc 0 (A15 da segurança E1.336, S44). Conte `${prefixo:=` e `${prefixo=` como nascimento, com fixture e mutante (R-CONFORMIDADE)

## Sondas
- S1 · : ${d:=.gi}; cp x "$d"t · espera: 2 · obtido: 0
- S2 · : ${d:=.gi}; cp -rT ev "$d"t · espera: 2 · obtido: 0

## Parecer
Reprovado no 74b42c69. As duas guardas da volta fecham as formas diretas da A13 (S42) e da A14 (S43), cada uma com fixture do ramo de falha e mutante que morre. Mas a mesma atribuição por expansão ainda escapa pela busca vizinha do prefixo (A1, a A15 da segurança). A volta corrige :693 e varre as outras buscas por nome da função.
