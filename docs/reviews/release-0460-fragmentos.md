---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/release-0460-fragmentos
commit: c095b82b4e232188b5ed07d3dd6f7a766f43be67
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Code review: fragmentos do #506 e #507 juntados à 0.46.0 (v0457, E23.68)

Escopo: pedido v0457, etapa E23.68, classe T, só review (`R-REVIEW`). Diff lido inteiro: `git diff c340c322209112218dd46c06aec8ba54e62d8de4..c095b82b4e232188b5ed07d3dd6f7a766f43be67` (1 commit, 3 arquivos, +6 -8). O revisor é uma instância que não fez o commit.

## O que foi conferido
- `CHANGELOG.md`: o item de `changelog.d/v0457-refs-push.md` entra como última linha do `### Alterado` da 0.46.0 (antes do `### Corrigido`); os 5 itens de `changelog.d/conformidade-caminho-git.md` entram como últimas linhas do `### Corrigido` da 0.46.0 (antes do `## [0.45.5]`).
- Texto igual: cada linha `- ` dos dois fragmentos em `c340c322` (`git show c340c322:changelog.d/<nome>.md`) aparece exatamente uma vez (comparação de linha inteira, `grep -cxF`) no `CHANGELOG.md` de `c095b82b`: 6 de 6, sem item perdido nem inventado.
- Nenhuma linha removida do `CHANGELOG.md` (`git diff -U0`, zero linhas `-`); o cabeçalho `## [0.46.0] - 2026-11-12` é igual nos dois commits: versão e data não mudaram.
- Os dois fragmentos foram apagados; em `c095b82b`, `changelog.d/` tem só o `README.md`. Nenhum outro arquivo mudou.
- Ferramentas (citadas, não refeitas): `python3 -m unittest tests.test_changelog` com ambiente limpo, 69 testes OK; `bin/forge-changelog conferir --base c340c322 --branch melhoria/release-0460-fragmentos`, rc 0, "ok: fechamento de 2 fragmento(s), linhas no CHANGELOG".
- Achados recorrentes (PA-7): nenhuma classe do arquivo alcança este diff (só texto do changelog, sem código, guarda nem teste).

## Achados

## Sondas

## Parecer
Aprovado. O commit faz só o que a etapa pede: move o texto dos dois fragmentos, igual, para as seções certas da 0.46.0, apaga os fragmentos e não toca versão, data nem outro arquivo.
