---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-meta85-recomendado
commit: cdea2f3807f456c317365703ce96398ce5cea80d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-19
---
# Review de segurança: v0479-meta85-recomendado

Pedido v0478, etapa E35.3 (META85-RECOMENDADO-VIRA-CARTAO, E35.1). Diff `eca1d21b..cdea2f38`: 17 arquivos, só texto de regra, agentes, skills, modelos de parecer, `tests/config.json` (invariantes) e `tests/test_achado_teto_doc.py`. Nenhum arquivo de `hooks/`, `bin/`, `.githooks/` nem `tests/catraca.py`.

## Gatilhos
Gatilhos: regra do portão de segurança (`docs/regras/R-SEGURANCA.md`, `agents/security-engineer.md`, modelos de parecer de segurança)

## Achados

## Sondas

## Detalhe dos achados
Ponto central conferido (decisão do dono E35: na segurança o recomendado continua corrigido antes):
- `docs/regras/R-SEGURANCA.md:17`: o recomendado "volta e é corrigida antes do merge"; o texto anterior dizia "não devolve". Endurece, não afrouxa.
- `docs/regras/R-REVIEW.md:16`: "a de review e QA vira cartão depois do merge; a de segurança é corrigida antes", protegida em `tests/config.json` (invariantes).
- `agents/security-engineer.md:17`: "o seu `recomendado` volta e é corrigido antes do merge".
- `agents/jarvis.md:30`: "recomendado de review e QA vira cartão, o de segurança volta".
- `skills/briefs-e-conferencia/SKILL.md:24` e `autor-ate-o-merge.md:9`: o recomendado da segurança entra no brief de volta por `--incluir <parecer>:A<n>` (invariante nova em `tests/config.json`); o mecanismo existe em `bin/forge-check:89,3856,9914` e aceita `A<n>` recomendado.
- `docs/security/_modelo.md:19` e o modelo do projeto: idênticos, com a regra da segurança.

Varredura de texto residual (agents, skills, docs/regras, templates, stacks, bin, hooks) por "não devolve", "não geram volta", "Recomendação não entra", "recomendado incluso": nenhum texto deixa recomendado de segurança sem correção. Resta `templates/projeto/docs/devops/_modelo.md:17` ("o resto é `recomendado` e não devolve"), fora deste diff e do portão de segurança.

Remoções de texto sem efeito de segurança: em `agents/security-engineer.md`, "teto que o `forge-check docs` e o pre-push barram" (a barreira segue na ferramenta, só sai a menção); em `agents/jarvis.md`, a repetição "retomada por `SendMessage` (o hook `agentes` avisa)" (o passo segue com `SendMessage`); em `agents/tech-lead.md`, o caminho do eval passa a `tests/evals/`. Nenhuma invariante removida (o diff de `tests/config.json` só acrescenta).

Neutralidade (`R-NEUTRO`): textos sem nome de projeto nem de stack.

Suíte: inteira só no CI; rodei o teste novo (`tests/test_achado_teto_doc.py`, 8 testes, OK) e, para tirar a dúvida das remoções, `tests.test_forge` nas classes RegrasInviolaveis, Neutralidade, NeutralidadeDoNucleo, Agentes, RegrasComId e ModeloDeSegurancaNoProjeto (25 testes, OK). Sem PR, sem CI do head a citar.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática do diff; sem segredo nem dependência nova, então sem varredura de segredos ou dependências aplicável.
