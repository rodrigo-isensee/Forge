### Corrigido
- forge-testes: o plano dirigido (--listar, --afetados e o filtro do pre-push) leva a catraca no modo do diff (tests/catraca.py --base REF) e o teste de custo (test_hooks_volta_corpus) quando o diff toca hooks/, bin/ ou um arquivo protegido da catraca (a PROTEGIDOS dela, lida sem cópia); o resto fica como estava (v048 E9.1).
- forge-testes: o --afetados com plano acima de 1.000 testes (LIMITE_LOCAL, contados pelo plano do --listar) roda no computador só a catraca, o teste de custo e os testes do arquivo mudado, e diz quantos testes ficam para o CI do PR (v048 E9.2).
