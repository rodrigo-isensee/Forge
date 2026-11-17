---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0474-texto-dir34-h1
commit: 593ff0351231f2d77f211fba7bff2b05b41f5636
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (texto da diretriz 34 e do H1)

Etapa E2.20. Delta revisado: `01b4e8ae..593ff035`, 3 commits (a0fb32b4 DIR-34-NO-PLUGIN, 167b75ba H1-texto, 593ff035 três trechos alinhados), 13 arquivos, +137/-22.

## Achados
- A1 (recomendado) agents/jarvis.md:37 · a ordem do dono (17/11 10:18) diz "até 2 por dia, ou mais se couber"; aqui, no tech-lead.md:43 e no templates/projeto/CLAUDE.md:14 só "até 2 por dia", que lê como teto; o "ou mais se couber" só está no ritmo-e-corte.md:23.

## Sondas

## Parecer
Aprovado.

- **Escopo (R-REVIEW):** os três commits batem com os itens do brief: Jarvis "Não trava" com ponteiro para `skills/falar-com-o-dono/nao-trava.md`; versão quando ficar pronta, até 2 por dia, no `ritmo-e-corte.md` e no tech-lead; invariantes e fixture 34; H1 no tech-lead e na skill, com o detalhe em `skills/engineering-practices/tamanho-por-item.md`; `TetoPorPr` reescrito; e os trechos alinhados na `trabalho-em-paralelo/SKILL.md`, no modelo de PR e no `CLAUDE.md` do modelo. O texto segue a ordem do dono da diretriz 34 (17/11 10:18) e a decisão do H1 (17/11 11:15).
- **Nada saiu nem afrouxou:** o diff de `tests/config.json` só acrescenta trechos em `invariantes`, `invariantes_motivo` e `invariantes_motivo_trecho`; nenhum trecho removido, só o `porque` do "Ritmo diário" no modelo ajustado à diretriz 34. Os textos que saíram: "Não é trava por volume" e a orientação do M14 viram o H1, mais estrito (teste deixa de contar, e passar do teto só se cortar mais deixa a suíte vermelha), por decisão do dono de 17/11 11:15; "de manhã, um PR só" vira a diretriz 34 pela ordem do dono; a linha do placar de mutação, do bench e do `decisoes --sem-cartao` mudou do tech-lead para o `ritmo-e-corte.md:26`, inteira, com ponteiro no tech-lead (diretriz 25).
- **Tetos de texto:** `tests.test_orcamento_instrucao`, `test_jarvis_nucleo` e `test_metricas_texto` verdes (abaixo). jarvis.md 7244 B, tech-lead.md 8573 B.
- **Tamanho (H1):** zero linhas de código (`bin/`, `hooks/`, `scripts/`, `.github/`, `.githooks/`) no `git diff --numstat --no-renames 01b4e8ae...593ff035`; só texto, `tests/config.json`, fixture e `tests/test_forge.py`.
- **Teste:** `TetoPorPr` troca as asserções do M14 pelas do H1 e ganha `test_o_auxiliar_conta_so_codigo`, que afirma a contagem nova e a ausência de `tests/*.py` e `tests/config.json` no auxiliar; o `assertNotIn("Não é trava por volume")` relido: o texto procurado de fato saiu do tech-lead e da skill (checklist 11).
- **Comandos rodados no head 593ff035:** `python3 -m unittest tests.test_orcamento_instrucao tests.test_jarvis_nucleo tests.test_metricas_texto tests.test_modelos_projeto tests.test_frontmatter_agentes`: `Ran 76 tests ... OK`; `python3 -m unittest tests.test_forge -k invariante -k Invariante -k TetoPorPr -k Neutralidade`: `Ran 12 tests ... OK`. A suíte inteira fica no CI do PR (sem PR nesta etapa).
- **Commits:** Conventional Commits em português, um por item, com o pedido e a etapa na mensagem.
