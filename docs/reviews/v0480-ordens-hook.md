---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: 35211762d50aec616625d3e7bd90ed88c7bb7f47
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E123.20, volta de CI do hook ordens)

Revalidação por delta (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0480-ordens-hook.md`, intervalo `fe14fb1e..35211762`, sem o merge da develop `51cb434d`. Parecer anterior: aprovado em `fe14fb1e` (`0637c6da`). Li só o commit do autor `35211762` (E123.19). A linha do `docs/indice-forge.md` que o delta lista (`forge_controle.py`) veio da develop (`ba201c86`) e fica fora do escopo.

## Delta lido
- **U6** (`tests/mutantes/v0479-conformidade-trilha-7.json`): o `de` passa a citar o texto atual de `CONTROLE_NO_TEXTO` (`hooks/conformidade.py:3828-3829`, com `ordens`), e o `para` ganha `ordens` também. Assim o mutante segue apertando só a posição, sem tirar a pasta nova.
- **`entrada_valida`** (`hooks/conformidade.py:3602-3612`): a função interna `texto` sai e as checagens ficam em linha. É equivalente: `isinstance(v, str) and bool(v)` vira `isinstance(v, str) and v != ""`. Na branch, `A or B and C` agrupa como `A or (B and C)`, que é o mesmo de antes. As entradas aceitas e recusadas não mudam. O motivo (custo do corpus) está na docstring.
- **Testes**: há 5 casos de falha novos em `test_politica_de_conformidade_malformada_bloqueia`: caminho vazio, caminho que não é texto, motivo vazio, item de `quem` que não é texto e branch vazia. Cada guarda tem um ramo de falha por comportamento, e nenhum teste foi afrouxado.
- **Mutantes**: M32 a M37 (`tests/mutantes/v0480-ordens-hook-6.json`), um por linha de guarda mudada.

## Provas
- `python3 -m unittest tests.test_hooks.Hooks.test_politica_de_conformidade_malformada_bloqueia tests.test_hooks.Hooks.test_fixtures_do_controle_so_jarvis` (`env -i`): `Ran 2 tests in 22.000s OK`.
- `bin/forge-mutante tests/mutantes/v0480-ordens-hook-6.json --processos 1`: M32 a M37 `morreu` (linhas 3605 a 3612). `--ids U6` na spec `trilha-7`: `U6 · morreu · hooks/conformidade.py:3828`.
- `bin/forge-mutante --conferir --base fe14fb1e`: `conferidas: o trecho de cada spec do diff está no lugar`.
- CI do PR #805 no head `35211762`: suíte 5/5 verde. Falham só `catraca` (`R-CONFORMIDADE`: falta o rótulo `afrouxa-regra`, autorizado pelo dono em 2026-11-23 15:25 e aplicado depois do último push), `bateria (pareceres)` (pareceres ainda não estão no head) e o agregado `bateria`. Nenhuma das falhas vem do código.

## Parecer
Aprovado. A volta de CI só refatora `entrada_valida` para uma forma equivalente e atualiza a spec U6 para o texto atual da guarda. Cada guarda tem caso de falha e mutante que morre.
