### Corrigido
- O leitor dos hooks falha fechado em `$'…'` com `\'` dentro: o `shlex` o junta ao `;` seguinte numa palavra só e o conformidade liberava `echo $'it\'s'; cat .env\'` (HOOK-ANSI-C).
