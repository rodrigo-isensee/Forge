---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: bc385524277c69f47a6cb0f7ed5d37cee5706626
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E51.19, revalidação de CONFORMIDADE-DESLIGADA-NA-SESSAO-DO-FORGE)

Delta lido (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0479-conformidade-sessao-forge.md`, intervalo `a554e345..bc385524`; no domínio, `changelog.d/v0479-conformidade-sessao-forge.md`, `docs/hooks.md`, `hooks/conformidade.py`, `tests/test_hooks.py`, `tests/mutantes/v0479-conformidade-sessao-forge-4.json`, `-5.json`, `-6.json` (novo) e sete fixtures `e51-wt-*` novas. O aviso do delta sobre o merge 2e2cfa7 fora da `origin/develop` só alarga a lista; o código do intervalo é o da E51.18.

## Sondas
- S1 · hook desta cópia, cwd nesta wt, `source /dev/stdin <<< 'git push origin develop'`, `. /dev/stdin <<< 'B=main; git push origin $B'` e `eval 'builtin . /dev/stdin <<< "git push origin develop"'` · espera: 2 · obtido: 2 nos três
- S2 · mesmo leiaute, `bash -c 'echo "git push origin develop" | bash'` e `bash -c "source /dev/stdin <<< 'git push origin develop'"` · espera: 2 · obtido: 2 nos dois
- S3 · mesmo leiaute, `source /dev/stdin <<< 'git log -1'`, `bash -c 'sh scripts/x.sh'`, `bash -c 'echo bash'` e `bash -c '. ./x.sh'` · espera: 0 · obtido: 0 nos quatro
- S4 · mesmo leiaute, `eval 'eval <<< "git push origin develop"'` · espera: 0 (o eval não lê a entrada) · obtido: 0

## Parecer
Aprovado. O A1 da segurança E51.16 está corrigido em `hooks/conformidade.py:3809-3857`: o `source` e o ponto releem o here-string como o shell (nível 0, `le_o_here_string`), e no texto reavaliado o shell é trava em qualquer forma (argumento, here-string ou pipe), o `eval` só com argumento e o `source` ou o ponto só com here-string, fechando na dúvida. A troca do `eval` com here-string no nível 1 para livre está certa: o `eval` não lê a entrada (S4). O pipe para shell no nível 0 segue lacuna da guarda base, dita em `docs/hooks.md:63` com o cartão CONFORMIDADE-SUBSTITUICAO-NO-PROJETO. Docstring, `docs/hooks.md` e o fragmento do changelog acompanham.

Tamanho (H1): cerca de 10 linhas de código em `hooks/` no delta, um comportamento. Guardas do delta: cinco linhas, um mutante por linha (M37 e M38 em `-5.json`; M39, M40 e M41 em `-6.json`); o M32 de `-4.json` segue a linha trocada.

Execução: `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_travas_do_conformidade`, ambiente limpo: 1 teste, OK (10,0 s), 55 fixtures. Mutantes: `forge-mutante --processos 1 --ids M37,M38,M39,M40,M41`, os cinco morreram (`hooks/conformidade.py:3849`, `:3847`, `:3851`, `:3856`, `:3810`). O resto da mutação: PQ do autor (V2), sem rerrodar. Suíte completa: CI do PR.

O A2 de review anterior (recomendado, `X=$(echo push); git $X origin develop`, também no projeto) segue como cartão depois do merge (`R-REVIEW`).
