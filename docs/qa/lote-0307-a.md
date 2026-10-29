---
tipo: qa
contrato: 1
pedido: lote-0307-a
branch: melhoria/lote-0307-a
commit: 683ddcf9db41143858ddb0b633041ff47bd3fa15
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-29
---
# QA: lote-0307-a

Revalidação sobre 683ddcf (merge da develop a55ec03, release 0.30.6): o código e os testes do lote não mudaram desde 05fd5c5; os arquivos novos vêm da develop. Lote: guarda do `index.lock` órfão no `bin/forge-fechar` (E1) e frase do bloco `## Achados` nos modelos de parecer (E2). Sem especificação de UX: as obrigações são E1 a E3 do pedido LOTE-0307-A. Sem interface, sem acessibilidade aplicável. Volta 1 (delta 38f3f71..05fd5c5): o A1 do QA anterior, os mutantes L2 e L3 e a worktree apagada.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| E1 lock presente para (código 1, caminho, idade, rm, não apaga) | test_lock_presente_na_worktree_da_branch_para_com_codigo_1_e_nao_apaga | lock em worktree vinculada; idade 7 min | passou; vermelho na base; L1 morreu |
| E1 lock ausente segue | test_lock_ausente_na_worktree_da_branch_segue | sem lock (regressão) | passou (passa na base, esperado) |
| E1 branch na raiz do repo (git-dir relativo), fechamento em outra árvore (A1 anterior) | test_lock_na_worktree_principal_com_o_fechamento_rodando_em_outra_arvore_para | git-dir `.git` relativo; cwd diferente | passou; vermelho na base; L2 morreu |
| E1 worktree da branch com a pasta apagada não para (regressão do review A1) | test_worktree_da_branch_com_a_pasta_apagada_nao_para_no_lock | registro órfão `prunable` | passou; L3 morreu (guarda de regressão do head, passa na base) |
| E2 quatro modelos (qa, review, security e raiz) com a frase nova | leitura do diff, cmp raiz/template | n/a | `docs/security/_modelo.md` igual ao do template; linha 27 agora admite `(recomendado)` |
| E3 mutantes e fragmento | forge-mutante, leitura | n/a | L1 a L3 morreram; fragmento presente |

## Cenários e resultado real
- `python3 -m unittest tests.test_fechar_base_andou` sobre 683ddcf: 24 testes, OK (suíte completa fica para o pre-push, corte 1 da decisão do dono).
- `bin/forge-mutante tests/mutantes/lote-0307-a.json` sobre 683ddcf, rc=0:
  - `L1 · morreu · bin/forge-fechar:598`
  - `L2 · morreu · bin/forge-fechar:597`
  - `L3 · morreu · bin/forge-fechar:595`
- Conferência da lista contra o diff (`a55ec03...683ddcf`): as três linhas de guarda mudadas (`-d` na 595, `case` na 597, `-e` na 598) têm um mutante cada.
- `bin/forge-mutante --cobertura --base a55ec03...`: `não coberto: bin/forge-fechar` (shell, por definição; conferência feita por leitura).
- Vermelho: verificado na rodada anterior (`prova (asserção)=2`: lock presente e git-dir relativo); os testes e o código do lote são idênticos no head.
- `scripts/validar-plugin.sh`: Validation passed.
- PA-7 conferido: sem teste redundante, sem skip, cada teste nomeia a obrigação e o mutante que o quebra.

## Parecer
Aprovado sobre 683ddcf, sem achados. Os achados do review e da segurança são dos outros portões.
