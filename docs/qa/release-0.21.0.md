---
tipo: qa
contrato: 1
pedido: release-0.21.0
branch: melhoria/release-0.21.0-fragmento
commit: b7cf5775be1168c85c17af586378070ead7d87bd
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-19
---
# QA - release 0.21.0 (E6: versão 0.22.0 e CHANGELOG)

Links: `~/.forge-contrib/docs/pedidos/release-0.21.0.md` (E6.3), `docs/reviews/release-0.21.0.md` (review do E6, aprovado). Não há UX nem API. Offline (`R-CUSTO`). Testado `b7cf577` (código do E6). O HEAD `1de8fab` soma só `docs/reviews/release-0.21.0.md` (`git diff --name-only b7cf577 1de8fab`). O parecer anterior (`e65a7a8`, E5) fica substituído por este.

## Escopo
Delta do E6: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.22.0, e `CHANGELOG.md` com a entrada `[0.22.0]` e a `[0.21.0]` sem as linhas da VV-2 e da reconciliação. Como o delta mexe em versão, a suíte inteira e a validação do plugin rodaram completas, e o escopo do parecer é `completo`.

## Resultado

| Obrigação | Verificação | Resultado |
|---|---|---|
| Suíte inteira verde (R-QA) | `python3 -m unittest discover -s tests -v` na raiz da worktree, `pgrep` sem suíte ativa | Ran 865 tests in 151.145s, OK, rc 0; 0 FAIL/ERROR, 0 skipped |
| Plugin válido | `scripts/validar-plugin.sh` na raiz da worktree | rc 0; "Validation passed" nas conferências exibidas |
| Changelog da entrega | `bin/forge-changelog conferir --base origin/develop` | rc 0: "arquivos da fábrica alterados: 3 \| versão base: 0.21.0 \| versão do PR: 0.22.0" |
| Changelog fechado (etapa que reprovou o #210) | `bin/forge-changelog conferir-release` | rc 0: "ok: changelog.d/ sem fragmentos pendentes" |
| Versão (testes de versão) | `test_changelog_tem_a_versao_atual` e `test_versao_igual_a_do_forge` (dentro da suíte): raiz e `dev/` em 0.22.0 e a primeira entrada numerada do CHANGELOG é `[0.22.0]` | passou |
| Versão (fronteira) | mutação em cópia (`git archive`, fora da worktree): raiz em 0.21.0 faz `test_changelog_tem_a_versao_atual` e `test_versao_igual_a_do_forge` falharem; `dev/` em 0.21.0 faz `test_versao_igual_a_do_forge` falhar | os testes reprovam o desvio |
| Nada perdido no CHANGELOG | conjunto de linhas da `[0.21.0]` no `36696f3` contra o das entradas `[0.21.0]` + `[0.22.0]` agora, sem contar cabeçalhos de seção | sem linha perdida nem acrescida; a diferença é só o cabeçalho `### Adicionado` / `### Corrigido` repetido na `[0.22.0]` |
| VV-2 e reconciliação inteiras | cada linha de conteúdo de `origin/develop:changelog.d/vv-2.md` e `reconcilia-homolog-main.md` com `grep -cxF` no CHANGELOG | 1 ocorrência cada (4 linhas, todas na `[0.22.0]`) |
| Escopo do delta | `git diff --name-only 36696f3 b7cf577` | só `CHANGELOG.md`, `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` |
| Árvore limpa | `git status --short` antes de gravar este parecer | vazio |

## Achados

## Observações
(1) `commit` é `b7cf577`, o código testado. O HEAD `1de8fab` e este parecer só somam arquivos de `docs/reviews/` e `docs/qa/`, que a regra de pareceres aceita.
(2) Sem bug aberto: a pasta `docs/qa/bugs/` não ganha arquivo, e `aceite_usuario` não entra no frontmatter.
(3) A decisão do dono de 2026-10-19 (destravar: "B") está refletida: a `[0.21.0]` fica como foi decidida, e as linhas da VV-2 e da reconciliação estão na `[0.22.0]`.
(4) O sandbox nega a telemetria do CLI (`api.anthropic.com`, `http-intake.logs.us5.datadoghq.com`) durante a suíte e a validação. Não afetou nenhum resultado.

## Riscos
Nenhum novo. A única diferença em relação ao código já revisado é versão e changelog. A conferência final de `forge-check pr` e a fusão continuam com o tech-lead e o dono (E6.4).
