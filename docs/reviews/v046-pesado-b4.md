---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/pesado-b4
commit: c443050f82ddd8d7118be5c6c59273050cbae47f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-11
---
# Review: v046 (E14.3, melhoria/pesado-b4, volta 1)

Escopo lido: `git diff 2b896503..3e830f9b` (3 commits: e5132755, 649921be, 3e830f9b), `hooks/pesado.py`, `tests/test_pesado_v046.py`, `tests/mutantes/v046-pesado-b4*.json`, `changelog.d/pesado-b4.md`. Instância que não escreveu o código; a branch foi lida numa worktree destacada, sem escrita.

## Achados
- A2 (recomendado) hooks/pesado.py:213 · palavra_casa aceita sufixo de pasta em todas as palavras do padrão, não só na primeira: `python3 -m x/unittest discover` vira pesado (sonda). Só sobra trava, não falta; restringir o sufixo à palavra do executável deixaria o B4 exato.
- A4 (recomendado) hooks/pesado.py:6 · 210 linhas de código e teste (62+14 no hook, 134 no teste) e duas classes de comportamento (B4 e PROCESSO-ORFAO) num PR em hooks/ (M14); a ordem do dono juntou as duas, então o corpo do PR leva `teto: excedido, 210 linhas, <motivo>`.

## Sondas

## Ferramentas (citadas, não refeitas)
- `bin/forge-testes tests/test_pesado_v046.py`: `Ran 11 tests ... OK (skipped=1)`; o pulado é `test_zumbi_de_verdade_nao_e_vivo`, que o próprio teste pula quando o /proc é de outro namespace (sandbox); o CI o roda.
- `bin/forge-testes tests/test_pesado_fila.py`: `Ran 5 tests ... OK`.
- `bin/forge-mutante tests/mutantes/v046-pesado-b4.json`: B1 a B7 `morreu`; `tests/mutantes/v046-pesado-b4-2.json`: O1 a O7 `morreu` (14 de 14).
- `bin/forge-mutante --cobertura --base 2b896503`: toda guarda mudada `coberta` (110, 140, 149, 166, 168, 205, 213, 218, 223, 231, 326); a comparação antiga da base (linha 179) `isenta`, coberta por B3 e B7.
- `bin/forge-testes tests/test_hooks.py tests/test_catraca.py` no head: `Ran 472 tests ... FAILED (failures=6)`. As 2 de test_catraca são as da develop (E18.5). As 4 de `test_fixtures` são as fixtures `agentes/*` de pid e sessão (`"sessao": "s1"`, `"pidns"`), que falham igual na base 2b896503 neste sandbox (`/proc` de outro namespace: `processo()` devolve None aqui, então `pid_vivo` segue o caminho antigo); na base falhou ainda `pesado/mesma-sessao-libera`, que no head passa. Sem regressão do diff; o CI decide fora do sandbox.

## Parecer
Aprovado. O B4 reusa a tabela de lançadores do `_comum` (`separar_lancadores`) em vez de duplicar opções, cai na leitura antiga quando o `_comum` recusa a leitura (`LancadorDemais`) e casa o padrão por palavra inteira com sufixo de pasta (`/x/bin/forge-testes` sim, `/x/xbin/forge-testes` e `tests/e2ex` não); as formas leves do MAQ-A1b seguem leves por caminho e atrás de lançador (`timeout 60 bin/forge-testes tests/x.py`, `/x/bin/forge-mutante --listar`). O PROCESSO-ORFAO lê estado e início do `/proc/<pid>/stat` (campo 22, índice 19 depois do `)`, conferido), trata zumbi e pid reaproveitado como mortos, não decide quando o `/proc` é de outro namespace de pid e mantém o comportamento antigo para trava sem `inicio`; o hook órfão na fila sai pelo `bloquear` dentro do `try`, e o `finally` tira a senha (testado). Limite anterior que segue fora do escopo: comando dentro de `bash -c "..."` não é lido (já era assim na develop). Os quatro achados são recomendados e não devolvem (`R-REVIEW`). Os arquivos de junção (`tests/test_hooks.py`, `hooks/_comum.py`, `docs/hooks-fixtures.md`) não foram tocados.

## Revalidação (volta 1, delta 3e830f9b..c443050f)
Delta lido: `git diff 3e830f9b c443050f` (hooks/pesado.py, tests/test_pesado_v046.py, 2 specs de mutantes; 128 inserções, 13 remoções). Instância que não escreveu o código; worktree sem escrita.
- hooks/pesado.py:182 · `inicios` soma o texto original (`[palavras] + ...`): padrão de projeto que começa por lançador (`nice make test`) volta a ser pesado, como na base. Corrige a regressão que o diferencial achou; mutante B8 morre.
- `gravar_a_vez(hook, arquivo, dono, inicio, ...)` grava o dono e o início lidos uma vez antes do laço (`esperar_a_vez`) e no caminho direto; `test_a_vez_grava_o_dono_ja_checado` prova (pid relido seria 1). Fecha o desvio de pid relido; O6 reapontado para `inicio_de(pid)`, morre.
- Teste diferencial `test_nada_pesado_na_base_vira_leve`: regra da base congelada no teste (`inicios_da_base`, `leve_da_base`, `casa_da_base`, `pesado_da_base`), conferida contra a develop 2b896503 (mesma lista de lançadores, mesmo `PELOS_ARGUMENTOS`/`--completa`/`--vermelho`/`--listar`); mínimo afirmado (`> 250` pesados na base), então não passa vazio.
- A1 (hooks/pesado.py:164, `except PermissionError: pass` sem teste do ramo nem mutante) resolvido: `test_sem_permissao_de_sinal_decide_pelo_proc` (4 casos) e mutante O8 `morreu`. A3 (tests/test_pesado_v046.py:106, `mkdtemp` sem limpeza) resolvido: `pasta_temporaria` com `addCleanup`, sem `mkdtemp`.
- A2 segue aberto (recomendado, só sobra trava, não devolve); A4 segue para o corpo do PR (`teto: excedido`, agora 210 + ~100 linhas de teste e spec; o motivo é a ordem do dono juntar B4 e PROCESSO-ORFAO).
- Sem guarda nova em linha de `if`/`except` no delta além das já declaradas; B8 cobre a soma da leitura antiga.

Ferramentas (rodadas no head c443050f): `bin/forge-testes tests/test_pesado_v046.py`: `Ran 15 tests ... OK (skipped=1)` (o pulado é o zumbi de verdade, do /proc de outro namespace; o CI roda). `bin/forge-mutante tests/mutantes/v046-pesado-b4.json`: B1 a B8 `morreu`; `v046-pesado-b4-2.json`: O1 a O8 `morreu` (16 de 16).

## Parecer da volta 1
Aprovado, sem bloqueante. O delta fecha A1 e A3 e o desvio achado pelos portões; A2 e A4 seguem recomendados.
