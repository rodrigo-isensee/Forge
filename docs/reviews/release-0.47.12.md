---
tipo: review
contrato: 1
pedido: release-0.47.12
branch: melhoria/v0479-release-04712
commit: ccae7261ac82e17d12ee021f26256b9a45d3b40d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: release-0.47.12

Code review da marca da versão 0.47.12 refeita no head ccae7261 (branch melhoria/v0479-release-04712, base develop 20bbbd8d, com o #732 e o #733), v0478 E59.10. Revalida o parecer anterior no head 61cda6b8.

## Parecer
Aprovado.

- Delta lido: `forge-check parecer delta docs/reviews/v0479-release-04712.md`, intervalo 61cda6b8..ccae7261, no domínio só o `CHANGELOG.md` (+2 linhas, uma em Adicionado e uma em Alterado da `[0.47.12]`); "revalida: não". O resto do intervalo é a develop (#732, #733) e pareceres.
- Marca refeita (ccae7261, 3 arquivos, 2+/4-): as duas linhas novas do `CHANGELOG.md` são idênticas às dos fragmentos apagados `changelog.d/v0479-melhorias-anti-erro.md` (Adicionado) e `changelog.d/v0479-pv-c1-pesos.md` (Alterado).
- Junção: `git merge-base --is-ancestor 20bbbd8d ccae7261` verdadeiro e `origin/develop` = 20bbbd8d; `git diff --stat 20bbbd8d ccae7261` traz só os dois `plugin.json`, o `CHANGELOG.md`, o `docs/engineering/placar-mutacao.md`, os 23 fragmentos apagados e os pareceres da marca.
- Versão: `v0.47.11` tem 0.47.11; `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.12; `CHANGELOG.md` com `[Não publicado]` vazio (linha 5), `[0.47.12] - 2026-11-20` (linha 7) e `[0.47.11]` (linha 42); 30 linhas na seção (28 de antes + 2), em português.
- Ferramentas no head: `bin/forge-changelog conferir --base 20bbbd8d`: "PR de release (versão mudou)" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base 20bbbd8d`: "versão base: 0.47.11 | versão da release: 0.47.12" (rc 0); `scripts/validar-plugin.sh`: "Validation passed" (rc 0; o sandbox nega só api.anthropic.com); `git diff --check`: limpo.
- Suíte: não rerrodada (brief: sem suíte local); a prova é o CI do PR, obrigatório para integrar (`R-REVIEW`).

## Achados
- A1 (recomendado) skills/trabalho-em-paralelo/ritmo-e-corte.md:49 · a regra nova do #733 manda a marca regerar tests/pesos-d4.json com scripts/pesos-do-ci.py; ccae7261 não o toca (último commit dele: c219c86b). Só afeta a divisão da suíte, não o veredito; regerar na próxima marca.
