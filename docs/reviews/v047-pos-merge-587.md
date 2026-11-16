---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-pos-merge-587
commit: 58dfa2ab016fbc10c730b369995b0f1e75b000d6
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047, depois do merge do #587 (E2.413)

Escopo: o que o #587 (`3b1b9e3f`, frontmatter dos agentes) levou à develop, lido contra a develop atual (`befbb464`, mesclada na branch em `ecc92bcb`): `agents/devops-engineer.md`, `bin/forge-testes`, `tests/test_frontmatter_agentes.py` (65 linhas de código e teste, dentro do teto M14). Nenhum dos três mudou depois de `3b1b9e3f`.

## Achados
- A1 (bloqueante) agents/jarvis.md:3 · citado dos pareceres de QA e de segurança desta branch (A1 de cada), com o E2.417: ': ' sem aspas vindo do #584 (e2e32879); test_frontmatter_agentes falha na develop (S1). Não repetido aqui (R-REVIEW).
- A2 (recomendado) bin/forge-testes:125 · a entrada do teste no mapa (8ff9da48) chegou depois do último parecer aprovado (58822e8d) e foi mesclada sem revalidação (R-REVIEW). Revista agora: correta, --listar de agents/ e stacks/*/agents/ traz o módulo.
- A3 (recomendado) tests/test_frontmatter_agentes.py:58 · o caso do ramo de falha cobre só ': '; ' #', valor terminado em ':', aspa que não fecha, falta de name ou description e falta de '---' não têm caso. Um assertTrue por ramo.

## Sondas
- S1 · python3 -I -m unittest discover -s tests -p test_frontmatter_agentes.py (ecc92bcb, develop befbb464) · espera: OK · obtido: FAILED (failures=1), agents/jarvis.md linha 3

## Parecer
Reprovado só pelo A1, que é da develop e não do #587: o teste do #587 faz o que devia e pegou o defeito que o #584 trouxe 6 minutos depois (#587 mesclado 18:34Z, #584 18:40Z; o CI do #584 rodou numa base sem o teste). O conserto é do E2.417; este parecer não o refaz.

O #587 em si: `agents/devops-engineer.md:3` entre aspas simples, sem aspa interna, `tools`, `model` e `skills` intactos. O teto do orçamento do devops-engineer (`test_orcamento_instrucao`) segue vermelho na develop e é do E2.412 (devops-engineer, PR develop-verde-576): citado, não achado deste parecer. `bin/forge-testes:125` entra em `LEITORES_DE_TEXTO`, logo em `CONTEUDO`, que as regras de `agents/` e `stacks/` do mapa levam (A2, revisto aqui). O teste usa só a biblioteca padrão, não roda subprocesso nem lê ambiente; `test_ha_agentes` afirma o mínimo de 12 arquivos (checklist 11).

As fraquezas do detector já registradas pela segurança (A2: aspa dupla interna; A3: `tools` e `model` vazios; A4: indicador no primeiro caractere) e pelo QA (A2, A3) ficam citadas, não repetidas; o A3 deste parecer é só o que falta neles: casos de comportamento dos outros ramos de erro.

Verificação: S1 rodado no merge da develop atual; suíte inteira com o CI (sem PR nesta etapa). Achados recorrentes (PA-7) conferidos: nenhuma classe deste parecer se repete na lista; nenhuma linha AR nova.
