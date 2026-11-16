---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-frontmatter-agentes
commit: 58822e8d07d7943af1475f73df344b9704f51bb6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.163, FRONTMATTER-AGENTES)

Revalidação por delta (E2.295) no head `58822e8d`, ao fim deste parecer. Parecer original: completo (não havia parecer anterior) sobre `bf475209..b1fa63a8`: `agents/devops-engineer.md` (description entre aspas simples), `tests/test_frontmatter_agentes.py` (novo, biblioteca padrão, sem PyYAML) e o fragmento `changelog.d/v047-frontmatter-agentes.md`. Tamanho: 64 linhas de código e teste (M14, dentro do teto).

## Achados
- A1 (recomendado) tests/test_frontmatter_agentes.py:37 · valor que começa com crase, @ ou [ sem fechar passa sem erro (sondado: '`x` y', '@x', '[a: b' dão []), mas é YAML inválido (indicador reservado ou fluxo aberto); sugestão: tratar crase e @ como erro e conferir o fechamento de [ e {.

## Sondas

## Parecer
Aprovado. Faz o que a E2.151 pede, nem mais nem menos (R-REVIEW): a description do devops-engineer fica entre aspas simples, sem aspa simples interna a escapar, e o teste percorre `agents/` e `stacks/*/agents/` (17 arquivos) com mínimo de 12 (checklist 11).

Verificação: `python3 -I tests/test_frontmatter_agentes.py -v` no head: 3 testes OK. Mutante: com o `agents/devops-engineer.md` da base (`bf475209`) numa cópia, o teste falha em `agents/devops-engineer.md` com "linha 3: 'description' tem ': ' ou ' #' sem aspas"; o teste prende o defeito. O ramo de falha também tem caso sintético (`test_detecta_dois_pontos_sem_aspas`).

O verificador é um subconjunto de YAML, declarado no docstring; o A1 aponta casos fora dele que hoje nenhum agente usa (nenhuma description começa com crase ou @), por isso recomendado. A suíte inteira fica com o CI do PR. Sem guarda em código de controle (só `tests/`), sem mutante declarado a exigir.

## Revalidação (E2.295, head 58822e8d)
Delta lido: `forge-check parecer delta docs/reviews/v047-frontmatter-agentes.md`, intervalo `b1fa63a8..58822e8d`, sem o que veio da develop; no domínio só `agents/devops-engineer.md`, a description encurtada (b33bed29: "do time" e "escrita por" saem), que conserta o B-v047-1 do QA (agente acima do teto do orçamento). Sentido e gatilhos de uso mantidos; segue entre aspas simples, sem aspa interna.

Verificação: `python3 -m unittest tests.test_frontmatter_agentes tests.test_orcamento_instrucao` no head: 11 testes OK. Mutante: com a description de `b1fa63a8` no lugar, `test_nenhum_agente_passa_do_teto` falha (`devops-engineer: agente_caracteres = 505...`); restaurado o arquivo, verde. O A1 segue recomendado (o teste não mudou). Suíte inteira com o CI do PR. Aprovado no head 58822e8d.
