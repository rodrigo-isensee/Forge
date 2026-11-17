---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v047-hook-estado-ilegivel
commit: a99c1a9fbb88229ad6b5d24dd25d2f664d0309e6
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v047-hook-estado-ilegivel

Pedido v047, etapa E1.231, lote A (classe C, `hooks/agentes.py`): HOOK-ESTADO-ILEGIVEL-LIBERA, plano de segurança `docs/security/v047-serie-hooks-pos-550.md` (R1 a R6). Intervalo `origin/develop..bc129c11` (base `7fff73e4`). Sem especificação de UX nem contrato de API: as obrigações são as linhas R1 a R6 e a tabela de fixtures do plano. Acessibilidade e E2E: n/a.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| R1 leitura estrita: texto, vazio, raiz lista, `agentes`/`lapides` não lista | fixtures `estado-ilegivel-{texto,vazio,lista-na-raiz,agentes-numero,agentes-texto,lapides}-bloqueia` | vazio, tipo da raiz, tipo das chaves | passou (rc 2, R-TETO) |
| R1 pasta, link para `/dev/null`, link para JSON válido | `estado-ilegivel-{pasta,link-dev-null,link-valido}-bloqueia` | não seguir link, não abrir pasta | passou |
| R1 arquivo ausente segue válido; chave ausente libera | `estado-sem-chave-agentes-libera` e fixtures de começo | ausência legítima | passou |
| R1 teto de 1 MiB | `ler_estado` (mutante M2) | limite máximo | passou (mutante morto); sem fixture dedicada |
| R1 JSON com aninhamento fundo | fixture `estado-ilegivel-profundo-bloqueia` | JSON profundo abaixo do teto | passou na revalidação (A1 corrigido) |
| R2 mensagem curta sem conteúdo do arquivo | fixtures acima (`stderr`) | vazamento de conteúdo | passou |
| R3 SubagentStart e SubagentStop não regravam e saem 0 | `estado-ilegivel-{inicio,fim}-nao-regrava-libera` | evento sem veto | passou |
| R3 retomada recusa | `estado-ilegivel-retomada-bloqueia` | RETOMADA | passou |
| R4 erro ao fixar a pasta do estado recusa depois do R-BRIEF | `erro-interno-clone-sem-estado-explore-bloqueia`, `erro-interno-estado-corrompido-sem-brief-bloqueia` | ordem R-BRIEF antes do estado | passou |
| R5 `.forge/config.json` ilegível ou raiz lista | `config-ilegivel-bloqueia`, `config-raiz-lista-bloqueia`, `config-ilegivel-fim-libera` | config corrompida | passou |
| R6 ADR 0003 e `docs/hooks.md` | diff | n/a | presente |
| Selado com estado ilegível (plano) | `estado-ilegivel-selado-bloqueia` | R-TETO, não R-BRIEF | passou na revalidação (A2 corrigido) |

## Provas

**Testes locais** (`python3 -m unittest tests.test_estado_ilegivel tests.test_agentes_clone`): `Ran 26 tests in 25.811s`, `OK`. A suíte inteira roda só no CI do PR; o check-run `bateria` deste sha não consultei (sem `gh` no ambiente), nenhuma citação de CI.

**Vermelho (à mão)**: `forge-testes --vermelho origin/develop` passou de 180 s e foi para segundo plano, sem veredito até esta entrega (nunca vale como vermelho). À mão: cópia do HEAD em `$TMPDIR` com `hooks/agentes.py` trocado pelo de `origin/develop`; `python3 -m unittest tests.test_estado_ilegivel` deu `Ran 8 tests`, `FAILED (failures=18, errors=6)` (ex.: `AssertionError: 0 != 2`). Com o código do lote, os mesmos 8 passam. Os testes provam a mudança.

**Mutação** (`bin/forge-mutante tests/mutantes/v047-hook-estado-ilegivel.json tests/mutantes/v047-hook-estado-ilegivel-2.json --processos 4`): rc 0; `forge-mutante: pedido=v047-hook-estado-ilegivel rev=bc129c11739d`; M1 a M15 `morreu` (15 de 15). Cobertura (`--cobertura --base origin/develop`): `base=7fff73e4… mb=7fff73e4… rev=bc129c11…`, 9 condições `coberta`; nenhuma sem mutante, nenhum sobrevivente. A captura da linha 286 não é condição mudada que a lista cubra (A3).

