---
tipo: qa
contrato: 1
pedido: v046
branch: melhoria/develop-verde-494
commit: 2e8eb8b5165d9b7fac3eab78fbf9c627cdaebf35
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-12
---
# QA: v046 · E18.5 develop verde (head 2e8eb8b5)

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Passo de pareceres lido só até o fim do próprio job | `ParecerReprovadoBarraSempre.test_workflow_declara_head_repo_e_base_repo_no_passo_de_pareceres` | corte no cabeçalho do job seguinte (`verificacoes:`); env e run continuam dentro do corte | passou; mutante (HEAD_REPO trocado no ci.yml) derruba |
| Lista de timeouts com o 20 do job de verificações (R-TETO) | `Workflows.test_ci_em_poucos_jobs_com_timeout_e_gate_sem_paths_ignore` | 13 valores, ordem exata | passou; mutante (primeiro 20 vira 21) derruba |
| Índice de fixtures em dia (2260; `pesado` 24; `mutacao-*`) | `test_indice_fixtures` (3 testes) | contagem total e conferir rc 0 | passou |

## Cenários e resultado real
- Head 2e8eb8b5, `python3 -m unittest tests.test_catraca tests.test_indice_fixtures` em clone de $TMPDIR: Ran 349 tests, OK.
- Simulação de merge: develop avançou (origin/develop 2282c242, a base 2b896503 é ancestral); merge --no-ff sem conflito (901aa129); mesma rodada: Ran 349 tests, OK.
- Vermelho: na develop 2282c242 sozinha, os testes tocados falham (5 falhas: passo de pareceres, lista de timeouts, 3 do índice); com a branch, verdes. Só testes e docs mudam; nenhum `bin/`, `hooks/`, `.githooks/` nem `tests/catraca.py`, então `forge-mutante` não se aplica; os 2 mutantes acima foram feitos à mão na cópia.
- Alcance das guardas: o corte (`\n\n  [a-z-]+:\n`) tira só o job seguinte (passo 1030 de 2313 caracteres); as afirmações de env/run seguem lendo o passo inteiro. Nenhuma asserção removida, só o 20 somado à lista.
- Suíte inteira: fica para o check-run `bateria` do PR no mesmo sha (não consultado aqui).

## Achados abertos
Nenhum.
