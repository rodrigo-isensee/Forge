---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-h2-autor-fica
commit: 482ee7c773597cad435a49acbee8fb535b802493
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E2.59, H2-AUTOR-FICA-ATE-O-MERGE, parte de ferramenta), revalidação

Delta lido: `forge-check parecer delta docs/reviews/v047-h2-autor-fica.md`, intervalo 6d73898a..482ee7c7: `hooks/agentes.py`, `tests/test_hooks.py`, `tests/test_hooks_agentes_autor.py`, 8 fixtures `autor-*` novas, `tests/mutantes/v047-h2-autor-fica{,-2,-3}.json` (22 mutantes), índice de fixtures e changelog.

Achados da rodada 1: A1 resolvido (`guardar_autores` tira só as branches em comum, e o registro fica com as que sobram; `test_autor_de_duas_branches_perde_so_a_tomada`). A2 resolvido (teste com um registro de várias branches; mutantes da guarda nova declarados). A3 resolvido (`AUTORES_MAX`, com `test_teto_proprio_de_autores`).

## Achados
- A4 (bloqueante) tests/mutantes/trava-agente-morto-3.json:22 · ConferirTodas falha no head (verde na base): o `de` do M19 aparece 2 vezes no hooks/agentes.py e o do A4 de v0440-decisoes-2.json:36 sumiu; alinhe as duas specs (R-REVIEW, S1)
- A5 (bloqueante) hooks/agentes.py:510 · a reserva da retomada nasce com id e vale expiracao_horas, não RESERVA_S; SendMessage negado ou falho prende a branch por horas na sessão (R-TETO, S2); reserva curta até o retomado dar sinal, com fixture

## Sondas
- S1 · `python3 -m unittest tests.test_forge_mutante.ConferirTodas` no 482ee7c7 e na base e2880b42 · espera: OK nos dois · obtido: head FAIL (trava-agente-morto-3 M19, v0440-decisoes-2 A4: `de` fora da fonte); base OK
- S2 · reserva `{id: a0123456789abcdef, tipo: SendMessage, desde: agora-400, escrita: [melhoria/a]}` e SendMessage a outro autor de melhoria/a · espera: código 0 · obtido: código 2 `R-TETO: melhoria/a ocupada por SendMessage`; com id null, 0

## Parecer
Reprovado por A4 e A5. A4 já estava no 6d73898a: o M19 ficou ambíguo com a cópia em `autores_vigentes` (linha 448), e o A4 saiu com a mudança do `avisar`. A rodada 1 não o pegou. A5 vem da `reservar_retomada` nova: a reserva da retomada não tem o prazo curto que a linha 70 dá à reserva sem início. O resto do delta atende à E2.47. `autores_retomaveis` só põe id de texto no conjunto. O aviso sai depois do `gravar_json`: `lancar` devolve o pendente e `atualizar_estado` avisa. Por isso, um erro no aviso não leva a reserva. `reservar_retomada` recusa com a branch do autor ocupada (Z10). Ela não faz nada com o alvo ativo, com quem não é autor ou com a entrada fora da forma. O harness confere o aviso por inteiro (só `systemMessage` no stdout e só linhas `R-*: aviso:` no stderr). Ele mede a linha sem a cauda `; registro em`, que `_comum.mensagem` deixa inteira.

Mutantes: 22 declarados, um por linha de guarda, nos três arquivos. A mutação ficou com o autor (V2), e não a rodei de novo.

Tamanho: 97 linhas de código em `hooks/` e 113 de teste. A decisão do dono H1 conta só o código, abaixo de 150.

Verificação (este revisor, no 482ee7c7):
- `python3 -m unittest tests.test_hooks_agentes_autor`: 10 testes, OK (os 20 fixtures `autor-*` verificados).
- `tests.test_forge_mutante.ConferirTodas`: FAIL (A4, S1).
- A suíte completa fica com o CI do PR (sem PR nesta etapa).