**Sonda do A1** (`ler_estado` sobre arquivo com `[` x 200000): saída `ESCAPA RecursionError` (esperado `EstadoIlegivel`). Confirma a sonda S1 do parecer de segurança (`e915233e`): rc 0 pelo hook, erros.log `RecursionError`. Bug: média (ator interno, `R-TETO` contornável pelo agente que escreve o `agentes.json`).

**Delta** (`forge-check parecer delta`): remoto avançou com `e915233e` (só `docs/security/v047-hook-estado-ilegivel.md`); fora do domínio do QA.

## Revalidação (E1.251, delta bc129c11..c3f86d7a)
Instância que não fez a entrega. Head de código `c3f86d7a`; o remoto trouxe só pareceres de review e segurança (`af699bdb`, merge sem conflito), fora do domínio do QA. Revalidação do A1 (bloqueante), A2 e A3 (recomendados): todos resolvidos, sem achado novo.

| Achado | Prova | Resultado |
|---|---|---|
| A1 RecursionError escapa (R-TETO) | `LerEstado.test_json_aninhado_fundo_e_ilegivel` (`[`x200000 e `{"agentes":[`x200000) e fixture `estado-ilegivel-profundo-bloqueia` (rc 2, arquivo intacto); `except Exception` em `ler_estado` | corrigido; fronteira: JSON fundo abaixo do teto de 1 MiB |
| A2 falta fixture do selado | `estado-ilegivel-selado-bloqueia` (R-TETO, `stderr_sem` R-BRIEF, estado intacto); passa também na base por desenho: guarda a ordem, não a correção | corrigido |
| A3 sem mutante da captura | M16 (volta a `(OSError, ValueError)`) e M17 (tira o `except EstadoIlegivel: raise`) | corrigido |

## Provas (revalidação)
**Testes locais** (`python3 -m unittest tests.test_estado_ilegivel tests.test_agentes_clone`): `Ran 27 tests`, `OK`. Suíte inteira só no CI do PR; o check-run `bateria` não consultei (sem `gh`), nenhuma citação de CI.

**Vermelho (à mão, `forge-testes --vermelho` não rodado por prazo)**: cópia do head com `hooks/agentes.py` de `bc129c11`; `unittest tests.test_estado_ilegivel`: `Ran 9 tests`, `FAILED (failures=1, errors=2)` (`test_json_aninhado_fundo_e_ilegivel` nos dois subcasos, e `test_fixtures_do_pedido` em `agentes/estado-ilegivel-profundo-bloqueia`). Com o código do head, passam.

**Mutação** (`bin/forge-mutante tests/mutantes/v047-hook-estado-ilegivel{,-2,-3}.json --processos 4`): rc 0, `rev=af699bdb1820`; M1 a M17 `morreu` (17 de 17). Delta (`--base bc129c11739dbaa9a3d0d12951adcbb7fe9bcae9`): `base=bc129c11739dbaa9a3d0d12951adcbb7fe9bcae9 mb=bc129c11739dbaa9a3d0d12951adcbb7fe9bcae9 rev=af699bdb…`, rc 0, M5, M16 e M17 `morreu`. Cobertura (`--cobertura --base 7fff73e4…`): rc 0, 9 condições `coberta`, nenhuma sem mutante nem `só equivalente`. Lista conferida contra o diff: toda linha de guarda mudada (287, 289) tem mutante.

**Fixture de 200 KB**: confirmada por tamanho (201783 bytes) e pontas; diff não impresso.

**Docs**: `forge-check docs` rc 0.

## Revalidação por delta (E2.134, junção c3f86d7a..b09916f7)
Head `b09916f7`: merge da `origin/develop` (`bf475209`) no lote A. `forge-check parecer delta` lista no domínio só `bin/forge-testes`, `tests/test_selo_e_entrega.py` e `tests/test_testes_tocados.py`, todos vindos da develop (E1.277, E1.185, E1.223), fora das obrigações R1 a R6. `git diff c3f86d7a HEAD` não toca `hooks/agentes.py`, `tests/test_estado_ilegivel.py` nem as fixtures do lote. Sem achado novo; A1 a A3 seguem resolvidos.

**Testes locais** (`python3 -m unittest tests.test_estado_ilegivel tests.test_agentes_clone`): `Ran 27 tests in 22.000s`, `OK`. Suíte inteira só no CI do PR; o check-run `bateria` não consultei, nenhuma citação de CI.

