---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-parecer-mesclado
commit: 9f4c3ca37024789b7994296fc3f9716021b098af
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E50.21 (ENTREGA-PARECER-MESCLADO, merge da develop e expectativa do teste antigo)

Revalidação pelo delta (`forge-check parecer delta`, intervalo `5376b86d..9f4c3ca3`; H3, `R-REVIEW`). No domínio: `bin/forge-check`, `docs/hooks.md`, `tests/test_hooks.py` e `tests/test_revisor_wt.py`. O delta avisa que o merge `bbdd9b0` (a branch com a própria cópia remota) não está na develop e conta inteiro; conferi pelo patch da branch: `git diff 8a503799 5376b86d` contra `git diff 20bbbd8d 9f4c3ca3`, sem as linhas `index` e `@@`, só difere nos pareceres (fora do domínio) e em `tests/test_revisor_wt.py`. Os trechos de `bin/forge-check`, `docs/hooks.md` e `tests/test_hooks.py` no delta vieram da develop (#713, #716, #718, #720, #723, #729), e o merge `6f41c645` não resolveu nada à mão.

## Parecer
Aprovado no head 9f4c3ca3.

`9f4c3ca3` muda só a expectativa de `ParecerTrazido` em tests/test_revisor_wt.py:314: sem `autoria.jsonl`, o parecer mesclado na volta deixa de sair `confira` e sai `ok (anexo do portão: parecer de tech-lead commitado na volta só com parecer)`. É o comportamento do E50.1, já aprovado nas rodadas anteriores (a mensagem está em bin/forge-check:3321 e em `docs/hooks.md`); o teste veio da develop e só ganhou a expectativa nova, sem afrouxar outra asserção. Nenhuma guarda mudou no delta, então não há mutante novo a declarar.

Rodei com ambiente limpo: `python3 -I -m unittest discover -s tests -p test_revisor_wt.py -k ParecerTrazido` → `Ran 4 tests · OK`. A suíte inteira fica com o CI do PR #734 (`R-REVIEW`); a `bateria (pareceres)` dele estava vermelha porque os pareceres apontavam para 5376b86d.
