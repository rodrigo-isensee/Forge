---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-entrega-por-branch
commit: f39a94ed266957ef62be4bc1061c2581da54a7db
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E79.2 e E79.7, ENTREGA-POR-BRANCH (K-345)

Escopo: `adc52def..f4689e12`, 1 commit, 5 arquivos; código só em `bin/forge-check` (8 linhas a mais, 2 a menos, dentro do H1). Comparado com o Entregar do E79.1 (as duas partes do K-345 que reproduzem).

## Ferramentas (saída citada, não refeita)
- Suíte do item (autor, `/root/.forge-contrib/wt/e791-saida/resumo.log`): 23 módulos `rc=0`, `falhas=0`. A suíte inteira fica no CI do PR.
- `bin/forge-mutante` (autor, `mutante.log`, spec `47c019ff…`): M1 a M4 `morreu` em `bin/forge-check:1044` e `:10081`; as duas linhas de guarda mudadas têm mutante declarado.
- Rodados aqui só os 2 testes novos (`test_k345_md_em_caminho_de_controle_da_classe_nao_isenta`, `test_k345_ponta_local_diferente_da_enviada_nao_grava`): `Ran 2 tests` / `OK`.

## Leitura
- `isencoes_do_diff` passa a usar `motivo_de_controle`, que já inclui o `MD_DE_CONTROLE`: o critério só fica mais estrito, nada antes exigido passa a ser isento. Catraca que não carrega não isenta (falha fechada, testada com `mock`).
- `cmd_entrega_conferir`: a recusa vale só com `gravar`; o `--sem-gravar` segue conferindo (M4 prova). O teste cobre recusa, o `--sem-gravar` e a gravação depois do envio.
- Commit em Conventional Commits, com fragmento em `changelog.d/` (R-CONTRIB); sem mudança em regra, invariante ou neutralidade (R-NEUTRO).

## Revalidação E79.7 (delta f4689e12..f39a94ed)
Delta lido: `forge-check parecer delta docs/reviews/v0479-entrega-por-branch.md`, no domínio `bin/forge-check`, `changelog.d/v0479-entrega-por-branch.md`, `tests/mutantes/v0479-entrega-por-branch.json` e `tests/test_selo_e_entrega.py`; nada fora dele relido.
- A1 e A2 da segurança e o meu A2: a gravação lê a ponta por `remoto_da_branch` (ls-remote, nome exato); `not lido` (sem resposta) e `remoto is None` (branch ausente) recusam, falha fechada; a ref de rastreio local não decide mais (M6). `recusa_da_gravacao` só monta o motivo, um por ramo (M7, M8).
- Meu A1: as duas mensagens "isento de QA" (1605, 1619) citam os caminhos de controle da classe C. Fechado.
- Testes: 3 novos (branch nunca enviada, ref de rastreio apagada ou forjada, origin sem resposta), cada um no ramo de falha, com o `--sem-gravar` ainda conferindo; os que gravam passam a enviar antes (`enviar`, `entrega_gravando`). Rodados aqui os 4 testes K-345 da `Entrega`: `Ran 4 tests` / `OK`.
- `bin/forge-mutante` (autor, `/root/.forge-contrib/wt/e795-saida/mutante.log`, rev f39a94ed2669): M1 a M8 `morreu`, `rc=0`; um mutante por guarda mudada (10024, 10026, 10091, 10092).
- Módulo `tests.test_selo_e_entrega` rodado aqui: o log do autor no `e795-saida` é de 15:06, antes da correção, e está cortado; `Ran 176 tests` / `OK` (`/root/.forge-contrib/wt/e797-tl-selo.log`).

## Parecer
Aprovado no head f4689e12. As duas correções fazem o que o E79.1 pede, com teste do ramo de falha e mutante morto por guarda (R-REVIEW). Revalidado no head f39a94ed: A1 e A2 fechados no delta, sem achado novo.
