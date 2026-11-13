---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-ambiente-sem-auto-update
commit: bd282fa7f5cfaf04f4c6b1bfe035e35853dc5a55
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 1
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-13
---
# QA: v047 AMBIENTE-SEM-AUTO-UPDATE (E1.94)

Head bd282fa7, base afba389e. Sem PR aberto: rodei só os testes afetados, em série (máquina com carga).

## Achados
- A1 (bloqueante) skills/trabalho-em-paralelo/SKILL.md:17 · a linha "Tamanho por risco" saiu e a regra M14 se perdeu do texto do Jarvis: `tests.test_forge.TetoPorPr.test_orientacao_e_classe_unica...` cai (2 subtestes) no head e passa na base afba389e. Restaurar a linha, com a Retomada ao lado.
- A2 (recomendado) bin/forge-testes:103 · `test_ambiente_sem_auto_update` entrou na lista no meio da tupla, sem ordem; alfabética facilita a leitura.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Orientação ao dono no README e no modelo | `AmbienteSemAutoUpdate.test_orientacao_ao_dono...` | frase exata nos 2 arquivos | passou |
| Retomada depois de reinício na skill | `AmbienteSemAutoUpdate.test_retomada_depois_de_reinicio...` | frases "briefs selados" e "sem refazer o feito" | passou |
| Nenhuma regra perdida com a saída de "Tamanho por risco" | `tests.test_forge.TetoPorPr` | frase do teto e classe única no texto do Jarvis | **falhou** (A1) |
| Teste novo é lido pelo filtro do pre-push | `LEITORES_DE_TEXTO` | módulo na lista | presente |

## Cenários e resultado real
- Regra M14 segue em `agents/tech-lead.md:21` e `skills/engineering-practices/SKILL.md:66`, mas a frase "uma classe de comportamento por PR em `hooks/`, com corpus próprio" só existia no texto do Jarvis: agora ela some do trecho que o Jarvis lê, e a regra da classe única em `hooks/` deixa de estar ali. O teto existente (decisão M14) a protege justamente por isso, e o teste prova a perda.
- Vermelho antes do verde: o teste novo (2 casos) é de presença de texto; sobre a base ele cairia por ausência das frases, e o dele passa no head. Não rodei `forge-testes --vermelho` (carga alta, sem veredito pedido); o teste que reprova é o antigo, não o novo.
- Outros módulos afetados: `test_jarvis_nucleo` (17) OK, `test_clareza` (9) OK, `test_modelos_projeto` (17) OK.
- Mutação: não se aplica (sem `bin/` com regra de guarda mudada; a linha de `bin/forge-testes` só soma um módulo à lista).

## Provas
- `python3 -m unittest tests.test_ambiente_sem_auto_update` → Ran 2 tests, OK
- `python3 -m unittest tests.test_forge.TetoPorPr` no head bd282fa7 → Ran 3 tests, FAILED (failures=2)
- mesmo comando na base afba389e → Ran 3 tests, OK