**Mutação** (`bin/forge-mutante tests/mutantes/v047-hook-estado-ilegivel{,-2,-3}.json --processos 4`): `rev=b09916f74ca8`, M1 a M17 `morreu` (17 de 17), nenhum sobrevivente. As specs do lote são as três de sempre (sem sufixo, `-2`, `-3`); o código sob mutação não mudou desde `c3f86d7a`.

**Vermelho:** inalterado (código e testes do lote idênticos aos já provados em `c3f86d7a`).

## Revalidação por delta (E2.426, junção b09916f7..05d68fce)
Head `05d68fce`: nova junção da `origin/develop` (`5e74c70e`, #581) no lote A. `forge-check parecer delta` lista no domínio `bin/forge-testes`, `docs/hooks-fixtures.md`, `docs/hooks.md`, `tests/test_selo_e_entrega.py` e `tests/test_testes_tocados.py`, todos vindos da develop (MAQ-I9, sessão automática, hook R-REVIEW), fora das obrigações R1 a R6. `git diff b09916f7 HEAD` sobre `hooks/agentes.py`, `tests/test_estado_ilegivel.py`, `tests/hooks/agentes` e `tests/mutantes/v047-hook-estado-ilegivel*` sai vazio. Sem achado novo; A1 a A3 seguem resolvidos. `achados-recorrentes.md` (PA-7) conferido: nenhuma classe nova.

**Testes locais** (`python3 -m unittest tests.test_estado_ilegivel tests.test_agentes_clone`): `Ran 27 tests in 61.302s`, `OK`. Suíte inteira só no CI do PR; o check-run `bateria` não consultei, nenhuma citação de CI.

**Mutação** (`bin/forge-mutante tests/mutantes/v047-hook-estado-ilegivel{,-2,-3}.json --processos 4`): `rev=05d68fcecaf5`, M1 a M17 `morreu` (17 de 17), nenhum sobrevivente.

**Vermelho:** inalterado (código e testes do lote idênticos aos já provados).

**Docs:** `forge-check docs` rc 0.

## Revalidação por delta (E2.706, junção 05d68fce..d2d82ffa)
Head `d2d82ffa`: merge da `origin/develop` (`5b1aacd5`) no lote A. `forge-check parecer delta` lista no domínio `bin/forge-testes`, `docs/adr/0003-...`, `docs/hooks-fixtures.md`, `docs/hooks.md`, `tests/test_selo_e_entrega.py` e `tests/test_testes_tocados.py`, vindos da develop, fora das obrigações R1 a R6. `git diff 05d68fce d2d82ffa` sobre `hooks/agentes.py` e `tests/test_estado_ilegivel.py` sai vazio. Sem achado novo; A1 a A3 seguem resolvidos.

**Testes locais** (`python3 -m unittest tests.test_estado_ilegivel tests.test_agentes_clone`, TMPDIR próprio): `Ran 27 tests in 25.088s`, `OK`. Suíte inteira só no CI do PR; o check-run `bateria` não consultei, nenhuma citação de CI.

**Mutação** (`bin/forge-mutante tests/mutantes/v047-hook-estado-ilegivel{,-2,-3}.json --processos 4`): rc 0, M1 a M17 `morreu` (visto M10 a M17 na cauda da saída; o rc 0 cobre as 17), nenhum sobrevivente.

**Vermelho:** inalterado (código e testes do lote idênticos aos já provados).

## Revalidação por delta (E1.8, d2d82ffa..a99c1a9f)
Head `a99c1a9f`: junção da develop e realinhamento do `de` de M22 e M32 (`tests/mutantes/v047-hook-erro-libera-3.json` e `-4.json`). `forge-check parecer delta` lista no domínio só essas duas specs. Sem achado novo; A1 a A3 seguem resolvidos.

**Mutação** (`bin/forge-mutante tests/mutantes/v047-hook-erro-libera-3.json tests/mutantes/v047-hook-erro-libera-4.json --processos 4`): `rev=a99c1a9fbb88`, rc 0, M17 a M32 `morreu` (16 de 16), inclusive M22 (`hooks/agentes.py:947`) e M32 (`hooks/agentes.py:961`).

**ConferirTodas** (`python3 -m unittest tests.test_forge_mutante.ConferirTodas`, TMPDIR próprio): `Ran 4 tests`, `OK`. Suíte inteira só no CI do PR; o check-run `bateria` não consultei, nenhuma citação de CI.
