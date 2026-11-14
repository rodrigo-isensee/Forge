---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-perguntas-abertas
commit: 2511f48b990a871fd4700a67ddd00942174edcba
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.145, perguntas abertas ao dono)

Intervalo `origin/develop..2511f48b` (base e60183d0): `cmd_abertas` e auxiliares em `bin/forge_dono.py` (+98), classe `PerguntasAbertas` em `tests/test_forge_dono.py` (+83), 15 mutantes em `tests/mutantes/v047-perguntas-abertas{,-2}.json`, fragmento em `changelog.d/`. Instância que não fez a entrega.

## Achados
- A1 (bloqueante) bin/forge_dono.py:519 · uma DECISÃO DO DONO qualquer fecha todas as perguntas anteriores do pedido; com duas abertas e uma respondida, a outra some e sai "Não há decisão sua pendente" (S1). Real: v047:298 (C12, pendente) some pela decisão de 13:48 sobre o teto (S2). Contraria a diretriz 29 e a docstring (517).
- A2 (recomendado) bin/forge_dono.py:555 · a leitura do KANBAN.md não captura OSError, ao contrário da dos pedidos (550): arquivo sem permissão de leitura derruba o comando com traceback; tratar igual, com aviso e fora da lista.
- A3 (recomendado) bin/forge_dono.py:473 · a diretriz 29 cita `PERGUNTA:` e itens "precisa de você"; o registro só lê `PERGUNTA AO DONO`. 387 pedidos têm a forma antiga `PERGUNTA:`, quase toda respondida na própria linha; registrar a escolha na docstring ou ler a forma antiga.

## Sondas
- S1 · pedido com PERGUNTA AO DONO 10:00 "1) pode A?", PERGUNTA AO DONO 10:05 "2) pode B?" e DECISÃO DO DONO 10:10 "pergunta 1 de 10:00"; cmd_abertas · espera: a pergunta de 10:05 na lista · obtido: (['Não há decisão sua pendente'], 0)
- S2 · perguntas_do_pedido('v047', texto de ~/.forge-contrib/docs/pedidos/v047.md) · espera: a pergunta de 2026-11-13 08:52 (C12, sem decisão que a cite) · obtido: []

## Verificação
- Regras de ferramenta: suíte inteira só no CI do PR (ainda sem PR); `R-REVIEW` cita o PQ do autor, sem rerrodar. Rodada aqui só a classe nova `PerguntasAbertas` (resultado no relatório da etapa).
- Rodada real sobre a raiz de pedidos (581 pedidos): 4 abertas, todas do painel do KANBAN.md; nenhuma vinda dos pedidos, o que confirma S2.
- Mutantes: 15 declarados (8 + 7), um por guarda; a conferência fica com o QA (E1.147).
- Tamanho (M14): 181 linhas de código e teste (98 + 83), acima da orientação de 150; um comportamento só, sem `hooks/`. O corpo do PR traz `teto: excedido, 181 linhas, <motivo>`.
- Registro no forge-check fora deste item, de propósito (E1.145); a docstring do módulo diz isso.

## Parecer
Reprovado por A1. `bin/forge_dono.py:519` · a regra "acima da última decisão" troca o lado seguro: o registro não liga decisão a pergunta, e o pedido tem perguntas pendentes simultâneas (v0457:259 a 268, v047:298). Sugestão: cada decisão fecha no máximo uma pergunta (a mais recente aberta antes dela, ou a que ela cita por `pergunta N de HH:MM`), com teste de duas abertas e uma resposta · bloqueia. A2 e A3 · recomendados, não devolvem. O resto (formas do registro, peso, corte da linha, links e arquivo ilegível nos pedidos) está correto e coberto.
