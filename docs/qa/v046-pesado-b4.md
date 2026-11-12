---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/pesado-b4
commit: c443050f82ddd8d7118be5c6c59273050cbae47f
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 E14.1 + E14.3, hooks/pesado.py B4 e PROCESSO-ORFAO (head c443050f)

Diff conferido (`2b896503..c443050f`): `hooks/pesado.py`, `tests/test_pesado_v046.py`, duas specs de mutantes, fragmento de changelog. Leitura na worktree limpa `conf-pesado-b4`, sem escrever nela (Z10). Sem especificação de UX: as obrigações são as da E14.1/E14.3 do pedido (B4, PROCESSO-ORFAO, A1 de segurança, A2 e A3 do review). Pedido sem PR: não há check-run `bateria` do sha para citar; a suíte inteira roda no CI do PR (`R-QA`).

## Achados
- A1 (recomendado) tests/test_pesado_v046.py:149 · `test_zumbi_de_verdade_nao_e_vivo` pula no sandbox do Bash (/proc de outro namespace); o zumbi fica coberto só pelo teste com /proc simulado aqui. Confirmar no CI que ele roda (R-QA).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| B4: bateria atrás de timeout/nice/env com opções | `B4.test_atras_de_lancador_com_opcoes` | opção com argumento (`-s KILL 60`, `-n 10`, `env -i -u`) | passou; vermelho na base |
| B4: caminho absoluto/relativo | `B4.test_por_caminho_absoluto_ou_relativo`, `test_padrao_do_projeto_com_pasta_no_meio` | `/x/bin/f`, `./.githooks/f`; pasta no meio do padrão | passou; vermelho na base |
| B4: formas leves seguem leves (citar não conta) | `B4.test_formas_leves_continuam_leves` | `echo`/`grep` com o nome, teste dirigido sem `--completa` | passou (guarda de não regressão, passa na base) |
| Segurança A1: padrão do projeto que começa por lançador segue pesado | `B4.test_padrao_do_projeto_que_comeca_por_lancador`, `test_nada_pesado_na_base_vira_leve` (diferencial base×head, regra da base congelada no teste) | nada pesado na base vira leve no head | passou; guardas de não regressão, passam na base; mortas por B8 |
| PROCESSO-ORFAO: zumbi e pid reaproveitado não ocupam a vez | `test_zumbi_nao_e_vivo`, `test_pid_reaproveitado_nao_e_vivo`, `test_trava_de_pid_reaproveitado_nao_ocupa` | estado Z/X; início do /proc diferente do gravado | passou; vermelho na base |
| PROCESSO-ORFAO: /proc de outro namespace não decide; PermissionError decide pelo /proc | `test_proc_de_outro_namespace_nao_se_le`, `test_sem_permissao_de_sinal_decide_pelo_proc` | /proc inválido; pid de outro usuário | passou; vermelho na base |
| PROCESSO-ORFAO: sessão que acabou sai da fila sem pegar a vez | `test_sessao_que_acabou_sai_da_fila_sem_pegar_a_vez` | dono muda durante a espera | passou; vermelho na base |
| Segurança A2: a vez grava dono e início checados | `test_a_vez_grava_o_dono_ja_checado`, `test_a_vez_grava_o_inicio_da_sessao` | pid relido depois da checagem | passou; vermelho na base |
| Review A1: PermissionError coberto | `test_sem_permissao_de_sinal_decide_pelo_proc` | pid de outro usuário | passou |
| Zumbi real | `test_zumbi_de_verdade_nao_e_vivo` | processo Z de verdade | pulou no sandbox (A1 acima) |

## Cenários e resultado real
- `python3 -m unittest tests.test_pesado_v046`: Ran 15, OK (skipped=1, o do namespace). `tests.test_pesado_fila`: Ran 5, OK.
- Vermelho antes do verde (`forge-testes --vermelho 2b896503 --modulos tests.test_pesado_v046`, rc 0; a corrida sem `--modulos` passou dos 590 s do meu prazo local, sem veredito, e não vale): `vermelho: base=2b89650303b0 head=c443050f82dd`; revertidos à base `hooks/pesado.py` e o changelog; contagem: não prova (passa na base)=3; prova (API ausente)=7; prova (asserção)=4; pulado=1. Os 3 que passam na base são de não regressão por desenho (A1 da segurança: o head não pode piorar a base); a morte deles vem dos mutantes B1, B7, B8.
- Mutantes (`forge-mutante` nas duas specs, rc 0): B1..B8 e O1..O8 todos `morreu` (16 de 16, nenhum sobrevivente). `forge-mutante --cobertura --base 2b896503`, rc 0: linhas de guarda 110, 140, 149, 171, 173, 211, 219, 224, 229, 237, 333 cobertas; `hooks/pesado.py:179(base)` isenta com motivo (comparação trocada por `comeca_com`, coberta por B3 e B7), aceita. Linhas 182 e 185 (soma da leitura antiga) mortas por B8 e B1.
- Sondas à mão sobre `pesado.pesado()`: `timeout 60`, `nice -n 10 /x/bin/…`, `env -i FOO=1 …`, `sudo timeout 5 make test`, `nice make test` pesados; `echo …`, `grep …` e `timeout 60 forge-testes tests/a.py` leves. `ionice -c3 …` e `bash -c '…'` seguem leves, como na base (A3 da segurança, recomendado já registrado, fora deste diff).
- Carga da máquina durante a rodada: média 6 com outros QAs; uma pesada minha por vez.
