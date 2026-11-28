---
tipo: revisao-seguranca
contrato: 1
pedido: v048
branch: melhoria/v048-jargao-id-duas-letras
commit: 51c259f8419594b6b077cc42ae7e15f67106627f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-28
---
# Review de segurança: v048-jargao-id-duas-letras (E13.29)

Rodada única sobre o head 51c259f8, base develop 9479650b, no PR #968, que substitui o #966 (E13.25). O objetivo é conferir que o patch é o mesmo que os três portões já aprovaram no #966 (parecer de segurança `aprovado` no head ff6bff06 da branch `melhoria/v047-jargao-id-duas-letras`, hoje no head 49ba5d52).

Gatilhos: `R-SEGURANCA` (hook `hooks/meta.py`, a medida de fim de resposta: só conta, nunca bloqueia).

## O que foi lido
- Escopo: `git diff 9479650b...51c259f8` toca só quatro arquivos, que são `hooks/meta.py` (1 linha), `tests/test_meta.py` (+5), `tests/mutantes/v048-jargao-id-duas-letras.json` (novo) e `changelog.d/v048-jargao-id-duas-letras.md` (novo). Nada além disso. No domínio (`hooks/`, `bin/`, `scripts/`, `.githooks/`, `.github/`), o diff é só `hooks/meta.py:174`.
- Mesmo patch: as linhas mudadas em `hooks/meta.py` e `tests/test_meta.py` de `9479650b..51c259f8` e de `a1971853..49ba5d52` (o #966 contra a base dele) são idênticas (diff dos dois diffs vazio). Os mutantes e o fragmento do changelog trocaram só de nome de arquivo. Dentro do JSON dos mutantes, a única diferença é o campo `pedido`, que passou de `v047-jargao-id-duas-letras` a `v048-jargao-id-duas-letras`. As duas specs de `tests/mutantes/v048-jargao-id-duas-letras.json` citam `R-[A-Z]{2,}(?![\w-])`, que aparece uma vez, em `hooks/meta.py:174`. Observação: o brief pedia o campo `pedido` igual a `v048`; o valor gravado segue o padrão da branch anterior (id da branch). Isso não tem efeito de segurança e fica para o code review.
- Correção: em `hooks/meta.py:174`, `R-[A-Z]{3,}` passa a `R-[A-Z]{2,}`. Não é controle: a classe `regra` só alimenta a contagem de jargão.
- Custo da regex: um quantificador só, entre lookarounds fixos de um caractere, sem aninhamento nem alternância. O custo é linear, e a medida roda sobre `texto[:TETO_DA_MEDIDA]` (`hooks/meta.py:347`; teto de 20000 em `:43`). Sondas no head, todas acima do teto: `R-` + 200.000 `A` + `-` em 0,006 s; `R-` repetido 100.000 vezes em 0,003 s; ` R-AA-` 50.000 vezes em 0,006 s; ` R-` + 200.000 `R` + `x` em 0,006 s.
- Fronteiras: `R-QA` conta (`{'regra': 1}`); `R-X`, `R-Qa` e `XR-QA` não contam; `R-QA-1` cai na classe `cartao` e não em `regra`, como antes.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Ferramentas usadas: git (diffs contra a base e contra o head 49ba5d52 do #966), sondas locais da regex e `python3 -m unittest tests.test_meta` no clone de revisão (56 testes, OK). A suíte inteira rodou no CI do PR #968 sobre o Revisar-sha (run 46167952981): `gh pr checks 968` com rc=0, as cinco partes da suíte, a instalação e as baterias em `pass`. As varreduras de segredos, de dependências e de workflow não se aplicam, porque o patch não toca segredo, dependência nem workflow.
