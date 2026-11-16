---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-tempo-a15
commit: 9050109479c1f4850cb5b92256b958f8d0eb08b5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (E2.358, melhoria/v047-tempo-a15)

Code review completo (`R-REVIEW`) por uma instância que não fez a entrega, sobre `1b88640e..90501094` (commits `f149180f` e `90501094`, E2.317): `bin/forge-check` (parser, repasse em `executar`, assinatura de `cmd_voltas`), `bin/forge_voltas.py` (`tempo_do_cartao`, `minutos_de_brief`, `razao_do_processo`, `linha_do_tempo`), `tests/test_voltas.py` (classe `VoltasTempo`), as duas specs em `tests/mutantes/` e o fragmento `changelog.d/v047-tempo-a15.md`. Não há parecer anterior: sem delta.

## Achados
- A1 (recomendado) tests/test_voltas.py:376 · O nome diz "parada fora", mas só a linha `- | -` sai dos movimentos: o intervalo parado (18:26:54 a 18:44:33, 17,7 min) entra nos 39,6 min de integracao. Se é o desejado, diga na docstring de tempo_do_cartao (bin/forge_voltas.py:104); senão, a parada fecha o trecho.
- A2 (recomendado) bin/forge_voltas.py:112 · O tempo em coluna fora de FASE_DA_COLUNA (ex.: "Aguardando sua validação" sem "Aguardando o dono" no motivo) some de todas as fases e do processo. Coerente com `esperas`, mas vale citar na ajuda do --tempo para quem lê a razão.

## Sondas

## Parecer
**Aprovado** no head `90501094`.

Escopo (A15 do `docs/propostas/tempo/consolidado.md`, E2.317): faz o pedido, nem mais nem menos. Minutos de autor, conferência, review, QA, integração, rodadas de brief e espera do dono, razão processo ÷ entrega com o dono fora, e `nao-medido` para fase sem trecho, trecho aberto, autor zero e brief sem `conferencias.md` ou com rodada sem hora. A fixture vem do histórico real anonimizado. Em `bin/forge-check`, só as três linhas liberadas.

Leitura: o código reaproveita `tipo_da_espera`, `_sem_acento` e `rodadas_de_brief` pelo `ctx_das_voltas`, sem mecanismo novo. Ordem estável no empate de hora (CARTAO-D) e fuso pela data com deslocamento. Sem `--tempo`, a saída não muda (teste e M10).

Achados recorrentes (PA-7) conferidos: AR-1 e AR-2, um mutante por condição mudada e o ramo de falha testado por comportamento; AR-4, o subprocesso roda com ambiente limpo e `python3 -I`; AR-12, as specs batem com o head (todos mortos abaixo). Nenhuma classe recorrente nova.

Ferramentas, citadas e não refeitas:
- `bin/forge-mutante --cobertura --base 1b88640e` no head `90501094`: 9 condições `coberta`, nenhuma `não coberto` nem `apagada`.
- `bin/forge-mutante tests/mutantes/v047-tempo-a15.json tests/mutantes/v047-tempo-a15-2.json`: M1 a M14 `morreu`.
- `python3 -m unittest tests.test_voltas` na raiz do clone: 46 testes, OK (1 pulado).
- Suíte inteira: só no CI do PR, que ainda não existe (brief sem PR); fica para o merge.

Tamanho (M14): 150 linhas contadas (`bin/` 67, `tests/test_voltas.py` 83), no teto; um comportamento só.

A1 e A2 não devolvem a entrega.
