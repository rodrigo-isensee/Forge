---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-relogio-hook
commit: b0ab26a0675cf77ba75749ca319243cc56624e9c
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: BP1, relógio injetado no vigia de prazo do hook (E37.30)

Escopo: `hooks/_comum.py` (`vigia_de_prazo`, `estender_prazo`, `executar` com `relogio` e `armar` só por palavra-chave), `SondaS1ComRelogioFalso` (S1 pequena), a S1 real endurecida (16 s de git contra 8 s) e o teste de AST em `tests/test_hooks_volta_corpus.py`. Só os testes dos arquivos tocados, com `TMPDIR`; a suíte inteira é do CI do PR. Sem UI.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| S1 pequena decide pelo relógio falso: recusa em 8 s, libera dentro, fronteira exata | `SondaS1ComRelogioFalso.test_s1_recusa_no_prazo_longo_libera_dentro_e_recusa_na_fronteira` | 3,99 s libera, 4,0+4,0 recusa; fora do merge recusa em 3 s | passou (10 de 10 sob carga) |
| Fora da thread principal o vigia não arma nem estende | `SondaS1ComRelogioFalso.test_fora_da_thread_principal_o_vigia_nao_arma_nem_estende` | sem SIGALRM | passou |
| S1 real só afirma a recusa | `Hooks.test_liberar_ou_provar_a_carga_recusa_a_sonda_s1` | 16 s contra 8 s | passou (22,8 s) |
| Nenhum hook nem o driver do lote passa `relogio`/`armar`; padrões reais | `CorpusDaVoltaUnica.test_hooks_reais_e_driver_nao_passam_relogio_nem_armar` (AST) | mínimo de 10 chamadas a `executar`, uma por hook | passou |
| Helper de git dos hooks sem regressão | `tests.test_hook_git_comum` | n/a | passou (1 teste, 58,8 s) |

## Vermelho antes do verde
`bin/forge-testes --vermelho <base>` estourou o prazo de 590 s do meu lado (a máquina compartilhada estava com carga 60 a 70) e não deu veredito; não conta como vermelho. Vermelho manual, contra a base ef186de8: cópia do head em `$TMPDIR` com só `hooks/_comum.py` trocado pelo da base, `python3 -I -m unittest discover -s tests`:
- S1 pequena: `TypeError: executar() got an unexpected keyword argument 'relogio'` (errors=6 em 2 testes).
- AST: `KeyError: 'relogio'` (errors=1).

Os dois caem na base e passam no head.

## Carga: S1 pequena 10 vezes com 12 laços de CPU
12 processos `while True: pass` em paralelo (12 núcleos; carga 18 na partida), 10 rodadas dos 2 testes: 10 de 10 `OK`, de 0,8 s a 5,5 s (a 1.ª, de partida fria). Sem flake: o relógio é falso, o resultado não depende da máquina.

## Mutantes (M1 a M5)
```
forge-mutante: pedido=v0478-bp1-relogio rev=ac4d6dc7325b spec=74087314fc26aed767bd02a3b8632ac624bd8881a9b72fe4ed33d173fe3cdb26
M1 · morreu · hooks/_comum.py:2832
M2 · morreu · hooks/_comum.py:2880
M3 · morreu · hooks/_comum.py:2863
M4 · morreu · hooks/_comum.py:2863
M5 · morreu · hooks/_comum.py:2834
rc=0
```
Mutante por linha de guarda mudada: `armado` (M1), `inicio` (M2), a conta do prazo longo (M3), o rearme (M4) e o desarme (M5). A condição removida do `getitimer` está declarada como isenta, com motivo, e coberta pelos testes do prazo longo e pelo teste fora da thread.

## Fixture `pesado/mesma-sessao-libera`
Ela estoura na suíte por causa da fila real da máquina (`pesado.fila/`, compartilhada com outras sessões), não pelo diff. Provas: (1) sozinha no head, passou em 1,2 s mesmo com carga 73; (2) sozinha na cópia com o `_comum.py` da base, sem o diff, falhou depois de 130 s de espera. O diff não toca `hooks/pesado.py` nem `tests/hooks/pesado/`. Efeito de ambiente, sem relação com BP1; não bloqueia.

## Cenários e resultado real
Execução local em 2026-11-20, `python3 -I -m unittest discover -s tests -p <módulo> -k <teste>`, com `TMPDIR`. Suíte inteira: check-run `bateria` do mesmo sha no CI do PR (não rerrodada aqui). Sem bug aberto.

## Revalidação (delta ac4d6dc7..b7e2f6b5, E37.35)
Domínio do delta (`forge-check parecer delta`): `tests/apoio_volta_unica.py` (`chamadas_do_executar` resolve o apelido do import e o módulo importado de `_comum`), `tests/test_hooks_volta_corpus.py` (teste novo e uso do helper) e `tests/mutantes/v0478-bp1-relogio-2.json` (N1 a N3). Sem mudança em código de produção.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Hook que importa `executar` com apelido, ou chama `c.executar`, e passa `relogio=`/`armar=` é achado | `CorpusDaVoltaUnica.test_chamada_com_apelido_do_import_e_pega_com_relogio` | apelido, módulo com apelido, módulo sem apelido, `**k`; `outro.executar` e `rodar` de outro módulo não contam | passou |
| Hooks reais e driver sem `relogio`/`armar` (agora pelo helper novo) | `CorpusDaVoltaUnica.test_hooks_reais_e_driver_nao_passam_relogio_nem_armar` | mínimo de 10 chamadas | passou |

