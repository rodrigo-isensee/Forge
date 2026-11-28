---
tipo: review
contrato: 1
pedido: v048
branch: melhoria/v047-jargao-id-duas-letras
commit: ff6bff0690d9046d570c5d2b5c04824382bcf9b8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Code review: retomada do jargão com ID de regra de duas letras (E13.3; revisão delta E13.11)

Escopo: revisão delta `cf59506c..ff6bff06`, sobre os três portões aprovados em cf59506c (pedido v047). O delta tem os commits de parecer da v047 (`ae25187b` e anteriores, só em `docs/reviews/`, `docs/qa/` e `docs/security/`) e o merge `ff6bff06` da develop `a1971853`. O revisor não fez a entrega.

## Sondas

## Parecer
Aprovado no head ff6bff06. O merge é limpo: não muda o comportamento do item nem perde nada da develop.

- Merge sem resolução manual: `git show --remerge-diff ff6bff06` sai vazio (0 linhas), com pais `ae25187b` e `a1971853`; a base do brief (`a1971853`) é ancestral do head.
- Nada da develop se perde: `git diff --stat a1971853 ff6bff06` mostra só os 7 arquivos do item (`hooks/meta.py` com 1 linha, `tests/test_meta.py`, a spec de mutantes, o fragmento de changelog e os três pareceres).
- O patch é o mesmo já aprovado: o diff de `hooks/`, `tests/` e `changelog.d/` em `1b88640e..cf59506c` e em `a1971853..ff6bff06` só difere nas linhas `index` e no deslocamento dos hunks (de 141 para 171 em `hooks/meta.py`, de 192 para 193 em `tests/test_meta.py`).
- `hooks/meta.py:174` no head: `"regra": re.compile(r"(?<![\w-])R-[A-Z]{2,}(?![\w-])")`.
- `cf59506c..ae25187b` só toca os três pareceres (103 linhas, todas em `docs/`).

Verificadores, rodados no clone próprio no head ff6bff06:
- `python3 -m unittest tests.test_meta`: 56 testes, OK.
- `bin/forge-mutante --processos 1 tests/mutantes/v047-jargao-id-duas-letras.json`: M1 e M2 morreram (`hooks/meta.py:174`).
- ci: ff6bff0690d9046d570c5d2b5c04824382bcf9b8 verde

O CI é o run 46166166392 do PR #966, concluído com sucesso no ff6bff06 (as cinco partes da suíte, a bateria e a instalação).

Tamanho (H1): 1 linha de código, dentro do teto. Neutralidade (`R-NEUTRO`): o merge não traz nada de projeto ao item. Não vi problema antigo fora do delta; nenhum cartão novo.
