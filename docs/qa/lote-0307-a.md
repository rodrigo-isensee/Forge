---
tipo: qa
contrato: 1
pedido: lote-0307-a
branch: melhoria/lote-0307-a
commit: 38f3f7194f36fd0e9b0dd1e0e01bf4c7280e4c19
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-28
---
# QA: lote-0307-a

Lote: guarda do `index.lock` órfão no `bin/forge-fechar` (E1) e frase do bloco `## Achados` nos modelos de parecer (E2). Sem especificação de UX: as obrigações são E1 a E3 do pedido LOTE-0307-A. Sem interface, sem acessibilidade aplicável.

## Achados
- A1 (bloqueante) bin/forge-fechar:597 · mutante sobrevive: sem a linha que completa o git-dir relativo (branch na raiz do repo, caso comum do fechamento) nenhum teste cai; a guarda mudada precisa de mutante declarado e teste (R-QA)

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 lock presente para (código 1, caminho, idade, rm, não apaga, nada aberto) | test_lock_presente_na_worktree_da_branch_para_com_codigo_1_e_nao_apaga | lock existente em worktree vinculada; idade 7 min | passou; vermelho na base |
| E1 lock ausente segue | test_lock_ausente_na_worktree_da_branch_segue | sem lock (regressão) | passou (passa na base, esperado) |
| E1 branch na raiz do repo (git-dir relativo) | nenhum no lote; sonda do QA | git-dir `.git` relativo | sonda passou (código 1, caminho `.git/index.lock`); sem teste no lote: A1 |
| E1 --dry-run não é barrado | sonda do QA | dry-run com lock | passou (código 0) |
| E1 branch destacada/sem worktree: lock ignorado | sonda do QA | ref sem worktree | passou (código 0) |
| E1 caminho com espaço | sonda do QA | espaço no caminho da worktree | passou |
| E2 três modelos e docs/security/_modelo.md com a frase nova | leitura do diff | n/a | os quatro iguais, frase "traz só linhas (recomendado) ou o bloco vazio"; teste de igualdade raiz/template roda no pre-push |
| E3 mutante e fragmento | forge-mutante, leitura | n/a | L1 morreu; fragmento presente |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar_base_andou`: 22 testes, OK (suíte completa fica para o pre-push, corte 1 da decisão do dono).
- `bin/forge-mutante tests/mutantes/lote-0307-a.json`: `L1 · morreu · bin/forge-fechar:598`, rc=0.
- Mutantes do QA (spec em `$TMPDIR`, 4 mutantes sobre a guarda): Q2 (`-n arvore_lock`) morreu, Q3 (guarda passa a apagar o lock) morreu, Q4 (idade em minutos) morreu, **Q1 (linha `case` do caminho relativo) sobreviveu**.
- `bin/forge-mutante --cobertura --base 3b94791a...`: `não coberto: bin/forge-fechar` (shell; leitura do diff: uma guarda declarada de quatro linhas de condição).
- Vermelho: `forge-testes --vermelho 3b94791a... --modulos test_fechar_base_andou`: `contagem: não prova (passa na base)=21; prova (asserção)=1`, rc=0; o teste do lock presente falha na base e passa no head.
- Itens de PA-7 conferidos: sem teste redundante, sem skip, obrigação nomeada em cada teste.

Correção sugerida (tech-lead): teste do lock com a branch da worktree na raiz do repositório (`.git/index.lock`) e mutante da linha `case`, ou justificativa de equivalência aceita pelo QA. Ao voltar, o delta é só esse teste e esse mutante.
