---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-s1-gancho
commit: e4b6bc4a8417bdb90338f24687c99219b19142fe
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: v0481 (E20.26, #920, hook `estado`, 1ª rodada completa)

- ci: e4b6bc4a8417bdb90338f24687c99219b19142fe verde

## Achados
- A1 (recomendado) tests/test_hook_estado.py:63 · test_controle_vira_espaco_e_linhas_e_tamanho_tem_teto indexa `linhas[1]` antes de afirmar a saída: na base dá IndexError (erro, não asserção) e o forge-testes --vermelho sai 2 (sem veredito). Afirmar o stdout inteiro antes de indexar.

## Critério → teste → resultado
Não há `CA-n` em docs/ux para este pedido; as obrigações são os 5 itens da emenda da ADR 0003 ("estado na pergunta do dono") e os mutantes M1 a M16.

| Obrigação (emenda ADR 0003) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 1 só a pergunta do estado | Termos.test_perguntas_do_estado, test_outras_mensagens, Injeta.test_outra_mensagem_e_outro_evento_silencio | palavra inteira (`estados`, `reestado`), vazio, não string | passou |
| 1 teto de 200 caracteres | Termos.test_teto_da_pergunta_no_limite | 200 aceita, 201 recusa | passou |
| 2 comando fixo, nada da mensagem | Injeta.test_o_comando_recebe_status_e_a_raiz_nunca_a_mensagem | `$(id)` na mensagem | passou |
| 3 prazo 8 s abaixo de 10 s | Prazo.test_prazo_vencido..., test_erro_de_sistema..., test_prazo_abaixo_do_timeout_do_hooks_json | timeout, OSError | passou |
| 4 só linhas `status:`, 10 linhas, 300 caracteres, controle vira espaço | Injeta.test_pergunta_do_estado..., test_controle_vira_espaco... | 15 linhas, 400 caracteres, ESC | passou |
| 4 rc diferente de 0 ou sem linha: manda rodar | Injeta.test_rc_diferente_de_zero..., test_sem_linha_status..., test_forge_check_ausente... | rc 2, ausente | passou |
| 5 nunca bloqueia, silêncio fora de projeto, desligado, erro interno | Injeta.test_fora_de_projeto..., test_hook_desligado..., fixtures estado/*.json + test_hooks (códigos {0}) | sem .forge/versao | passou |
| Registro no hooks.json após o merge com #921 | test_hooks.test_hooks_json, test_doutor (UserPromptSubmit: ordens, estado) | ordem e unicidade | passou |

## Cenários e resultado real
- CI do PR #920 no head e4b6bc4a (`gh pr checks 920`): suítes 3.12 e 3.14 (5 partes cada), passos, verificações longas, catraca, instalação, teto de pulados e árvore provada, todos verdes. Vermelhos: `bateria` e `bateria (pareceres)`, que esperam este parecer e o rótulo (anotação: "Process completed with exit code 1"); não são falha de código.
- Local, com a trava: `python3 -m unittest tests.test_hook_estado tests.test_hooks` verde (8 min; pulados do próprio test_hooks), e test_hook_estado sozinho: Ran 15 tests, OK.
- Vermelho: `bin/forge-testes --vermelho 346a7860 --modulos test_hook_estado` abre com `vermelho: base=346a7860515c head=e4b6bc4a8417`: 12 provam (7 asserção, 5 API ausente), 2 não provam (passam na base por serem de silêncio, guardados pelos mutantes M1 e M2), 1 sem veredito (A1); rc 2.
- Mutação: `bin/forge-mutante tests/mutantes/v0481-s1-gancho.json tests/mutantes/v0481-s1-gancho-2.json --processos 2`: rc 0, M1 a M16 todos `morreu` (M4, M7, M8 por erro do teste declarado, aceito pela regra). `--cobertura --base 346a7860`: toda condição de hooks/estado.py coberta; hooks/hooks.json e tests/pesos-d4.json `não coberto` (JSON, sem linha de código).
- Sem skip novo; sem acessibilidade nem E2E (hook sem interface).
