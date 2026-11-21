---
tipo: review
contrato: 1
pedido: release-0.47.14
branch: melhoria/v0479-release-04714
commit: 5067fedacf87005b2a96c13e5af4b8d57b32d0fa
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

## Revalidação no head 5067feda (v0478 E76.15)
Aprovado; mesmo veredito e conteúdo de `docs/reviews/v0479-release-04714.md` no 5067feda (54227c27). Delta lido: `forge-check parecer delta docs/reviews/release-0.47.14.md` (intervalo d35b56f6..d3c4cbac, sem o que veio da develop): `CHANGELOG.md` (10 linhas novas na `[0.47.14]`) e `docs/engineering/placar-mutacao.md` (linha e nota da 0.47.14). De 5067feda a d3c4cbac só mudam os três pareceres.

- Versão inteira (`git diff v0.47.13..5067feda`, 398 arquivos): `git log --first-parent v0.47.13..9d5dcb6e` (= `origin/develop`) dá 24 itens e 24 fragmentos novos em `changelog.d/`; as 33 linhas `- ` deles estão todas na `[0.47.14]` (`grep -qxF`, falta=0). `changelog.d/` em 5067feda só com o README.
- Junção: merge ac544ac5 da develop 9d5dcb6e sem resolução à mão (`git show --cc` sem `@@@`).
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.14 = `[0.47.14] - 2026-11-21` (linha 7); `[Não publicado]` vazio (linha 5); `[0.47.13]` na linha 45; entrada em português.
- Ferramentas no head 5067feda: `bin/forge-changelog conferir --base origin/develop`: "PR de release (versão mudou)" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/develop`: "versão base: 0.47.13 | versão da release: 0.47.14" (rc 0). `git diff --check v0.47.13 5067feda` acusa só 3 linhas de contexto vazias dentro de `docs/propostas/k339-pre-push.patch` (formato de patch, não defeito).
- Placar: linha 0.47.14 (mortos=66 sobreviveu=0, specs=9) e nota gravadas (`docs/engineering/placar-mutacao.md:24` e `:32`); fecha o A1 recomendado do parecer de d35b56f6.
- Suíte: não rerrodada (brief: sem suíte local); a prova é o CI do PR (`R-REVIEW`).
