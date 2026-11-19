---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-develop-relogio
commit: 76cbce17155b2a769e40155c7fcb47b8bb904f46
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-19
---
# QA: v0478 (relógio nos testes da develop, E33.4)

Diff contra a base c720891e: só testes (`tests/test_hooks.py`, `tests/test_hooks_volta_corpus.py`), a spec `tests/mutantes/v0478-develop-relogio.json` e o fragmento de changelog. Nenhum código de produção mudou, então não há regra nova de produção a provar por reversão. Revisado no head 3298def5; o merge de 05c5254c só trouxe os pareceres de review (18fb9603) e segurança (4464a1d7).

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Obrigação 1 (TESTE-SONDA-S1-RELOGIO): a S1 real (sono a mais) é recusada em qualquer carga | `Hooks.test_liberar_ou_provar_a_carga_recusa_a_sonda_s1` (parcela fixa 0,36 da S1 do review) | limite do aproveitamento mínimo da CPU; sem depender da carga da hora | passou (rodado local: 1 teste, OK, 10,7 s); mutante M1 morre |
| Obrigação 2: o corpus nos dois hooks não reprova por carga, e a regressão real ainda reprova | `CorpusDaVoltaUnica.test_corpus_nos_dois_hooks` (menor de até 3 medidas, `menor_custo`) | limite de CPU do corpus; código acima do orçamento passa dele em toda medida | passou (H=ok no `--vermelho`) |

## Cenários e resultado real
- Teste tocado 1, rodado: `python3 -I -m unittest discover -s tests -p test_hooks.py -k test_liberar_ou_provar_a_carga_recusa_a_sonda_s1` → `Ran 1 test in 10.708s · OK`.
- Os dois módulos tocados, completos, no `--vermelho` (lado H): `test_hooks` 153 testes, todos ok ou pulados por ambiente (11 pulados são de ns de pid e `/proc`, que já pulavam na base); `test_hooks_volta_corpus` 16 ok. O autor rodou os dois módulos 5 vezes sob carga (rodada1 a rodada5); não repeti.
- Suíte inteira: no CI do PR, check-run `bateria` do mesmo sha (não rodada local, E33.4).

## Vermelho antes do verde
Saída 1ª tentativa (prazo padrão), `forge-testes --vermelho c720891e --modulos test_hooks,test_hooks_volta_corpus`:
```
vermelho: base=c720891e7103 head=05c5254cfff4 módulos=test_hooks,test_hooks_volta_corpus (restrito por --modulos)
revertidos à base: changelog.d/v0479-develop-relogio.md, docs/reviews/v0479-develop-relogio.md, docs/security/v0479-develop-relogio.md
mantidos no HEAD: tests/mutantes/v0478-develop-relogio.json, tests/test_hooks.py, tests/test_hooks_volta_corpus.py
test_hooks · sem veredito (prazo, sinal ou executor sem registro em H,B)
(16 testes de test_hooks_volta_corpus: H=ok · B=ok · não prova (passa na base))
contagem: não prova (passa na base)=16; sem veredito=1
rc=2
```
2ª tentativa só do `test_hooks` com `--prazo 2400` (o módulo passa dos 600 s do padrão):
```
vermelho: base=c720891e7103 head=05c5254cfff4 módulos=test_hooks (restrito por --modulos)
contagem: não prova (passa na base)=142; pulado=11
nenhum teste prova a mudança.
rc=1
```
Leitura: o `--vermelho` reverte só arquivos de produção e mantém os testes no HEAD nas duas cópias; como o PR muda apenas testes, a base e o HEAD rodam o mesmo teste e o resultado só poderia diferir pela carga, que é a causa do defeito (não reproduzível sob demanda numa máquina livre). O vermelho do defeito está no CI da develop (corpus: 180,79 s e 181,40 s contra 180 s; S1: recusa pela parcela da hora, descrito no docstring) e, no que decide, no mutante M1 abaixo, que faz o teste da S1 cair quando a guarda é afrouxada. Não é achado: não há teste novo de regra de produção sem prova; é limite da ferramenta para correção só de teste.

## Mutação
`bin/forge-mutante tests/mutantes/v0478-develop-relogio.json` (um mutante, a única guarda de decisão mudada: o aproveitamento mínimo em `tests/prova_de_carga.py:70`; o diff não toca `bin/`, `hooks/` nem `.githooks/`):
```
forge-mutante: pedido=v0478-develop-relogio rev=05c5254cfff4 spec=be9f345fde28c872534eb14a12e4f4e07ecd7a3770239a41c1f350dbb1e37e52
M1 · morreu · tests/prova_de_carga.py:70
rc=0
```
Nenhum sobrevivente. Para `menor_custo` (corpus) não há mutante declarado e a lógica é de 8 linhas em `tests/apoio_volta_unica.py`, conferida por leitura: para na primeira medida abaixo do limite, senão toma a menor de até 3; regressão real passa do limite em todas e reprova.

## Bugs
Nenhum aberto (`docs/qa/bugs/` sem entrada).

## Revalidação no head 76cbce17 (E33.9)
`forge-check parecer delta` listou no domínio do QA só `tests/test_hooks.py` (constantes `PAREDE_DA_S1_S`, `CPU_DA_S1_S`, `PARCELA_DA_S1`; o teste da S1 injeta relógio, CPU e parcela e confere que a recusa é a do vigia), a spec do mutante M1 (só o texto da guarda) e o fragmento de changelog. Nenhum código de produção nem fixture mudou. O remoto avançou só com os pareceres de review e segurança (23fbc5ad); trazido por fast-forward, sem mudar o domínio do QA.

- **S1, 10 rodadas seguidas sob carga** (`python3 -I -m unittest discover -s tests -p test_hooks.py -k test_liberar_ou_provar_a_carga_recusa_a_sonda_s1`, com 3 cópias de `test_hooks_volta_corpus` em paralelo; carga da máquina 15 a 27 em 12 núcleos): 10 de 10 `OK`, de 9,4 s a 10,0 s (antes: 10,7 s sem a injeção).
- **M1:** `bin/forge-mutante tests/mutantes/v0478-develop-relogio.json` → `forge-mutante: pedido=v0478-develop-relogio rev=76cbce17155b spec=94298d3763d32e2dc2981ca3eb57a259cb8756ed1942d8a6477ed7d42dafc9ff` · `M1 · morreu · tests/prova_de_carga.py:70` · rc=0. Sem sobrevivente.
- **`test_hooks` inteiro no head:** `Ran 150 tests in 1141.992s · OK (skipped=11)` (os 11 pulados são de ns de pid e `/proc`, como na base). Nenhum estouro de prazo.
- **Fixture `pesado/mesma-sessao-libera`, head contra base b23124f8 (extraída por `git archive`):** isolada pelo `executar_em_lote`, 6 execuções em cada árvore, todas ok, de 0,20 s a 0,71 s (a maior, 0,71 s, foi na base). Dentro do lote, `-k Hooks.test_fixtures` (27 testes): head `OK (skipped=4)` em 589 s; base `OK (skipped=4)` em 609 s. Não consegui reproduzir o estouro visto pelo autor em nenhuma das duas árvores. O diff não toca fixture, hook nem o `executar_em_lote`; a única evidência é que a base roda no mesmo patamar de tempo e a fixture pesa menos de 1 s isolada. Conclusão: sem evidência de que o estouro venha do diff; é compatível com carga da máquina (o lote de 460 fixtures é paralelo), mas isso não foi provado aqui. Não bloqueia.
- Suíte inteira: segue no CI do PR (`bateria` do mesmo sha).

Parecer mantido: aprovado, sem achado.
