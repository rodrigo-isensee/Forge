---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-raiz-pedidos-dados
commit: ccd65b30e4075f293df74851fa5ab09919c105e2
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-15
---
# QA: v047 (E2.101), lote PL1 RAIZ-PEDIDOS-PERDE-DADOS

Escopo: `bf475209...ccd65b30`, um commit: `forge-check voltas` passa a ler quadro, briefs e pedidos do `--raiz-pedidos`; `forge-placar` ganha `--raiz-pedidos` (vale sobre `--raiz`). Máquina carregada (load 17): só os testes do item; a suíte inteira fica com o check-run `bateria` do CI do PR.

## Achados
- A1 (recomendado) bin/forge-placar:8 · a docstring "Fontes (na `--raiz`...)" não cita que o `--raiz-pedidos` vale sobre ela (AR-9); o mesmo A1 do review. Não bloqueia.

## Critério → teste → resultado
Sem especificação de UX; as obrigações são o requisito do item E2.73 do pedido (RAIZ-PEDIDOS-PERDE-DADOS).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| `voltas --raiz-pedidos` lê histórico e pedido da pasta de fora, com clone vazio | `tests.test_voltas.VoltasComRaizDePedidos.test_historico_e_pedido_vem_do_raiz_pedidos` | clone sem `docs/`; números exatos (minutos=66, reversoes=1) | passou |
| `forge-placar --raiz-pedidos` vale sobre `--raiz` | `tests.evals.test_placar.Medir.test_raiz_pedidos_fora_do_clone_vale_sobre_o_raiz` | clone vazio; (vereditos, delegações, negativos)=(4,3,1) | passou |
| Sem `--raiz-pedidos`, comportamento antigo | `tests.test_voltas.Voltas` e `tests.evals.test_placar.Medir` (restante da classe) | caminho padrão | passou (7 testes na rodada) |

## Cenários e resultado real
- Rodada local: `python3 -m unittest tests.test_voltas.VoltasComRaizDePedidos tests.evals.test_placar.Medir` -> Ran 7, OK.
- Vermelho antes do verde (manual; `forge-testes --vermelho bf475209` não terminou com a máquina carregada, sem veredito): cópia em `$TMPDIR` do head com `bin/forge-check` e `bin/forge-placar` da base; os dois testes novos caem:
  - `FAIL test_historico_e_pedido_vem_do_raiz_pedidos`: `1 != 0 : voltas: aviso: docs/kanban/historico.md ausente`
  - `FAIL test_raiz_pedidos_fora_do_clone_vale_sobre_o_raiz`: `2 != 0 : usage: forge-placar [-h] [--raiz RAIZ] ...` (opção inexistente)
  - `Ran 2 tests ... FAILED (failures=2)`.
- Mutação (`bin/forge-mutante tests/mutantes/v047-raiz-pedidos-dados.json`, rev ccd65b30): `RP-M1 · morreu · bin/forge-check:9691`; `RP-M2 · morreu · bin/forge-placar:499`.
- Cobertura (`forge-mutante --cobertura --base bf475209`): `coberta · bin/forge-check:9691 · RP-M1`; `coberta · bin/forge-placar:499 · RP-M2`. Uma condição de guarda mudada por arquivo, as duas com mutante (AR-1).
- PA-7: AR-1 ok (lista completa); AR-4 e AR-5 ok (testes em subprocesso, `-I`, `PATH`/`HOME` próprios, `cwd` no clone vazio); AR-9 vira A1 recomendado; os demais sem relação com o diff.
- Merge: trouxe `origin/melhoria/v047-raiz-pedidos-dados` (pareceres de review e segurança) por merge, sem rebase.

## Parecer
Aprovado. Nenhum bug aberto.
