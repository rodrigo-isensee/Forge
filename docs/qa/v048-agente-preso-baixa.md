---
tipo: qa
contrato: 1
pedido: v048
branch: melhoria/v048-agente-preso-baixa
commit: 2a310c7c3f20f9d34118eff8602c6829819eaf01
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-28
---
# QA: v048 agente preso sem baixa (#963, classe C, E12.2)

Escopo: `hooks/agentes.py` (`nota_na_fila`, `notificacao_terminal` com o anexo `queued_command`, `limpar`/`--limpar`), `hooks/vigia.py` (`agentes_rodando` com `Liberacao`), `tests/test_agente_preso_baixa.py` (17) e as specs `v048-agente-preso-baixa{,-2}.json` (M1-M13). Diff lido contra a Base d056c2ca no head 2a310c7c, em cópia própria de revisão. O mérito do código passa; reprova só pelo CI do Revisar-sha vermelho (A1, o mesmo defeito do parecer de segurança).

- ci: 2a310c7c3f20f9d34118eff8602c6829819eaf01 vermelho (run 46160762619: `suíte (python 3.12, parte 4/5)` e `bateria` com falha; as outras partes e os demais jobs verdes)

## Achados
- A1 (bloqueante) tests/mutantes/trava-agente-morto.json:46 · M6 (C1, promptSource system) não casa mais com a fonte: a linha hooks/agentes.py:492 terminou em ":"; o teste test_toda_spec_do_forge_confere_com_a_fonte falha e o CI do head fica vermelho. Realinhar o `de` de M6 ou retirá-lo.
- A2 (recomendado) tests/mutantes/v048-agente-preso-baixa.json:M6 · M6, M7 e M12 morrem por erro (exceção sob o mutante), não por asserção; o comportamento guardado (rc 1 e mensagem, EstadoIlegivel capturado, registro não-objeto pulado) só se prova pela exceção. Afirmar a mensagem de stderr no unitário.
- A3 (recomendado) hooks/agentes.py:481 · No transcript real, 126 de 2801 notificações de agente (id a+16 hex) vêm sem `<tool-use-id>` (agente retomado); C2 as recusa, e esse caso segue sem baixa, no hook e no --limpar. Registrar como limite conhecido.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Anexo `queued_command` da fila libera o agente (failed, completed, killed) | `NotificacaoNaFila.test_anexo_da_fila_libera` | os 3 status | passou (vermelho na base) |
| Texto digitado no meio do turno não libera | `test_texto_digitado_no_meio_do_turno_nao_libera` | commandMode prompt, origem human | passou |
| Campo fora da forma (type, commandMode, origin) não libera | `test_anexo_com_um_campo_fora_da_forma_nao_libera` | 4 variantes, origin string | passou |
| Anexo de sidechain não libera | `test_anexo_de_sidechain_nao_libera` | isSidechain True e None | passou |
| Sem tool-use-id não libera | `test_anexo_sem_tool_use_id_nao_libera` | C2 | passou |
| Vigia não conta o parado como rodando | `VigiaSemOParado.test_parado_pela_notificacao_nao_roda` | registro parado | passou (vermelho na base) |
| Vigia mantém o que roda; trava `pesado` é a da pasta do registro | `test_sem_notificacao_segue_rodando`, `test_trava_pesado_e_a_da_pasta_do_registro` | escrita com pesado ocupado | passou (guardas de regressão; passam na base) |
| `--limpar` dá baixa, lápide e log | `Limpar.test_da_baixa_no_parado_e_deixa_lapide_e_log` | liberacoes.log | passou (vermelho na base) |
| `--limpar` sem prova deixa o registro; dois transcripts, nenhum vale | `test_sem_prova_o_registro_fica`, `test_dois_transcripts_da_mesma_sessao_nenhum_vale` | 0 e 2 transcripts | passou |
| `--limpar` tolera registro fora da forma e sem sessão (prazo) | `test_registro_fora_da_forma_nao_derruba`, `test_sem_sessao_ainda_tira_o_vencido` | item int, sem sessao | passou |
| Sessão fora da forma não procura transcript | `test_sessao_fora_da_forma_nao_procura_transcript` | `*`, None | passou |
| Registro ilegível e fora de projeto saem 1 sem regravar | `test_registro_ilegivel_recusa_sem_regravar`, `test_fora_de_projeto_sai_1`, `ComandoLimpar` | JSON `{`, sem projeto, linha de comando | passou |
| Specs de mutante conferem com a fonte (R-QA) | `test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` | de fora da fonte | FALHOU (A1) |

## Cenários e resultado real
- Local: `python3 -m unittest tests.test_agente_preso_baixa` · Ran 17 tests, OK.
- Vermelho: `bin/forge-testes --vermelho d056c2ca0b2e73f1770b933e2aa698ec7cc241ae --modulos test_agente_preso_baixa`
  - `vermelho: base=d056c2ca0b2e head=2a310c7c3f20 módulos=test_agente_preso_baixa`; revertidos à base: changelog.d, hooks/agentes.py, hooks/vigia.py.
  - `contagem: não prova (passa na base)=6; prova (API ausente)=8; prova (asserção)=3`. Os 6 que passam na base são negativos (não libera) e guardas de regressão; as 3 asserções são liberação do anexo, vigia e `ComandoLimpar`.
- Mutantes: `bin/forge-mutante tests/mutantes/v048-agente-preso-baixa.json tests/mutantes/v048-agente-preso-baixa-2.json` · M1 a M13 todos `morreu`, sem sobrevivente. M6, M7 e M12 morrem com `(erro)` (A2). `--cobertura --base d056c2ca`: as 10 linhas de guarda mudadas saem `coberta`, nenhuma `não coberto`.
- Formato real: 2801 notificações de agente copiadas de transcripts reais em `~/.claude/projects` (`queued_command`, `commandMode` e `origin.kind` `task-notification`, producer `session-task`); 2675 passam por `notificacao_terminal`. Uma delas (id e tool-use-id trocados pelos do fixture, carimbo recente) rodada em `agentes.limpar` deu baixa: registro `[]`, rc 0. Teste ad hoc, fora do repositório.
- A1 reproduzido: `python3 -m unittest tests.test_forge_mutante.ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` · FAILED (failures=1), `spec com o de fora da fonte atual`.
- Segurança e review em paralelo, fora do domínio do QA.
