---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-desde-marca
commit: 752cf974ae6918a4e3103c4bc05f2fed13d293e6
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E138.3, placar desde a marca; PR #825)

Escopo: diff `0e59c446..752cf974` (6 arquivos, cerca de 20 linhas de código; H1 dentro do teto). Não há regra "decidida por: leitura" no `docs/engineering/praticas.md` que alcance o diff.

Verificado nesta revisão:
- Classes tocadas, `python3 -m unittest tests.test_forge_mutante.PlacarDaRelease tests.test_changelog.ReleaseAvisaMedidasDaVersao`: 14 testes, OK.
- Spec do item, `bin/forge-mutante -- tests/mutantes/v0480-placar-desde-marca.json`: rc=0, 6 mutantes, todos mortos (placar-mutacao.py:61 e :95; forge-changelog:284 e :285).
- Na develop real, o `git log -1 -G '"version"' HEAD -- .claude-plugin/plugin.json` acha 2b9cd322 (marca da 0.47.15), sem tag nele: o caso que o item corrige existe.
- CI do PR no head 752cf974 vermelho (citado, não rerrodado): suíte parte 4/5 (run 45296945035, Python 3.12 e 3.14) e catraca (run 45296944993); o job de pareceres falta só pelos pareceres.

## Achados
- A1 (bloqueante) tests/mutantes/v047-placar-mutacao.json:57 · O `de` do mutante "o aviso do --desde é impresso" saiu da fonte: a chamada ganhou o argumento `commit`. A suíte parte 4/5 falha em `ConferirTodas.test_toda_spec_do_forge_confere_com_a_fonte_fora_as_pendentes` (run 45296945035). Alinhe `de` e `para` à linha nova no mesmo commit.
- A2 (bloqueante) tests/mutantes/v046-mutacao-bench-2.json:19 · O `de` do mutante "sem tag anterior, o comando do placar pede a tag" foi apagado de bin/forge-changelog, e o teste citado (`test_sem_tag_pede_a_tag_anterior_a_mao`) foi renomeado; mesma falha da suíte (run 45296945035). Realinhe-o à guarda nova ou aposente-o com motivo.
- A3 (bloqueante) bin/forge-changelog:282 · Catraca (run 45296944993) recusa por R-QA: a guarda `tag.returncode == 0 and tag.stdout.strip()` (linha 282 da base) foi apagada sem mutante declarado nem isenção. `bin/forge-mutante --cobertura --base 0e59c446` lista o que falta; declare ou isente com motivo.
- A4 (recomendado) scripts/placar-mutacao.py:61 · A isenção compara com a marca do HEAD no momento da rodada: se o placar rodar depois do commit da marca nova, a marca anterior passada em --desde volta a avisar "não é tag". Sugestão: aceitar o commit que mudou a versão do manifesto antes da marca do HEAD.

## Sondas

## Parecer
Reprovado. A lógica está correta e os testes novos matam os 6 mutantes do item, mas o diff deixou duas specs antigas com o `de` fora da fonte (A1, A2) e uma guarda apagada sem mutante nem isenção (A3). Por isso a suíte do CI e a catraca estão vermelhas no head, e o merge não passa. O conserto fica só nas specs: alinhar as duas e declarar ou isentar a guarda apagada. Depois disso, `bin/forge-mutante --cobertura --base 0e59c446` e as duas specs rodadas pelo autor fecham a volta. A4 não bloqueia e vira cartão depois do merge.
