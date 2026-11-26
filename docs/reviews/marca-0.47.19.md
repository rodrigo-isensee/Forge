---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/marca-0.47.19
commit: 9487d956120b90e783ef1462fcfe83c2b1df7230
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-26
---
# Review: v0481 (E12.23, marca da 0.47.19; PR #905, classe C)

Escopo: `cc4376fe..9487d956` (Base-sha do brief até o Revisar-sha), 13 arquivos, um commit (`chore(release): marca da 0.47.19 na develop`). Primeira revisão da branch, sem parecer anterior. Corte com 10 itens, abaixo do teto de 20, pela autorização fixa do dono de 25/11 07:52, citada no corpo do #905.

Verificado nesta revisão:
- Reprodução: numa worktree descartável em `cc4376fe`, `bin/forge-changelog release 0.47.19 2026-11-26` ("10 fragmento(s) juntado(s) e apagado(s)") e a troca `0.47.18` → `0.47.19` nos dois `plugin.json` dão uma árvore idêntica à do `9487d956` (`git diff --cached --stat 9487d956` vazio). A marca é o que a ferramenta produz, nada a mais.
- Nada de código mudou: o diff toca só `.claude-plugin/plugin.json:3`, `dev/.claude-plugin/plugin.json:3` (os dois `0.47.18` → `0.47.19`), `CHANGELOG.md` (+16, nenhuma linha removida) e apaga os 10 fragmentos de `changelog.d/`.
- `bin/forge-changelog conferir-release`: "ok: changelog.d/ sem fragmentos pendentes" (rc 0); `git diff --check cc4376fe 9487d956`: limpo.
- Base em dia: `git ls-remote origin refs/heads/develop` = `cc4376fe` (o Base-sha) na leitura; nenhum fragmento entrou depois do corte.
- Data: commit de 2026-11-26 07:39:54 -0300; o cabeçalho `2026-11-26` bate com o dia local.
- Corpo do #905: traz `teto: excedido, 522 linhas, marca de versão`, a classe C e a lista dos pareceres `release-0.47.19`. Conferi a conta com as funções do `forge-check` (`contagens_do_intervalo` de três pontos e `linhas_de_codigo`): 522 contra `origin/main` e contra `origin/homolog`, 0 contra `origin/develop` (a base da entrega, onde o `pr` não pede a linha). `forge-check classe`: C (`dev/.claude-plugin/plugin.json`), pareceres review, qa e revisao-seguranca.
- Guardas: o diff não muda guarda nenhuma; não há mutante a declarar.
- Suíte: não rerrodada (`R-REVIEW`); vale o CI do #905 no head, linha abaixo.

## Parecer
Aprovado. A marca reproduz byte a byte o `forge-changelog release 0.47.19 2026-11-26` sobre a develop do corte, sobe a versão nos dois manifestos, apaga os 10 fragmentos e não toca código; a linha de teto do corpo do #905 confere com a medida do `forge-check`.
- CI lido pela API dos check-runs no 9487d956: 20 checks `success` (as 10 partes da suíte, os dois `teto de pulados`, `instalação`, `bateria`, `bateria (python 3.14)`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (pareceres)`, `catraca` e `árvore já provada na develop`) e 7 `skipped` (os de push na develop e a cobertura informativa); nenhum vermelho.
- ci: 9487d956120b90e783ef1462fcfe83c2b1df7230 verde
