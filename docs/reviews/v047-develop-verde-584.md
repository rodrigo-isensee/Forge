---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-develop-verde-584
commit: 6105741af55f9eedc2c5873c34d10cd4d48948c9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.432, conserto da develop do #584)

Parecer completo (não havia parecer anterior). Diff `befbb464...6105741a`: `agents/jarvis.md` (3 linhas) e o fragmento `changelog.d/v047-develop-verde-584.md`. Sem guarda, sem código de controle: não há mutante a declarar.

## Achados
- A1 (recomendado) skills/ci-cd/SKILL.md:1 · CI do head 6105741a segue vermelho (suíte partes 1, 3, 4 e 5); localmente test_metricas_texto falha só por este arquivo (caracteres 7579/6781, do #576). O item sozinho não deixa a develop verde; o merge espera o CI (R-FLUXO).
- A2 (recomendado) changelog.d/v047-develop-verde-584.md:2 · Catraca do PR 602 vermelha: corpo sem '## Projeto de origem' e '## Como medir' preenchidas (R-CONTRIB). Texto do PR, não do diff: preencher antes do merge.

## Sondas

## Parecer
Aprovado. O diff faz o que o item pede, nem mais nem menos:
- `agents/jarvis.md:3`: a description tinha `: ` dentro de um escalar sem aspas (`sessão: entende`), o que o YAML lê como mapeamento; com aspas duplas (sem aspas internas) o frontmatter volta a ler.
- `agents/jarvis.md:8` e `:47`: corte de 3 caracteres ("e em" → ", em"; "9 a 11" → "9-11") sem tocar invariante de `tests/config.json` (conferi a lista de `agents/jarvis.md`: nenhum trecho alterado está nela) e sem mudar sentido.

Evidência (antes/depois, `python3 -m unittest` na raiz):
- base `befbb464`: `test_frontmatter_agentes.test_todo_frontmatter_le_como_yaml (agente='agents/jarvis.md')` FAIL; `test_metricas_texto`: `agents/jarvis.md: caracteres = 7796 passa do teto 7795`.
- head `6105741a`: `tests.test_frontmatter_agentes tests.test_jarvis_nucleo tests.test_jarvis_n_jar_a tests.test_textos_dono_f7 tests.test_skills_v0442 tests.test_metricas_texto`, 36 testes, 1 falha, só `skills/ci-cd/SKILL.md` (A1, fora do diff).

Suíte: não rerrodada (R-REVIEW); o CI do head está vermelho e não li o log das partes (o host dos logs do Actions está fora do sandbox). A1 e A2 não devolvem o item, mas a integração na develop só com CI e catraca verdes.

Achados recorrentes (PA-7): conferi AR-1 a AR-14; nenhum alcança um diff só de texto de agente e fragmento.
