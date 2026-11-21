---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-por-branch
commit: f4689e1254bf579f5110b4f58c677fac1b9f05e3
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E79.2, ENTREGA-POR-BRANCH (K-345)

Escopo: `adc52def..f4689e12`, 1 commit, 5 arquivos; código só em `bin/forge-check` (8 linhas a mais, 2 a menos, dentro do H1). Comparado com o Entregar do E79.1 (as duas partes do K-345 que reproduzem).

## Ferramentas (saída citada, não refeita)
- Suíte do item (autor, `/root/.forge-contrib/wt/e791-saida/resumo.log`): 23 módulos `rc=0`, `falhas=0`. A suíte inteira fica no CI do PR.
- `bin/forge-mutante` (autor, `mutante.log`, spec `47c019ff…`): M1 a M4 `morreu` em `bin/forge-check:1044` e `:10081`; as duas linhas de guarda mudadas têm mutante declarado.
- Rodados aqui só os 2 testes novos (`test_k345_md_em_caminho_de_controle_da_classe_nao_isenta`, `test_k345_ponta_local_diferente_da_enviada_nao_grava`): `Ran 2 tests` / `OK`.

## Leitura
- `isencoes_do_diff` passa a usar `motivo_de_controle`, que já inclui o `MD_DE_CONTROLE`: o critério só fica mais estrito, nada antes exigido passa a ser isento. Catraca que não carrega não isenta (falha fechada, testada com `mock`).
- `cmd_entrega_conferir`: a recusa vale só com `gravar`; o `--sem-gravar` segue conferindo (M4 prova). O teste cobre recusa, o `--sem-gravar` e a gravação depois do envio.
- Commit em Conventional Commits, com fragmento em `changelog.d/` (R-CONTRIB); sem mudança em regra, invariante ou neutralidade (R-NEUTRO).

## Achados
- A1 (recomendado) bin/forge-check:1605 · a mensagem "isento de QA" (e a da linha 1619) ainda descreve o critério como só o MD_DE_CONTROLE; com o K-345 ele é o motivo_de_controle da classe. Atualizar o texto.
- A2 (recomendado) bin/forge-check:10081 · sem origin/<branch> (branch nunca enviada) a gravação segue com a ponta local, como em test_cumpriu_grava_uma_vez; e a ref lida é a de rastreio local, não o ls-remote. Decidir se "só a ponta enviada" cobre esse caso.

## Parecer
Aprovado no head f4689e12. As duas correções fazem o que o E79.1 pede, com teste do ramo de falha e mutante morto por guarda (R-REVIEW). A1 e A2 são recomendações e viram cartão depois do merge.
