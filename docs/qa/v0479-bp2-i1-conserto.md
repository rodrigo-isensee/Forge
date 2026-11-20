---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp2-i1-conserto
commit: d816262d85319c97fed47261d3179f485df5bf08
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-20
---
# QA: v0479-bp2-i1-conserto (BP2 I1, `forge-fechar --conserto`, E38.7)

Escopo: diff `004ce869..d816262d` (`bin/forge-fechar`, `docs/fechamento-integrador.md`, `tests/test_fechar.py`, `tests/mutantes/fechar-conserto*.json`). Só os módulos tocados; sem suíte local (o CI do PR é o portão dela).

## Achados
- A1 (bloqueante) bin/forge-fechar:1089 · C4 falha aberto: o sed descarta a anotação de subteste com `)` no parâmetro (`test_b.Caso.test_um (entrada='f()'): ...`); com outro teste anotado, o perdido não é conferido nos pulados (S1). Nenhum mutante cobre a linha 1089.
- A2 (bloqueante) bin/forge-fechar:1109 · C4 falha aberto: teste pulado por `setUpClass` ou por módulo tem nos pulados outro id (`setUpClass (mod.C)`, `ModuleSkipped.mod`); o grep não acha e conta como passou (provado pela segurança, S2).

## Sondas
- S1 · anotações `tests/test_b.py<TAB>test_b.Caso.test_um (entrada='f()'): AssertionError` e `tests/test_c.py<TAB>test_c.K.test_dois: AssertionError` no sed da linha 1089 · espera: os dois ids · obtido: só `test_c.K.test_dois` (reproduzido por mim, igual ao A1 do review)
- S2 · pulados `setUpClass (test_m.C)` e `unittest.loader.ModuleSkipped.test_n` contra o grep da linha 1109, que só procura `"<id>"` e `"<id> ("` (sonda da segurança em `docs/security/v0479-bp2-i1-conserto.md`, lida, não reexecutada) · espera: pulado (para) · obtido: não achado (segue como passou)

## Critério → teste → resultado
Sem especificação de UX; as obrigações são C1 a C7 e D2/D5 (`docs/fechamento-integrador.md`, "Conserto da develop vermelha").

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| C1 (run do push vermelho do topo; topo relido antes do merge) | `test_fechar.Conserto` c1_* | run de outra branch, outro sha, sem falha, topo andou | passou |
| C3 (head é o revisado ou o merge dele com o topo) | `Conserto` c3_* | pai errado, árvore diferente, marca ausente | passou |
| C4 (testes que falharam passaram no PR) | `Conserto` c4_* | leitura falha, 10 anotações, pulado, SP4 | falhou nas bordas: A1, A2 |
| C5 (diff com relação ao vermelho) | `Conserto` c5_* | sem relação, revert, último verde ausente | passou |
| C6 (recusa --lote e --armar) | `Conserto` c6_* | combinações | passou |
| C7 (registro no log e no Histórico) | `Conserto` c7_* | falha de gravação vira pendência | passou |

## Cenários e resultado real
- `python3 -I -m unittest discover -s tests -p test_fechar.py -k Conserto`: `Ran 38 tests ... OK`, 78 s.
- `bin/forge-mutante` (6 specs, `--processos 2`), rev=d816262d8531: 44 mutantes (CS1 a CS44), todos `morreu`, rc=0. A lista não cobre a linha 1089 (sed do C4, a do A1): os mutantes pulam de 1088 a 1090.
- `bin/forge-mutante --cobertura --base 004ce869...`: `não coberto: bin/forge-fechar` (a cobertura só lê Python; a conferência da lista contra o diff foi à mão e achou só a linha 1089 sem mutante).
- Vermelho antes do verde: `forge-testes --vermelho 004ce869...` (67 módulos) estourou o prazo de 590 s do meu comando e saiu sem veredito (13 de 67 módulos; `test_fechar` H 160 s, B 91 s; `bin/forge-fechar`, changelog e doc voltaram à base). O rerun só de `test_fechar` foi barrado pela fila de tarefa pesada (R-TETO, outra sessão). Sem veredito: não vale como vermelho; cada mutante morto prova, por teste, que `Conserto` cai quando a guarda muda.
- CI do PR: não consultado (brief sem PR).

## Parecer
Reprovado pelo A1 e A2 (R-QA): C4 é o requisito que garante que o conserto só entra com a falha resolvida, e tem duas formas de falhar aberto. O A1 reproduzi; o A2 vem da segurança. Correção: capturar o id até o primeiro espaço ou `:` no sed; parar também com `setUpClass (mod.Classe)`, `tearDownClass`, `setUpModule`, `tearDownModule` e `ModuleSkipped.mod` nos pulados; um caso de teste e um mutante para cada. Na revalidação: `forge-check parecer delta docs/qa/v0479-bp2-i1-conserto.md`, `forge-mutante --base <head aprovado>` e o `forge-testes --vermelho` que ficou sem veredito aqui.
