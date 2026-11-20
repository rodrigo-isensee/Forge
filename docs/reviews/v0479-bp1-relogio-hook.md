---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-relogio-hook
commit: ac4d6dc7325b437958cbf61505259b20d90bfe1a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E37.28), BP1, relógio injetado no vigia de prazo

Head revisado `ac4d6dc7` (E37.16), base `ef186de8`. Código: `hooks/_comum.py`, +20/-18 linhas, dentro do teto H1, um comportamento só.

## Achados
- A1 (recomendado) tests/test_hooks.py:3152 · se `decidir` falhar dentro da thread, a falha some e o teste cai em `IndexError` no `resultado[0]`; guardar a exceção da thread (ou afirmar `len(resultado) == 1` com mensagem) daria o motivo real.

## Sondas

## Parecer
Aprovado.

**Produção sem mudança.** Os padrões de `executar` são `time.monotonic` e `signal.setitimer` (o `getattr(..., None)` só vale sem `setitimer`, e aí o vigia sai antes de chamar `armar`), só por palavra-chave. O `armado` que o vigia entrega substitui o `hook.prazo_s and getitimer > 0` de antes: o vigia só entrega `True` com `segundos` não nulo, `setitimer` presente e na thread principal, logo com o alarme recém-armado e o `prazo_s` posto; o `getitimer` acima de zero logo depois era sempre verdadeiro nesse ramo (o vencimento lança `PrazoVencido`). Fora da thread principal o caminho antigo já não estendia por falta de alarme; o novo também não, agora sem ler o timer do processo. O desarme e a troca do sinal no `finally` seguem iguais. Nenhum hook nem o driver do lote passa `relogio`/`armar`: o teste de AST (`test_hooks_reais_e_driver_nao_passam_relogio_nem_armar`) confere a assinatura, as chamadas de `executar` nos hooks (mínimo de 10, inclusive `**`) e as chaves dos dicionários do driver (`EXECUCAO` e `PRAZO_LONGO`, de onde saem os `**` do driver).

**Mutantes.** `forge-mutante --processos 1 tests/mutantes/v0478-bp1-relogio.json`: M1 a M5 morreram (`_comum.py:2832, 2880, 2863, 2863, 2834`). Os realinhados `--ids P7,P8,P10,P12 tests/mutantes/v0455-prazo.json`: os quatro morreram. `forge-mutante --cobertura --base ef186de8`: a guarda nova `:2885` coberta por P8/P12, a removida (`getitimer`) isenta com motivo; `--conferir --base ef186de8`: trechos no lugar. A guarda `yield False` (P7) tem teste do ramo de falha (fora da thread principal, `armados == []`).

**Testes.** `SondaS1ComRelogioFalso` (2) e o teste de AST rodados: OK em 8,8 s. A S1 pequena prova recusa em 8 s, liberação dentro, a fronteira exata de 8,0 s e a sequência armar 3 s, rearmar 8 s, desarmar; a S1 real passa a 16 s de git contra 8 s, só na direção da recusa, o que tira a folga de 0,2 s que liberava no CI. Suíte inteira: fica no CI do PR (não há PR nem run nesta branch ainda); não rerrodei.

**Docs e changelog.** `docs/hooks.md` (Orçamento da linha) e `changelog.d/v0479-bp1-relogio-hook.md` atualizados na mesma entrega.
