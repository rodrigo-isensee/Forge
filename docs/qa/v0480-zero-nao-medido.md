---
tipo: qa
contrato: 1
pedido: v0478
branch: melhoria/v0480-zero-nao-medido
commit: 099850609cd17b04189cdfd49281ae3b8da6d810
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-24
---
# QA: v0478 · E147.4 (PR #834, nao-medido no lugar de 0)

Obrigação testada: E147.1. Pedido sem cartão com movimento no quadro mostra `nao-medido`, não 0, em `forge-check voltas` e `metricas`. Pedido com cartão movido continua medido (0 é 0). O brief vem do registro e segue contado.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E147.1 voltas: sem cartão, voltas do quadro e minutos `nao-medido`, total `nao-medidos=N` | `test_voltas.RodadasDeBrief.test_pedido_so_em_docs_pedidos_existe_sem_historico` | pedido só no registro, Histórico vazio | passou |
| E147.1 o brief segue contado e a rodada extra mede minutos sem cartão | `test_rodada_extra_sem_cartao_conta_o_brief_e_nao_mede_o_quadro` | pedido sem cartão com rodada de brief | passou |
| E147.1 reversão do pedido segue na saída | `test_sem_cartao_com_movimento_a_reversao_do_pedido_segue_na_saida` | pedido sem cartão | passou |
| E147.1 cartão movido continua medido (0 continua 0) | `test_voltas` já existentes (linhas 147 e 175, intocadas) e mutante M1 | cartão com movimento e zero voltas | passou |
| E147.1 metricas: pedido e período sem item saem `nao-medido` no texto e `null` no JSON | `test_governanca.Metricas.test_pedido_sem_item_com_movimento_sai_nao_medido_e_nao_zero` | Histórico sem item | passou |

## Cenários e resultado real
Base para o vermelho: `9d239ddadcd1429fdafb29715ebe70566ceb5c11`. Testes dos arquivos tocados, local: `test_voltas` 48 testes OK (1 skip já existente, fora do diff); `test_governanca` 51 testes OK. A suíte inteira fica para o check-run `bateria` do CI do PR.

Vermelho antes do verde. O `bin/forge-testes --vermelho` estourou o prazo de 170 s no ambiente (sem veredito, não vale como vermelho). Fiz o recuo equivalente: cópia em `$TMPDIR` do head com `bin/forge_voltas.py` e `bin/forge_governanca.py` da base, sem tocar a árvore do autor. Resultado, os 4 testes novos caem:
- FAIL `test_voltas.RodadasDeBrief.test_pedido_so_em_docs_pedidos_existe_sem_historico`
- FAIL `test_voltas.RodadasDeBrief.test_rodada_extra_sem_cartao_conta_o_brief_e_nao_mede_o_quadro`
- FAIL `test_voltas.RodadasDeBrief.test_sem_cartao_com_movimento_a_reversao_do_pedido_segue_na_saida`
- FAIL `test_governanca.Metricas.test_pedido_sem_item_com_movimento_sai_nao_medido_e_nao_zero`

Mutação (`bin/forge-mutante tests/mutantes/v0480-zero-nao-medido.json`), 7 mutantes, um por linha de guarda do diff (conferido contra o diff: nenhuma condição mudada sem mutante). Saída:
```
forge-mutante: pedido=v0478 rev=2cfb734c5d8e spec=af1e34a9ce5e8e081886d0386a7c047a2185c7027a5f6c4ee5ec200e59acd929
M1 · morreu · bin/forge_voltas.py:185
M2 · morreu · bin/forge_voltas.py:186
M3 · morreu · bin/forge_voltas.py:197
M4 · morreu · bin/forge_voltas.py:207
M5 · morreu · bin/forge_voltas.py:211
M6 · morreu · bin/forge_voltas.py:213
M7 · morreu · bin/forge_governanca.py:627
```
Saída 0, nenhum sobrevivente.

Sem bug aberto, sem acessibilidade aplicável (CLI sem tela).

## Revalidação por delta (head 09985060)
`forge-check parecer delta` lista no domínio do QA só `tests/mutantes/v0457-f6-4-5.json` (M38 alinhado à linha nova do resumo de voltas, minutos com `nao-medido`); base origin/develop 998e2e4, sem o que veio da develop.
- `bin/forge-mutante tests/mutantes/v0457-f6-4-5.json --base 2cfb734c5d8e26e47cc794b4256c985a02aa7cd2`: `base=2cfb734c... rev=09985060...`; M33 a M40 `morreu`, inclusive `M38 · morreu · bin/forge_voltas.py:197`. Saída 0, nenhum sobrevivente.
- `python3 -I -m unittest discover -s tests -p test_forge_mutante.py -k ConferirTodas`: 4 testes OK (a catraca de specs segue verde com a spec alterada).
- O resto do domínio (código e testes do E147.1) não mudou desde o parecer anterior. A suíte inteira fica no check-run `bateria` do CI do PR; na consulta, `gh pr checks 834` mostrava `bateria (pareceres)` e `catraca` em fail e as partes da suíte pendentes (log ilegível no sandbox); não cito como prova.
