---
tipo: qa
contrato: 1
pedido: suite-concorrente
branch: melhoria/suite-concorrente
commit: 82c32f816268d0f32ee8298946043b9b3a0ff22b
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-20
---
# QA - suite-concorrente (trava de suíte no pre-push)

Sem UX nem API. Código `82c32f8` (autor: tech-lead); HEAD testado `73fc943` (os commits depois de `82c32f8` só trazem os pareceres de review `d62fea2` e segurança, ambos `aprovado` sobre `82c32f8`). Não escrevi o diff. Antes de cada suíte: `.githooks/pre-push --status` saiu 1 ("nenhuma suíte do Forge rodando") e `pgrep -af "python3 -m unittest discover"` não achou outra suíte.

## Obrigação -> teste -> resultado
Reprodução à mão num repositório descartável em `$TMPDIR` (remoto bare, hook da worktree em `core.hooksPath`, `tests/` com um teste de 4 s que registra início e fim).

| ID | Obrigação (pedido, E1 a E3, e brief E1.4) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|---|
| Q-1 | Duas execuções do pre-push ao mesmo tempo: a segunda espera a vez, a suíte não roda em paralelo | à mão: dois `git push` com 1 s de intervalo; log: `ini 26`, `fim 26`, `ini 49` (0,03 s depois do fim), `fim 49`; a segunda imprimiu "esperando a vez ... (R-TETO)"; automático `test_segunda_execucao_espera_a_vez` | sobreposição de intervalos | passou |
| Q-2 | `--status` com um argumento só testa: não cria subpasta nem trava, não segura a trava | à mão: sem `forge-<uid>` -> rc 1 e `$TMPDIR` segue vazio; seis `--status` em laço durante um push, que terminou normalmente; durante a suíte: rc 0 e "pid .. desde .."; `test_status_nao_cria_subpasta_nem_trava`, `test_status_acompanha_a_trava` | pasta e arquivo inexistentes | passou |
| Q-3 | Remoto chamado `--status` segue o caminho normal | à mão (`-c remote.--status.url=...`, `push -- --status feat:b2`) com outra suíte rodando: esperou a vez e rodou a suíte (2 `ini` no log); `test_remoto_chamado_status_segue_o_caminho_normal` | `$#` = 2 (nome e URL) | passou |
| Q-4 | Envio direto para develop, homolog e main continua barrado | à mão: os três, rc 1 e suíte não rodou (log sem linha nova); também com remoto `--status` para develop: barrado; `test_envio_direto_continua_barrado_com_trava_e_com_status` | refs protegidas | passou |
| Q-5 | Trava que é link é recusada, hook sai 1, suíte não roda | à mão: `forge-suite-<uid>.lock` -> link inexistente: rc 1, 0 execuções, alvo não criado, `--status` rc 1; `test_trava_que_e_link_simbolico_e_recusada` | link no arquivo | passou |
| Q-6 | Subpasta `forge-<uid>` que é link é recusada (não pula a suíte) | à mão: link para outra pasta: rc 1, 0 execuções, pasta alvo vazia, `--status` rc 1; `test_subpasta_que_e_link_e_recusada`, `test_trava_link_dentro_da_subpasta_e_recusada`, `test_subpasta_que_nao_da_para_criar_falha_fechado` | link, pasta de outro dono, falha ao criar | passou |
| Q-7 | O descritor da trava não vaza para o filho | à mão: teste da suíte do repositório descartável checou `/proc/self/fd/9`: `False`; `test_descritor_da_trava_nao_vaza_para_a_suite` | fd 9 | passou |
| Q-8 | Trava órfã de processo morto é liberada; limite estourado sai com erro e mensagem; limite inválido recusado; recuo cria subpasta 700 | `test_trava_orfa_de_processo_morto_e_liberada`, `test_limite_estourado_sai_com_erro_e_nao_roda_a_suite`, `test_limite_invalido_e_recusado`, `test_recuo_cria_subpasta_700_do_usuario` | espera 0/estourada, não numérico, modo 700 | passou |
| Q-9 | Suíte sem concorrente roda e devolve o código dela | `test_suite_sem_concorrente_roda_e_devolve_o_codigo_da_suite` | suíte vermelha -> envio barrado | passou |

## Suítes
- `python3 -m unittest discover -s tests -q` na raiz da worktree (`73fc943`): `Ran 966 tests in 232.635s`, `OK`.
- `scripts/validar-plugin.sh`: `Validation passed` (plugin e dev).
- Nenhum teste falhou e passou de novo sem mudança; nenhum instável.

## Vermelho antes do verde
Comando: `git archive HEAD` da worktree numa pasta de `$TMPDIR`, com `.githooks/pre-push` trocado por `git show 50997b7:.githooks/pre-push` (o da develop), `FORGE_TRAVA_ESPERA=5 python3 -m unittest tests.test_pre_push_trava -v`. Resultado: `Ran 15 tests`, `FAILED (failures=11, errors=1)`.
- Falham (12): `limite_estourado`, `limite_invalido`, `recuo_cria_subpasta_700` (erro), `remoto_chamado_status`, `segunda_execucao_espera_a_vez`, `status_acompanha_a_trava`, `status_nao_cria_subpasta_nem_trava`, `subpasta_que_e_link`, `subpasta_que_nao_da_para_criar`, `trava_link_dentro_da_subpasta`, `trava_orfa`, `trava_que_e_link_simbolico`.
- Passam sem a implementação (3, guardas de regressão, não provam a trava): `test_descritor_da_trava_nao_vaza_para_a_suite` (sem trava não há descritor), `test_envio_direto_continua_barrado_com_trava_e_com_status` (o barramento já existia) e `test_suite_sem_concorrente_roda_e_devolve_o_codigo_da_suite`. `test_status_nao_cria_subpasta_nem_trava` falha contra a develop (sem `--status`); contra o hook de `af586f1` seria guarda (R5 do review).

## Mutação
Sem ferramenta gratuita de mutação para shell em `stacks/`; a fronteira do A1 (`$# -eq 1`) e a do descritor foram exercidas pelas reproduções Q-3 e Q-7 em vez de mutação.

## Riscos
`flock` não cobre macOS (declarado pelo autor). Sandbox e terminal fora dele podem usar pastas diferentes e não se enxergar (declarado). `forge-<uid>` existente é conferida só por dono, não por modo (cartão TRAVA-MODO-SUBPASTA, baixa, da segurança).

## Achados
