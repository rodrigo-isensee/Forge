---
tipo: qa
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a5
commit: a6c8952657ecfb58d38d6ac7cbbfd42b9f87c6b0
parecer: reprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-furo-hook-a, branch a5 (A5 ROTULO-VARIAVEL)

Diff lido: 234dbe0..a6c8952. Item do pedido: E5/A5, `aplica_afrouxa_regra` com o rótulo vindo de variável, substituição, `xargs`, alias ou escape JSON exige o dono (`R-CONTRIB`). Código: `hooks/conformidade.py` +25/-9, `tests/test_hooks.py` +5, 19 fixtures `rotulo-variavel-*`, spec `tests/mutantes/impl-furo-hook-a-a5.json`, `docs/hooks.md`. M14 (`agents/tech-lead.md:19`): 39 linhas de código e teste, uma classe em `hooks/`. Cumpre. O comportamento está provado (testes e vermelho abaixo); o que reprova é a prova de mutação do pedido que toca `hooks/`.

## Achados
- A1 (bloqueante) tests/mutantes/impl-furo-hook-a-a5.json:1 · a spec ficou velha depois da volta 1: A5-m3 sai "inválido" (o trecho `or por_xargs and bool(pedidos)` não existe mais), rc=2, sem veredito; a guarda `or por_xargs` de hooks/conformidade.py:1367 não tem mutante declarado

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A5: rótulo por variável, substituição, prefixo, aspas ANSI ou comentário em expansão exige o dono | fixtures `rotulo-variavel-por-variavel`, `-por-substituicao`, `-com-prefixo`, `-aspas-ansi`, `-comentario-em-expansao` (bloqueia) | outro argumento e outro rótulo literal liberam (`-outro-argumento-libera`, `-rotulo-literal-outro-libera`) | passou |
| A5: opção de rótulo sem valor no fim da linha e `xargs` com qualquer comando antes exigem o dono | fixtures `-opcao-sem-valor`, `-por-xargs`, `-por-xargs-cat`, `-por-xargs-echo`, `-por-xargs-printf`, `-por-xargs-com-valor` | entrada do `xargs` que o hook não vê | passou |
| A5: `gh alias`, alias do shell e `gh api` com escape JSON exigem o dono | fixtures `-gh-alias`, `-alias-do-shell`, `-api-input`, `-api-escape-json`, `-api-escape-malformado`; `-api-escape-inofensivo-libera` | escape que não decodifica conta como ilegível; escape inofensivo libera | passou |
| A5: spec de mutantes declarada cobre cada linha de guarda | `bin/forge-mutante tests/mutantes/impl-furo-hook-a-a5.json` | cobertura "declarado, não provado" | falhou (rc=2, A5-m3 inválido; A1) |

## Cenários e resultado real
- Vermelho antes do verde (manual, cópia em `$TMPDIR` com `hooks/conformidade.py` da base e os testes do head): `test_fixtures_do_lote_furo_hook_a` falha nas fixtures de `alias-do-shell`, `api-escape-json`, `api-escape-malformado`, `com-prefixo`, `gh-alias`, `opcao-sem-valor`, `por-substituicao`, `por-variavel`..., FAILED. Verde no head: OK. O `forge-testes --vermelho` sobre a suíte inteira estourou o prazo aqui, sem veredito.
- Mutação da spec do autor: `A5-m1 morreu :1366`, `m2 :1367`, `m4 :1368`, `m5 :1379`, `m6 :1380`, `m7 :1415`, `m8 :354`, `m9 :1440` morreram; `A5-m3` inválido (rc=2).
- Mutante escrito pelo QA para a linha sem mutante (spec em `$TMPDIR`, nada gravado no repositório): retirar `or por_xargs` de `:1367` morreu (`QA-a5-m3 · morreu`). Ou seja, o código e os testes protegem a guarda; falta só a spec declarar um mutante que rode.
- `--cobertura --base 234dbe0`: as demais condições mudadas têm mutante declarado.
- Sem interface de usuário: acessibilidade e E2E não se aplicam.
- Para liberar: trocar o trecho de A5-m3 pela forma atual (`or palavras[-1] in ROTULO_COM_VALOR or por_xargs)` para `or palavras[-1] in ROTULO_COM_VALOR)`) e rodar a spec até rc 0.
