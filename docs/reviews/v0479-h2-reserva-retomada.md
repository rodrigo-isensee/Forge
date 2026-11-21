---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-reserva-retomada
commit: 768c27efebe14607a881fd4f60b3395fc7444bf5
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

## Revalidação (E87.7, head 768c27ef)
Delta lido (`forge-check parecer delta`, `610ba4ce..768c27ef`): só `tests/mutantes/v0479-h2-reserva-retomada.json`, bloco `isentas` com as duas guardas apagadas que a catraca do PR #774 apontou.
- `a.get("id")` (base 982): a ternária saiu de `recusar_branch_ocupada` para `prazo_do_registro` (hooks/agentes.py:366), coberta por M23 e I55; a chamada nova (994) tem M2. Motivo verdadeiro.
- `a["id"] == alvo` (base 745): virou `a["id"] == aid` em `escrita_do_autor` (hooks/agentes.py:746), coberta por M22. Motivo verdadeiro.
- `bin/forge-mutante --cobertura --base origin/develop`: rc=0; 366, 371, 746 e 1302 cobertas; 982(base) e 745(base) isentas.
- `bin/forge-mutante --processos 1 --ids`: M22, M23, I55 e M2 mortos no head 768c27ef.
