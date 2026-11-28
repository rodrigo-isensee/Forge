---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0474-texto-dir34-h1
commit: 593ff0351231f2d77f211fba7bff2b05b41f5636
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0474, texto do H1 e da diretriz 34 (E2.22)

Entrega de texto com teste: `TetoPorPr` reescrito em `tests/test_forge.py` para o H1, invariantes novos em `tests/config.json`, fixture 34 em `tests/fixtures/diretrizes-do-dono.json`. Sem UI: E2E e acessibilidade não se aplicam. Base `01b4e8ae`, head `593ff035`.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| H1: até 150 linhas de código, fora testes e documentação | `TetoPorPr.test_teto_do_h1_no_tech_lead_e_na_skill` | texto do tech-lead e da skill sem o resumo antigo ("Não é trava por volume") | passou no head; cai na base |
| H1: detalhe da contagem no auxiliar | `TetoPorPr.test_o_auxiliar_conta_so_codigo` | `tests/` inteira fora da contagem; sem `tests/*.py` e `tests/config.json` | passou no head; erro na base (arquivo não existe) |
| H1 no Jarvis, tech-lead e skill, classe única em `hooks/` | `TetoPorPr.test_orientacao_e_classe_unica_no_jarvis_no_tech_lead_e_na_skill` | `400 linhas` ausente | passou no head; erro na base |
| Diretriz 34 (não trava, versão quando ficar pronta) | fixture 34 + `DiretrizesDoDonoNaRWip` | trechos da fixture presentes na fonte | passou |
| Invariantes novos (`tests/config.json`) | `RegrasInviolaveis`, `RegrasComId`, `Neutralidade`, `NeutralidadeDoNucleo` | texto protegido não some | passou |

## Vermelho antes do verde
O TetoPorPr prova o H1. Duas formas:

1. `bin/forge-testes --vermelho 01b4e8ae --modulos test_forge` (timeout do Bash em 600000 ms; também com `--prazo 2400`): saída
```
vermelho: base=01b4e8aec3cd head=593ff0351231 módulos=test_forge (restrito por --modulos)
revertidos à base: agents/jarvis.md, agents/tech-lead.md, changelog.d/v0474-texto-dir34-h1.md, skills/engineering-practices/SKILL.md, skills/engineering-practices/tamanho-por-item.md, skills/falar-com-o-dono/nao-trava.md, skills/trabalho-em-paralelo/SKILL.md, skills/trabalho-em-paralelo/ritmo-e-corte.md, templates/projeto/.github/pull_request_template.md, templates/projeto/CLAUDE.md
mantidos no HEAD: tests/config.json, tests/fixtures/diretrizes-do-dono.json, tests/test_forge.py
test_forge · sem veredito (prazo, sinal ou executor sem registro em H,B)
sem veredito: volta ao autor; não vale como vermelho nem como já falhava.   (rc=2)
```
O módulo `test_forge` inteiro não termina em 600 s por lado neste ambiente (rodado direto numa cópia: 9m20 de relógio e 1m13 de CPU, morto pelo meu timeout de 560 s). Esse resultado é sem veredito e não vale como vermelho; fica registrado como limite da ferramenta nesta máquina (a bateria completa roda no CI).
2. Equivalente manual, só da classe: cópia de `01b4e8ae` (textos da base) com `tests/test_forge.py` e `tests/config.json` do head, `python3 -m unittest tests.test_forge.TetoPorPr`: `FAILED (failures=2, errors=2)` (`test_o_auxiliar_conta_so_codigo` ERROR, `test_orientacao_e_classe_unica...` ERROR, `test_teto_do_h1_no_tech_lead_e_na_skill` FAIL em `agents/tech-lead.md` e em `skills/engineering-practices/SKILL.md`). No head: `Ran 4 tests ... OK`.

## Execução (head 593ff035)
- `python3 -m unittest tests.test_orcamento_instrucao tests.test_jarvis_nucleo tests.test_metricas_texto tests.test_modelos_projeto tests.test_frontmatter_agentes`: `Ran 76 tests in 0.546s`, `OK`.
- `tests.test_forge.DiretrizesDoDonoNaRWip`, `Neutralidade`, `NeutralidadeDoNucleo`: `Ran 8 tests`, `OK`; `RegrasInviolaveis`, `RegrasComId`: `Ran 6 tests`, `OK`.
- A suíte inteira roda no CI do PR (`bateria`); não rerrodada aqui.
- Mutação: não se aplica (texto, sem código de produção no diff; o que o teste guarda é o texto, e o vermelho acima o prova).
