### Corrigido
- forge-testes: o plano dirigido (--listar, --afetados e o filtro do pre-push) leva a catraca no modo do diff (tests/catraca.py --base REF) e o teste de custo (test_hooks_volta_corpus) quando o diff toca hooks/, bin/ ou um arquivo protegido da catraca (a PROTEGIDOS dela, lida sem cópia); o resto fica como estava (v048 E9.1).
