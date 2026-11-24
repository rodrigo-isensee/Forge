---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.47.16
branch: melhoria/v0480-release-04716
commit: 2b8d11be7024106a2fd96f41633676f45d93595e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: release 0.47.16 (versão inteira), marca no head 2b8d11be

Etapa E167.3 do pedido v0478. Conteúdo: `git diff v0.47.15..2b8d11be`, 37 merges de primeiro pai em `v0.47.15..35b05bd3` (#795, #803 a #811, #814 a #838, #840 a #842, #850; 36 itens no CHANGELOG), cada um com o parecer próprio da classe, mais a marca 2b8d11be (parecer do pedido `docs/security/v0480-release-04716.md`, aprovado: só metadado de versão). Corte por DECISÃO DO DONO de 2026-11-24 09:05 (sem o teto de 20 desta vez).

Gatilhos: hooks (`conformidade`, `meta`), execução de comando (`bin/forge-check`, `bin/forge-fechar`, `bin/forge-copia`, `bin/forge-testes`, `bin/forge_autorizacao.py`, `bin/forge_controle.py` novo), arquivos protegidos tocados, release usada por todos os projetos.

## Detalhe dos achados
Sem achados.

- **Junção.** `v0.47.15` é ancestral de 35b05bd3, que é o pai de 2b8d11be. A develop andou depois do corte (`origin/develop` = 6161978d: #839, #843, #844, #845, #848); se a marca for refeita com `--anexar 0.47.16`, a versão muda e este parecer pede revalidação por delta, com o #844 (`fix(dora)`, código) no escopo.
- **Versão.** `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3` em `0.47.16`, igual a `## [0.47.16] - 2026-11-24` do `CHANGELOG.md:7`; `[Não publicado]` vazio; `changelog.d/` só com `README.md` (`bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes`).
- **Hooks medidos.** `bin/forge-check comparar v0.47.15 2b8d11be`: `so-aperta: medido base=5a232208 head=2b8d11be casos=239 aceites-novos=0` (famílias merge-pr, push-forcado e sem-verificar com 8 casos cada). A medida cobre só os hooks.
- **Superfície.** Nenhum arquivo em `.github/`, `.devcontainer/` nem manifesto de dependência no diff da versão. `bin/forge_controle.py` (#795, AE3.1) é capacidade nova de commit local na pasta de controle, sem chamador em `bin/`, `hooks/`, `scripts/` nem `.githooks/` neste head (só o teste); não afrouxa regra existente.
- **#810 sem rótulo.** O #810 (`forge-check autorizacao gravar`) entrou na develop com a catraca vermelha e sem o rótulo (DECISÃO DO DONO de 2026-11-24 09:05 manda apurar quem mesclou). O código mesclado em 216413c9 é o do head que a segurança aprovou com só aperta por escrito (`docs/security/v0479-sieg-g1-gravar.md`, d4960f8e, ancestral do head do PR 50a3022d): `git diff 50a3022d 216413c9` nos quatro arquivos de código só difere em `bin/forge-testes`, e a diferença é do #806 e do #817 vinda da develop. A falha é de processo, não de conteúdo; a apuração segue com o dono.

## Aceites novos
Nenhum: `git diff --name-status v0.47.15..2b8d11be` não toca `docs/security/aceites/`, e a medida dos hooks dá `aceites-novos=0`.

## Só aperta? (para o rótulo afrouxa-regra da promoção)
Sim, por escrito: frente à 0.47.15, a versão só aperta ou é neutra. Nenhum item afrouxa regra, conforme o parecer de segurança de cada um:
- **Só aperta:** #806 (`v0480-copia-nome-unico`), #810 (`v0479-sieg-g1-gravar`), #811 (`v0480-ordens-guarda`), #837 (`v0480-repo-publico-v2`, só aperta ou neutro contra a base), #834 (`v0480-zero-nao-medido`), #826 (`v0480-comando-pronto-resto`).
- **Neutros:** #814 e #850 (`v0480-develop-verde-ordens`, `v0480-tempo-fixture`: mesma decisão, só desempenho), #817, #821, #822, #824, #825, #831, #816 e #835 (receita do envio), #832, #833 e o #795 (capacidade nova sem chamador).
- **Só documento ou teste, sem gatilho:** propostas, retrospectivas, pareceres pós-merge e #823.

A versão toca arquivos protegidos (`hooks/conformidade.py`, `hooks/conformidade.json`, `hooks/meta.py`, `bin/forge-check`, `bin/forge-fechar`), então a catraca da promoção pede o rótulo afrouxa-regra. Autorização: DECISÃO DO DONO de 2026-11-23 15:25 (até 2026-11-27 23:59, com a confirmação escrita de só aperta da segurança, que é esta seção; listar no aviso de marco), DECISÃO DO DONO de 2026-11-23 21:11 (vale também a main, nas condições de 2026-11-21 20:15: só develop → homolog → main, checks verdes conferidos antes, pareceres aprovados, sem `--admin`, sem exceção do ruleset, sem merge automático) e DECISÃO DO DONO de 2026-11-24 09:05 (promover à homolog e abrir o PR da main). O merge homolog → main segue do usuário (`R-MAIN`).

## Riscos aceitos e ferramentas
Nenhum risco aceito nem pendente de aceite. A suíte inteira vale pelo CI do PR de promoção; localmente só `comparar`, `conferir-release` e `tests.test_changelog` (91, OK). Lacuna: gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH; a versão não toca workflow nem dependência.
