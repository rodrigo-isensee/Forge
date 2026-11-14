---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-perguntas-abertas
commit: 3da5f24a4bb8aacb7fbf314e12f48ff955b93aba
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.164, perguntas abertas ao dono, volta 1 por delta)

Revalidação por delta da volta 1 (E1.135) sobre o parecer da E1.145 (reprovado em 2511f48b por A1). Instância que não fez a entrega.

## Delta lido
`forge-check parecer delta docs/reviews/v047-perguntas-abertas.md` (rc=0), intervalo `2511f48b..3da5f24a`, no domínio: `bin/forge_dono.py`, `tests/test_forge_dono.py`, `tests/mutantes/v047-perguntas-abertas{,-3,-4}.json`.

## Achados
- A4 (recomendado) bin/forge_dono.py:488 · a CITACAO só reconhece `pergunta N de HH:MM`; `pergunta 1 de 3` (lote-unico-032:38-39) não cita, e as perguntas de lote-unico-032:49-50, já respondidas, seguem na lista. Lado seguro; ler `pergunta N de M` com data só ou registrar a escolha.

## Sondas

## Revalidação dos achados anteriores
- A1 (bloqueante) resolvido: `_respondida` (535) fecha no máximo uma pergunta, a citada por `pergunta N de HH:MM` ou, sem citação, a aberta mais recente se nenhuma outra fala do dono caiu entre as duas. S1 virou `test_cada_decisao_fecha_no_maximo_uma_pergunta` e S2 virou `test_decisao_sobre_outro_assunto_nao_fecha_a_pergunta`; rodada aqui sobre v047.md, S2 devolve a pergunta de 2026-11-13 08:52.
- A2 resolvido: OSError do KANBAN.md vira aviso (`test_quadro_ilegivel_vira_aviso`).
- A3 resolvido: a forma antiga `PERGUNTA:` é lida, com a resposta na própria linha (`nenhuma`, `resposta:`, `respondida`, `→`) fechando-a.
- A1 e A2 da segurança (pasta por link, regex quadrática): ficam com a segurança; os testes novos passam.

## Regra mais estreita que a sugestão do A1: aceita
A sugestão do parecer anterior era "a mais recente aberta antes dela"; o autor exige também que nenhuma outra fala do dono (`ORDEM`, `PEDIDO`, outra `DECISÃO`...) esteja entre a pergunta e a decisão (541). Aceito: o registro não liga decisão a pergunta, e a regra mais larga reabre o defeito da S2 (a decisão de 13:48 sobre o teto, com a ORDEM de 10:56 no meio, fecharia a C12). Medida na raiz real de pedidos, regra estreita contra a larga: 13 perguntas contra 8; das 5 a mais, v047 08:52 (S2) e v0457 14:11 (a decisão de 16:21 trata da 5a, outra pergunta) são acertos, lote-unico-032 (2) é falso positivo (A4) e v046 20:44 é incerta. O erro fica do lado seguro da diretriz 29: mostrar a mais, nunca esconder pendência.

## Verificação
- Regras de ferramenta: suíte inteira só no CI do PR (ainda sem PR); rodada aqui só a classe `PerguntasAbertas` (15 testes, OK).
- Mutantes PA-M16 a PA-M25 e os reescritos PA-M1 a PA-M4: um por guarda mudada; a execução fica com o QA.
- Tamanho (M14): o PR traz `teto: excedido, <n> linhas, <motivo>`, como no parecer anterior.

## Parecer
Aprovado no head 3da5f24a. A1 resolvido com regra mais estreita, aceita pelo motivo acima; A2 e A3 resolvidos. A4 · recomendado, não devolve.
