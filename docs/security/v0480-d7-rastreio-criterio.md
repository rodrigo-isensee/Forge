---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 334af9c91abe5c6bbb4a4abe2a5fb4f20933a2bb
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E174.37, PR #868, D7), revalidação 2

Volta por delta. Lido: `forge-check parecer delta` de `3ed7a573..334af9c9` (no domínio: `bin/forge-check` em `etapas_conferidas` e `provas_por_criterio`; fora: `tests/test_criterios.py` e `tests/mutantes/v0480-d7-rastreio-criterio-3.json`, lidos para conferir o teste da S2). Já lido nas rodadas anteriores: o resto do diff `aabc476c..3ed7a573`.

Gatilhos: controle do Forge que lê registro de pedido e brief (forge-check), integridade do selo do brief.

**Só aperta ou neutro:** só aperta. `etapas_conferidas` ganha o parâmetro opcional `selados`; com ele (só no `criterios`, `bin/forge-check:8194`), o brief cujo sha256 não confere com o selo deixa de contar. Sem ele (`bin/forge-check:8252` e `:9647`), o caminho é o de antes, sem mudança. Nenhuma guarda, hook, regra ou invariante foi afrouxada.

## Achados anteriores
- A1 (bloqueante): corrigido na rodada 2; S1 de novo no head 334af9c9: rc 1, 0 entregues, 2 não entregues.
- A2 (bloqueante): corrigido. `bin/forge-check:7986-7988` com `selados` pula o brief cujo par (nome, sha256 do selo) não está em `briefs_selados`, que recalcula o sha256 dos bytes (`bin/forge-check:10121`). S2 de novo no head 334af9c9 (`python3 -I sonda_d7.py <caminho absoluto>/bin/forge-check`): antes da edição de Y, C-1 não entregue e C-2 entregue (p1-y.md PQ-1); depois da edição de Y para `Cobre: E1.1`, rc 1, 0 entregues, 2 não entregues (C-1 não entregue, como esperado). Teste: `test_outro_brief_alterado_depois_do_selo_nao_confere_a_etapa` em `tests/test_criterios.py` (o cenário da S2).

## Detalhe
Recomendação não bloqueante, fora do escopo desta entrega: `proximo` (`bin/forge-check:8252`) e `brief gerar` (`bin/forge-check:9647`, K-166) continuam a ler o `Cobre:` do brief cru. Ali o efeito de um brief editado é de planejamento (a etapa some da lista de próximas ou o aviso de etapa coberta aparece), não de prova de critério; o portão do D7 (`criterios`) está fechado. Fica como melhoria, sem achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do head 334af9c9 no momento da leitura: `bateria (passos)`, `bateria (verificações longas)`, `instalação` e `árvore já provada na develop` verdes; `bateria (pareceres)` e `catraca` vermelhos (o parecer reprovado anterior estava na branch); suíte pendente. O merge segue preso ao CI verde. Rodados: `python3 -m unittest tests.test_criterios` (9 OK), S1 e S2. Sem ferramenta externa de varredura (diff só de Python da biblioteca padrão).
