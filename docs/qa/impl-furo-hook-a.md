---
tipo: qa
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a5
commit: 6ddca7a8890c3a153bf00ab4d75962a5a99c78de
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-furo-hook-a, branch a5 (A5 ROTULO-VARIAVEL)

Diff lido: 234dbe0..6ddca7a. Item do pedido: E5/A5, `aplica_afrouxa_regra` com o rótulo vindo de variável, substituição, `xargs`, alias ou escape JSON exige o dono (`R-CONTRIB`). Código: `hooks/conformidade.py`, `tests/test_hooks.py` +5, 19 fixtures `rotulo-variavel-*`, spec `tests/mutantes/impl-furo-hook-a-a5.json`, `docs/hooks.md`. M14 (`agents/tech-lead.md:19`): 39 linhas de código e teste, uma classe em `hooks/`. Cumpre.

Revalidação sobre o head novo. Delta lido (`forge-check delta`, a6c8952..6ddca7a): só `tests/mutantes/impl-furo-hook-a-a5.json:25-26` (+2 -2), o trecho de A5-m3 passa a `or palavras[-1] in ROTULO_COM_VALOR or por_xargs)` para `... or False)`. Os demais arquivos não mudaram desde o parecer anterior.

## Achados
- A1 (recomendado) tests/mutantes/impl-furo-hook-a-a5.json:25 · o A1 anterior (A5-m3 inválido, guarda `or por_xargs` sem mutante) foi corrigido em 6ddca7a: A5-m3 morre; nada bloqueante aberto

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A5: rótulo por variável, substituição, prefixo, aspas ANSI ou comentário em expansão exige o dono | fixtures `rotulo-variavel-por-variavel`, `-por-substituicao`, `-com-prefixo`, `-aspas-ansi`, `-comentario-em-expansao` (bloqueia) | outro argumento e outro rótulo literal liberam (`-outro-argumento-libera`, `-rotulo-literal-outro-libera`) | passou |
| A5: opção de rótulo sem valor no fim da linha e `xargs` com qualquer comando antes exigem o dono | fixtures `-opcao-sem-valor`, `-por-xargs`, `-por-xargs-cat`, `-por-xargs-echo`, `-por-xargs-printf`, `-por-xargs-com-valor` | entrada do `xargs` que o hook não vê | passou |
| A5: `gh alias`, alias do shell e `gh api` com escape JSON exigem o dono | fixtures `-gh-alias`, `-alias-do-shell`, `-api-input`, `-api-escape-json`, `-api-escape-malformado`; `-api-escape-inofensivo-libera` | escape que não decodifica conta como ilegível; escape inofensivo libera | passou |
| A5: spec de mutantes declarada cobre cada linha de guarda | `bin/forge-mutante tests/mutantes/impl-furo-hook-a-a5.json` | cobertura "declarado, não provado" | passou (rc=0, 9 mutantes mortos) |

## Cenários e resultado real
- Vermelho antes do verde (manual, cópia em `$TMPDIR` com `hooks/conformidade.py` da base e os testes do head): `test_fixtures_do_lote_furo_hook_a` falha nas fixtures de `alias-do-shell`, `api-escape-json`, `api-escape-malformado`, `com-prefixo`, `gh-alias`, `opcao-sem-valor`, `por-substituicao`, `por-variavel`..., FAILED. Verde no head: OK. O `forge-testes --vermelho` sobre a suíte inteira estourou o prazo aqui, sem veredito.
- Mutação da spec do autor, no head 6ddca7a: `bin/forge-mutante tests/mutantes/impl-furo-hook-a-a5.json` rc=0; `A5-m1 morreu :1366`, `m2 :1367`, `m3 :1367`, `m4 :1368`, `m5 :1379`, `m6 :1380`, `m7 :1415`, `m8 :354`, `m9 :1440`, todos morreram, nenhum inválido nem sobrevivente.
- `bin/forge-mutante --cobertura --base 234dbe0`: todas as condições mudadas saem `coberta` (354, 1366 com m1 a m3, 1368, 1380, 1415, 1440); conferido contra o diff, a guarda `or por_xargs` de :1367 tem agora mutante declarado.
- Suíte: `python3 -m unittest tests.test_hooks` 53 testes OK; `scripts/validar-plugin.sh` Validation passed. A suíte completa roda no pre-push do envio.
- Sem interface de usuário: acessibilidade e E2E não se aplicam.
