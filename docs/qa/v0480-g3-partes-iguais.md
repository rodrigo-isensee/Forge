---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-g3-partes-iguais
commit: 0cb38c94f37af4125a6bb3f8b08d5613e0332f4c
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-22
---
# QA: v0478 (E102.7, reequilíbrio das partes do CI)

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

## Revalidação (segunda volta, head 790f114d)
- Delta (`forge-check parecer delta`): só tests/test_hooks.py e o fragmento de changelog.
- A1 resolvido: `corpus_da_fatia` é o corte único; sonda `[k::4][1:]` nela derruba `test_t1_as_fatias_cobrem_todo_o_corpus` (failures=1). Base: 2 OK.
- A2 resolvido: `test_fatias_travadas_aos_metodos`; constante FATIAS_DO_T1=5 e FATIAS_DE_FIXTURES=5 derrubam o teste (failures=1 cada). Base: 1 OK.
- test_pesos_teto OK. Sondas em cópia (`git archive`) em $TMPDIR; árvore intacta. Suíte inteira: check-run `bateria` do CI do PR.

## Revalidação (terceira volta, head 782d788e)
- Delta do parecer: intervalo 790f114d..782d788e sem o que veio da develop; só tests/pesos-d4.json, com a linha test_trilha_forge_check: 1.5 trazida no merge.
- test_pesos_teto (2 OK) e test_pesos_do_ci (16 OK), com TMPDIR e -I. Peso novo 1,5 s, abaixo de 225 s.
- Nada mais mudou no domínio do QA. Suíte inteira: check-run bateria do CI do PR.

## Revalidação (quarta volta, head 0cb38c94)
Merge da develop (#784). Único conflito: `tests/pesos-d4.json`, com a entrada `"test_fechar_checks_do_head": 5.2` vinda da develop. `forge-check parecer delta` lista só essa linha no domínio.
Provas:
- test_pesos_teto: Ran 2 tests, OK.
- test_pesos_do_ci: Ran 16 tests, OK.
- Suíte inteira: check-run `bateria` do CI do PR, mesmo sha.
Parecer: aprovado; sem achados.
