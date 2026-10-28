---
tipo: review
contrato: 1
pedido: metade-k6
branch: melhoria/metade-k6
commit: 6dda8fdf285d5c5c2387c8ac4594fe1d0299a17d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: metade-k6

Volta 2 (pedido METADE-MINUTOS-REV, E1.1; decisão do dono K6 de 2026-10-27). Revalidação por delta do parecer anterior (`d9639dd`, sobre `053f416`).

## Achados
- A2 (recomendado) scripts/suite-paralela.py:234 · o hash cobre só o que o git versiona; arquivo ignorado pelo .gitignore que algum teste leia não entra. Registrar o limite na docstring ou cobrir com --ignored se algum teste depender disso (era o A3 da volta 1, segue aberto).
- A3 (recomendado) tests/mutantes/metade-k6-2.json:9 · o `de` do M9 (4 espaços) casa dentro da linha que agora tem 8 (dentro do `if`); a troca deixa o `print("OK")` dentro do `if`. O mutante ainda morre, mas o `de` devia trazer a indentação nova.

## Delta lido
`bin/forge-check delta --parecer docs/reviews/metade-k6.md` sobre `053f416..6dda8fd`: `scripts/suite-paralela.py` 21-23, 234-239, 241-242, 245-247, 252, 497-498; `tests/mutantes/metade-k6-2.json` 34-63; `tests/mutantes/metade-k6.json` 9, 17, 20; `tests/test_suite_paralela.py` 147, 185-186, 199-214; `tests/test_suite_reuso.py` 111-127. Já lido na volta 1 e fora do delta: o resto do lote `ce1a341..053f416` (conferido sem achado no parecer `d9639dd`). Pareceres de QA e segurança na branch não são revisados aqui.

## Parecer
**Aprovado.**

- A1 da volta 1 (bloqueante, CI herdado no Brinquedo): resolvido em `tests/test_suite_paralela.py:147` (`self.env.pop("CI", None)`). Evidência: `CI=true python3 -m unittest tests.test_suite_paralela tests.test_suite_reuso` → `Ran 37 tests ... OK`, rc=0; `env -u CI` igual, rc=0 (logs em `$TMPDIR/tech-lead-metade-k6/`).
- A2 da volta 1 (recomendado, código de saída da terceira chamada): resolvido em `tests/test_suite_paralela.py:185-186`.
- `fora_do_hash` (`scripts/suite-paralela.py:234`): a pasta tem de ser igual a um item de `FORA_DO_HASH` (`in` na tupla compara por igualdade), então subpasta, `_modelo.md`, `README.md`, arquivo não `.md` e `docs/reviewsx/` entram no hash; arquivo na raiz dá pasta vazia e entra. Coberto por `test_modelo_readme_e_subpasta_das_pastas_de_parecer_mudam_o_hash` e pelo M12.
- `ls-files -v -z` (`:245-247`): recusa minúscula (assume-unchanged, inclusive `s`) e `S` (skip-worktree); erro do git devolve `None`. Coberto por `test_skip_worktree_e_assume_unchanged_nao_dao_hash` e pelo M13.
- Recálculo no fim (`:497-498`): só grava se o hash final for o do começo; com os dois `None`, `gravar_carimbo` já recusa hash vazio (`:267`). O commit no meio passa pela `conferir_arvore` (status limpo antes e depois), por isso a guarda nova é necessária; `test_commit_no_meio_da_suite_nao_grava_carimbo` volta à árvore do começo e prova que não há reuso (M14).
- Mutantes: `bin/forge-mutante tests/mutantes/metade-k6.json tests/mutantes/metade-k6-2.json` no `6dda8fd` → M1 a M14 `morreu`, rc=0.
- Teto M14: 287 linhas de código e teste (`scripts/` 89, `tests/*.py` 198); mutantes, changelog e `.md` fora. Sem `hooks/` nem caminho de `PROTEGIDOS`.
- `R-NEUTRO`, `R-CUSTO`: nada específico de projeto nem pago. Fragmento `changelog.d/metade-k6.md` presente. PA-7: `docs/engineering/achados-recorrentes.md` sem itens.

Segurança: parecer próprio do `security-engineer` (E2.1), não refeito aqui. QA: E3.1.
