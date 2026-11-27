---
tipo: review
contrato: 1
pedido: release-0.47.20
branch: melhoria/v0481-release-0-47-20
commit: 1e301536467df853dae1e7229952b930078c979d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: release-0.47.20

Code review da versão 0.47.20 inteira contra a main (`v0.47.19`, a2f516d5), no head 1e301536 do PR #935 (branch melhoria/v0481-release-0-47-20, base `develop` 8855671d), v0481 E43.2. Conteúdo: `git log origin/main..1e301536` com 23 itens já mesclados na `develop` com os próprios portões, a marca (3bf1456e), o merge da `develop` 8855671d (df12c5f5) e o anexo do #933 e do #934 (1e301536). Aqui se confere a junção, a marca e o anexo; o mérito de cada item ficou nos pareceres de cada PR.

## Conferência
- Itens: #909, #910, #913, #914, #916, #917, #918, #919, #920, #921, #922, #923, #924, #925, #926, #927, #928, #929, #930, #931, #932, #933, #934, todos `MERGED` com base `develop`. Contador acima do teto (23 de 20) pela ordem do dono de 27/11 09:20 e 10:08 (promover a 0.47.20 com o #933 e o #934).
- Junção: `git diff 8855671d 1e301536` toca só `.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json` (0.47.19 → 0.47.20), `CHANGELOG.md` (+29) e os 23 fragmentos apagados; o merge df12c5f5 não traz resolução que mude código.
- Seção `[0.47.20]`: 24 linhas `- ` (7 Adicionado, 9 Alterado, 8 Corrigido; o #924 tem duas); as 24 linhas dos fragmentos apagados estão, iguais, no `CHANGELOG.md` (conferido linha a linha com `grep -xF`).
- Regras afrouxadas: os 7 itens com a marca no título (#909, #918, #920, #928, #929, #931, #932) citam no título a ordem, a ADR ou a regra do aceite; a conferência de cada aceite contra as decisões do pedido é do parecer de segurança da release. O rótulo `afrouxa-regra` está em 20 dos 23 PRs; o #918 tem a marca no título sem o rótulo, e #917 e #934 não têm nenhum dos dois.
- Pareceres por item na `develop`: review e segurança aprovados em 22 itens; QA ausente em 6 itens de classe C (A2); o #934, juntado pelo dono, sem parecer (só testes: `tests/test_hooks.py` alarga também `PRAZO_DA_SESSAO_S` fora do modo produção; lido, correto).
- Ferramentas no head 1e301536: `bin/forge-changelog conferir --base origin/develop`: "PR de release (versão mudou): o changelog fechado é conferido na promoção para a main." (rc 0); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `git diff --check 8855671d 1e301536`: limpo; `python3 -m unittest tests.test_changelog`: 91 testes, OK.

## Achados
- A1 (recomendado) CHANGELOG.md:7 · A ordem do dono de 27/11 10:08 pede listar toda regra afrouxada no PR da versão oficial; o corpo fixo do `forge-fechar --corte` (bin/forge-fechar:1627) não a lista e o #935 também não. O PR homolog → main deve citar os 7 (#909, #918, #920, #928, #929, #931, #932) com o aceite de cada um.
- A2 (recomendado) CHANGELOG.md:21 · Segue o A2 da 0.47.19: 6 itens de classe C sem `docs/qa/` na `develop` (#919, #921, #922, #923, #926, #927; CHANGELOG.md:21, 11, 32, 22, 28, 23) e o #934 (CHANGELOG.md:34) sem nenhum parecer. O parecer de QA da release cobre a leva; vira cartão.

## Parecer
Aprovado. A junção é só a marca e o anexo sobre a `develop` 8855671d, a seção `[0.47.20]` traz os 23 itens sem fragmento pendente, as duas versões batem e o CI do head está todo verde, a instalação de ponta a ponta incluída.

- ci: 1e301536467df853dae1e7229952b930078c979d verde
