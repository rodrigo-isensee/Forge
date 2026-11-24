---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-d7-rastreio-criterio
commit: 334af9c91abe5c6bbb4a4abe2a5fb4f20933a2bb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E174.35, D7, PR #868, `forge-check criterios`), volta 2

## Parecer
Aprovado no head 334af9c9.

- Delta lido: `forge-check parecer delta` deste arquivo, intervalo 3ed7a573..334af9c9, 3 arquivos no domínio (bin/forge-check, tests/mutantes/v0480-d7-rastreio-criterio-3.json, tests/test_criterios.py); cerca de 12 linhas de código, dentro do H1.
- Segurança A2 (S2) resolvido: `etapas_conferidas` ganhou `selados` opcional; com ele, o `Cobre:` e a `Branch:` saem só do texto de `briefs_selados` pela chave (nome, sha256 do selo), e brief sem selo que confere é pulado. `provas_por_criterio` monta os selados antes e os passa; um conjunto só, sem leitura crua nova.
- Os outros consumidores (`proximo`, bin/forge-check:8252, e o `brief gerar`, :9647) seguem sem o argumento e com o comportamento de antes, como diz o commit: fora do D7, que trata só do `criterios`.
- Teste novo `test_outro_brief_alterado_depois_do_selo_nao_confere_a_etapa` reproduz a S2 (Y intacto: 0 entregues; Y editado para o `Cobre:` de X: rc 1 e 0 entregues), com o sha256 real. Rodei `python3 -m unittest tests.test_criterios`: 9 testes OK.
- Guardas novas com um mutante por linha (D718 a D720, ramo de falha por comportamento); rodei `bin/forge-mutante --ids D718,D719,D720` na spec -3: os três morreram (bin/forge-check:7987, :7988, :8194).
- CI do head: suíte pendente no momento do parecer; `bateria (pareceres)` vermelha pela falta dos pareceres desta volta; `catraca` vermelha pelo R-CONFORMIDADE (mudança em bin/forge-check pede o rótulo `afrouxa-regra` do dono depois do último push), não é defeito do diff. O merge espera a suíte verde, os pareceres e o rótulo.
- A2 e A3 da primeira rodada (recomendados) seguem sem mudança e viram cartão depois do merge.
