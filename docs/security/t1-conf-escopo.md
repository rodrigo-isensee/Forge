---
tipo: revisao-seguranca
contrato: 1
pedido: t1-conf-escopo
branch: melhoria/t1-conf-escopo
commit: 5d1e769b0165f2e892f7d51b2569c5f8cb34b86b
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: t1-conf-escopo (volta 1 e merge da develop, T1-CONF-ESCOPO-REV)

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-check entrega` (conferência de escopo) e `agents/conferente.md`. Revalidação por delta do parecer anterior (`5737021`, sobre `b9426d8`): `forge-check delta --parecer` sobre `b9426d8..5d1e769`, com releitura integral das linhas tocadas em `bin/forge-check` e `agents/conferente.md`. PA-7 conferido item a item (AR-1 a AR-9): sem recorrência; a exclusão do A1 é a lista que o `conferente.md` já fixa como nunca anexo, não lista negativa de ambiente (AR-3), e o mapa de testes acompanha o módulo novo (AR-9, 29 para 30).

## Achados

## Detalhe dos achados
**A1 (era bloqueante): corrigido.** `bin/forge-check:1122`: o ramo da merge-integracao exclui `ACEITES_DO_USUARIO` (`docs/security/aceites/`, linha 718) e `tests/config.json`; os dois caem em `anexo_implicito`, que não os aceita (aceite tem `tipo` zerado, config não é parecer nem fragmento), e saem `escopo: confira`. Teste `test_aceite_e_config_nunca_sao_anexo_nem_com_pareceres_aprovados` cobre ref viva e mergeCommit; mutantes da condição em `tests/mutantes/t1-conf-escopo-2.json` (aceite e config separados). O texto de `agents/conferente.md:80` agora diz o mesmo que o código.

**A2 (era recomendado): corrigido** pela segunda opção proposta. `bin/forge-check:1013-1016`: com mais de um pedido nos reviews do mergeCommit (inclusive frontmatter ilegível, que entra como `None` no conjunto) o pedido fica vazio e a etapa reprova; teste `test_dois_pedidos_nos_reviews_do_squash_reprovam` e mutante M20. Resíduo sem caminho realista: um único review de outro pedido no squash ainda escolhe esse pedido; o squash só traz o que a própria branch mudou, o PR passou pela catraca do CI e o `--branch` é escolhido pelo Jarvis.

**A3 (era recomendado): corrigido.** `bin/forge-check:1037-1039`: o parecer trazido por merge só vira anexo com `tipo` da pasta, `parecer` aprovado ou reprovado e `branch: melhoria/<slug>`; teste com os três desvios e três mutantes. `agents/conferente.md:80` registra que o rótulo não atesta o parecer (quem atesta é o `forge-check pr`).

**Merge da develop f3f63f9 (T6T3-MENSAGEM), em 76a27ee:** sem conflito em `bin/forge-check` (`git show --cc` só resolve `agents/conferente.md`, `bin/forge-testes` e `tests/test_testes_tocados.py`, sem mudar lógica). O código novo (`mensagem_de_entrega`, `--entrega`, `--worktree`, etapa do brief) fica em `brief mensagem`, não em `cmd_entrega`: não abre caminho novo no `forge-check entrega`, e o `Desde:` gerado continua conferido pelo conferente contra o Histórico, cuja linha `conferida` só o Jarvis grava. O lote já tem parecer de segurança próprio aprovado na develop; o mesmo vale para `bin/forge-fechar` (LOTE-0307-A, d14a713). O commit 5d1e769 só remove uma linha em branco do `conferente.md`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, `forge-check delta --parecer` e `python3 -m unittest tests.test_conf_escopo` (10 testes, OK, local); `gitleaks`, `semgrep` e demais varreduras não rodadas (o delta não toca segredo, dependência nem workflow); sem lacuna de instalação registrada.
