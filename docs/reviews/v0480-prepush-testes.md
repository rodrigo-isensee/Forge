---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-prepush-testes
commit: 8ceaaa99f12e26036ade7be21c29c6750d521963
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E137.4, testes do envio local; review E137.19)

Base 0e59c446, head 8ceaaa99. Item só de teste: por decisão do dono, este review é o único parecer. PR #824 (rascunho).

## O que foi conferido
- Diff: `tests/test_pre_push_afetados.py` (+7 -3), `tests/test_pre_push_leve.py` (+15 -1) e o fragmento `changelog.d/v0480-prepush-testes.md` (nome da branch sem prefixo, `CHANGELOG.md` intocado). `.githooks/pre-push` intocado. Três commits em Conventional Commits; tamanho fora do teto H1 (só teste e texto).
- Testes dos arquivos tocados no head: `ChecagensBaratasAntesDaTrava` e `test_pre_push_leve`, 14 testes, OK (1 pulado: shellcheck fora do PATH). Suíte inteira só no CI do PR (`R-REVIEW`), não rerrodada aqui.
- Teste novo do processo morto (`tests/test_pre_push_leve.py:142`): não é vazio. Mutante no hook que, com a suíte falha, imprime a causa, sai 1 e ainda anota a prova: o teste reprova na asserção do `*.verde` (S2). Aprovado no mérito.
- Troca do `assertLess` de 15 s (`tests/test_pre_push_afetados.py:294-306`): ver A1. A guarda principal (`assertNotIn("pre-push: entrou")`) continua, e a espera pelo caminho real do hook sempre imprime "entrou" e "esperando a vez". As asserções novas do estado do flock pegam a espera silenciosa sem limite (o hook só voltaria depois do `sleep 60` do segurador, que então estaria morto). Mas a espera silenciosa com limite, menor que a vida do segurador, passa: o teste antigo a pegava a partir de 15 s, o novo não a pega abaixo de 60 s. É teste enfraquecido, provado pela S1, e pela ordem do dono não entra.

## Achados
- A1 (bloqueante) tests/test_pre_push_afetados.py:303 · troca do assertLess enfraquece o teste: espera silenciosa de 18 s na trava antes das baratas passa no novo e reprova no antigo (S1). Sugestão sem relógio e mais forte: `flock` falso no PATH que registra a chamada, e afirmar zero chamadas; manter as asserções de estado.

## Sondas
- S1 · mutante `flock -w 18 "$(trava_arquivo criar)" true || true` antes de `checagens_baratas`, test_sintaxe_python_reprova_antes_da_trava no head e na base · espera: os dois reprovam · obtido: head OK em 18,1 s; base FAILED "18.07 not less than 15"
- S2 · mutante que anota a prova com a suíte falha e sai 1, test_suite_inteira_com_processo_morto_nao_anota_prova_nem_carimbo · espera: reprova · obtido: FAILED, `forge-suite-0.verde` presente

## Parecer
Reprovado por A1. O teste do processo morto está correto e pode seguir como está. Na troca do teto de tempo, o comentário em `tests/test_pre_push_afetados.py:301` diz que o estado da trava prova a ausência de espera, e a S1 mostra que não prova: só pega a espera que dura mais que o segurador. Correção sugerida, determinística e mais forte que o teto antigo: pôr na frente do PATH do hook um `flock` falso que registra os argumentos num arquivo e chama o verdadeiro, e afirmar que o registro fica vazio quando a checagem barata reprova (antes de "entrou" o hook não chama `flock`: as chamadas das linhas 80, 96 e 120 ficam em funções do caminho da fila e do `--status`). Pega qualquer espera na trava pelo `flock`, curta ou longa, com ou sem mensagem. Na volta, a S1 tem de reprovar no head novo.
