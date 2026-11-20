---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-relogio-hook
commit: b0ab26a0675cf77ba75749ca319243cc56624e9c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E37.28), BP1, relógio injetado no vigia de prazo

Head revisado `ac4d6dc7` (E37.16), base `ef186de8`. Código: `hooks/_comum.py`, +20/-18 linhas, dentro do teto H1, um comportamento só.

## Achados
- A1 (recomendado) tests/test_hooks.py:3152 · se `decidir` falhar dentro da thread, a falha some e o teste cai em `IndexError` no `resultado[0]`; guardar a exceção da thread (ou afirmar `len(resultado) == 1` com mensagem) daria o motivo real.
- A2 (bloqueante) tests/apoio_volta_unica.py:1198 · `forge-mutante --cobertura --base ef186de8` sai 1: `sem mutante` em :1198 (`isinstance ImportFrom and module == '_comum'`), :1199, :1200 e :1201; N1 e N2 trocam só a expressão `asname or name`, não o nó da condição. Declare um mutante por linha (ex.: tirar `no.module == "_comum"`).

## Sondas

## Parecer
Aprovado no head `b0ab26a0` (revalidações abaixo); o A2 fechou com N4 a N17. O A1 segue recomendado.

**Produção sem mudança.** Os padrões de `executar` são `time.monotonic` e `signal.setitimer` (o `getattr(..., None)` só vale sem `setitimer`, e aí o vigia sai antes de chamar `armar`), só por palavra-chave. O `armado` que o vigia entrega substitui o `hook.prazo_s and getitimer > 0` de antes: o vigia só entrega `True` com `segundos` não nulo, `setitimer` presente e na thread principal, logo com o alarme recém-armado e o `prazo_s` posto; o `getitimer` acima de zero logo depois era sempre verdadeiro nesse ramo (o vencimento lança `PrazoVencido`). Fora da thread principal o caminho antigo já não estendia por falta de alarme; o novo também não, agora sem ler o timer do processo. O desarme e a troca do sinal no `finally` seguem iguais. Nenhum hook nem o driver do lote passa `relogio`/`armar`: o teste de AST (`test_hooks_reais_e_driver_nao_passam_relogio_nem_armar`) confere a assinatura, as chamadas de `executar` nos hooks (mínimo de 10, inclusive `**`) e as chaves dos dicionários do driver (`EXECUCAO` e `PRAZO_LONGO`, de onde saem os `**` do driver).

**Mutantes.** `forge-mutante --processos 1 tests/mutantes/v0478-bp1-relogio.json`: M1 a M5 morreram (`_comum.py:2832, 2880, 2863, 2863, 2834`). Os realinhados `--ids P7,P8,P10,P12 tests/mutantes/v0455-prazo.json`: os quatro morreram. `forge-mutante --cobertura --base ef186de8`: a guarda nova `:2885` coberta por P8/P12, a removida (`getitimer`) isenta com motivo; `--conferir --base ef186de8`: trechos no lugar. A guarda `yield False` (P7) tem teste do ramo de falha (fora da thread principal, `armados == []`).

**Testes.** `SondaS1ComRelogioFalso` (2) e o teste de AST rodados: OK em 8,8 s. A S1 pequena prova recusa em 8 s, liberação dentro, a fronteira exata de 8,0 s e a sequência armar 3 s, rearmar 8 s, desarmar; a S1 real passa a 16 s de git contra 8 s, só na direção da recusa, o que tira a folga de 0,2 s que liberava no CI. Suíte inteira: fica no CI do PR (não há PR nem run nesta branch ainda); não rerrodei.

**Docs e changelog.** `docs/hooks.md` (Orçamento da linha) e `changelog.d/v0479-bp1-relogio-hook.md` atualizados na mesma entrega.

## Revalidação (b7e2f6b5)
Lido só o `forge-check parecer delta` (`ac4d6dc7..b7e2f6b5`; o aviso do merge `2c4af41` fora da `origin/develop` local vale como informado). Domínio: `tests/apoio_volta_unica.py`, `tests/test_hooks_volta_corpus.py`, `tests/mutantes/v0478-bp1-relogio-2.json`; produção intocada.
- `chamadas_do_executar` resolve `from _comum import executar as x`, `import _comum as c` e `_comum.executar`, e rejeita `from outro import executar`; o teste de AST dos hooks reais passa a usá-la. Os dois testes (apelido e AST dos hooks) rodados: OK em 0,3 s.
- `forge-mutante --processos 1 tests/mutantes/v0478-bp1-relogio-2.json`: N1, N2 e N3 morreram (`apoio_volta_unica.py:1199, 1201, 1205`).
- Cobertura: rc=1, ver A2. Suíte inteira fica no CI do PR; não rerrodei.

## Revalidação (b0ab26a0)
Lido só o `forge-check parecer delta` (`b7e2f6b5..b0ab26a0`). Domínio: `tests/apoio_volta_unica.py`, `tests/test_hooks_volta_corpus.py`, `tests/mutantes/v0478-bp1-relogio-3.json`; produção intocada.
- A2 fechado: `forge-mutante --cobertura --base ef186de8` sai rc=0; as linhas :1197, :1198, :1199, :1200, :1208, :1222, :1224, :1226 e :1228 de `apoio_volta_unica.py` aparecem cobertas por N1 a N17.
- `forge-mutante --processos 1 tests/mutantes/v0478-bp1-relogio-3.json`: N4 a N17 morreram, rc=0. N10 (`if True`) morreu por erro do teste sob o mutante, que passa sem ele; vale como morte.
- `referencias_ao_executar_fora_de_chamada` acha nome e apelido soltos, atributo `.executar` e a cadeia `"executar"`, e ignora as chamadas diretas. Os três testes novos (referência fora de chamada, outro nome de `_comum`, hooks reais e driver só com chamada direta) rodados: OK em 2,2 s.
- Suíte inteira fica no CI do PR; não rerrodei.
