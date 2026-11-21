---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-reserva-retomada
commit: 610ba4ce1568a305a58e9cebf7e4bb289695dd8a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 · E87.2 · H2-RESERVA-DA-RETOMADA-PRAZO

Escopo: `ad3b3b6f..610ba4ce` (1 commit, E87.1). Código: `hooks/agentes.py`, cerca de 30 linhas (teto H1 folgado); o resto é teste, fixture, spec de mutante e documentação.

## Achados
- A1 (recomendado) hooks/agentes.py:1303 · o retomado tardio grava as branches sem olhar se outra reserva de escrita as tomou no intervalo (o SubagentStart não recusa); fica dupla ocupação calada. Sugestão: linha no erros.log ou aviso quando `escritas_do_registro` de outro registro cruza `escrita`.

## Parecer
Aprovado (R-REVIEW).

- Requisito: `prazo_do_registro` é a fonte única do prazo; `dentro_do_prazo` e `recusar_branch_ocupada` passam a usá-la, o que corrige a hora anunciada da reserva `RETOMADA` (antes saía com expiracao_horas, com `id` presente). `iniciar` recebe `autores` e o id que está lá e não tem registro reserva de novo as branches; o caminho comum (casar a reserva sem id) segue igual e não é mais consumido pelo retomado, o que tira o roubo de vaga de um disparo do Task.
- `escrita_do_autor` extrai o conjunto que `reservar_retomada` já montava: sem duplicação, mesmo critério de id exato.
- Testes: 2 fixtures ponta a ponta (recusa da branch refeita; liberação no SubagentStop) e 3 unitários (prazo por tipo de registro, hora da recusa curta, início sem autor sem branch).
- Alinhamento das specs antigas (pedido do Jarvis): M22, M23 e I55 apontam o texto que mudou de lugar e cada um tem `de` único no arquivo. M22 agora cobre os dois usos de `escrita_do_autor` (retomada e início) e morre nos dois testes; M23 também morre nos dois; I55 saiu de dois testes caros indiretos para o unitário do prazo e morre nele. Nenhum enfraqueceu.

Comandos (rodados nesta cópia, TMPDIR de `mktemp -d`, ambiente limpo):
- `python3 -m unittest -v tests.test_hooks_agentes_autor`: 13 testes, OK.
- todas as 127 fixtures de `tests/hooks/agentes/` pelo `executar_em_lote` do módulo: OK (4 subcasos de pid pulados pelo próprio harness).
- mutantes M1 a M4 (`v0479-h2-reserva-retomada.json`), M22, M23 (`v047-h2-autor-fica-3.json`) e I55 (`v0432-integracao-4.json`), aplicados um a um com os testes declarados: 7 de 7 mortos.
- Suíte inteira: fica no CI do PR (R-CUSTO, M8), não rerrodada.
