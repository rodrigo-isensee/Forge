---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i1-conserto
commit: b96357e9cdaa807422be47d586676cbbcf7e0612
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-bp2-i1-conserto (BP2 I1, `forge-fechar --conserto`, E38.7), revalidação

Escopo: delta `d816262d..b96357e9` (`bin/forge-fechar` C4, `tests/test_fechar.py`, `tests/mutantes/fechar-conserto-7.json`, changelog). Só `test_fechar`; sem suíte local (o CI do PR é o portão dela). O resto do parecer anterior (C1, C3, C5 a C7) não mudou no domínio.

## Resolução dos achados anteriores
- A1 (sed do subteste com parêntese): resolvido. O id agora vai até o primeiro espaço ou `:`; `test_c4_subteste_com_parentese_no_parametro_e_conferido` e o mutante CS45 (morreu, linha 1090) o guardam.
- A2 (pulado por classe ou módulo): resolvido. O grep cobre `setUpClass`, `tearDownClass`, `setUpModule`, `tearDownModule` e `ModuleSkipped.<mod>`; `test_c4_teste_pulado_pela_classe_ou_pelo_modulo_para` (5 formas, subTest) e CS46/CS47 (morreram); `test_c4_pulado_de_outra_classe_ou_modulo_segue` guarda o falso positivo (`Outra`, `test_bb`, `test_b2`).
- Guarda nova do autor, fora dos meus achados: C4 para se o método foi apagado no head (`git grep -wF "def <nome>"` no arquivo do módulo). Coberta por `test_c4_teste_apagado_no_pr_para` e pelos mutantes CS48 e CS49 (morreram).

## Critério → teste → resultado (delta)
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C4 (id de subteste) | `Conserto.test_c4_subteste_com_parentese_no_parametro_e_conferido` | `)` no parâmetro, outro teste anotado | passou |
| C4 (pulado por classe/módulo) | `Conserto.test_c4_teste_pulado_pela_classe_ou_pelo_modulo_para`, `..._pulado_de_outra_classe_ou_modulo_segue` | 5 formas de pulo; nome parecido não confunde | passou |
| C4 (teste apagado no PR) | `Conserto.test_c4_teste_apagado_no_pr_para` | método ausente no arquivo do head | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_fechar.py -k Conserto`: `Ran 42 tests in 99.452s OK`.
- `bin/forge-mutante tests/mutantes/fechar-conserto-4.json tests/mutantes/fechar-conserto-7.json --ids CS31,CS45,CS46,CS47,CS48,CS49 --processos 2`, rev=b96357e9cdaa: CS31 1113, CS45 1090, CS46 1113, CS47 1114, CS48 1117, CS49 1111, todos `morreu`, rc=0.
- Delta: `bin/forge-mutante --base d816262d85319c97fed47261d3179f485df5bf08 tests/mutantes/fechar-conserto-*.json --processos 2`: `base=d816262d85319c97fed47261d3179f485df5bf08 mb=d816262d85319c97fed47261d3179f485df5bf08 rev=b96357e9cdaa807422be47d586676cbbcf7e0612`; 41 mutantes, todos `morreu`, rc=0. Conferência da lista contra o diff, à mão: as 5 linhas de guarda mudadas (sed 1090, classe 1113, módulo 1114, apagado 1117, arquivo 1111) têm mutante.
- Vermelho: `forge-testes --vermelho 004ce869d641ca62394d705c4453d8a014002f15 --modulos test_fechar`:
```
vermelho: [1/1] test_fechar H 365.2 s, B 289.8 s; 657 s no total
vermelho: base=004ce869d641 head=b96357e9cdaa módulos=test_fechar (restrito por --modulos)
revertidos à base: bin/forge-fechar, changelog.d/v0479-bp2-i1-conserto.md, docs/fechamento-integrador.md, ...
contagem: não prova (passa na base)=111; prova (asserção)=41; pulado=1
rc=0
```
  Os 4 testes novos do delta (`subteste_com_parentese`, `pulado_pela_classe_ou_pelo_modulo`, `pulado_de_outra_classe_ou_modulo_segue`, `teste_apagado_no_pr`) saem `H=ok · B=falha · prova (asserção)`. O pulado (`test_shellcheck_fechar_passa_limpo`) é preexistente e depende de ambiente, fora do delta.
- CI do PR: não consultado (brief sem PR).

## Parecer
Aprovado no head b96357e9: A1 e A2 resolvidos com teste que prova (vermelho) e mutante que morre; sem achado novo, sem bug aberto.
