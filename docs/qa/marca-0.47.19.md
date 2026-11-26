---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/marca-0.47.19
commit: 9487d956120b90e783ef1462fcfe83c2b1df7230
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-26
---
# QA: marca da 0.47.19 (#905, classe C)

Diff `cc4376fe..9487d956`: 13 arquivos, 3 modificados (`.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md`) e 10 fragmentos de `changelog.d/` apagados. Nenhum código, teste, hook ou doc de processo mudou. Modelo: `docs/qa/marca-0.47.18.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A marca é o `forge-changelog release 0.47.19 2026-11-26` e nada mais | clone em `cc4376fe`, `bin/forge-changelog release 0.47.19 2026-11-26`, `git add -A`, `git diff --cached --quiet 9487d956` | árvore gerada idêntica à da marca (IDENTICO) | passou |
| Os 10 itens estão no CHANGELOG com o texto dos fragmentos | script: cada linha não vazia dos 10 fragmentos da base buscada literal no CHANGELOG | 21 linhas, 21 achadas | passou (21/21) |
| Fragmentos apagados, README mantido | árvore da reprodução: `bin/forge-changelog conferir-release` | `changelog.d/README.md` fica | passou (`ok: changelog.d/ sem fragmentos pendentes`) |
| Versão nos dois manifestos | `grep '"version"'` | os dois = 0.47.19 = `## [0.47.19]` | passou |
| Seção no formato e na ordem | leitura do diff do CHANGELOG | `[Não publicado]` vazio; `[0.47.19]` acima da `[0.47.18]`; Adicionado 4, Alterado 2, Corrigido 5 | passou |
| Data da release | `date -u` = 2026-11-26 | 2026-11-26 | passou |
| Linha de teto no corpo do #905 | `gh pr view 905`: `teto: excedido, 522 linhas, marca de versão`, com a autorização fixa do dono (ordem de 25/11 07:52) para o corte abaixo de 20 itens | corte de 10 itens | passou (o valor 522 não foi reproduzido por mim) |
| Pareceres da promoção listados no corpo | `gh pr view 905` | `docs/{reviews,qa,security}/release-0.47.19.md` | passou |

## Cenários e resultado real
- Vermelho antes do verde e mutantes: não se aplicam, a marca não traz teste nem regra de código.
- Segurança e acessibilidade: sem gatilho, sem tela.
- Parecer anterior da branch: não havia. O clone é `git clone` por `bin/forge-copia`.
- O corpo do PR diz que o `forge-fechar --corte --dry-run` parou no V4 e que os passos do V5 foram feitos à mão; a reprodução acima confirma que o resultado é o do `forge-changelog release`.

## CI
- Run 45803496622 (sha `9487d956`): `completed success`; todas as partes da `suíte` (3.12 e 3.14), `instalação`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (pareceres)`, `catraca` e `árvore já provada na develop` verdes. Os `skipping` são jobs de push na develop. Sem suíte local; a marca não toca código.
- ci: 9487d956120b90e783ef1462fcfe83c2b1df7230 verde
