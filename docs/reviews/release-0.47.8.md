---
tipo: review
contrato: 1
pedido: release-0.47.8
branch: melhoria/v0478-release-0478
commit: 3a621ba09372145609a045581aba0e79c85f6688
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: release-0.47.8

Code review da versão 0.47.8 inteira no head 3a621ba0 (marca da release na branch melhoria/v0478-release-0478, base develop 2904a68a), para integrar na develop e promover à homolog (v0478 E27.2). Os dois pareceres, `docs/reviews/v0478-release-0478.md` e `docs/reviews/release-0.47.8.md`, têm o mesmo veredito e o mesmo conteúdo.

## Achados
- A1 (recomendado) scripts/placar-mutacao.py:94 · o placar roda o forge-mutante com capture_output e descarta o stderr: spec com rc diferente de zero sai só `rc=2` e contagens zeradas, sem a causa (placar.json na 0.47.8). Imprimir a última linha do stderr na linha `spec:` quando rc != 0.

## Parecer
Aprovado.

- Ponto de partida: o brief cita `v0.47.6..3a621ba0`, mas a 0.47.7 já está publicada; o intervalo da 0.47.8 é `v0.47.7..3a621ba0`. A tag `v0.47.7` (merge na main) não é ancestral do head; a marca da 0.47.7 na develop, 4182a6b9 (#672), é, e `git diff --stat 4182a6b9 v0.47.7` é vazio (mesma árvore). Os itens #667 e #668 citados no brief são da 0.47.7, já revisada em `docs/reviews/release-0.47.7.md`.
- Leva: `git log --first-parent 4182a6b9..3a621ba0` traz 9 entradas: devops #675 (544b659e), token do bot #676 (fec4dd60), T1 portão #677 (7468d9fb), mutante pulado #678 (ec7b63d7), índice do Forge #680 (1621a5c7), mensagem da promoção #679 (82bb9e57), develop verde #681 (0c47762a), guardas do forge-check #683 (2904a68a) e a marca (3a621ba0). `git diff --stat 4182a6b9..3a621ba0`: 68 arquivos, 2847+/79-.
- Pareceres dos itens (não refeitos, `R-REVIEW`): `parecer: aprovado` em review, QA e segurança para v0478-devops-lote, v0478-cobertura-c1 (mais devops), v0478-mutante-pulado, v0478-indice-forge, v0478-fechar-mensagem e v0478-guardas-forge-check; review e QA para v0478-develop-verde (pesos e spec, sem código); review para v0478-token-bot (só documentação).
- Junção: os arquivos em comum entre itens são `bin/forge-testes` (#675, #680, #683) e `tests/pesos-d4.json` (#675, #681, #683); o item develop verde (#681) é justamente o acerto da junção depois do vermelho em 82bb9e57, e o CI da develop em 0c47762a é `success`.
- CI da develop na base 2904a68a: `failure`, só em "suíte (push na develop, python 3.12, parte 1/5)": `suite-partes: processo 2 morto pelo sinal 9` (rc -9, 0 testes) e `o discover acha 959 testes e os processos rodaram 491`; a mesma parte em python 3.14 e as outras 9 partes estão verdes. Processo morto por SIGKILL do runner, sem teste vermelho: infraestrutura, não defeito provado dos itens. A prova da integração é o CI do PR da marca para a develop, obrigatório para o merge (`R-REVIEW`); a suíte local falha por ambiente (sandbox: /proc e gh) e não foi rerrodada.
- Marca (3a621ba0, 11 arquivos): `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.8"`; `CHANGELOG.md` com `[Não publicado]` vazio (linha 5) e `[0.47.8] - 2026-11-18` (linha 7) acima de `[0.47.7]` (linha 24), em português, com Adicionado, Alterado e Corrigido.
- Fragmentos: os 8 fragmentos apagados na marca (lidos em 3a621ba0^) têm 12 linhas `- `, e cada uma aparece uma vez no `CHANGELOG.md` (`grep -cxF`: 1 nas 12); `changelog.d/` só traz o `README.md`; `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes".
- Placar de mutação (`/root/.forge-contrib/placar-0478.log`): 47 mortos, 0 sobreviventes nas 8 specs novas; a spec fixa `tests/mutantes/placar.json` saiu `rc=2` com contagens zeradas. Não é defeito da release: as 8 âncoras `de` da spec casam uma vez cada no head, a spec não mudou desde v0.47.7, e `bin/forge-mutante --processos 1 tests/mutantes/placar.json` no head 3a621ba0, árvore limpa, dá rc 0 e os 8 mutantes `morreu` (bin/forge-check:2432 e 2419, hooks/conformidade.py:3208, hooks/parecer.py:859, hooks/doutor.py:116). O rc 2 sem veredito só sai das recusas do forge-mutante (árvore mudou durante a rodada, árvore suja com spec fora do commit, spec ilegível), cuja mensagem vai ao stderr, que o placar descarta (A1); a causa da rodada original não é recuperável pelo log. Defeito da ferramenta (falta de diagnóstico), não da versão.
- CI do head: `gh run list --commit 3a621ba0` vazio (sem PR ainda); a suíte inteira fica no CI do PR da marca.
