---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-f4-vigia-fluxo
commit: 8d755e503e51f53e37af2befea60ba7622b26dc8
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 F4 (vigia: PR sem agente e agente preso), 1ª rodada completa

- ci: 8d755e503e51f53e37af2befea60ba7622b26dc8 verde
  (`gh pr checks 931` no head: suíte 5/5, verificações longas, passos, python 3.14, instalação e teto de pulados verdes; `bateria`, `bateria (pareceres)` e `catraca` vermelhos. Os dois primeiros esperam os pareceres; a `catraca` é o A1 abaixo. As anotações do check-run só trazem "exit code 1".)

## Achados
- A1 (bloqueante) hooks/vigia.py:717 · R-QA: a catraca e `forge-mutante --cobertura --base ee05ee84` listam `apagada · hooks/vigia.py:618(base) · agentes_rodando(hook, raiz) != 0`; a guarda virou `livres = [] if vivos else ...` sem mutante que cubra a linha da base. Declare mutante para a linha ou mantenha a guarda.

## Critério → teste → resultado
O pedido não tem especificação de UX nem `CA-n`; as obrigações vêm de E34.1 (ordem do dono de 26/11) e do R-TETO.

| Obrigação | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| PR aberto sem agente na branch entra no aviso, com o papel | `PrsParados.test_pr_sem_agente_aparece_com_o_papel`, `TimeParado.test_pr_parado_sem_cartao_avisa_com_o_papel` | lista de PRs vazia ou 1 | passou |
| PR com agente vivo na branch não conta | `PrsParados.test_pr_com_agente_vivo_na_branch_nao_conta` | branch ocupada | passou |
| Sem vaga no teto do R-TETO não conta | `PrsParados.test_sem_vaga_no_teto_nao_conta` | vivos = teto | passou |
| Papel por estado do PR: conflito, check quebrado, portão faltando, tudo verde | `PapelDoPr.*` (10 testes) | check pendente, base main, rótulo do dono | passou |
| PR que espera só o dono ou o CI não conta | `test_base_main_espera_so_o_dono`, `test_check_pendente_espera_o_ci`, `test_afrouxa_regra_sem_rotulo_espera_o_dono`, `test_so_pr_do_dono_cala` | espera do dono | passou |
| Agente com transcript parado há mais de 10 min aparece | `InstanciasPresas.test_transcript_parado_ha_mais_de_10_min_aparece`, `test_transcript_recente_nao_conta` | 600 s | passou |
| Tipo e id do agente vão ao modelo só no formato | `test_tipo_fora_do_formato_vira_agente`, `test_reserva_sem_id_e_id_fora_do_formato_nao_contam` | entrada hostil | passou |
| Falha do gh, sem gh, fora de git, item fora da forma calam só a parte | `PrsParados.test_gh_com_erro_nao_conta`, `test_sem_gh_na_maquina_nao_conta`, `test_fora_de_repositorio_git_nao_chama_o_gh`, `test_item_fora_da_forma_e_ignorado`, `test_falha_do_gh_cala_so_a_parte_dele_e_registra` | falha da API | passou |
| Agente vigente não cala mais o aviso de PR e preso; sem nada a contar cala | `test_agente_rodando_nao_cala_o_pr_parado`, spec v0480 M3/M8 | silêncio | passou |

## Cenários e resultado real
- Afetados locais (em `tests/`): `python3 -m unittest test_hook_vigia_f4 test_vigia_parado test_vigia`: 62 testes OK.
- Vermelho antes do verde, `bin/forge-testes --vermelho ee05ee8439f8dac1743ecd61c8b64dab29688a41 --modulos tests.test_hook_vigia_f4` (rc 0): `vermelho: base=ee05ee8439f8 head=8d755e503e51 módulos=test_hook_vigia_f4` e `contagem: prova (API ausente)=28`; os 28 testes novos falham na base.
- Mutantes: `bin/forge-mutante` nas 4 specs v0481-f4-vigia-fluxo (rev=8d755e503e51): M1 a M30 todos `morreu` (M9, M10, M19, M20, M22, M25 por erro com o controle verde, que mata). Spec v0480-vigia-time-parado (editada no diff): M1 a M8 `morreu`. Nenhum sobrevivente.
- `forge-mutante --cobertura --base ee05ee8439f8dac1743ecd61c8b64dab29688a41`: toda condição mudada `coberta`, exceto `apagada · hooks/vigia.py:618(base)` (A1); `não coberto: scripts/preparar-estacao.sh` e `tests/pesos-d4.json` vêm do merge da develop, fora do diff do pedido.
- Fora do escopo do QA: a segurança (E34.4) registrou o PR de fork contado pelo vigia; o teste desse caso é do autor na volta.

## Revalidação
Na volta, `forge-check parecer delta docs/qa/v0481-f4-vigia-fluxo.md`; reteste o A1 (cobertura com `--base` do head aprovado) e o teste do achado da segurança, se mexer em hooks/vigia.py.
