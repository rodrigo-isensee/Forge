---
tipo: review
contrato: 1
pedido: release-0.33.0
branch: melhoria/release-0.33.0
commit: c004a70a01459b483322b006a012bac382bb36e6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-05
---
# Review: release-0.33.0

Review da leva da 0.33.0 contra a main 0.32.0 (`1b62cfd..c004a70`): os 10 PRs da develop 360186e (#436 a #445) e o commit de release. Cada PR já passou pelos próprios portões; aqui só a coerência da leva (E1, E2, E3), sem refazer o review de cada um.

## Achados
- A1 (recomendado) bin/forge-check:110 · o texto de ajuda do TEMPO-B2 (#445) diz "só pareceres e quadro" depois da entrega conferida, mas o código (linha 768) também libera docs/ux/ (#442) e o fragmento do changelog; alinhar o texto ao código num PR seguinte.
- A2 (recomendado) bin/forge-check:94 · a ajuda do `delta` lista as pastas fora do delta sem docs/ux/, que o #442 pôs em LIVRES e o fragmento do PARECER-UX-LIVRE anuncia; acrescentar a pasta ao texto (também na linha 6277).
- A3 (recomendado) CHANGELOG.md:11 · duas entradas da leva afrouxam controle (E8 do conferente e PREPUSH-SO-DOCS); o PR homolog → main (E1.7) deve destacá-las no corpo para o dono ver ao mesclar.

## Parecer
Aprovado.

**Escopo da leva.** `git log 1b62cfd..c004a70` traz exatamente os 10 PRs do E1 (#436 a #445) e o commit de release; nada fora do escopo confirmado pelo dono em 2026-11-05 07:30. O #443 (LOTE-TEXTOS-033-VOLTA) devolve o que o #434 reverteu na 0.32.0, coerente com a decisão daquela release.

**Arquivos que mais de um PR tocou** (lidos só onde se juntam):
- `bin/forge-check` (#437, #439, #441, #442, #445): a escolha do parecer pela branch (#439, `branch_da_ref`) é a base que o E10 do #445 reusa com o `headRefName` do PR mesclado (linhas 667, 681, 758, 897-902); a exigência de entrega conferida do TEMPO-B2 (#445, linha 768) usa `LIVRES`, que já inclui docs/ux/ do #442, mais o fragmento do pedido, então um commit só em docs/ux/ não derruba nem o parecer nem a conferência; a falha do git que reprova (#437) não conflita com o ato-github do #445, que tem caminho próprio sem diff. Sem conflito lógico; só o texto de ajuda ficou atrás do código (A1, A2).
- `hooks/conformidade.py` (#438, #444): o bloqueio do `gh pr merge --admin` e do merge por API vale para todo papel; a leitura de `git branch`/`git worktree list` do conferente é gramática de leitura de git, sem interseção com o `gh`. Sem conflito.
- `agents/conferente.md`, `docs/hooks.md`, `skills/briefs-e-conferencia/SKILL.md`, `agents/jarvis.md` (#441, #443, #444, #445): os textos se somam (mensagem só com cabeçalho e hash, nova ordem da conferência, leituras de git liberadas); nenhum contradiz o outro.
- Testes compartilhados (`tests/test_forge.py`, `test_conferencia_base_dono.py`, `test_volta_por_delta.py`, `test_testes_tocados.py`, `test_mensagem_conferente.py`): ajustes do #445 sobre o que o #437 e o #441 criaram; a suíte inteira é do QA (E1.5) e o CI do PR.

**CHANGELOG e versão (E2, E3).** A seção `## [0.33.0] - 2026-11-05` tem as 15 entradas dos 10 fragmentos, texto idêntico, agrupadas em Adicionado (1), Alterado (7) e Corrigido (7); `## [Não publicado]` ficou vazio e `changelog.d/` só com o README (`bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes"). Versão 0.33.0 em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json`; o `marketplace.json` não carrega versão, como o teste exige. Minor está certo: melhorias compatíveis e correções, nenhuma quebra para os projetos (o pre-push do modelo só deixa de rodar o local em envio só de texto; o CI segue completo).

**Testes rodados (D-5, só o que o commit de release toca):** `python3 -m unittest tests.test_changelog` (46 testes, OK) e `tests.test_forge.Manifestos` (3 testes, OK, inclui versão do plugin.json igual à primeira do CHANGELOG).

**Outros portões:** segurança (E1.3), devops (E1.4, workflow Release do #440) e QA (E1.5) têm parecer próprio; não refeitos aqui. A1 a A3 são recomendações e não devolvem.
