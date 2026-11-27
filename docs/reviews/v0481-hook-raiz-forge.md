---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-hook-raiz-forge
commit: 1644a83f0b3c4ed16e9fd5c8b49b71d4c6288980
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E37.19, HOOK-NAO-PROTEGE-RAIZ-DO-FORGE, PR #930, volta 4)

Esta é a revalidação por delta (H3) do head `1644a83f`, sobre o parecer aprovado de `aa347213`. O critério é o mesmo das rodadas anteriores, sem `critério mudou:`.

## Achados
- A1 (recomendado) hooks/conformidade.py:4317 · vem da 1ª rodada e fica fora do delta: `rm -rf .` na raiz passa (rc 0), como no projeto. Não é regressão; vira cartão para os dois.
- A2 (bloqueante) hooks/conformidade.py:4357 · o teste novo `"*" in palavra_juntada(caminho).split("/")[0]` recusa qualquer variável colada sem valor calculado, inclusive em linhas que não citam nenhuma entrada (S1 a S4), também na cópia de wt/. A docs diz que essa cópia segue livre. Isso é regressão do delta.

## Sondas
- S1 · `for f in a b; do printf x > $f.log; done`, cwd numa cópia `wt/x` · espera: rc 0 (é livre em `aa347213`) · obtido: rc 2, "variável sem valor calculado numa linha que cita o que roda fora do sandbox"
- S2 · a mesma linha com cwd na raiz da sessão · espera: rc 0 (a linha não cita entrada) · obtido: rc 2, a mesma mensagem
- S3 · `printf x > ${TMPDIR}x/y`, cwd em `wt/x` · espera: rc 0 · obtido: rc 2
- S4 · `for n in 1 2; do printf x > saida-$n.txt; done`, cwd em `wt/x` · espera: rc 0 · obtido: rc 2

## Parecer
**Reprovado pelo A2.** O resto do delta está correto.

- **Delta lido** (`forge-check parecer delta docs/reviews/v0481-hook-raiz-forge.md`, intervalo `aa347213..1644a83f`):
  - `hooks/conformidade.py:4357-4358` e a docstring.
  - As fixtures S10, S11 e S12.
  - Os mutantes: o RD4 foi reancorado, e o RD10 e o RD11 são novos.
  - O piso de recusas passa a 37 em `tests/test_hooks.py:2931`.
  - `docs/hooks.md:69`.
- **A2, como foi provado:**
  - Gravei as quatro sondas como fixtures `-libera` temporárias (removidas, nada commitado) e rodei `tests.test_hooks.Hooks.test_fixtures_da_raiz_do_forge` sob `trava-teste-a.lock`.
  - Em `1644a83f`, as quatro recusam. Com o `hooks/conformidade.py` de `aa347213`, as quatro passam (só S10, S11 e S12 falham, como se espera).
  - A mensagem também mente: diz "numa linha que cita o que roda fora do sandbox", e a linha não cita nada.
  - `docs/hooks.md:69` não descreve esse alcance. O texto diz "a variável colada no primeiro componente (`${d}s/pre-push`) recusa" sem dizer que é toda variável colada, e a mesma página diz "A cópia de `~/.forge-contrib/wt/` segue livre".
  - O `$f.log` dentro de um laço é comum no trabalho dos agentes nas cópias de `wt/`.
- **Sugestão ao autor:** recusar só quando o primeiro componente lido como curinga puder casar uma entrada em vigor (`glob_casa(componente, nome)` para `.githooks`, `.git`, `.devcontainer`, `.devcontainer.json` e `.claude-plugin`, como o `nome_da_c18` faz). Assim `*s` (S12) recusa, e `*.log`, `saida-*.txt` e `*x` passam. As quatro sondas acima entram como fixtures `-libera` (o piso de liberam sobe para 25), com um mutante que troca o casamento por `True`.
- **O que está certo no delta:** o `palavra_juntada(t)` sobre os textos largos fecha S10 e S11 sem falso positivo, porque só conta quando o texto cita a entrada.
- **Mutantes:** rodei `bin/forge-mutante` em `1644a83f`, sob a trava: RD10 morreu em :4357, RD11 em :4358 e RD4 em :4357.
- **Tamanho (H1):** o delta tem 3 linhas de código.
- **Commits (item 9):** `aa064b86` (fix) e `1644a83f` (test) seguem Conventional Commits em português, com a etapa.
- **CI (`gh pr checks 930` no `1644a83f`):** verdes a suíte 3.12 (partes 1 a 5), `teto de pulados (python 3.12)`, `instalação (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)` e `árvore já provada na develop`. Ficam de fora `bateria`, `bateria (pareceres)` e `catraca`.
- ci: 1644a83f0b3c4ed16e9fd5c8b49b71d4c6288980 verde
