---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/diretriz-20-texto
commit: 29fa5da070a90c0a2b492621f73df5fc5cf271c4
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v046 (E26.11, texto da diretriz 20)

Entrega só de texto (agents/agile-coach.md, skills/kanban-scrum/SKILL.md, fragmento do changelog). Obrigação: diretriz 20 (1 triagem aplica no quadro, 2 número de backlog só da ferramenta, 3 plano substituído em `arquivo/`). Sem UX nem API.

## Achados
- A1 (bloqueante, resolvido) skills/kanban-scrum/SKILL.md:41-42 · agora diz "Até o `forge-check kanban` recusar destino divergente, o agile-coach confere com a última triagem": não afirma controle inexistente (`cmd_kanban`, bin/forge-check:420, segue sem a recusa; é a E25.3).
- A2 (recomendado, resolvido) tests/config.json · invariante nova da frase do agile-coach:9 com motivo `R-DECISAO` em `invariantes_motivo_trecho`; cobre também "plano ou pedido substituído".

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| D20-1 triagem termina com o quadro atualizado | leitura agile-coach:9, SKILL:41 | n/a | texto presente; recusa agora condicionada à E25.3 (A1 resolvido) |
| D20-2 backlog só da contagem do quadro, conferida com a última triagem | leitura agile-coach:9, SKILL:42 | n/a | presente; condizente com "até o comando existir" |
| D20-3 plano substituído vai para `arquivo/` | leitura agile-coach:9, SKILL:43 | n/a | presente; protegido pela invariante nova (A2 resolvido) |
| Cortes (burocracia, estabilidade do DORA, itens delegado, "Dois relógios" da skill, 3 itens de métricas fundidos) | `tests.test_orcamento_instrucao`, invariantes de `tests/config.json` | orçamento de texto | passou; nenhuma invariante do que saiu (ver abaixo) |

## Cenários e resultado real
- Invariantes: os trechos de `skills/kanban-scrum/SKILL.md` (5) e `agents/agile-coach.md` (10) seguem todos presentes; nenhum cobria o que saiu. `test_clareza` e `R-DECISAO` guardam `delegado`; o corte da frase "Mais de 30% de itens `delegado`" não é protegido por teste (nenhum teste o citava, conferido por grep). A linha `relogios:` segue descrita no agile-coach.md:17 e testada em `tests/test_voltas.py`; a definição dos relógios saiu da skill (fica só no agente, sem perda de medida).
- `bin/forge-testes --base c340c322 --afetados` (28 módulos, 1368 testes, 2 processos): único vermelho `test_forge.PesosDaSuite.test_no_maximo_20_por_cento_dos_modulos_sem_peso` (develop, corrigida em outro PR, conforme o brief); 1 skip do sandbox. `test_orcamento_instrucao` verde. A bateria completa é o check-run `bateria` do CI do PR.
- Vermelho antes do verde e mutação: não se aplicam (nenhum teste novo, nenhum código).
- `forge-check docs` na worktree acusa só `docs/security/*` de outros pedidos (fora do diff).

## Revalidação por delta (473ffd09..29fa5da0, volta E26.12)
`forge-check parecer delta` lista no domínio: agents/agile-coach.md, changelog.d/diretriz-20-texto.md, skills/kanban-scrum/SKILL.md, tests/config.json (o resto do intervalo veio da develop). Conferido: ressalva até o `forge-check kanban` existir (SKILL:41-42); "plano ou pedido substituído" vai para `arquivo/` (agile-coach:9, SKILL:43); invariante nova com motivo; fragmento do changelog atualizado. Sem teste novo de código: vermelho antes do verde e mutação não se aplicam. Cortes da volta: nenhuma invariante os cobria (já conferido no parecer anterior).
- `python3 -m unittest tests.test_forge.Orcamento tests.test_forge.RegrasInviolaveis`: 5 testes, OK. `tests.test_orcamento_instrucao`: 8 testes, OK.
- Sem PR aberto: bateria completa fica para o CI do PR.

## Resultado
Aprovado no head 29fa5da0. Sem bug aberto.