Vermelho: cópia do head em `$TMPDIR` com `chamadas_do_executar` trocado pelo helper antigo (só o nome `executar`, por `id` ou `attr`): o teste novo falha (`failures=2`, subtestes), por exemplo `AssertionError: Lists differ: [<ast.Call ...>] != []` na linha do `from outro import executar as rodar`. Com o helper do head: `OK`.

Mutantes do delta, `forge-mutante tests/mutantes/v0478-bp1-relogio-2.json --base ac4d6dc7...` (rc=0):
```
base=ac4d6dc7325b437958cbf61505259b20d90bfe1a mb=ac4d6dc7325b437958cbf61505259b20d90bfe1a rev=b7e2f6b565bd80f60f7df8f7cdcb0509417c3adc
N1 · morreu · tests/apoio_volta_unica.py:1199
N2 · morreu · tests/apoio_volta_unica.py:1201
N3 · morreu · tests/apoio_volta_unica.py:1205
```
Um mutante por linha de guarda do helper (apelido do `from`, apelido do `import`, restrição ao módulo). Parecer mantido: aprovado, sem achado, sem bug aberto. Suíte inteira: check-run `bateria` do mesmo sha.

## Revalidação (delta b7e2f6b5..b0ab26a0, E37.39)
Domínio do delta (`forge-check parecer delta`): `tests/apoio_volta_unica.py` (`nomes_do_executar` extraído e `referencias_ao_executar_fora_de_chamada`), `tests/test_hooks_volta_corpus.py` (3 testes novos) e `tests/mutantes/v0478-bp1-relogio-3.json` (N4 a N17). Sem mudança em código de produção.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Só o `executar` de `_comum` conta como chamada | `CorpusDaVoltaUnica.test_chamada_de_outro_nome_do_comum_nao_e_do_executar` | outro nome de `_comum`, outro módulo com apelido, outra função de `_comum` | passou |
| Referência fora de chamada (reatribuição, `getattr`, `import_module`, `partial`, atributo solto) é achada; chamada direta e outros nomes não | `CorpusDaVoltaUnica.test_referencia_ao_executar_fora_de_chamada_e_achada` | 6 formas achadas, 6 diretas/outras vazias | passou |
| Hooks reais e driver só chamam o `executar` direto | `CorpusDaVoltaUnica.test_hooks_reais_e_driver_so_chamam_o_executar_direto` | mínimo de 10 hooks lidos | passou |

Os 5 testes do módulo (3 novos, apelido do import e hooks reais sem `relogio`/`armar`) passaram no head: `Ran 5 tests in 5.490s OK`.

Vermelho: cópia do head em `$TMPDIR` com `tests/apoio_volta_unica.py` trocado pelo de b7e2f6b5 (helper anterior): `ImportError: cannot import name 'referencias_ao_executar_fora_de_chamada' from 'apoio_volta_unica'`, `FAILED (errors=1)` no módulo. Com o helper do head: `OK`.

Mutantes do delta, `forge-mutante tests/mutantes/v0478-bp1-relogio-3.json --base b7e2f6b5` (rc=0):
```
base=b7e2f6b565bd80f60f7df8f7cdcb0509417c3adc mb=b7e2f6b565bd80f60f7df8f7cdcb0509417c3adc rev=b0ab26a0675cf77ba75749ca319243cc56624e9c
apoio de teste no diff: tests/apoio_volta_unica.py · todos os mutantes entram
N4 · morreu · tests/apoio_volta_unica.py:1197
N5 · morreu · tests/apoio_volta_unica.py:1198
N6 · morreu · tests/apoio_volta_unica.py:1199
N7 · morreu · tests/apoio_volta_unica.py:1200
N8 · morreu · tests/apoio_volta_unica.py:1209
N9 · morreu · tests/apoio_volta_unica.py:1210
N10 · morreu · tests/apoio_volta_unica.py:1208 · (erro) o teste declarado deu erro sob o mutante e passa sem ele
N11 · morreu · tests/apoio_volta_unica.py:1222
N12 · morreu · tests/apoio_volta_unica.py:1224
N13 · morreu · tests/apoio_volta_unica.py:1226
N14 · morreu · tests/apoio_volta_unica.py:1228
N15 · morreu · tests/apoio_volta_unica.py:1224
N16 · morreu · tests/apoio_volta_unica.py:1226
N17 · morreu · tests/apoio_volta_unica.py:1228
```
Cobertura: `forge-mutante --cobertura --base ef186de8` rc=0, todas as linhas de guarda do helper `coberta`. N10 morre por erro do teste (não por falha de asserção), mas o erro some sem o mutante: veredito válido. Parecer mantido: aprovado, sem achado, sem bug aberto. Suíte inteira: check-run `bateria` do mesmo sha.
