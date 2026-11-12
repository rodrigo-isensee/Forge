---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/diretriz-20-texto
commit: bad4f5aaab7776ab2efaeec2c5e52c05b6ac3564
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 (E26.11, texto da diretriz 20)

Entrega só de texto (agents/agile-coach.md, skills/kanban-scrum/SKILL.md, fragmento do changelog). Obrigação: diretriz 20 (1 triagem aplica no quadro, 2 número de backlog só da ferramenta, 3 plano substituído em `arquivo/`). Sem UX nem API.

## Achados
- A1 (bloqueante) skills/kanban-scrum/SKILL.md:41 · afirma "`forge-check kanban` recusa destino divergente", mas `cmd_kanban` (bin/forge-check:420) só confere WIP e limites; a recusa é a E25.3, ainda não feita. A skill passa a descrever controle inexistente; diga "passará a recusar (E25.3)" ou espere a E25.3.
- A2 (recomendado) agents/agile-coach.md:9 · nenhuma invariante (tests/config.json) nem teste protege o texto novo (triagem termina com o quadro atualizado; contagem conferida; `arquivo/`); apagar a frase passa verde. Sugestão: 1 invariante por arquivo e subir o contador de invariantes_sem_motivo.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| D20-1 triagem termina com o quadro atualizado | leitura agile-coach:9, SKILL:41 | n/a | texto presente; o "recusa" não existe na ferramenta (A1) |
| D20-2 backlog só da contagem do quadro, conferida com a última triagem | leitura agile-coach:9, SKILL:42 | n/a | presente; condizente com "até o comando existir" |
| D20-3 plano substituído vai para `arquivo/` | leitura agile-coach:9, SKILL:43 | n/a | presente; sem teste (A2) |
| Cortes (burocracia, estabilidade do DORA, itens delegado, "Dois relógios" da skill, 3 itens de métricas fundidos) | `tests.test_orcamento_instrucao`, invariantes de `tests/config.json` | orçamento de texto | passou; nenhuma invariante do que saiu (ver abaixo) |

## Cenários e resultado real
- Invariantes: os trechos de `skills/kanban-scrum/SKILL.md` (5) e `agents/agile-coach.md` (10) seguem todos presentes; nenhum cobria o que saiu. `test_clareza` e `R-DECISAO` guardam `delegado`; o corte da frase "Mais de 30% de itens `delegado`" não é protegido por teste (nenhum teste o citava, conferido por grep). A linha `relogios:` segue descrita no agile-coach.md:17 e testada em `tests/test_voltas.py`; a definição dos relógios saiu da skill (fica só no agente, sem perda de medida).
- `bin/forge-testes --base c340c322 --afetados` (28 módulos, 1368 testes, 2 processos): único vermelho `test_forge.PesosDaSuite.test_no_maximo_20_por_cento_dos_modulos_sem_peso` (develop, corrigida em outro PR, conforme o brief); 1 skip do sandbox. `test_orcamento_instrucao` verde. A bateria completa é o check-run `bateria` do CI do PR.
- Vermelho antes do verde e mutação: não se aplicam (nenhum teste novo, nenhum código).
- `forge-check docs` na worktree acusa só `docs/security/*` de outros pedidos (fora do diff).

## Resultado
Reprovado por A1. Revalidar com `forge-check parecer delta docs/qa/diretriz-20-texto.md`.
