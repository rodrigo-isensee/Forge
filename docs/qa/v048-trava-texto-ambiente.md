---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-trava-texto-ambiente
commit: 2ba3d2d0a724d5e0a1903968a1982ed0177f24bb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v048-trava-texto-ambiente (#949, TRAVA-TEXTO-LIMITE-AMBIENTE)

- ci: 2ba3d2d0a724d5e0a1903968a1982ed0177f24bb verde

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| TRAVA-TEXTO-LIMITE-AMBIENTE: o texto da trava sai sem controle | `test_texto_da_trava_sai_limitado_e_sem_controle` (sem ESC nem BEL no `--status` e no stderr da fila) | caractere de controle no 1.º e no 2.º campo da trava | passou (M1 morre) |
| o texto da trava sai com até 200 bytes (+120 no status) | idem (trava de 1 MiB) | máximo | passou (M2 morre) |
| a fila corta o pid lido da trava em 12 | idem, tamanho do stderr até 600 sem o aviso de locale | logo fora do limite (pid de 1 MiB) | passou (M3 morre) |
| o aviso de locale do bash não entra na medida | `AVISO_DE_LOCALE` tira só a linha `line N: warning: setlocale` | ambiente com locale ausente | passou |

## Cenários e resultado real
- Diff contra a base: só teste (`tests/test_pre_push_trava.py`, 8 linhas), a spec de mutantes e o fragmento de changelog; o hook `.githooks/pre-push` não mudou.
- Regex: tira só a linha de aviso; ESC e limite de 600 continuam medidos. O 2.º campo agora tem controle e não tem fim, então o corte do pid é exercitado.
- Vermelho em caminho longo (cópia em `$TMPDIR`, 90 caracteres de caminho): o teste da base contra o hook do head dá `AssertionError: 689 not less than or equal to 600`; o teste do head passa (`OK`). Logs: `/root/.forge-contrib/wt/v048-qa-logs/longo-antigo.log` e `longo-novo.log`.
- `forge-testes --vermelho b3dfe15 --modulos test_pre_push_trava`: rc=1, "nenhum teste prova a mudança". Esperado: a mudança é o próprio teste e o código não mudou; nesta máquina o caminho da cópia é curto e a base passa. A prova vale pelo caso de caminho longo acima, que reproduz a falha da base.
- Mutantes `bin/forge-mutante tests/mutantes/v048-trava-texto-ambiente.json` (head, `rev=2ba3d2d0a724`): M1 morreu · .githooks/pre-push:60; M2 morreu · .githooks/pre-push:60; M3 morreu · .githooks/pre-push:506; rc=0. Sem linha de guarda mudada no diff, portanto nada sem mutante.
- CI do PR #949 no head 2ba3d2d0: todos os checks concluídos e verdes (bateria, partes 1 a 5 da suíte, python 3.14, instalação, catraca, pareceres, passos, verificações longas, teto de pulados).
