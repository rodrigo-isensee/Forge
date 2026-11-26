---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-voltas-alinhada
commit: e871982cedd65cf23e497336cb388bc173a3d3e1
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (melhoria/v0481-voltas-alinhada, #902, E14.72)

Revalidação por delta (H3), `46000ed5..e871982c`, lida por `forge-check parecer delta docs/reviews/v0481-voltas-alinhada.md`: `bin/forge-check` (sai o teto e a `recusa_da_volta`; entram `VOLTA_EM_DUPLA`, `TIPOS_DE_PORTAO` e a medida por teste `forca_por_teste`), R-QA, `agents/jarvis.md`, `autor-ate-o-merge.md`, fragmento do changelog, 4 specs ajustadas e 1 nova (`v0481-voltas-alinhada-3.json`), `tests/test_volta_por_delta.py`. O código de controle encolhe no saldo (H1 dentro do teto).

Achados da rodada anterior:
- A1 (teto e recusa da 4ª): resolvido. Sem teto; da 3ª em diante a restrição segue; da 4ª, `Volta N (R-QA): o tech-lead e o revisor que reprovou trabalham juntos ...` no brief gerado, e a conferência cobra as duas marcas pela contagem real do item (`real = max(n, n_anterior + 1, voltas + 1)`). S1 da rodada anterior virou teste (`test_volta_quatro_sai_sem_o_dono_com_o_trabalho_em_dupla`, 4ª e 5ª geradas com rc 0).
- A2 (textos): resolvido. R-QA:17, `jarvis.md:31`, `autor-ate-o-merge.md:10` e o fragmento seguem a ordem de 17:07, sem teto nem oferta de corte.
- A3 e A4 (recomendados): não mexidos (VA-M7 ainda morre por erro); seguem como cartão depois do merge.
- Segurança A2 (`TIPOS_DE_PORTAO`) e A3 (medida por teste) conferidos no código e nos testes novos; o mérito é da segurança.

## Achados
- A1 (bloqueante) bin/forge-check:4679 · A mensagem nova interpola `{texto_da_volta}` cru; SaidaSanitizada.test_todo_valor_de_caminho_numa_fstring_passa_pelo_sanitizador falha no CI (suíte 3/5 em 3.12 e 3.14) e à mão no head (S1). Passar pelo sanitizador ou escrever as duas mensagens com as constantes.
- A2 (bloqueante) bin/forge-check:4429 · O delta apagou `VOLTA_NA_DECISAO` daqui, mas o M23 de tests/mutantes/v0480-g1-1-uma-volta-3.json:66 ainda a muta e cita um teste removido; ConferirTodas falha no CI (suíte 4/5 em 3.12 e 3.14) e à mão (S2). Tirar o M23, como nas specs -1 e -2 (AR-12).
- A3 (recomendado) tests/test_volta_por_delta.py:981 · O auxiliar `autorizar` ficou sem uso depois da saída da decisão canônica; apagar.

## Sondas
- S1 · python3 -m unittest tests.test_forge.SaidaSanitizada.test_todo_valor_de_caminho_numa_fstring_passa_pelo_sanitizador (head e871982c) · espera: OK · obtido: FAIL, interpolação crua em 4679: volta {real} do item sem {texto_da_volta}
- S2 · python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes (head e871982c) · espera: OK · obtido: FAIL, tests/mutantes/v0480-g1-1-uma-volta-3.json M23

## Verificações
- Testes do diff, à mão no head e871982c: `python3 -m unittest tests.test_volta_por_delta tests.test_volta_alinhada` · Ran 120 tests, OK.
- Mutantes: `bin/forge-mutante` nas specs v0481 (-1, -2, -3): VA-M1..VA-M20 morreram (VA-M7 por erro, A3 anterior). Specs v0478 tocadas (`v0480-g1-1-uma-volta.json`, `-2`): M6, M8, M12..M15 morreram. `--cobertura --base 46000ed5`: toda guarda nova ou mudada coberta; as apagadas são as do teto que saiu.
- CI do head e871982c (check-runs do commit): suíte partes 1, 2 e 5 verdes nas duas versões do Python; partes 3 e 4 vermelhas nas duas (A1 e A2). Sem a linha `ci:`. `bateria (pareceres)` e `catraca` fora (esperam parecer e rótulo).
- Catraca do head: pede o rótulo `afrouxa-regra` pelos 5 testes apagados ou renomeados (cobriam o teto que a ordem de 17:07 tirou; coerentes com o diff), pelas guardas apagadas do teto e pela mudança em `bin/forge-check` (ADR 0008). O rótulo é do dono.

## Parecer
Reprovado. A correção da ordem de 17:07 está certa e bem testada: sem teto, restrição da 3ª, dupla da 4ª cobrada pela contagem real, `TIPOS_DE_PORTAO` e medida por teste com mutantes mortos. Mas o CI do head exato está vermelho por dois defeitos do próprio delta: A1, a mensagem nova fere o sanitizador de saída; A2, a spec `v0480-g1-1-uma-volta-3.json` ficou com o M23 apontando para o código apagado. São correções de uma linha, sem mudar lógica. A3 vira cartão.
