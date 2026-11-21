---
tipo: review
contrato: 1
pedido: release-0.47.14
branch: melhoria/v0479-release-04714
commit: d35b56f6087072354d6a25d976a9fa94329d3010
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: release-0.47.14

Code review da marca da versão 0.47.14 no head d35b56f6 (branch melhoria/v0479-release-04714, corte 5e3ca873 = `origin/develop`), v0478 E76.2. Parecer da versão inteira: `git diff v0.47.13..d35b56f6` (332 arquivos); cada item já entrou na develop com os próprios pareceres, e aqui se confere a junção e a marca.

## Parecer
Aprovado.

- Junção: `git log --first-parent v0.47.13..5e3ca873` dá 14 merges e `changelog.d/` tinha 14 fragmentos no corte; d35b56f6 (17 arquivos, 30+/40-) apaga os 14 e junta as 23 linhas na `[0.47.14]`, idênticas às dos fragmentos (`diff` ordenado vazio), em português, em `### Adicionado`, `### Alterado` e `### Corrigido`.
- Versão no head: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` de 0.47.13 a 0.47.14; `CHANGELOG.md` com `[Não publicado]` vazio (linha 5), `[0.47.14] - 2026-11-21` (linha 7) e `[0.47.13]` (linha 35); `changelog.d/` só com o README.
- Ferramentas no head d35b56f6: `bin/forge-changelog conferir --base origin/develop`: "PR de release (versão mudou)" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/develop`: "versão base: 0.47.13 | versão da release: 0.47.14" (rc 0); `git diff --check 5e3ca873 d35b56f6`: limpo.
- `tests/pesos-d4.json` não muda: a mensagem do commit registra "sem amostra válida" (PR-VERDE C1, skills/trabalho-em-paralelo/ritmo-e-corte.md:49), motivo escrito.
- Suíte: não rerrodada (brief: sem suíte local); a prova é o CI do PR, obrigatório para integrar (`R-REVIEW`).

## Achados
- A1 (recomendado) docs/engineering/placar-mutacao.md:23 · falta a linha 0.47.14 ("uma linha por release", linha 3); a medida (mortos=66 sobreviveu=0, 9 specs) ficou só na mensagem de d35b56f6. Medida, não portão (M-5); a 0.47.13 a gravou na marca.
