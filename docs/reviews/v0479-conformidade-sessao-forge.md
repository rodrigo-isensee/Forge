---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: b22efaae57691ca4bc95d62eda389f75b60e6869
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E51.23, revalidação de CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)

Delta lido (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0479-conformidade-sessao-forge.md`, intervalo `bc385524..b22efaae`; no domínio, `changelog.d/v0479-conformidade-sessao-forge.md`, `docs/hooks.md`, `hooks/conformidade.py`, `tests/mutantes/v0479-conformidade-sessao-forge-6.json`, `-7.json` (novo) e quatro fixtures `e51-wt-*` novas. O aviso do delta sobre o merge d733d10 fora da `origin/develop` local só alarga a lista; o código do intervalo é o da E51.22.

## Sondas
- S1 · hook desta cópia, cwd em `wt/x`, `bash -c 'echo "git push origin develop" | source /dev/stdin'`, `eval 'echo "git push origin develop" | builtin . /dev/stdin'` e `bash -c 'echo "git push origin develop" | command -- . /dev/stdin'` · espera: 2 · obtido: 2 nos três
- S2 · mesmo leiaute, `bash -c 'echo "git push origin develop" | find . -name x'` e `bash -c 'echo "git push --force origin melhoria/x" > a; ls .'` · espera: 0 (o ponto é argumento) · obtido: 0 nos dois
- S3 · `toca_uma_trava(t, 1)` direto: `X=1 source`, `time source`, `\.`, `"."`, `builtin command .`, `{ . …; }`, `( . … )`, `! . …` lendo o pipe · espera: True · obtido: True em todos
- S4 · `toca_uma_trava(t, 1)` direto: `find .`, `ls .`, `cp a .` · espera: False · obtido: False nos três

## Parecer
Aprovado. O A2 da segurança E51.20 está corrigido em `hooks/conformidade.py:3811-3817` e `:3858`: no texto reavaliado, o `source` ou o ponto na posição de programa (primeira palavra depois das atribuições e de `ANTES_DO_PROGRAMA`, ou depois só de `builtin`/`command` e das opções deles) é trava também sem here-string, porque lê o pipe; o ponto argumento (`find .`) segue livre (S2). `nice` e `exec` antes do ponto não chegam a rodar o builtin e ficam fora com razão. Docstring, `docs/hooks.md:63` e o fragmento do changelog acompanham.

Tamanho (H1): cerca de 6 linhas de código em `hooks/` no delta, um comportamento. Guardas do delta: três linhas, um mutante por linha e mais um na opção do `command` (M42 a M45 em `-7.json`); o M39 de `-6.json` segue a linha trocada.

Execução: `python3 -m unittest tests.test_hooks.HookSessaoDoForge.test_travas_do_conformidade`: 1 teste, OK (8,4 s). Mutantes: `forge-mutante --processos 1 tests/mutantes/v0479-conformidade-sessao-forge-7.json`, os quatro morreram (`hooks/conformidade.py:3858`, `:3817`, `:3811`, `:3817`). O resto da mutação: PQ do autor (V2), sem rerrodar. Suíte completa: CI do PR.

O A2 de review anterior (recomendado, `X=$(echo push); git $X origin develop`, também no projeto) segue como cartão depois do merge (`R-REVIEW`).
