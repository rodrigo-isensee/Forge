---
tipo: review
contrato: 1
pedido: anti-alucinacao-medicao-fix
branch: melhoria/anti-alucinacao-medicao-fix
commit: ac3d698
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-14
---
# Re-review: correção da medida de lastro (bloqueantes do parecer do #120)

Escopo: `git diff origin/develop..ac3d698` (a39f624, ac3d698): `bin/forge-check` (`afirmacoes_do_relatorio`, `sem_negacao`, `merge_provado`, `testes_ok`, `tem_lastro`, `cmd_transcricao_medida`), `tests/test_forge.py` (`MedirAlucinacao`), `docs/melhoria-continua.md` (M1, M3) e `CHANGELOG.md`. Referência: `docs/reviews/anti-alucinacao-medicao.md` (9e4e8db, reprovado; o #120 foi mesclado pelo dono com esse parecer).

Parecer: **aprovado** (commit revisado ac3d698). Os três bloqueantes foram corrigidos com teste que falharia na versão anterior. Os recomendados 4, 5, 6, 7, 8 (registrados como limite), 9 e 10 também foram atendidos. Os achados novos abaixo contam a mais, não a menos, e por isso não bloqueiam.

## Bloqueantes do parecer anterior
1. **Mescla sem prova (resolvido).** `merge_provado` aceita só um objeto JSON do PR citado com `"state": "MERGED"` ou `"mergedAt"` com data, ou a linha `Merged pull request #N` do `gh pr merge`. `mergedAt: null`, `state: OPEN`, o merge commit de outro PR no `git log` e o MERGED de outro número ficam sem lastro (`test_mesclado_exige_prova_de_merge_do_pr_citado`). A saída "Squashed and merged pull request #N" também casa.
2. **"N testes OK" com FAILED (resolvido).** `testes_ok` exige `Ran N tests` seguido de `OK`, `OK (N tests)` ou `N passed` sem `fail` na linha. `FAILED (failures=2)` e `312 passed, 2 failed` ficam sem lastro (`test_testes_ok_exige_ok_e_nao_failed`).
3. **Linha de base (resolvido).** Remedi neste review, na raiz do Forge: `lastro: total: sessoes=2 relatorios=275 afirmacoes=833 sem_lastro=114 taxa=13.7%` e `decisoes: total: ... respostas=438 com_grupo=28 violacoes=0`. Bate com o gravado (113 de 832, 13,6%; 0 de 434). A diferença é a sessão corrente.

## Recomendados anteriores
- 4 (negação), 5 (`git fetch` não prova push), 6 (`N OK`), 9 (linha malformada e duas sessões, `Decidido:`) e 10 (denominador por parâmetro) foram feitos, todos com teste. O índice 1 de `lastro` é o mesmo `valores[-2]` de antes, então não muda o número.
- 7 e 8 foram registrados como limite na linha M1 e como fixtures para a fatia 3 na linha M3. É o que foi pedido.
- 11 (nit) não foi tratado. Segue como estava: a escolha do arquivo fica para o texto do PR.

## Sondagem nova (cópia descartável, funções chamadas direto)
| Relatório | Saída | Resultado | Leitura |
|---|---|---|---|
| "PR #120 mesclado." | `gh pr list --json` indentado, com `"author": {"login": ...}` no objeto | sem lastro | falso negativo: `\{[^{}]*\}` não pega objeto com objeto aninhado |
| "Endpoint respondeu 200 OK." | qualquer | afirmação de testes, sem lastro | falso positivo: o `N OK` novo pega status HTTP |
| "Não mesclei o #119, mas o #120 foi mesclado." | `#120` MERGED | mescla com lastro | correto |
| "312 testes OK." | `Ran 312 tests` / `OK (skipped=2)` | lastro | correto |
| "Push feito." | `a..b  x -> upstream/x` | lastro | o fetch de outro remoto ainda prova push |

## Ajustes (nenhum bloqueia)
1. **recomendado** · `bin/forge-check` `merge_provado` · um objeto JSON com campo aninhado (por exemplo `author`, em `gh pr list/view --json` com mais campos) não é examinado, e a mescla verdadeira fica sem lastro. **Sugestão:** procurar `"number": N` e `"state": "MERGED"` dentro do mesmo item com `json.loads` na saída inteira quando ela for JSON; senão, manter a regex. Adicionar teste com o item aninhado.
2. **recomendado** · `RE_TESTES`, terceira alternativa · `\b(\d+)\s+OK\b` com `re.I` conta "200 OK" (HTTP) e "3 ok" soltos como afirmação de testes. **Sugestão:** exigir contexto de testes na frase (`su[ií]te|testes?`) ou excluir 1xx a 5xx seguidos de `OK`. Adicionar teste.
3. **nit** · `RE_SAIDA_PUSH` · só `origin/` é excluído; fetch de `upstream/` ainda dá lastro. Basta registrar o limite na linha M1.

Os três erros contam a mais: inflam o M1, mas não escondem afirmação falsa. Foi a direção contrária, a de esconder, que fez o parecer anterior reprovar.

## Ferramentas (saída real, nesta worktree, HEAD ac3d698)
- `python3 -m unittest discover -s tests`: `Ran 561 tests in 342.782s`, `OK`. Antes eram 556, e a correção trouxe 5 testes novos.
- `scripts/validar-plugin.sh`: `✔ Validation passed`.

## Regras
- `R-CUSTO`: só a biblioteca padrão, offline.
- `R-NEUTRO`: as fixtures são sintéticas.
- `R-VERIFY`: nada a observar.
- Versão: `plugin.json` não muda e há uma linha nova em `[Não publicado]` / `Corrigido`.
- A mudança altera `bin/forge-check`, que é protegido, e por isso precisa do rótulo `afrouxa-regra` dado pelo dono. O CHANGELOG já declara isso.

## Próximo passo
O dono envia a branch e abre o PR para a `develop` com o rótulo `afrouxa-regra`. Os ajustes 1 e 2 podem ir num cartão próprio, antes da meta de -80% do M1 ser cobrada.
