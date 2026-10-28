---
tipo: review
contrato: 1
pedido: guarda-sem-mutante
branch: melhoria/guarda-sem-mutante
commit: 65a62c9677469556e2939392b61d3097682341cd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-28
---
# Code review: GUARDA-SEM-MUTANTE, PR 1 (`bin/forge-mutante --cobertura`, núcleo Python)

Diff revisado: `991cd092b42c88d86a16912ff8ddc1b72b8da026...7c86f530cb491355a40f2699215ebd45f3d2c5d4` (4 commits). Referências: as 5 linhas DECISÃO TÉCNICA da ata `docs/alinhamentos/2026-10-28-revisao-desenho-guarda-sem-mutante.md` (fora do repositório, em `~/.forge-contrib/docs/alinhamentos/`), com a linha do PR 1 da tabela como escopo. Shell sai como `não coberto` até o PR 2: é o plano e não gera achado. Primeira rodada, sem delta.

## Achados
- A3 (recomendado) bin/forge-mutante:417 · o teto de 300 arquivos só é conferido depois de mudancas() rodar um git diff por arquivo; conferir o --name-status antes do laço evita trabalho (T7). Não devolve
- A4 (recomendado) bin/forge-mutante:363 · SyntaxError do texto mutado sai como rc 2 sem o id do mutante. Não devolve
- A5 (recomendado) bin/forge-mutante:382 · `apagadas` indexado pelo texto esconde a 2a guarda apagada na saída (o rc fica certo). Não devolve

## Revalidação por delta (volta 2)
Head `65a62c9677469556e2939392b61d3097682341cd`. Delta lido: `forge-check delta --parecer` sobre `7c86f53..65a62c9` (só 65a62c9 é do autor): `bin/forge-mutante`, `tests/test_forge_mutante.py` e as specs `tests/mutantes/guarda-sem-mutante*.json` (ajuste de `de` e a spec -7). Já lido na rodada 1 e não relido: o resto de `bin/forge-mutante`, os docs de QA e segurança e os `.md`.

**Aprovado.** A1 e A2 do parecer anterior estão resolvidos:
- A1: `ler_no_commit` devolve bytes; `fonte()` decide o UTF-8 só para Python e specs; binário e não UTF-8 fora do Python saem `não coberto`; Python não UTF-8 e `\r` solto dão rc 2 citando o arquivo; `git()` decodifica com `errors="replace"`. `test_binario_e_fora_do_utf8...` cobre os cinco casos.
- A2: tirado o pulo do removido; o removido não Python sai `não coberto: run.sh` (teste invertido na l. 453).
- Condição editada (decisão técnica de 09:23): o par velho/novo é feito por hunk (`HUNK` agora lê os dois lados), a editada é coberta pelo mutante da nova e só sai `apagada` quando nada a substitui no hunk; o teste `test_condicao_editada...` trava os dois lados. O pareamento é por hunk e não pela posição exata do nó, o que a decisão de 09:23 aceita ("no mesmo hunk").
- `--text --no-textconv` no diff fecha o A1 da segurança (atributo `-diff`, `binary`, textconv), com teste nos quatro atributos.

Teto M14: `bin/` 183 + `tests/test_forge_mutante.py` 217 = 400 linhas (`git diff --numstat --no-renames 991cd09...65a62c9`); "até 400", dentro. `.md`, specs e `changelog.d/` ficam fora.

Citado, sem refazer: `python3 -m unittest tests.test_forge_mutante`: `Ran 54 tests ... OK`; `bin/forge-mutante --cobertura --base 991cd09 --rev 65a62c9`: rc 0, 28 linhas `coberta`, nenhuma `sem mutante` ou `apagada`. A rodada de mutantes é do QA. Segurança e QA têm parecer próprio.

Achados recorrentes (PA-7): `docs/engineering/achados-recorrentes.md` conferido; sem linha nova (A3 a A5 são recomendados e novos).

## Rodada 1 (histórico, 7c86f53)
Reprovado por A1 (arquivo não UTF-8 e binário derrubava o rc 2) e A2 (removido não Python saía calado), ambos pequenos; o resto da leitura da rodada 1 (decisões 1 a 5, T4, T6, T7, qualidade, testes) ficou sem achado e vale no delta, pois o código não mudou fora do que está acima.
