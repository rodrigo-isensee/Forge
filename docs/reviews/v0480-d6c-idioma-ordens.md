---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0480-d6c-idioma-ordens
commit: 66c9f9a1869ca39537b97be3a3e70c73456ec93b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 E1.2 (PR #866, revalidação por delta do merge da develop)

Terceira rodada, só o delta. `forge-check parecer delta` no head `66c9f9a1` deu `revalida: sim`: `docs/hooks-fixtures.md` mudou depois do parecer (base `origin/develop` a27eab7). Delta lido, `0c7e8f0c..66c9f9a1`: é o merge `66c9f9a1` de `a27eab7e` (#859, já revisado na develop). O patch do PR contra a develop (`git diff a27eab7e 66c9f9a1`) é o da rodada anterior; `hooks/ordens.py` e `tests/mutantes/v0480-d6c-idioma-ordens.json` não mudaram (`git diff 0c7e8f0c 66c9f9a1` vazio neles). O único arquivo do domínio que o merge tocou é o índice gerado: o conflito em `docs/hooks-fixtures.md` foi resolvido somando os dois lados (3579 fixtures; `ordens` 14, `agentes` 133, `pesado` 30; linha `idioma-*` presente), e `python3 -I scripts/indice-fixtures.py --conferir` no head dá "em dia" (rc 0). `python3 -m unittest tests.test_hooks.OrdensEmVigor` no head, ambiente limpo: 23 OK. CI do head na hora deste parecer: catraca, instalação e baterias verdes; a suíte em partes pendente, e o CI verde segue obrigatório para o merge. Parecer mantido: aprovado.

Rodada anterior (E174.13, head `0c7e8f0c`), texto mantido abaixo. Segunda rodada. A primeira (E174.6, head `748f2975`) reprovou por A1 (RecursionError cala as ordens no clone do Forge). Esta lê só o delta que o `forge-check parecer delta` aponta: `748f2975..0c7e8f0c`, domínio código e testes, 5 arquivos (`hooks/ordens.py`, `tests/test_hooks.py`, `tests/mutantes/v0480-d6c-idioma-ordens.json`, a fixture nova `tests/hooks/ordens/idioma-config-aninhada-no-forge-ordens-seguem.json` e o índice gerado `docs/hooks-fixtures.md`). Uma linha de código mudada, dentro do teto H1.

## Achados
- A2 (recomendado) hooks/ordens.py:80 · Sem mudança na volta: `{"idioma_do_dono": null}` dá None aqui e "pt" no meta.py:237, e a docstring (ordens.py:11) cita o critério do meta.py. Vira cartão depois do merge: alinhar (null como ausente) ou tirar a citação.

## Parecer
**Aprovado.**

A1 (resolvido): `hooks/ordens.py:78` agora é `except (OSError, ValueError, RecursionError)`. A sonda S1 da rodada anterior, refeita em processo no head (`python3 -I`, `.forge/config.json` = `'[' * 60000`), dá `None` em vez de escapar `RecursionError`; as ordens seguem. O teste `test_idioma_torto_sai_none_sem_erro` (`tests/test_hooks.py:4091`) ganhou o caso aninhado de 40000 caracteres (abaixo dos 64 KiB do `ler_ordens`) e a fixture nova cobre o efeito ponta a ponta no clone do Forge (`config_bruta`, suportada pelo harness em `tests/test_hooks.py:480`; contexto inteiro conferido, só a linha fixa sem o idioma e a ordem). Guarda mudada com mutante por linha: M8 tira o `RecursionError`; M2 e M3 foram reescritos sobre a linha nova, cada um ainda tirando um só tipo. Teste de comportamento do ramo de falha, nenhum por texto da fonte.

A2 segue recomendado e fora da volta, como previsto na rodada anterior (sem gatilho de defeito; R-REVIEW).

Ferramentas, citadas: `python3 -m unittest tests.test_hooks.OrdensEmVigor` no head, ambiente limpo: 23 testes OK. `bin/forge-mutante tests/mutantes/v0480-d6c-idioma-ordens.json` no head `0c7e8f0c`: M1 a M8 morreram. Suíte inteira: só no CI; `gh pr checks 866` não trazia checagem na hora deste parecer, e o CI verde segue obrigatório para o merge.

Commit do delta: um, `fix(ordens): ...`, Conventional Commits em português, descreve o defeito, a correção e os testes.
