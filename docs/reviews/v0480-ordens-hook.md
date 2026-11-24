---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-ordens-hook
commit: a6e0d1014e2643e21e1b261154a1ce9160c87662
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E140.7, revalidação do #805 depois do merge da develop)

Revalidação por delta (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0480-ordens-hook.md`, intervalo `35211762..a6e0d101`, sem o que veio da base. Parecer anterior: aprovado em `35211762` (`b8443170`). O único commit novo do intervalo é o merge `a6e0d101` da develop `216413c9`, que já traz o corte 1 (a guarda das ordens no `conformidade`, `GuardaDasOrdens` e as specs `v0480-ordens-guarda*.json`).

## Delta lido
- **`hooks/conformidade.py:1612`**: a linha que o delta lista é a resolução do merge e fica igual à da develop. `git diff 216413c9 a6e0d101 -- hooks/conformidade.py hooks/conformidade.json bin/forge-init` sai vazio.
- **Mutantes retirados** (os 10 da guarda nas specs `v0480-ordens-hook-3.json`, `-4.json` e `-5.json`, e os 6 da spec `-6.json`, apagada): cada um está na develop `216413c9`, com o mesmo alvo. Os mutantes das pastas das ordens, da cópia principal e dos ignorados do `forge-init` estão em `tests/mutantes/v0480-ordens-guarda.json`. Os do mapa de donos do projeto e de `entrada_valida` estão em `tests/mutantes/v0480-ordens-guarda-2.json`. O mutante da cópia principal já cita o texto novo, com `em_qualquer_lugar`. Nenhuma guarda perde mutante. As specs que ficam na branch (`v0480-ordens-hook*.json`, 20 mutantes) miram só `hooks/ordens.py`, e nenhum ID repete os da guarda.
- **Testes retirados de `OrdensEmVigor`**: os 4 `test_conformidade_*` e `worktree` passam para `GuardaDasOrdens` (`tests/test_hooks.py:3804`), igual à develop, com uma classe só e sem duplicata. `OrdensEmVigor` reusa `worktree = GuardaDasOrdens.worktree` (`tests/test_hooks.py:3969`). O comentário de `entrada_valida` aponta a spec `-guarda-2.json`. Nenhuma asserção foi afrouxada.
- **Índices**: `docs/indice-forge.md` e `docs/hooks-fixtures.md` só acrescentam as linhas do `ordens` (11 fixtures) e do `vigia` (`time-*`, 4 fixtures do commit `c63e9615`, já no escopo aprovado antes).

## Escopo contra a develop
`git diff --stat 216413c9 a6e0d101` mostra só o corte 2: `hooks/ordens.py`, `hooks/hooks.json`, a emenda da ADR 0003, `changelog.d/`, os pareceres, as fixtures `tests/hooks/ordens/`, as 4 fixtures `vigia/time-parado-*`, as specs `v0480-ordens-hook*.json`, `tests/test_hooks.py`, `tests/test_doutor.py`, `tests/test_vigia_parado.py` (sai um `import subprocess` sem uso) e os dois índices.

## Teto H1
`git diff --numstat 216413c9 a6e0d101 -- hooks/` dá `hooks/ordens.py` 107+ e `hooks/hooks.json` 32+/1-, ou seja 140 linhas de código. Fica dentro do teto de 150 e é um comportamento só: o hook `ordens`.

## Provas
- `bin/forge-mutante --conferir --base 216413c9`: `conferidas: o trecho de cada spec do diff está no lugar`.
- `python3 -m unittest tests.test_hooks.OrdensEmVigor tests.test_hooks.GuardaDasOrdens tests.test_doutor.HookDoutor.test_hooks_json_registra_o_doutor_so_em_sessionstart_e_stop tests.test_hooks.Hooks.test_hooks_json` (`env -i`): `Ran 26 tests in 10.388s OK`.
- CI do PR #805 no head `a6e0d101`: `catraca` verde (rótulo `afrouxa-regra` aplicado). `bateria (pareceres)` está vermelha porque os pareceres ainda não estão no head. A suíte 10/10 estava pendente na hora da leitura. O merge espera tudo verde.

## Parecer
Aprovado. O merge da develop só tira da branch o que o corte 1 já levou para a develop, com os mesmos mutantes e testes. O diff restante é o corte 2, com 140 linhas de código.
