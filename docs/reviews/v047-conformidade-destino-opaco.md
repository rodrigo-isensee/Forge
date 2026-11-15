---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-conformidade-destino-opaco
commit: 000cd0c8a7f69497fd41b5f64c786ed9df5f5274
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 · CONFORMIDADE-A9-DESTINO-OPACO e CONFORMIDADE-A10-OPERADOR-COLADO (E1.327)

Revalidação por delta do head 000cd0c8, a volta da E1.326 sobre o A4 do review E1.323. Quem revisou foi uma instância que não fez a entrega.

Delta lido: `forge-check parecer delta docs/reviews/v047-conformidade-destino-opaco.md` (rc 0), intervalo `19df94ed..000cd0c8`, no domínio de código e testes. O delta traz em `hooks/conformidade.py` o `CONTEXTO_ARITMETICO` (:513), o `LE_INDICE`, o `INDICE_LITERAL` e a `linha_juntada` (:528), além de `linha_conhecida` (:543, mais a leitura de `f ( )` e do índice da atribuição) e de `valor_calculado` (:1412). Também traz o piso do `opaco-u4` (131 → 159) em `tests/test_hook_destino_opaco.py`, 28 fixtures `opaco-u4-v-*`, os mutantes `tests/mutantes/v047-destino-opaco-20.json` e `-21.json` (O133 a O148), `docs/hooks.md`, `docs/hooks-fixtures.md` e o fragmento do changelog.

Verificadores: rodei `tests/test_hook_destino_opaco.py HookDestinoOpaco.test_fixtures_opaco_u4` no 000cd0c8 e deu OK (159 fixtures). A mutação das specs 20 e 21 fica com o PQ do autor, e a suíte completa com o CI do PR (ainda não há PR aberto).

O A4 fecha para a linha. As sondas S10 a S12 viraram as fixtures `-v-s10` a `-v-s12`, que recusam. Também recusam pela `linha_conhecida`, sondadas aqui, estas grafias: `${a[@]:PATH=5}`, `${#a[PATH=5]}`, `${x:-${y:PATH=5}}`, `x[PATH=5]+=1`, `a=(…)`, `{a[PATH=5]}>f`, `test -v a\[PATH=5\]`, `[[ … ]]` (fora da lista) e `$\`+quebra+`((…))`. A junção pela `juntar_continuacoes` segue o bash: a aspa simples e o `#` falham fechados, e o heredoc sai antes da leitura. O `test 1 -eq PATH=5` do bash não avalia aritmética (conferido). Os livres seguem livres: `${x:0:1}`, `${x: -1}`, `${a[1]}`, `a[1]=b` e `f  (  )  { echo; }`.

## Achados
- A5 (bloqueante) hooks/conformidade.py:543 · O corpo de heredoc sem aspas no delimitador é expandido pelo bash, mas o `CONTEXTO_ARITMETICO` só olha a linha sem heredocs. `$[…]` e `${a[…]}` no corpo atribuem `PATH` antes do `"$(date)"`, o hook dá rc 0 e o bash grava .git/config (S14, S15; R-CONFORMIDADE)
- A6 (recomendado) hooks/conformidade.py:1367 · `textos_do_valor` ainda junta com `.replace("\\\n", "")`, e não com a função comum. Não abre furo, porque quem libera é o U4, que usa a `linha_juntada`; troque pela função comum para a junção ter um só lugar

## Sondas
- S14 · `cat <<E > "$(date)"\n${a[PATH=5]}\nE` (quebras reais; 5/date imprime .git/config) · espera: hook rc 2 · obtido: hook rc 0; bash --norc grava .git/config
- S15 · `cat <<E > "$(date)"\n$[PATH=5]\nE` (quebras reais) · espera: hook rc 2 · obtido: hook rc 0; bash --norc grava .git/config
- S16 · `: <<E > "$(date)"\n${a[PATH=5]}\nE` e `cat <<-E` com tab · espera: hook rc 2 · obtido: hook rc 0 nas duas
- S17 · `cat <<E > "$(date)"\n$((PATH=5))\nE` · espera: hook rc 2 · obtido: hook rc 2, controle

## Parecer
Reprovado no 000cd0c8. A volta fecha o contexto aritmético na linha que o hook lê, e a junção de barra e quebra pela função comum está certa. A classe, porém, não fecha: o corpo de heredoc com delimitador sem aspas também é palavra que o bash expande, com `$[`, `${…[…]}` e `${…:…}`, e a `linha_conhecida` não o vê. As sondas S14 a S16 rodaram pela máquina do `tests/test_hooks.py` (`executar_em_lote`), com a montagem da fixture `opaco-u4-v-s10-aritmetica-virgula-bloqueia` e só o comando trocado. O efeito de S14 e S15 foi conferido com `bash --norc -c` num repositório de teste: o `.git/config` muda. O `$((…))` recusa no corpo por outra guarda (S17), o que mostra que só as grafias novas ficaram de fora.

Sugestão (o desenho é do autor e da segurança): mantenha a falha fechada. Com destino opaco na linha, a `linha_conhecida` também passa o `CONTEXTO_ARITMETICO` no corpo de todo heredoc cujo delimitador não tem aspas (ou em todos, o que é mais simples e mais estrito). Cada sonda S14 a S16 vira fixture `-bloqueia`, com mutante da guarda nova.
