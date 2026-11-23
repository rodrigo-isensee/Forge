---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-gravar-sem-item
commit: e77e13e88b11df8c820004ec37392296ee174708
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-23
---
# QA: v0478 E90.28, corte (a) do G1.2a (`forge-check autorizacao gravar` sem o alvo `item:`)

Base `fc488261`, head `e77e13e8`. Obrigações: ADR 0018 (itens 1 a 6, corte G1.2a), `R-QA`. O alvo `item:` (PV-A2) fica para o G1.2b e, nesta etapa, recusa porque o leitor recusaria a concessão sem `Commit`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Alvo `item:` recusa e nada grava (corte G1.2a) | `test_autorizacao_gravar` · `test_o_que_o_leitor_recusaria_nao_e_gravado_alvo_item_nesta_etapa` (recusa com "Commit não é sha de 40 caracteres") | alvo `item:` sem Commit | passou |
| Ato e alvos derivados do texto todo; sem termo de ato ou ato diferente recusa | `test_sem_termo_de_ato_ou_com_ato_diferente_recusa_e_nada_grava`, `test_recorte_ou_ressalva_nasce_pendente_com_o_motivo` | negação, condição, dois atos, número solto, alvo genérico | passou |
| Transcrição só da sessão em curso (link, pasta, outra sessão, `HOME` do chamador) | classe `TranscricaoDaSessaoEmCurso` | caminho fora de `~/.claude/projects`, link, sessão alheia | passou |
| Validade: 48 h, fim do pedido, prazo local pendente, fala no futuro ou fora de 48 h | classe `Validade` e `VoltaDosPortoes` | futuro, 48 h, termo fora do mapa | passou |
| Emoji e outra escrita contam como palavra fora do vocabulário; ponto final após o alvo deixa pendente | `VoltaDosPortoes` | caractere não latino | passou |
| "fim deste pedido" só com pedido aberto no registro | `test_fim_deste_pedido_so_com_o_pedido_aberto`, `test_forge_check_confere_o_pedido_no_registro` | pedido inexistente ou fechado | passou |
| `ler` trata fala no futuro como adulterada | `test_fala_no_futuro_escrita_na_pasta_nao_fica_ativa_no_ler` | fala no futuro | passou |
| Leitura (G1.1) sem regressão | `tests.test_autorizacao` | n/a | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_autorizacao_gravar tests.test_autorizacao` (raiz, sem `-I`): `Ran 45 tests ... OK`.
- Vermelho antes do verde: `forge-testes --vermelho fc488261 --modulos test_autorizacao_gravar`, rc 0:
  `vermelho: base=fc488261d507 head=e77e13e88b11 módulos=test_autorizacao_gravar (restrito por --modulos)`; `revertidos à base: bin/forge-check, bin/forge-testes, bin/forge_autorizacao.py, changelog.d/v0480-gravar-sem-item.md, docs/adr/0018-autorizacao-do-dono-gravada.md, docs/indice-forge.md, tests/pesos-d4.json`; `contagem: prova (API ausente)=28`, nenhum teste cai no head (H=ok em todos).
- Mutantes do pedido, uma chamada: `forge-mutante --base fc488261` sobre as nove specs `tests/mutantes/v0479-sieg-g1-gravar.json` e `-2` a `-9`: `base=fc488261d507... rev=e77e13e88b11...`, `apoio de teste no diff: tests/pesos-d4.json · todos os mutantes entram`, 57 mutantes, 57 `morreu`, nenhum sobrevivente, rc 0. Cobrem `bin/forge_autorizacao.py` (gravar, leitura, fala no futuro, vocabulário, `pedido_aberto`, recusa do alvo `item:`) e `bin/forge-check:10835`.
- Mutantes do leitor: `forge-mutante --base fc488261 tests/mutantes/v047-sieg-g1-autorizacao-6.json` (spec editada no diff, a linha de hora dada à leitura), 8 mutantes, todos `morreu`, rc 0.
- Cobertura: `forge-mutante --cobertura --base fc488261`, rc 0; toda condição Python mudada sai `coberta`; `não coberto: tests/pesos-d4.json` é arquivo de dados (apoio de teste, sem guarda); `spec editada` só avisa a alteração da spec do leitor, conferida acima.
- Linhas de guarda do diff conferidas contra as specs: `forge-check` (`pedido_existe`), `estado` (fala futura), `fora_do_vocabulario`, `mensagem_do_dono`, `leitura`, `concessao_lida`, `pedido_aberto`, `cmd_gravar`, `executar`: todas com mutante.
- Sem E2E nem acessibilidade: é CLI, sem tela. Suíte inteira: no CI do PR (check-run `bateria`), não rodada local.

## Observações (sem achado)
- A ADR 0018 declara que a origem da transcrição não está provada (`CLAUDE_CODE_SESSION_ID` vem do ambiente do chamador); é limite documentado, coberto pelo corte do hook em item próprio, não defeito desta etapa.
- O remoto da branch avançou depois do head revisado; o parecer vai sobre o `Revisar-sha`.
