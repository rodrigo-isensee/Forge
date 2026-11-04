---
tipo: qa
contrato: 1
pedido: versao-033
branch: melhoria/teste-heredocs-orcamento-estavel
commit: 09e0f132b78bef588c7d6a6b0e931e057a6065fe
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-04
---
# QA: teste-heredocs-orcamento-estavel (revalidação em 09e0f13, sobre a97ea35)

## Achados
- A1 (recomendado) tests/test_hooks.py:572 · O lançador reimplementa o `__main__` do hook (`_comum.executar("conformidade", ...)`) em vez de rodar o arquivo; se o `__main__` de hooks/conformidade.py mudar, o teste diverge sem aviso. Aceito: hoje são idênticos (conformidade.py:~1000) e o modo `producao` roda o arquivo de verdade.

A1 do parecer anterior (bloqueante, e23-01) está resolvido.

## Injeção e produção
- Delta em a97ea35..09e0f13 fora de docs: só tests/test_hooks.py (+9/-1); nada em hooks/.
- A atribuição `PRAZO_DA_LINHA_S = PRAZO_DA_DECISAO_S` mora na string LANCADOR, que só roda via `lancador()` dos testes, e só quando o hook é `/conformidade.py` e `modo != "producao"`. `rodar` passa `producao or como_o_claude_code`, então os testes de prazo de produção e os de `como_o_claude_code` (apoio_volta_unica.py:136,432; test_hooks.py:1981) ficam com 3,0 s. `PRAZO_DA_LINHA_S = 3.0` segue em hooks/conformidade.py:41; o hook real nunca importa o lançador.

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Orçamento estável sob carga | test_muitos_heredocs_recusam_dentro_do_orcamento x3 (load 7 a 12, 12 núcleos) | razão 3 contra controle e teto de metade do prazo | 3 de 3 OK (47, 47, 60 s) |
| Mutante quadrático reprovado | e23-mutante.sh (cópia qa-e23) | quadrático | morreu pela razão de CPU, rc=0, 188 s |
| Vigia de produção intacto | test_hooks_volta_propriedades.py | prazo de produção | 9 OK, 183 s |

## Cenários e resultado real
- Estabilidade: 6 rodadas no total (load 7 a 12). Na primeira série de 3 o `tail` cortou a linha final, e só as linhas de CPU apareceram, sem falha; a segunda série, com `grep`, deu OK x3. Nenhuma falha (antes 2 de 5). CPU: ./x{i} 1,1 a 1,2 s; sh -s 1,5 a 1,65 s; python3 - 0,9 s; python3 - a{i} 1,74 a 1,79 s (controles 0,36 a 0,65 s; razão máx. ~3,0, teto 6).
- Mutante, saída: "5,57 s contra 0,83 s do controle 3,0 vezes menor", "7,22 vs 1,14", "5,66 vs 0,91", "8,09 vs 1,23"; "mutante morreu pela razão de CPU".
- test_hooks inteiro não rodado (17 min), como instruído; só o teste do pedido e o módulo de propriedades.
- Vermelho antes do verde: o teste já foi visto falhando (mutante e a97ea35, 2 de 5) no parecer anterior; este delta só toca o lançador.
