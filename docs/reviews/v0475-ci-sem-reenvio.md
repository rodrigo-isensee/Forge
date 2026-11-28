---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-sem-reenvio
commit: 6cbb20bc801d3b0014ce62f97cdc8b20221edfd4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.87, branch melhoria/v0475-ci-sem-reenvio)

Escopo: E3.43 e E3.81 (só texto, `R-CUSTO`): linha **CI pago** no tech-lead, devops-engineer, qa-engineer e nos três agentes de stack; detalhe em `## CI pago` de `skills/trabalho-em-paralelo/ritmo-e-corte.md`; CI vermelho no brief de volta da `briefs-e-conferencia`; teste `tests/test_textos_ci_custo.py`. Faz o pedido, nem mais nem menos.

## Cortes conferidos (nenhuma regra sumiu)
- devops-engineer:16, Dependabot (triagem, dev da stack corrige o bump): continua na skill `ci-cd` (linhas 22, 57 a 61) e na ADR 0014.
- devops-engineer:17-18, "o tech-lead o cita" e o caminho repetido: o caminho segue no item 6; a citação segue em "Limites" do tech-lead.
- qa-engineer: ponteiros de seção ("Plano antecipado", "Teste-oráculo do portão"): a skill `qa-testing` segue citada no item 2; "placar e bench, por versão" é dever do tech-lead (Versão), que o mantém.
- tech-lead: "a trava nasce ao tirar o `@expectedFailure`": segue em `skills/qa-testing/SKILL.md` e `docs/melhoria-continua.md`; `--dry-run` do `forge-fechar` é ajuda da ferramenta.
- trabalho-em-paralelo: "Lote por arquivo" movido inteiro (mesmas cláusulas) para `ritmo-e-corte.md`:16, com ponteiro.
- briefs-e-conferencia: exemplos de dúvida do conferente, só ilustração.

## Ferramentas (citadas, não refeitas)
- Teste novo: `python3 -I tests/test_textos_ci_custo.py` → `Ran 5 tests ... OK`.
- `tests/test_metricas_texto.py` (tetos de texto) → OK; `tests/test_orcamento_instrucao.py` → OK; `tests/test_forge.py` (invariantes, regras com ID, teto) → `Ran 11 tests ... OK`.
- CI: sem PR nem run na branch ainda; a suíte completa fica no CI do PR (`forge-testes --listar`: suíte completa).
- Tamanho (M14): 86 linhas em `tests/*.py`, abaixo de 150.

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/ritmo-e-corte.md:18 · regra de texto nova sem medida nem prazo (R-DECISAO); sugestão: citar o aviso de minutos (E3.42) como medida e reverter se as rodadas de push não caírem.

## Sondas
