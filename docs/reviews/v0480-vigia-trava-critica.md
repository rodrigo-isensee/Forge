---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-vigia-trava-critica
commit: cf8b8f696d2acb4431d62506b5f0667f25fad698
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E169.3, PR #853, VIGIA-PRAZO-TRAVA)

Diff revisado: `0f4a7791..cf8b8f69` (o merge da `develop` só traz commits já integrados; diff líquido de 9 arquivos, 24 linhas em `hooks/_comum.py`, dentro do teto H1).

## Achados
- A1 (recomendado) hooks/agentes.py:1421 · `agentes` e `pesado` também recusam e rodam sem `regra_do_prazo`: o timeout de 10 s do Claude Code ainda os libera. A decisão fala em "toda trava que pode recusar"; vale um cartão para decidir se o vigia se estende a eles.
- A2 (recomendado) hooks/_comum.py:2863 · Sem o marcador e sem corpo pendente, a recusa diz "a chamada com ação crítica", e a linha não tem ação crítica. Um texto neutro ("a chamada") evita confundir quem lê o stderr.

## Sondas

## Parecer
Aprovado. O vigia de prazo segue a DECISÃO DO DONO de 2026-11-24 07:43 (`docs/pedidos/v0478.md:986`): em `prazo_vencido`, sai a isenção `hook.marcado is False and not hook.corpos_pendentes`. A linha sem o marcador passa a recusar numa sessão vigiada, antes da ferramenta. Continuam liberando o hook sem `critico`, o `PostToolUse` e a sessão não vigiada. A mudança só aperta.

- **Fixture renomeada** (`errointerno-prazo-sem-escrita-libera` → `-bloqueia`): só mudam `descricao`, `codigo` (0 → 2) e o `stderr` esperado. `forcar` e `entrada` estão iguais, então nenhuma outra mudança vem junto. O nome antigo não aparece em mais nenhum lugar do repositório. `tests.test_hook_erro_libera` (glob `errointerno-prazo-*`, mínimo 7) segue verde, com 11 testes OK.
- **Fixture nova** `vigia-prazo-trava-gh-com-aspas-bloqueia.json`: é o caso `"g"h repo create --public` do parecer de segurança. Esperado: código 2.
- **ADRs 0003 e 0009 e `docs/hooks.md`:** o word-diff troca só o comportamento do prazo vencido ("segue o mesmo marcador"/"libera" → "recusa com ou sem o marcador", com o ID VIGIA-PRAZO-TRAVA). As ADRs só se alinham ao código e não mudam outro ponto.
- **Testes do item, rodados no head:** `test_vigia_prazo_trava_sem_marcador_recusa_e_fora_da_sessao_vigiada_libera`, `test_fixtures_do_vigia_prazo_trava` e `test_prazo_vencido_com_corpo_de_heredoc_pendente_recusa` passaram (3 OK).
- **Mutantes** (`bin/forge-mutante tests/mutantes/v0480-vigia-trava-critica.json`, rev cf8b8f696d2a): M1 a M5 morreram, um por guarda mudada. M2 a M4 morreram por erro (`SystemExit` não esperado), que é uma falha de comportamento do ramo.
- **CI do PR #853 no head:** suíte pendente. `bateria (pareceres)` e `catraca` estão vermelhos porque faltam os pareceres deste head. A suíte inteira fica com o CI (R-REVIEW) e não foi rodada de novo aqui.
- **Commits:** dois commits de autor, em Conventional Commits em português e com a etapa citada, e o merge da base. O fragmento `changelog.d` está presente.
