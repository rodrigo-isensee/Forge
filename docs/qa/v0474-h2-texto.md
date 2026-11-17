---
tipo: qa
contrato: 1
pedido: v0474
branch: melhoria/v0474-h2-texto
commit: 5a590bf3e8465df0b7a283fefe871ef504b50ad4
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-17
---
# QA: v0474 H2 no texto (E2.44)

Entrega de texto (H2, o autor fica com o item até o merge), sem código de controle: não há mutante a declarar nem teste novo de comportamento; a obrigação testável são os invariantes novos em `tests/config.json` (R-BRIEF).

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| 13 invariantes novos casam com o texto (jarvis 3, tech-lead 2, SKILL 1, autor-ate-o-merge.md 7) | regex de cada um contra o arquivo no head | trecho ausente | passou (13 de 13) |
| Cada invariante falha se o trecho sair | sonda: remove o trecho casado e reaplica a regex | trecho removido | passou (13 de 13 falham sem o trecho) |
| Regras com ID e motivo dos novos | `-k Invariante -k RegrasInviolaveis` | `invariantes_motivo` | passou |
| Neutralidade | `-k Neutralidade` | termo de projeto | passou |
| Orçamento de instrução, núcleo do Jarvis, métricas de texto, frontmatter | 4 módulos | teto de caracteres | passou |

## Cenários e resultado real
- `python3 -m unittest tests.test_orcamento_instrucao tests.test_jarvis_nucleo tests.test_metricas_texto tests.test_frontmatter_agentes`: Ran 56 tests, OK.
- `python3 -m unittest tests.test_forge -k Invariante -k RegrasInviolaveis -k Neutralidade`: Ran 9 tests, OK.
- Sonda dos invariantes: diff de `invariantes` contra a base ba968580 deu 13 novos, todos com `casa` e `falha sem trecho`.
- A suíte inteira roda no CI do PR (R-QA); aqui só os arquivos tocados.
