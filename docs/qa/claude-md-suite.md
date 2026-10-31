---
tipo: qa
contrato: 1
pedido: claude-md-suite
branch: melhoria/claude-md-suite
commit: d9c232fdba5a8b4afd6fa0288718db7c50a46d0a
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: claude-md-suite

## Achados

## Critério → teste → resultado
O pedido não numera CA-n; a obrigação única é o escopo E1 (linhas 16 e 34 do `.claude/CLAUDE.md` citam `.githooks/pre-push --suite`).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 linha 16 | CT-01: `sed -n 16p .claude/CLAUDE.md` contém `pre-push --suite` | n/a | passou |
| E1 linha 34 | CT-02: `sed -n 34p .claude/CLAUDE.md` contém `pre-push --suite` | n/a | passou |
| E1 sem resíduo | CT-03: `grep -n 'unittest discover' .claude/CLAUDE.md` sem saída | n/a | passou |
| E1 o comando citado é a suíte inteira | CT-04: `.githooks/pre-push --suite` e `python3 -m unittest discover -s tests` com a mesma contagem | contagem igual (2315) | passou |
| Fora do escopo | CT-05: `git diff --stat 8c07b44..d9c232f` só toca `.claude/CLAUDE.md`, o fragmento e o parecer de review | n/a | passou |

## Cenários e resultado real
- Diff lido (`8c07b44..d9c232f`): 2 linhas trocadas no `.claude/CLAUDE.md`, fragmento `changelog.d/claude-md-suite.md`, parecer de review. Nenhum código nem teste mudou; não há teste novo, então vermelho antes do verde e mutação não se aplicam (sem `bin/`, `hooks/`, `.githooks/`, `tests/catraca.py` no diff).
- CT-04, `.githooks/pre-push --suite`: "suite-paralela: 2315 testes em 79 módulos, 4 processos". Resultado: rc 1, `FAILED (failures=2, skipped=27, guarda=2)`, sob load médio de 9 a 13 na máquina compartilhada. Falharam `test_fechar_orfao.Teste.test_push_delete_que_trava_e_cortado_pelo_teto_e_a_remota_viva_e_dita` (2 != 3) e `test_atualizar.AtualizarComDevelopQueAvancou.test_parado_na_develop_atrasada_ela_avanca_e_a_branch_nasce_dela` (download da versão 9.9.0 recusado). Ambos fora do diff (diff só de texto).
- Cada um isolado: `python3 -m unittest <teste>` deu OK nos dois (13,4 s e 0,7 s).
- `python3 -m unittest discover -s tests` na mesma árvore: `Ran 2315 tests in 1768.355s`, `OK (skipped=27)`, rc 0. Contagem igual à do `--suite`: 2315.
- Linhas 16 e 34 do `.claude/CLAUDE.md` citam `.githooks/pre-push --suite`; nenhuma ocorrência de `unittest discover` restou no arquivo.
- M14 (agents/tech-lead.md:19): cumpre. `git diff --numstat --no-renames origin/develop...HEAD`: 2+2 em `.claude/CLAUDE.md`, 2 no fragmento, 23 no parecer; zero linhas de código ou teste contadas; um comportamento só.
- Acessibilidade e E2E: não se aplicam (texto de documentação). Sem gatilho de segurança.
- Risco residual: as duas falhas do `--suite` são sensíveis a carga (temporização e rede), sem relação com a mudança; reportadas, não reclassificadas.
