---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-g3-partes-iguais
commit: 4c0b3842edfc6916e013bc5fcef7f749a094493f
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 1
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0478 (E102.7, reequilíbrio das partes do CI)

## Achados
- A1 (bloqueante) tests/test_hooks.py:2682 · o teste de cobertura do T1 refaz o corte `corpus[k::4]` por conta própria e não passa pelo código que roda (linha 2704): sonda que tira 1 linha de cada fatia em 2704 sobrevive (OK).
- A2 (recomendado) tests/test_hooks.py:190 · subir FATIAS_DE_FIXTURES ou FATIAS_DO_T1 para 5 sem criar o 5º teste passa nos testes de cobertura e deixa uma fatia sem rodar; falta travar a constante contra o número de métodos.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Mesmo conjunto de antes (fixtures) | test_fixtures_as_fatias_cobrem_todas; união = self.fixtures, sem repetição | fatia sem caso | passou; sonda `and i > 0` derrubou |
| Mesmo conjunto de antes (T1) | test_t1_as_fatias_cobrem_todo_o_corpus | fatia sem linha | passou, mas sonda em 2704 sobreviveu (A1) |
| Piso do T1 não afrouxa | `-(-500*N//4)` por fatia, soma >= piso antigo | piso | passou (leitura) |
| Sem skip novo | grep `skip\|expectedFailure` no diff de tests/ | n/a | nenhum |
| Unidade <= 225 s | test_pesos_teto (2 testes OK); maior peso 195,2 (test_hooks), 0 chaves acima | 225 s | passou |
| Pesos coerentes | test_pesos_do_ci (16 OK), PesosDaSuite (3 OK) | módulo sem peso | passou |

## Cenários e resultado real
- Módulos rodados (TMPDIR, `-I`): test_pesos_teto, test_pesos_do_ci, test_forge -k PesosDaSuite, test_hooks -k as_fatias_cobrem (2 OK).
- Sondas (cópia em $TMPDIR, HEAD intacto): M1 fixtures perde i=0: cai. M2 T1 perde 1 linha por fatia: sobrevive (A1). M3/M4 constante 5: sobrevive (A2). M5 constante 3: fatia 4 cai.
- Pesos: as chaves antigas `test_fixtures` e `t1_variantes` saíram e as 8 fatias entraram (soma 210,9 s e 156,8 s, contra 198,9 e 157,2 s da base, sem escala). As fatias de test_hooks não rodaram aqui (suíte no CI do PR).
- Vermelho antes do verde: não rodei `forge-testes --vermelho`; os testes novos são de cobertura e as sondas M1 e M5 os viram falhar.
