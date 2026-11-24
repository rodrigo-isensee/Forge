---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-hook-decisao-aviso
commit: c517dbe315987b500310e684b95a1cafee385d68
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E172.6 (PR #857, hook decisao só avisa)

Obrigação: o hook `decisao` no Stop do Jarvis avisa o usuário (`systemMessage`, saída 0, nunca bloqueia) quando a mensagem traz mais de um grupo de opções ou um grupo sem "Recomendo" (R-DECISAO), pela regra única de `medir_decisoes`; cala nos demais casos.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Dois grupos avisam, só `systemMessage` (ADR 0003) | `test_dois_grupos_de_opcoes_avisam_e_nao_bloqueiam` | limite de 1 grupo; aviso numa linha até 200 caracteres | passou |
| Grupo sem Recomendo avisa | `test_grupo_sem_recomendo_avisa` | grupo único sem recomendação | passou |
| Um grupo com Recomendo cala | `test_um_grupo_com_recomendo_cala` | limite logo dentro da regra | passou |
| Sem opções cala | `test_lista_de_pendencias_sem_opcoes_cala` | texto sem grupo | passou |
| Sem mensagem nem transcrito cala sem erro | `test_sem_mensagem_nem_transcrito_cala_sem_erro` | vazio | passou |
| Sem o campo, lê o transcrito | `test_sem_o_campo_le_a_ultima_mensagem_do_transcrito` | campo ausente | passou |
| Só o Stop | `test_outro_evento_cala` | outro evento | passou |
| Só o Jarvis | `test_sessao_que_nao_e_do_jarvis_cala`, `test_sessao_sem_agent_type_cala` | permissão por papel | passou |
| Fora de projeto do Forge cala | `test_fora_de_projeto_do_forge_cala` | cwd fora | passou |
| Ligado só no Stop, teto 10 s | `test_hooks_json_liga_o_decisao_so_no_stop_com_teto_de_10_s` | ligação e prazo | passou |

## Cenários e resultado real
Local: `test_hook_decisao.py` 11 testes OK. Vermelho (`forge-testes --vermelho 5f1c6e97 --modulos test_hook_decisao`): `vermelho: base=5f1c6e977230 head=2ecd153cf643`, 11 de 11 provam por asserção (H=ok, B=falha). Mutantes (`bin/forge-mutante tests/mutantes/v0480-hook-decisao-aviso.json`): M1 a M6 mortos; M6 morre por erro do teste declarado, que passa sem o mutante (vale como morte). `--cobertura --base 5f1c6e97`: as 6 condições Python mudadas têm mutante; `hooks.json` sai "não coberto" (JSON), guardado pelo teste de ligação. Documentação (`docs/hooks.md`, índice, changelog) conferida no diff. A suíte inteira fica para o check-run `bateria` do CI do PR.

## Revalidação por delta (head f2db561b, E172.29)
Delta `2ecd153c..f2db561b` (`forge-check parecer delta`): `bin/forge-testes`, `docs/hooks-fixtures.md`, 4 fixtures de `tests/hooks/decisao/`, `tests/pesos-d4.json`, `tests/test_hooks.py`. Fecha o que a review e a segurança reprovaram (A1 a A4): decisao na lista do Stop com checagem estática de `additionalContext`/`decision`, fixtures (aviso, silêncio, sem-forge-versao, erro-interno), peso do módulo e mapa de testes tocados. Os critérios do parecer anterior seguem passando; nenhum CA novo.
- `test_hook_decisao` (`-I`, discover): 11 testes OK. `test_hooks_json`, `test_cada_hook_tem_caso_que_passa_e_que_bloqueia`, `PesosDaSuite.test_pr_nao_aumenta_os_modulos_sem_peso`, `MapaCobreOQueOsTestesLeem`: 9 OK; `test_hooks -k decisao`: OK.
- Mutantes no delta (`--base 2ecd153c`): M1 a M6 mortos; M6 morre por erro do teste declarado (vale como morte).
- CI do head f2db561b (run 45436685276): suítes 3.12 e 3.14 (todas as partes), catraca, passos, longas, instalação e teto de pulados verdes; `bateria` e `bateria (pareceres)` vermelhas, esperado enquanto os pareceres do head não estão commitados.
- Observação: `tests/pesos-d4.json` também reordenou `test_fechar_limpar_clone` (valor igual), sem efeito no teste.

## Revalidação por delta (head c517dbe3, E172.41)
Delta `f2db561b..c517dbe3` (`forge-check parecer delta`, sem o que veio da develop): só o merge da develop (ad113d80) e o índice `docs/hooks-fixtures.md` regerado (3570 fixtures); `forge-testes`, `pesos-d4.json` e `test_hooks.py` mudam pelo que a develop trouxe, sem tocar o hook `decisao`. Nenhum CA novo; os critérios do parecer anterior seguem passando.
- `scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`.
- `test_hook_decisao` (`-I`, discover): 11 testes OK. `test_hooks -k decisao`: 1 OK. `test_indice_fixtures*`: 7 OK.
- Sem mutante novo: nenhuma linha de guarda mudada no delta; M1 a M6 do parecer anterior valem (código do hook idêntico).
- A suíte inteira fica para o check-run `bateria` do CI do PR, no mesmo sha.
