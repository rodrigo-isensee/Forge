---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-meta-notas
commit: e31f2416990cc6ed223b76584141805061eea624
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E109.4 e E109.9, melhoria/v0480-meta-notas)

Escopo: diff `900bfdfe..064e58ce`, dois cartões no `hooks/meta.py`. META-NOTAS-ENTRE-FERRAMENTAS (`988f0ab4`, absorve a `melhoria/v0479-meta-notas`, aprovada em `docs/reviews/v0479-meta-notas.md`) e META-NOTAS-RECONTA (`064e58ce`, A1 e A2 daquele parecer). Cerca de 55 linhas de código em `hooks/meta.py`, um comportamento por commit (H1).

## Achados
- A1 (recomendado) hooks/meta.py:320 · `notas.json` guarda a marca de um transcrito só: duas sessões no mesmo projeto alternando o Stop apagam a marca uma da outra e a reconta de A1 da v0479 volta (sonda: A, B, A com aviso dá 1 no 2o Stop de A, esperado 0). Guardar a marca por transcrito.
- A2 (recomendado) hooks/meta.py:20 · Docstring, `tests/test_meta.py:315` e `tests/evals/test_erros_por_papel.py:187,218` datam o E25.1 em 0.47.9, mas ele não saiu nessa versão (plugin em 0.47.14); citar só o E25.1 ou a versão da release.

## Parecer
Aprovado. O cartão RECONTA fecha os dois recomendados da v0479: o segundo Stop sem fala nova do dono para na marca (uuid do registro mais novo lido) e pula a final anterior pelo sha256 (caso D13, final que chega depois ao transcrito), e o pré-filtro passou a `"type":"tool_result"`, que não casa com o mesmo texto dentro de um `input` (ali as aspas vêm escapadas). A marca só leva uuid e hash, nunca texto; marca de outro transcrito, ilegível ou fora da forma é ignorada e a medida volta ao comportamento do E25.1, sem contar a menos. Falha de escrita da marca cai no `except` do `principal` (só mede, não muda a decisão do Stop). O eval `MensagemEmOutroIdioma` perdeu o `expectedFailure` e passa (erro por papel). Changelog com custo medido e critério de reversão nos dois fragmentos. A spec M6 do SIEG-G4 segue a linha nova.

Ferramentas no SHA revisado: `python3 -m unittest tests.test_meta tests.evals.test_erros_por_papel.MensagemEmOutroIdioma` com 52 testes OK; `bin/forge-mutante` nas três specs `tests/mutantes/v0478-meta-notas*.json` com M1 a M21 mortos (M11 a M14, M19 e M21 por erro do teste declarado, que conta como morto) e em `tests/mutantes/v047-g4-medida-idioma.json` com M4 a M8 mortos. Um mutante por linha de guarda mudada. Suíte inteira e corpus `tests/hooks/`: no CI do PR (`R-REVIEW`). Segurança no mesmo head: `docs/security/v0480-meta-notas.md`.

A1 e A2 não bloqueiam (`R-REVIEW`): A1 só infla a medida com sessões paralelas, sem efeito na decisão do Stop, e degrada para o comportamento já aprovado do E25.1; A2 é texto. Viram cartão depois do merge.

## Revalidação (E109.9, head e31f2416)
Delta lido: `forge-check parecer delta docs/reviews/v0480-meta-notas.md`, intervalo `064e58ce..e31f2416`, no domínio `changelog.d/v0480-meta-notas.md`, `hooks/meta.py`, `tests/mutantes/v0478-meta-notas-3.json` e `tests/test_meta.py`; nada fora dele relido.

O commit `e31f2416` fecha o A1 da segurança (`docs/security/v0480-meta-notas.md`): em `hooks/meta.py:323-326` a falha de `gravar_json` na marca (`OSError`) vai ao `hook.registrar_erro` (`hooks/_comum.py:2737`, que já engole a própria falha) e a contagem segue, então a linha do `mensagens.jsonl` não se perde. O `except` é estreito (`OSError`, não `Exception`) e comentado; a marca não gravada só faz o próximo Stop recontar, o comportamento já aprovado do E25.1. O teste novo cria `notas.json` como pasta e afirma a linha `(1, True)` e um `IsADirectoryError` no log (ramo de falha por comportamento, não pela fonte). Fragmento do changelog com a entrada em `### Corrigido`. Os A1 e A2 deste parecer seguem como recomendados.

Ferramentas no SHA e31f2416: `python3 -m unittest tests.test_meta` com 50 testes OK; `bin/forge-mutante --ids M22 tests/mutantes/v0478-meta-notas-3.json`: `M22 · morreu · hooks/meta.py:326`. Um mutante para a única guarda nova. Suíte inteira no CI do PR (`R-REVIEW`).
