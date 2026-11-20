---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp1-relogio-hook
commit: ac4d6dc7325b437958cbf61505259b20d90bfe1a
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
