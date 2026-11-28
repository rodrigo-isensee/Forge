---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0480-d7-rastreio-criterio
commit: e2913240f744397a877fae759260d30be43db911
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0481 (E1.9, PR #868, D7), regravação no head com a develop atual

Volta por delta. Lido: `forge-check parecer delta` de `334af9c9..e2913240` (base trazida de `a27eab7` para `8d7914b`, sem o que veio da develop): nenhum arquivo do domínio mudou, `revalida: não`. Fora do domínio, lidos: `tests/test_criterios.py` e `tests/mutantes/v0480-d7-rastreio-criterio.json` (1467c342, o teste novo do QA para o mutante D73, que só aperta), `tests/pesos-d4.json` (peso do `test_criterios`). O merge `e2913240` é limpo (`git diff-tree --cc` sem trecho de conflito). Já lido nas rodadas anteriores (v0478, E174.37): o diff `aabc476c..334af9c9`.

Gatilhos: controle do Forge que lê registro de pedido e brief (forge-check), integridade do selo do brief.

**Só aperta ou neutro:** só aperta, inalterado desde a rodada anterior. `etapas_conferidas` com `selados` (só no `criterios`) descarta o brief cujo sha256 não confere com o selo; `proximo` e `brief gerar` seguem pelo caminho de antes. O delta desta rodada é neutro (base trazida) ou aperta (teste novo). Nenhuma guarda, hook, regra ou invariante foi afrouxada.

## Achados anteriores
- A1 (bloqueante): corrigido (rodada 2), sem mudança no domínio desde então.
- A2 (bloqueante): corrigido (rodada 3), sem mudança no domínio; o teste novo `test_brief_alterado_nao_prova_mesmo_com_outro_brief_intacto_conferindo_a_etapa` reforça o mesmo portão.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI do head e2913240 no momento da leitura: `bateria (passos)`, `catraca` e `instalação` verdes; `bateria (verificações longas)`, `bateria (pareceres)` e `árvore já provada na develop` pendentes. O merge segue preso a todos os checks verdes. Rodado: `python3 -m unittest tests.test_criterios` (10 OK). Sem ferramenta externa de varredura (diff só de Python da biblioteca padrão).
