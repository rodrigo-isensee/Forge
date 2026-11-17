### Corrigido
- Hook `conformidade`: o número colado à redireção (`2>/dev/null`, `9<x`, `{fd}>x`) é o descritor e não vira destino nem programa (`cp a .git/config 2>/dev/null`, `2>/dev/null git push --force`); `$@` e `$*` são parte opaca do destino; `declare|typeset|local -n d=_` e a atribuição como argumento de comando não dão o valor de `$d` (A17 a A19, v047).
