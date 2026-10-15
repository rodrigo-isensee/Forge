# AA2-01 - Mensagem de recusa do conferente corta a forma que passa e nomeia a variável por uma letra
- Status: corrigido em 276b7f8 (reconferido em b377f35: recusa mostra `no lugar de echo $?: && echo contém || echo não contém` e `$TMPDIR` inteiro, pelo hook real)
- Severidade: baixa
- Responsável sugerido: `forge:tech-lead` (hooks/conformidade.py, `mensagem` em hooks/_comum.py)
- Ambiente: melhoria/anti-alucinacao-regras 6a63087, hook `conformidade` PreToolUse, papéis `conferente` e `tech-lead`

## Passos para reproduzir
1. Projeto descartável com `.forge/versao`; entrada `{"tool_name":"Bash","tool_input":{"command":"echo $?"},"agent_type":"forge:conferente"}` no `hooks/conformidade.py`.
2. Repetir com `cp $TMPDIR/x docs/reviews/y.md` como `forge:tech-lead`.

## Resultado esperado
ADR 0011, "Efeito nos falsos bloqueios": a mensagem mostra a forma que passa (para `echo $?`, `&& echo contém || echo não contém`; para a variável, o nome literal) e diz qual construção barrou.

## Resultado obtido
rc 2, mas a linha de 200 caracteres termina em "...nunca com $…" (`mensagem` corta em `LIMITE_MENSAGEM`), então a forma de `echo contém || echo não contém` não aparece. Na recusa de `$TMPDIR` a mensagem diz "`$T` com ação crítica": só a primeira letra do nome.

## Evidência
```
R-CONFORMIDADE: `$` fora da gramática do papel só de leitura (conferente). Corrigir: um comando por chamada; $, crase, \, #, chaves, glob e < > só entre aspas simples ('HEAD@{1}', 'v1$'), nunca com $…
R-CONFORMIDADE: `$T` com ação crítica: o hook não modela. Corrigir: branch literal, um comando por linha, ...
```
Contorno simples: o conferente.md e a ADR já trazem as formas. Aceite do dono necessário (baixo aberto).
