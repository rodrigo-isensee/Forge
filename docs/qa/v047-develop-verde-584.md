---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-develop-verde-584
commit: 6105741af55f9eedc2c5873c34d10cd4d48948c9
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-16
---
# QA: v047 develop-verde-584 (E2.434)

Conserto de `agents/jarvis.md` que o #584 deixou vermelho na develop: aspas na `description` (o `: ` sem aspas quebrava o YAML) e corte de 3 caracteres para voltar ao teto de métricas. Sem especificação de UX; a obrigação é o teste que já existe (frontmatter lê como YAML, métrica abaixo do teto).

## Achados
- A1 (recomendado) tests/test_metricas_texto.py:80 · com o conserto, jarvis.md fica exatamente no teto (7795 de 7795), sem folga; a próxima edição de uma palavra o derruba. Não bloqueia (R-QA).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| frontmatter do agente lê como YAML (jarvis.md) | tests.test_frontmatter_agentes.test_todo_frontmatter_le_como_yaml | `description` com `: ` | passou no head, falhava na base |
| jarvis.md dentro do teto de métricas | tests.test_metricas_texto.test_nenhuma_metrica_passa_do_teto (linha do jarvis.md) | caracteres 7796 contra 7795 | passou no head, falhava na base |
| núcleo do Jarvis e invariantes de texto mantidos | tests.test_jarvis_nucleo, tests.test_forge | frases protegidas de `tests/config.json` | passou |

## Cenários e resultado real
- Diff `befbb464..6105741a`: só `agents/jarvis.md` (aspas na description, "primeira pessoa, em português", "regras 9-11") e o fragmento `changelog.d/v047-develop-verde-584.md`. Nenhum trecho de `invariantes` nem teto de `tests/config.json` mudou (afrouxar: não).
- Vermelho antes do verde, na base `befbb464` extraída em `$TMPDIR`: `FAIL test_todo_frontmatter_le_como_yaml (agente='agents/jarvis.md')` e `agents/jarvis.md: caracteres = 7796 passa do teto 7795`; 2 falhas em 28 testes. No head: `tests.test_frontmatter_agentes tests.test_jarvis_nucleo` = 26 testes, OK.
- Mutação: o diff é texto de agente, sem código nem guarda; não se aplica. Sem pedido de controle: sem `forge-mutante`.
- `tests.test_metricas_texto` segue vermelho só por `skills/ci-cd/SKILL.md` (caracteres 7579/6781, frase_media_x10 184/172, linhas_longas 29/27), do #576 (E2.412), que o E2.430 reverte; nenhuma linha do `jarvis.md`. Não é deste item.
- CI do PR 602 no mesmo sha (6105741a): `bateria` e `bateria (python 3.14)` em FAILURE (suíte partes 1, 3, 4, 5 vermelhas nas duas versões; a 2 verde) e `catraca` em FAILURE porque o corpo do PR não tem "Projeto de origem" e "Como medir" preenchidos (R-CONTRIB). Não consegui ler o log das partes da suíte (rede do sandbox); as 4 partes vermelhas não foram atribuídas uma a uma ao ci-cd. O item só fica verde na develop quando o E2.430 entrar e o corpo do PR for preenchido; o conserto do jarvis.md em si está provado.
