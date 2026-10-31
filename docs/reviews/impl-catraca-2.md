---
tipo: review
contrato: 1
pedido: impl-catraca-2
branch: melhoria/impl-catraca-2-c3
commit: 2d9ff06fbf557056b95ed98bc16957ae19497ee0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: impl-catraca-2 (branch c3)

## Achados

## Parecer
Aprovado. A branch entrega o item E3 do pedido (CATRACA-ISENCAO-AMBIENTE, C3 do desenho com a correção do modelo de ameaças). Diff lido: `234dbe0..2d9ff06`, dois commits (`7ef13bc` teste, `2d9ff06` fragmento).

M14 (`agents/tech-lead.md:19`): 28 linhas contadas (`git diff --numstat --no-renames 234dbe0 2d9ff06`: `tests/test_ambiente_git.py` 26+2; o fragmento `changelog.d/` fica fora), abaixo de 150. Um comportamento só (o motivo da isenção da catraca e a guarda dele). Não toca `hooks/` nem `PROTEGIDOS` (`tests/catraca.py` não muda).

Conferido contra o pedido e o modelo de ameaças (`docs/security/ameacas/catraca-2.md`, 3.3):
- C3-1: o motivo novo (`tests/test_ambiente_git.py:29-34`) cita o `merge-tree --write-tree` pelo forge-check e o `fetch` com `maintenance.auto=false` e `gc.auto=0` na própria chamada, e não diz mais que só lê.
- C3-4 e T3-1: `test_motivo_da_excecao_cita_o_que_o_arquivo_escreve` (`:279`) fica vermelho com o texto antigo (o motivo antigo não cita `fetch` e diz que só lê).
- C3-2: `test_todo_fetch_da_catraca_leva_a_manutencao_desligada_na_propria_chamada` (`:291`) lê pela árvore de sintaxe, por chamada, e exige as duas chaves na mesma chamada do `fetch` (`tests/catraca.py:912`), com piso de um `fetch` achado.
- C3-3 (lista positiva dos subcomandos do git da catraca) não entrou. O pedido (E3) pede o motivo e a guarda do fetch, e a branch cumpre os dois; a lista positiva fica como recomendação, que levo à revisão de segurança (E1.3) para ela decidir se pede. Não devolve.

Regras ferramenta: rodei `python3 -m unittest tests.test_ambiente_git` no head revisado: 17 testes, OK. A suíte completa fica com o CI do PR e o pre-push. Segurança: parecer próprio do `security-engineer` (E1.3), não refeito aqui.
