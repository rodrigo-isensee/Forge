---
tipo: review
contrato: 1
pedido: release-0.47.16
branch: melhoria/v0480-release-04716-anexo
commit: 51fc24a74534d3ba419d2f7f08c9ae307aa07347
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: release-0.47.16

Code review da versão 0.47.16 inteira, revalidado no head 51fc24a7 (branch melhoria/v0480-release-04716-anexo, anexo sobre a `develop` 5f1c6e97), v0478 E167.7. A rodada anterior (head 2b8d11be, branch melhoria/v0480-release-04716, E167.2) aprovou a marca do corte 35b05bd3, que entrou na `develop` pelo PR #852 (89db5b73). Conteúdo: `git diff v0.47.15..51fc24a7`; cada item já entrou na develop com os próprios pareceres, e aqui se confere a junção, a marca e o anexo. O anexo tem parecer em `docs/reviews/v0480-release-04716-anexo.md`.

## Revalidação
Delta lido: `forge-check parecer delta docs/reviews/release-0.47.16.md` responde "2b8d11b não é ancestral de 51fc24a" (o #852 entrou por squash e o head antigo ficou fora da história). O delta conferido à mão é o do código da release: `89db5b73..51fc24a7` traz 5 itens da `develop` com pareceres próprios (#805, #812, #847, #851, #853) e o commit do anexo 51fc24a7; nada da marca (versões, placar, linhas da `[0.47.16]`) foi mudado ou apagado.

## Parecer
Aprovado.

- Junção: os 36 fragmentos da marca (42 linhas `- ` mais a linha da marca, 43) seguem na `[0.47.16]`; o anexo juntou os 11 fragmentos que chegaram depois do corte (6 entre o corte e o #852: #839, #843, #844, #845, #846, #848; 5 depois: #805, #812, #847, #851, #853), cada linha idêntica ao fragmento (`grep -qxF`, falta=0), mais a linha do anexo: 55 linhas `- ` na seção.
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.16 = `[0.47.16] - 2026-11-24` (`CHANGELOG.md:7`); `[Não publicado]` vazio (linha 5); `[0.47.15]` na linha 67. `changelog.d/` no head só com o README.
- Ferramentas no head 51fc24a7: `bin/forge-changelog conferir --base origin/develop`: "ok: fechamento de 11 fragmento(s), linhas no CHANGELOG" (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/homolog`: "versão base: 0.47.15 | versão da release: 0.47.16" (rc 0); `git diff --check 5f1c6e97 51fc24a7`: limpo.
- Placar: linha 0.47.16 (mortos=59 sobreviveu=0, specs=9) e nota do corte (`docs/engineering/placar-mutacao.md:26` e `:38`), sem mudança; a nota não cita as specs do anexo (recomendado A1 no parecer do anexo).
- Suíte: não rerrodada (sem suíte local); a branch do anexo não tem PR nem run de CI, e a prova é o CI do PR de promoção à `homolog`, obrigatório para integrar (`R-REVIEW`). Teste do arquivo tocado (`tests.test_changelog`): 91, OK.
- Integração: a `develop` está em 5f1c6e97, base do anexo, sem item novo depois dele; o anexo deixa `changelog.d/` sem fragmento pendente, como o passo 3 do `scripts/promover-homolog.py` pede.
