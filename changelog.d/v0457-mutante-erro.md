### Corrigido
- forge-mutante: o mutante que leva o teste declarado a erro (exceção, não falha de asserção) conta como morto quando o mesmo teste passa sem ele (controle verde), com a linha `morreu · <arq>:<linha> · (erro) ...`; erro de carga, de fixture de classe ou também sem o mutante segue inválido ou controle vermelho.
