---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-k165-e2e-incremental
commit: b4a5764717bf5d03815bf9071b9bf93aeabe47ad
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-21
---
# QA: v0479-k165-e2e-incremental (E73.4)

Item K165: a skill `qa-testing` manda gravar o JSON de cada caso, em rodada de mais de 10 min, em `relatorios/<rodada>/` fora do git. Mais a invariante correspondente em `tests/config.json` (com `invariantes_motivo_trecho`, R-QA).

## Achados
- A1 (recomendado) skills/qa-testing/SKILL.md:44 · o diff também enxuga frases que não são do K165 (independência do plano, "Cobertura de linhas não é meta", "zero violações" no critério de pronto) sem invariante; vale um item à parte.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Skill traz a regra da rodada longa (pasta do projeto, nunca /tmp) | `RegrasInviolaveis.test_trechos_obrigatorios` (regex da invariante casa o texto: True) | texto some ou muda | passou |
| Invariante tem regra e porquê | `RegrasInviolaveis` (invariantes_motivo_trecho) | invariante sem motivo | passou |
| Skill continua dentro do orçamento e das métricas de texto | `test_orcamento_instrucao` (8), `test_metricas_texto` (2) | teto de tamanho | passou |
| Demais leitores da skill intactos | `test_forge -k Skills/qa_/invariante/afrouxa` (13), `test_forge_mutante.TextoQueMandaUsarAFerramenta` (3), `test_aq1_texto` (6), `test_invariante_gatilho` (1) | frases lidas por outros testes | passou |

## Prova de que o teste pega
Mutação à mão no trecho da skill (`nunca em /tmp, que some` → `nunca em outro lugar, que some`): `test_forge -k RegrasInviolaveis` falha (FAILED failures=1); desfeita com `git checkout`, árvore limpa. Vermelho por `forge-testes --vermelho` não rodado: o brief proíbe vermelho sem `--modulos`, e a mutação à mão cobre o único teste novo (a invariante).

## Execução
Local, só os módulos acima, com TMPDIR; sem suíte inteira (a bateria roda no CI do PR).

## Revalidação (E73.8, head b4a57647)
Delta desde f700354c (`forge-check parecer delta`): `skills/qa-testing/SKILL.md` (ordem de acrescentar `relatorios/` ao `.gitignore` antes da rodada) e `tests/config.json` (invariante e motivo mais estritos, regex alinhada ao texto). Rodados com TMPDIR: `test_metricas_texto` (2 OK), `test_invariante_gatilho` (1 OK), `test_forge -k RegrasInviolaveis` (3 OK). Mutação à mão no trecho novo (`ao .gitignore antes` por `depois`): `RegrasInviolaveis` falha (failures=1); desfeita com `git checkout`. A1 segue recomendado. Parecer: aprovado.
