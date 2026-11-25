---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/marca-0.47.18
commit: 217e73ed2e9bc41ac0ba09550b76721fbd36359d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E12.14, marca da 0.47.18; PR #894, classe C)

Escopo: `eeb81062..217e73ed` (Base-sha do brief até o Revisar-sha), 7 arquivos, um commit (`chore(release): marca da 0.47.18 na develop`). Primeira revisão da branch, sem parecer anterior. Corte com 4 itens (abaixo do teto de 20) pela autorização do dono só da noite de 24/11, citada no corpo do #894.

Verificado nesta revisão:
- Reprodução: num clone descartável em `eeb81062`, `bin/forge-changelog release 0.47.18 2026-11-25` e a troca `0.47.17` → `0.47.18` nos dois `plugin.json` dão uma árvore idêntica à do `217e73ed` (`git diff --cached --stat 217e73ed` vazio). A marca é exatamente o que a ferramenta produz, nada a mais.
- Nada de código mudou: o diff toca só `.claude-plugin/plugin.json:3`, `dev/.claude-plugin/plugin.json:3` (os dois `0.47.17` → `0.47.18`), `CHANGELOG.md` (+9, nenhuma linha removida) e apaga os 4 fragmentos de `changelog.d/`, que fica só com o `README.md`.
- Fragmentos: as linhas de item de `v0481-catraca-ajudante`, `v0481-copia-mensagem`, `v0481-corte-completo` e `v0481-g3-testes-uma-vez` estão literais na seção `## [0.47.18] - 2026-11-25` (`grep -qxF`, 4 de 4); `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0).
- Base em dia: `origin/develop` = `eeb81062` (o Base-sha) na leitura; nenhum fragmento entrou depois do corte.
- Data: commit de 2026-11-25 05:58:49 -0300; o cabeçalho `2026-11-25` bate com o dia local, como o `--corte` agora grava (#887).
- Corpo do #894: traz `teto: excedido, 1349 linhas, marca de versão`, a classe C e a lista dos pareceres `release-0.47.18`. Conferi a conta com as funções do próprio `forge-check` (`contagens_do_intervalo` sobre `origin/main...HEAD`, `linhas_de_codigo`, `aviso_de_linhas`): 1349, acima do teto; `classe_da_entrega` contra a `develop`: C.
- Guardas: o diff não muda guarda nenhuma; não há mutante a declarar.
- Suíte: não rerrodada (`R-REVIEW`); vale o CI do #894 no head, linha abaixo.

## Parecer
Aprovado. A marca reproduz byte a byte o `forge-changelog release 0.47.18 2026-11-25` sobre a develop do corte, sobe a versão nos dois manifestos, apaga os 4 fragmentos e não toca código; a linha de teto do corpo do #894 confere com a medida do `forge-check`.
- CI lido pela API dos check-runs: no 217e73ed, 18 jobs verdes e `suíte (python 3.14, parte 1/5)` e `teto de pulados (python 3.14)` cancelados pelo push da segurança (be4ff39a, que só acrescenta `docs/security/marca-0.47.18.md` e `docs/security/release-0.47.18.md`); no be4ff39a, mesma árvore de código, 20 checks `success` e 7 `skipped` (os de push na develop e a cobertura informativa), nenhum vermelho, os dois cancelados inclusos.
- ci: 217e73ed2e9bc41ac0ba09550b76721fbd36359d verde
