---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-gerador-unico
commit: aae451ccb8dd8a651cce82ccba20af2a955e2f51
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 gerador único (E48.4, PR 946)

- ci: aae451ccb8dd8a651cce82ccba20af2a955e2f51 verde

CI lido do `gh pr checks 946` (run do mesmo sha, headSha conferido): tudo verde (suíte 5 partes, passos, python 3.14, instalação, verificações longas, teto de pulados, catraca, árvore já provada) fora `bateria` e `bateria (pareceres)`, que esperam este parecer. Sem rerrodar o sha; a falha de `tests/test_pre_push_trava.py:610` é o cartão TRAVA-TEXTO-LIMITE-AMBIENTE, fora deste PR.

## Critério → teste → resultado
Não há especificação de UX; as obrigações vêm do brief (E48.4) e do docstring do script.

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Roda os geradores que existem e diz o que mudou | `test_grava_e_diz_o_que_mudou`, `test_derivado_que_nao_existia_conta_como_mudou` | derivado inexistente | passou; mutantes M6, M10 mortos |
| `--conferir` não grava; rc 1 se algo ficaria diferente; rc 0 em dia | `test_conferir_nao_grava_e_sai_1_...`, `test_conferir_sai_0_com_tudo_em_dia` | derivado velho vs novo | passou; M3, M5, M8, M9, M11 mortos |
| rc 0 só se todos rodaram (gerador vermelho = 1; ausente avisado e pulado) | `test_gerador_vermelho_sai_1_nos_dois_modos`, `test_gerador_ausente_e_pulado_...` | gerador rc 3; gerador ausente | passou; M2, M4 mortos |
| Caminho literal, `python3 -I`, sem `GIT_*` | `test_gerador_roda_sem_o_git_dir_de_quem_chamou`, `test_todo_gerador_da_lista_existe_no_forge` | GIT_DIR exportado por hook; lista não vazia (5 linhas) | passou; M7 morto |
| Uso errado sai 2 sem rodar gerador | `test_uso_errado_sai_2_sem_rodar_gerador` | argumento desconhecido, excesso | passou; M1 morto |
| Diz o que fica fora | `test_diz_o_que_fica_fora` | n/a | passou |
| Linha nova na skill engineering-practices (6 frases encurtadas) | leitura do diff; testes de teto de texto no CI | teto de texto | passou (CI verde); frases encurtadas mantêm o sentido |

## Cenários e resultado real
- `python3 -m unittest tests.test_gerar_derivados`: 10 testes, OK (local, só o afetado).
- No repositório real: `scripts/gerar-derivados.py --conferir` rc=0 (os dois índices em dia, sem gravar); `scripts/gerar-derivados.py` rc=0, "sem mudança" nos dois, `git status` limpo; com `GIT_DIR=/nonexistent` no ambiente, `--conferir` rc=0.
- Mutantes (`bin/forge-mutante tests/mutantes/v0481-gerador-unico.json tests/mutantes/v0481-gerador-unico-2.json`, rev=aae451ccb8dd): M1 a M12 todos `morreu`, rc=0. Log em `/root/.forge-contrib/wt/qa150-v0481-logs/mut.log`.
- `bin/forge-mutante --cobertura --base 319a968df760...`: 12 linhas "coberta", nenhuma `não coberta`, nenhuma `isenta velha`; as 12 linhas de guarda do script têm mutante.
- Vermelho antes do verde: `bin/forge-testes --vermelho 319a968df760dd6f991d2308676321f6a2719b65 --modulos test_gerar_derivados` rc=0: `vermelho: base=319a968df760 head=aae451ccb8dd`, 10 testes `H=ok · B=erro · prova (API ausente)` (o script não existia na base), nenhum cai no HEAD.
- Acessibilidade e E2E: não se aplicam (script de linha de comando do Forge).
