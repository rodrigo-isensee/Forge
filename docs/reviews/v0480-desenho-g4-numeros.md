---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-desenho-g4-numeros
commit: b146a2e249bd645cc8f099d24555ea54cd60dcc9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E137.9, números do desenho G4, PR #819)

Escopo: `docs/propostas/g4-trava-real-bp8.md` (4 linhas) e `changelog.d/v0480-desenho-g4-numeros.md` (novo), base 0e59c446. Só documentação: sem código, sem guarda, sem mutante.

## Conferência dos 4 números (no head b146a2e2)
- T4, "passo 9b": a seção (c) tem o passo 9 (tags protegidas) com o subitem b (Restrict creations sem bypass do Actions); confere.
- T6, "depois do passo 10": o passo 10 é o CODEOWNERS; confere.
- T10, "passo 11": o passo 11 é o `strictAllowlist`; confere.
- Linha 22, "111 pontos `barrar(`": `grep -oE 'barrar\(\s*"R-[A-Z]+"' hooks/conformidade.py` no head dá 63 R-CONFORMIDADE, 19 R-REVIEW, 11 R-CONTRIB, 9 R-VERIFY, 6 R-MAIN, 3 R-FLUXO, total 111, igual à soma da quebra; confere. Fecha o A1 e o A2 de `docs/reviews/v0480-desenho-g4.md`.

## Checagens de ferramenta (citadas)
- `bin/forge-changelog conferir --base 0e59c446 --branch melhoria/v0480-desenho-g4-numeros`: `ok: 1 fragmento(s) novo(s)`, rc=0.
- `python3 -m unittest test_forge.Neutralidade`: 3 testes OK.
- CI do PR #819 no head: catraca vermelha só pelo texto do PR (R-CONTRIB: faltam as seções `## Projeto de origem` e `## Como medir`); a suíte estava em andamento. Não é defeito do diff: é o corpo do PR, a completar antes do merge.

## Parecer
Aprovado. Os quatro números batem com a seção (c) e com a contagem por ID no head; o fragmento de changelog é válido. Pendência fora do diff: preencher as duas seções do corpo do PR para a catraca ficar verde.
