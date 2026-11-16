---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-frontmatter-agentes
commit: b1fa63a82ac4d91e898ef790a248de426c61116f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-15
---
# Review: v047 (E2.163, FRONTMATTER-AGENTES)

Parecer completo (não havia parecer anterior) sobre `bf475209..b1fa63a8`: `agents/devops-engineer.md` (description entre aspas simples), `tests/test_frontmatter_agentes.py` (novo, biblioteca padrão, sem PyYAML) e o fragmento `changelog.d/v047-frontmatter-agentes.md`. Tamanho: 64 linhas de código e teste (M14, dentro do teto).

## Achados
- A1 (recomendado) tests/test_frontmatter_agentes.py:37 · valor que começa com crase, @ ou [ sem fechar passa sem erro (sondado: '`x` y', '@x', '[a: b' dão []), mas é YAML inválido (indicador reservado ou fluxo aberto); sugestão: tratar crase e @ como erro e conferir o fechamento de [ e {.

## Sondas

## Parecer
Aprovado. Faz o que a E2.151 pede, nem mais nem menos (R-REVIEW): a description do devops-engineer fica entre aspas simples, sem aspa simples interna a escapar, e o teste percorre `agents/` e `stacks/*/agents/` (17 arquivos) com mínimo de 12 (checklist 11).

Verificação: `python3 -I tests/test_frontmatter_agentes.py -v` no head: 3 testes OK. Mutante: com o `agents/devops-engineer.md` da base (`bf475209`) numa cópia, o teste falha em `agents/devops-engineer.md` com "linha 3: 'description' tem ': ' ou ' #' sem aspas"; o teste prende o defeito. O ramo de falha também tem caso sintético (`test_detecta_dois_pontos_sem_aspas`).

O verificador é um subconjunto de YAML, declarado no docstring; o A1 aponta casos fora dele que hoje nenhum agente usa (nenhuma description começa com crase ou @), por isso recomendado. A suíte inteira fica com o CI do PR. Sem guarda em código de controle (só `tests/`), sem mutante declarado a exigir.
