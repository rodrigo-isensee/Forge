---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 3ed7a573dc9999ff05f8cc9c485603286c72fc59
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E174.30, D7, PR #868, `forge-check criterios`), volta 1

## Parecer
Aprovado no head 3ed7a573.

- Delta lido: `forge-check parecer delta` deste arquivo, intervalo 64c4dd9b..3ed7a573, 5 arquivos no domínio (bin/forge-check, skills/produto-criterios/SKILL.md, skills/produto-criterios/rastreio.md novo, spec de mutantes, tests/test_criterios.py).
- A1 anterior resolvido: o detalhe do id `C-n` e do `cobre:` foi para `skills/produto-criterios/rastreio.md`, que o passo 4 manda ler; regra intacta, sem teto subido. Rodei `test_metricas_texto`: OK.
- Segurança A1 da rodada: `provas_por_criterio` lê só pelos `briefs_selados` (sha256 conferido), com chave (nome, sha) e selos deduplicados por `dict.fromkeys` na ordem do Histórico; brief reselado só prova pelo selo cujo sha bate. Reaproveita a função existente, sem leitura crua nova; o `try/except` saiu.
- Testes: o selo do teste usa o sha256 real; o caso novo `test_brief_alterado_depois_do_selo_nao_prova` afirma a saída inteira; o caso da linha `id:` agora afirma a lista inteira (QA A1). Rodei `test_criterios`: 8 testes OK.
- Mutantes D73 e D74 redeclarados sobre as guardas novas, um por linha; rodei `bin/forge-mutante --ids D73,D74`: os dois morreram (bin/forge-check:8190 e :8189).
- CI do head: suíte pendente no momento do parecer; `bateria (pareceres)` vermelha pela falta dos pareceres desta volta; `catraca` vermelha só pelo R-CONFORMIDADE (mudança em bin/forge-check pede o rótulo `afrouxa-regra` do dono depois do último push), não é defeito do diff. O merge espera a suíte verde e o rótulo.
- A2 e A3 da rodada anterior (recomendados) seguem sem mudança e viram cartão depois do merge.
