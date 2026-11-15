---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: e34924b4e6d18a37f1454420d1bfc759c787576d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.331)

Revalidação por delta do head e34924b4, a volta da E1.330 sobre o A5 do review E1.327 (o corpo de heredoc), o A12 da segurança E1.328 e o A5 do QA E1.329. Revisou uma instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (rc 0), intervalo `000cd0c8..e34924b4`, domínio de código e testes. Em `hooks/conformidade.py`, o delta traz a `expansao_conhecida` (:537), com as três buscas de texto que saíram da `linha_conhecida` (`CONTEXTO_ARITMETICO`, `PADRAO_QUE_ATRIBUI` com `NOME_INOFENSIVO` e `EXPANSAO_QUE_ESCONDE`), e a `corpos_conhecidos` (:551), que aplica essas buscas ao corpo expandido (`expandir_heredoc`) de todo heredoc sem `h.literal`. Traz também a marca `corpo_desconhecido` (:1131), gravada em `conferir_linha` (:1721) e salva e restaurada por nível (:1677), e o `valor_calculado` (:1431), que não libera com a marca. Fora disso: a `textos_do_valor` passa a usar `juntar_continuacoes` (:1385, A4 do QA E1.329, que também resolve o A6 recomendado do E1.327), 14 fixtures `opaco-u4-h-*`, o piso do `opaco-u4` sobe de 159 para 173, a spec `tests/mutantes/v047-destino-opaco-22.json` (O149 a O152), `docs/hooks.md` e o fragmento do changelog.

Verificadores: `tests/test_hook_destino_opaco.py HookDestinoOpaco.test_fixtures_opaco_u4` dá OK no e34924b4, com 173 fixtures. `bin/forge-mutante --processos 1 tests/mutantes/v047-destino-opaco-22.json`: O149, O150, O151 e O152 morreram. `bin/forge-mutante --cobertura --base 000cd0c8` mostra as quatro guardas novas cobertas (:555, :564, :1431, :1721). A suíte completa fica com o CI do PR, que ainda não foi aberto.

O A5 do E1.327 fecha. As sondas S14 a S16 do parecer anterior viraram as fixtures `-h-s14`, `-h-s15`, `-h-s16-dois-pontos` e `-h-s16-tab`, que recusam, e a S17 segue recusando. Pela mesma máquina do `tests/test_hooks.py`, sondei também 14 entradas. Recusam, como esperado: `cp config "$(date)"` e `cp config "$(mktemp)"` depois de um corpo com `$[PATH=5]` (o caminho do U3); o heredoc dentro de um `$(…)` (`x=$(cat <<E … E); echo a > "$(date)"`); o segundo de dois heredocs (`<<A <<B`); o heredoc dentro de `{ … }`; e, no corpo, `${PATH=5}` sem dois-pontos, `${x@P}`, `${a[$((PATH=5))]}`, `${#a[PATH=5]}` e `$[ PATH=5 ]` com `"$(date +%F)"`. Passam: `<<E""` e `<<\E`, cujo corpo o bash não expande; `"$(pwd)/x"`, que tem resto e cujo `pwd` é builtin; e o heredoc sem fim e sem destino opaco. A marca é restaurada por nível como o `texto_da_linha`. O falso positivo novo (corpo sem aspas que atribui, junto de um destino opaco) falha fechado e está em `docs/hooks.md`.

## Achados

## Sondas

## Parecer
Aprovado no e34924b4. A volta aplica ao corpo de heredoc sem aspas no delimitador as mesmas três buscas da linha, pela função extraída, sem duplicar código. O corpo literal (`<<'E'`, `<<"E"`, `<<\E`, `<<E""`) fica de fora, como no bash. Cada guarda nova tem fixture do ramo de falha e mutante que morre. Não há achado novo.
