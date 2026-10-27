### Corrigido
- O leitor dos hooks falha fechado em `$'…'` com `\'` dentro: o `shlex` o junta ao `;` seguinte numa palavra só e o conformidade liberava `echo $'it\'s'; cat .env\'`; o mesmo vale para `\$'…'` no argumento entre aspas duplas de `bash -c`, `sh -c` e `eval`, que o shell de dentro lê como `$'…'` (HOOK-ANSI-C).
