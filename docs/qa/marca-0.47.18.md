---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/marca-0.47.18
commit: 217e73ed2e9bc41ac0ba09550b76721fbd36359d
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: marca da 0.47.18 (#894, classe C)

Diff `eeb81062..217e73ed`: 7 arquivos, 3 modificados (`.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json`, `CHANGELOG.md`) e 4 apagados (fragmentos de `changelog.d/`). Nenhum código, teste, hook ou doc de processo mudou (`git diff --name-status`). Modelo: `docs/qa/marca-0.47.17.md`.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A marca é o `forge-changelog release 0.47.18 2026-11-25` e nada mais | clone em `eeb81062`, `bin/forge-changelog release 0.47.18 2026-11-25`, `git add -A`, `git diff --cached --quiet 217e73ed` | árvore gerada idêntica à da marca (IDENTICO) | passou |
| Os 4 itens estão no CHANGELOG com o texto dos fragmentos | script: cada linha não vazia dos 4 fragmentos da base (`git show eeb81062:changelog.d/<f>.md`) buscada literal no CHANGELOG | 8 linhas (2 por fragmento, título e item), 8 achadas | passou (8/8) |
| Fragmentos apagados, README mantido | `git diff --name-status` (4 D) e `bin/forge-changelog conferir-release` | `changelog.d/README.md` fica | passou (`ok: changelog.d/ sem fragmentos pendentes`) |
| Versão nos dois manifestos | `grep '"version"'` | `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` = 0.47.18 = `## [0.47.18]` | passou |
| Seção no formato e na ordem | leitura do diff do CHANGELOG | `[Não publicado]` vazio; `[0.47.18]` acima da `[0.47.17]`; Adicionado 1, Alterado 1, Corrigido 2 | passou |
| Data da release | `date -u` = 2026-11-25; dia local igual | 2026-11-25 | passou |
| Linha de teto no corpo do #894 | `gh pr view 894`: `teto: excedido, 1349 linhas, marca de versão` | `<n>` acima do total do diff de código que o PR mede; ver nota | passou |
| Pareceres da promoção listados no corpo | `gh pr view 894` | `docs/reviews|qa|security/release-0.47.18.md` | passou |
| Testes do changelog | `python3 -I -m unittest discover -s tests -p 'test_changelog*.py'` | n/a | 91 testes OK |

Nota do teto: o corpo diz 1349 e o parecer de segurança o reproduz como medida da marca (`origin/main...217e73ed`). Pelo meu lado, o diff `5fb8e328..217e73ed` (os 4 itens) dá 312 linhas de código pela `forge_tamanho.linhas_de_codigo`, abaixo de 1349; o corpo cobre o que se pede (`<n>` de pelo menos o medido). O corte com 4 itens, abaixo dos 20, segue a ordem do dono de 24/11 20:46 (citada no corpo); `teto_versao` e configs não mudaram.

## Cenários e resultado real
- CI: ver a seção de CI abaixo.
- Vermelho antes do verde e mutantes: não se aplicam, a marca não traz teste novo nem regra de código.
- Segurança e acessibilidade: sem gatilho, sem tela.
- Parecer anterior da branch: não havia.
- O clone é `git clone` por `bin/forge-copia`, porque `git worktree add` é bloqueado no sandbox.

## CI
- Run 45581199574 (sha `217e73ed`): 15 das 16 partes de `suíte` e `bateria (verificações longas)` verdes; `suíte (python 3.14, parte 1/5)` e `teto de pulados (python 3.14)` saíram `cancelled`, porque o commit de segurança `be4ff39a` chegou durante a rodada (concorrência do CI), não por falha de teste.
- Run 45582740158 (sha `be4ff39a`, que só soma `docs/security/marca-0.47.18.md` e `docs/security/release-0.47.18.md` ao `217e73ed`): `success`, com todas as partes da suíte nas duas versões do Python.
- Por isso não gravo a linha `- ci: <sha40> verde` do `217e73ed`: nenhum run completo existe nesse sha. A prova é o run do descendente só de documentação, acima. Sem rerrodar a suíte inteira; localmente rodei só os módulos do assunto (`test_changelog*`: 91 testes OK).
