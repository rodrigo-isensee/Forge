---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.15
branch: melhoria/v0480-release-04715
commit: a151f1d254124ebb23e4f82f1a8bd44404c53f06
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: release 0.47.15 (versão inteira), marca no head a151f1d2

Etapa E125.8 do pedido v0478. Conteúdo: `git diff v0.47.14..a151f1d2`, 20 itens (#776, #780 a #799), cada um com parecer próprio aprovado, mais a marca `3b6cfad5` (parecer do pedido `docs/security/v0480-release-04715.md`, commit `1c1e35bd`, aprovado: só metadado de versão).

Gatilhos: hooks (`vigia`, `ordens`, `conformidade`), execução de comando (`bin/forge-check`, `bin/forge-fechar`, `bin/forge-contador`, `bin/forge-testes`, `.githooks/pre-push`), regra afrouxada (#786, #788), release usada por todos os projetos.

## Detalhe dos achados
Sem achados.

- **Junção.** `origin/develop` = `f4836717` = corte da marca, ancestral de `a151f1d2`; os 20 merges de primeiro pai em `v0.47.14..f4836717` são os itens listados; fora deles só a marca e os pareceres dela (`1c1e35bd`, `0e9af4d7`, `a151f1d2`).
- **Versão.** `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3` em `0.47.15`, igual a `## [0.47.15] - 2026-11-22` do `CHANGELOG.md:7`, em português; `[Não publicado]` vazio; `changelog.d/` só com `README.md` (`bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes`).
- **Hooks medidos.** `bin/forge-check comparar v0.47.14 a151f1d2`: `so-aperta: medido base=96804a37 head=a151f1d2 casos=239 aceites-novos=0` (famílias merge-pr, push-forcado e sem-verificar com 8 casos cada). A medida cobre só os hooks.
- **Superfície.** Nenhum arquivo em `.github/`, `.devcontainer/` nem manifesto de dependência no diff da versão.

## Aceites novos
Nenhum: `git diff --name-status v0.47.14..a151f1d2` não toca `docs/security/aceites/`, e a medida dos hooks dá `aceites-novos=0`.

## Só aperta? (para o rótulo afrouxa-regra da promoção)
A versão não só aperta frente à 0.47.14; o rótulo afrouxa-regra é obrigatório na promoção.
- **Afrouxam:** #786 (vigia: time parado adia o Stop do Jarvis uma vez; ADR 0003 item 7) e #788 (emenda da ADR 0003 para os hooks ordens e vigia; ADR 0003 item 1). São os dois únicos commits da faixa com `afrouxa-regra` no título.
- **Demais itens:** só apertam ou só corrigem, conforme o parecer de cada um.

Autorização do rótulo: DECISÃO DO DONO de 2026-11-21 20:15 (até 2026-11-23 09:00, só por develop → homolog → main, checks verdes conferidos logo antes, sem `--admin`, sem exceção do ruleset, sem merge automático) e DECISÃO DO DONO de 2026-11-22 05:21 ("rótulo afrouxa-regra autorizado até segunda"). O merge homolog → main segue do usuário (`R-MAIN`).

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. A suíte inteira vale pelo CI do PR de promoção; localmente só `comparar` e `conferir-release`. Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; a versão não toca workflow nem dependência.
