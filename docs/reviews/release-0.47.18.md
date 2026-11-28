---
tipo: review
contrato: 1
pedido: release-0.47.18
branch: melhoria/marca-0.47.18
commit: 217e73ed2e9bc41ac0ba09550b76721fbd36359d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: release-0.47.18

Code review da versão 0.47.18 inteira, no head 217e73ed (branch melhoria/marca-0.47.18, sobre a `develop` eeb81062), v0481 E12.14. Conteúdo: `git diff 5fb8e328..217e73ed` (a marca da 0.47.17, #882, até a marca da 0.47.18; 49 arquivos, +1914 −88). Cada item já entrou na `develop` com os próprios pareceres (#887, #889, #891 e #893); aqui se confere a junção, a marca e a versão. A marca tem parecer próprio em `docs/reviews/marca-0.47.18.md`; este é o primeiro parecer da versão inteira, sem rodada anterior nem delta.

## Achados
- A1 (recomendado) CHANGELOG.md:7 · Os 4 itens (#887, #889, #891, #893) entraram com o rótulo `afrouxa-regra`; o PR homolog → main da 0.47.18 vai pedir o mesmo rótulo ao dono. Cite-o no corpo do PR da promoção para o dono não ser surpreendido.

## Parecer
Aprovado.

- Junção: `5fb8e328` é ancestral do head; a cadeia de primeiros pais `5fb8e328..217e73ed` é exatamente #887 (8833d0f6), #889 (220ba3fa), #891 (42442a67), #893 (eeb81062) e a marca, os quatro `MERGED` com os pareceres de review, QA e segurança na `develop` (`docs/reviews|qa|security/v0481-{corte-completo,copia-mensagem,catraca-ajudante,g3-testes-uma-vez}.md`). Nenhum código fora da `develop` entra na versão.
- CHANGELOG: os 4 fragmentos criados em `5fb8e328..eeb81062` estão literais na seção `## [0.47.18] - 2026-11-25` (4 itens: um Adicionado, um Alterado, dois Corrigido; falta=0, nenhum além); nenhuma linha antiga saiu (diff só com `+`); `[Não publicado]` vazio (linha 5), `[0.47.17]` na linha 16.
- Coerência entre os itens: o `- ci:` do PARECER-LE-O-CI (#893) vale para os pareceres `release-0.47.18`, cujo `commit:` já traz a regra; o corpo da marca do #887 lista esses pareceres e a linha de teto (1349 contra `origin/main`, conferida); o `--revisao` do #889 está no `bin/forge-copia` do head (a cópia instalada 0.47.15 ainda não o tem). Não vi conflito entre as mudanças de `bin/forge-check`, `bin/forge-fechar`, `bin/forge-copia` e `tests/catraca.py`.
- Versão: `0.47.18` em `.claude-plugin/plugin.json:3` e `dev/.claude-plugin/plugin.json:3`; patch sobre a 0.47.17 da `homolog`.
- Ferramentas no head 217e73ed: `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `scripts/conferir-release.py --base origin/homolog`: "versão base: 0.47.17 | versão da release: 0.47.18"; `git diff --check 5fb8e328 217e73ed`: limpo.
- Suíte: não rerrodada (`R-REVIEW`); vale o CI do #894 no head, linha abaixo. A prova obrigatória da promoção segue sendo o CI do PR à `homolog`.
- Guardas: a marca não muda guarda nenhuma; as dos itens têm mutantes declarados (`tests/mutantes/v0481-*.json`) e pareceres nos PRs de cada um.
- CI lido pela API dos check-runs: no 217e73ed, 18 jobs verdes e `suíte (python 3.14, parte 1/5)` e `teto de pulados (python 3.14)` cancelados pelo push da segurança (be4ff39a, que só acrescenta `docs/security/marca-0.47.18.md` e `docs/security/release-0.47.18.md`); no be4ff39a, mesma árvore de código, 20 checks `success` e 7 `skipped`, nenhum vermelho, os dois cancelados inclusos.
- ci: 217e73ed2e9bc41ac0ba09550b76721fbd36359d verde
