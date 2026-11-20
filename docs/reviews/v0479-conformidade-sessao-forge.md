---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: a554e34536490ff7af78000f76b67a1652f6e840
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E51.15, revalidação de CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)

Delta lido (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0479-conformidade-sessao-forge.md`, intervalo `29cbd24d..a554e345`; no domínio, `changelog.d/v0479-conformidade-sessao-forge.md`, `docs/hooks.md`, `hooks/conformidade.py`, `tests/test_hooks.py`, `tests/mutantes/v0479-conformidade-sessao-forge-5.json` e oito fixtures `e51-wt-*` novas. O aviso do delta sobre o merge 39013d7 fora da `origin/develop` só alarga a lista; o código do intervalo é o da E51.14.

## Sondas
- S1 · hook desta cópia, CLAUDE_PROJECT_DIR=/workspaces/Forge, cwd nesta wt, forge:tech-lead, `eval 'eval "B=develop; git push origin \$B"'` e `sh -c 'eval "git push origin \$B"'` · espera: 2 · obtido: 2 nos dois
- S2 · mesmo leiaute, `bash -c` com `bash <<EOF` cujo corpo faz `B=main; git push origin $B` · espera: 2 · obtido: 2 (heredoc no 2.º nível segue lido)
- S3 · mesmo leiaute, `bash -c 'bash -c "git log -1"'`, `bash -c 'sh scripts/x.sh'` e `git push origin melhoria/x` · espera: 0 · obtido: 0 nos três (o fecho do 2.º nível só pesa com recusa opaca na linha)

## Parecer
Aprovado. O A1 da segurança E51.12 está corrigido por uma guarda só (`hooks/conformidade.py:3842`): no texto reavaliado (nível 1), o `eval` ou o shell com argumento ou here-string é trava e fecha na dúvida, em vez de reler um terceiro nível; o heredoc do 2.º nível continua lido pelo corpo (S2). As quatro formas S1 a S4 da segurança têm fixture `-bloqueia`, e as formas legítimas citadas no parecer dela têm fixture `-libera`. O docstring e `docs/hooks.md:63` dizem o limite ("um nível só"); o fragmento do changelog acompanha.

Tamanho (H1): 2 linhas de código em `hooks/` no delta, um comportamento. Guarda do delta: uma linha, com M37 (a guarda inteira) e M38 (o ramo do here-string) em `-5.json`.

Execução: `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_travas_do_conformidade`, ambiente limpo: 1 teste, OK (12,6 s), 48 fixtures. Mutantes: `forge-mutante --processos 1 --ids M37,M38`, os dois morreram em `hooks/conformidade.py:3842`. O resto da mutação: PQ do autor (V2), sem rerrodar. Suíte completa: CI do PR.

O A2 do review anterior (recomendado, `X=$(echo push); git $X origin develop`, também no projeto) segue como cartão depois do merge (`R-REVIEW`).
