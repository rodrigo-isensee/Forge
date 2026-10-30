---
tipo: review
contrato: 1
pedido: pn3-pr-contra-main
branch: melhoria/pn3-pr-contra-main
commit: 34e3c1b5849fe59cfce45ae5560766381539d3d7
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: pn3-pr-contra-main

Diff revisado: `31257c14...34e3c1b` (d916037 script, docs e testes; a7d328e spec de mutantes; 34e3c1b fragmento). Teto M14: 79 linhas de código e teste (`scripts/promover-homolog.py` 24+3, `tests/test_promover_homolog.py` 45+7), um comportamento; dentro do teto. Testes do item: `python3 -m unittest tests.test_promover_homolog`, 32 testes, OK.

## Achados
- A1 (bloqueante) scripts/promover-homolog.py:154 · para em todo "sem parecer" do forge-check, inclusive devops e segurança: com --base main os gatilhos leem a leva inteira e exigem revisao-devops/seguranca de release-<v>, que a release não produz; as promoções reais da 0.30.4 e 0.30.5 parariam (classe: guarda com alcance maior que o requisito)
- A2 (recomendado) scripts/promover-homolog.py:147 · o slug fixo release-<versão> segue a R-FLUXO, mas a 0.30.4 saiu como release-0.30.4b; a parada diz "sem parecer" sem lembrar a convenção; uma linha na mensagem (a branch tem de ser melhoria/release-<versão>) evita a caça

## Conferência das escolhas relatadas (decisão técnica 22:37)
- Só com versão nova: `promover()` chama `conferir_contra_main` quando a versão da ref difere da da base (linha 233); `conferir_versao` já parou antes se ela for menor, então "difere" equivale a "maior". Sem versão nova imprime que não roda. Confere.
- Antes de qualquer `gh`: a conferência roda no passo 3, antes de `comando_gh()` e de `pr_aberto` (linhas 241 e 248); os testes de parada afirmam `gh_chamadas() == []`. Confere.
- No dry-run: roda (só leitura de refs locais); `docs/promocao-integrador.md` e a docstring dizem isso. Confere.
- Slug `release-<versão>`: coerente com a `R-FLUXO` (trava de release, só a `melhoria/release-<versão>` entra); ver A2.
- Parada citando a saída: cita stdout e stderr do forge-check, indentados. Confere. `python -I` no forge-check (classe AR-5 evitada).
- `docs/promocao-integrador.md`: atualizado no passo 3 e no `--dry-run`; o texto promete parar por parecer "de review ou de QA", e o código para também por devops e segurança: a divergência é o A1.

## Evidência do A1 (execução, sem rede)
Clone descartável em `$TMPDIR` com `origin/main`, `origin/homolog` e `origin/develop` postos no estado de cada promoção real, rodando o `promover-homolog.py --dry-run` desta branch:
- Promoção #363 (0.30.6) e #371 (0.30.7): passam ("pareceres de release-0.30.x valem contra a main").
- Promoção #352 (0.30.5): para com `docs/devops: revisao-devops: sem parecer para o pedido release-0.30.5` e `docs/security: revisao-seguranca: sem parecer ... (.github/workflows/release.yml)`; review e QA da release estavam válidos.
- Promoção #343 (0.30.4): mesmo com o slug real (`forge-check pr release-0.30.4b --ref origin/develop --base main`), rc 1 por `revisao-devops` e `revisao-seguranca` (`.github/workflows/ci.yml`).

Causa: o `cmd_pr` calcula os gatilhos de devops e segurança sobre `main...develop`, que reúne todos os PRs da leva; os pareceres de devops e segurança desses PRs existem nos pedidos deles, não no `release-<versão>`. O pedido E1 manda parar por "parecer desatualizado ou faltando" da release; o documento da própria entrega restringe a review e QA. Duas de cinco promoções reais da 0.30 parariam sem defeito, e a única saída seria fabricar pareceres de devops e segurança para a release.

Sugestão (decisão do autor; `bin/forge-check` está fora do escopo): considerar só as linhas de `docs/reviews` e `docs/qa` da saída para a parada, ou chamar a conferência só para os tipos review e QA; e um teste de regressão com um commit em `.github/` na leva que hoje para e depois passa.

## Achado do QA
O A1 do QA (ramo `except` da linha 152 sem teste nem mutante, classe AR-2) já está no parecer de QA; não o repito aqui, e a volta única o leva junto.

## Parecer
Reprovado pelo A1 (defeito de comportamento provado em execução sobre o histórico real). O resto da entrega confere com o E1: ordem antes do `gh`, dry-run, slug, citação da saída e documentação. Sem linha AR nova nesta rodada (decisão técnica 15:28 do T1-CONF-ESCOPO-REV); classe do A1: guarda com alcance maior que o requisito (falso bloqueio).
