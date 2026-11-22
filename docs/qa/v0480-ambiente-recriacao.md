---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-ambiente-recriacao
commit: 09457540dde8f8b4d47c47d32cc6d57e9b883b10
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0478 E119.1 (AMBIENTE-SOBREVIVE-RECRIACAO, Claude Code atual no preparo do container)

Revisão completa e única no head 09457540 (base 38c37de9e). Só os testes afetados, as sondas e os mutantes da spec; sem suíte local (a bateria é o check-run do PR). Sem rede: curl falso. `shellcheck` ausente nesta máquina (não rodado; fica com o CI).

## Achados
- A1 (recomendado) scripts/preparar-estacao.sh:193 · o guarda de simular em garantir_path_local não tem mutante nem teste: removido, test_container_simular passa. Em --simular o .bashrc seria escrito. Declare mutante e afirme a ausência do .bashrc no teste.
- A2 (recomendado) scripts/preparar-estacao.sh:200 · o ramo "sem curl" (nos dois scripts, também preparar-ambiente.sh:107) não tem teste: o curl é sempre falso. Cubra com curl fora do PATH e a linha "falta: ... sem curl aqui".

## Critério → teste → resultado
| Critério (E119.1) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Sem binário em ~/.local/bin, instala pelo instalador oficial (nos 2 scripts) | ClaudeNoPreparo.test_sem_claude_local_instala... | claude antigo do PATH não conta | passou |
| Idempotente: 2ª rodada não baixa nem duplica o PATH no .bashrc | mesmo teste | 2ª rodada | passou |
| Sem rede: vira `falta:`, sem binário, sem barrar | test_instalacao_que_falha_vira_falta... | curl com saída 22 | passou |
| Baixa para arquivo, nunca por pipe | test_o_instalador_e_baixado... | n/a | passou |
| --verificar diz o comando e não altera nada | test_verificar_diz_o_que_falta... | home vazio, sem .local nem .bashrc | passou |
| Com binário presente, nada é baixado | test_com_claude_local_nada_e_baixado | n/a | passou |
| --simular não altera nada | test_forge.test_container_simular_nao_altera_nada | simulação (sonda manual: sem .bashrc) | passou; guarda do PATH sem mutante (A1) |
| postStart do container aciona o preparo, sem segredo | ConfiguracaoDoContainer (2 testes) | falha do preparo não impede subir | passou |
| Hook de ambiente continua ok com o novo requisito | test_ambiente_hook (9) | n/a | passou |

## Provas
- test_ambiente_recriacao.py: 7 testes, OK. test_ambiente_hook.py: 9 testes, OK. test_forge.py -k PrepararEstacao: 27 testes, OK.
- `bin/forge-mutante tests/mutantes/v0480-ambiente-recriacao.json`: M1..M9 todos `morreu` (saída 0), rev=09457540dde8.
- Mutante meu (remover o guarda de simular, linha 193): sobreviveu, base do A1.
- `forge-mutante --cobertura --base ...`: shell sai `não coberto` por desenho da ferramenta; não é pedido de controle (sem bin/, hooks/).
- Sonda `--container --simular` em home vazio: `[simular] baixar https://claude.ai/install.sh...`, sem .bashrc. `--verificar`: `falta: Claude Code atual ausente em .../.local/bin/claude ...: rode bash .../preparar-estacao.sh --container`.
- Vermelho antes do verde: `forge-testes --vermelho` não rodado (fila R-TETO ocupada); os mutantes M1..M9 mortos mostram que os testes caem sem o código novo.
