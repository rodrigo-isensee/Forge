---
tipo: qa
contrato: 1
pedido: impl-furo-hook-a
branch: melhoria/impl-furo-hook-a-a1
commit: b9aa6c8196ae4706c3ecda16bed09d5b7dcd5355
parecer: aprovado
revisor: forge:qa-engineer
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-10-31
---
# QA: impl-furo-hook-a, branch a1 (A1 TESTE-MATRIZ-CRITICO)

Diff lido: 234dbe0..b9aa6c8 (código e teste: `tests/test_hooks.py` +26/-1 e a spec `tests/mutantes/impl-furo-hook-a.json`; o resto é fragmento de changelog e pareceres). Item do pedido: E1/A1, a matriz de variantes crítica no teste dos hooks. M14 (`agents/tech-lead.md:19`): 27 linhas de teste, abaixo do teto; nenhum arquivo de `hooks/` tocado; um comportamento só (o teste T6 e o campo `stderr_sem` do executor de fixtures). Cumpre.

## Achados

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1: a ação sem marcador crítico, com cada variante que o bash ignora, é recusada pela leitura e não pela rede | `tests.test_hooks.Hooks.test_t6_a_leitura_ve_a_acao_sem_marcador_com_cada_variante` | ação sem marcador (piso de 2 ações), merge reprovado no parecer, toda variante da matriz; `stderr_sem` recusa o motivo da rede | passou (1 teste, OK, 10 s) |
| A1: o teste mede o hook real | spec `tests/mutantes/impl-furo-hook-a.json` | leitura do corpo da crase e da substituição na atribuição | A1-m1 e A1-m2 morreram (`bin/forge-mutante`) |

## Cenários e resultado real
- Vermelho antes do verde: o item é só teste e mede um hook que já recusa; não há implementação a retirar. A prova de que o teste falha é a mutação: com a leitura da crase (m1) ou da atribuição (m2) removida, o T6 cai. O `forge-testes --vermelho 234dbe0` sobre a suíte inteira estourou o prazo aqui (570 s em primeiro plano; em segundo plano o processo foi encerrado sem log), sem veredito, e por isso não vale como vermelho.
- Saída da mutação: `A1-m1 · morreu · hooks/conformidade.py:725`; `A1-m2 · morreu · hooks/conformidade.py:893`.
- Fronteiras: o piso de 2 ações sem marcador e a contenção dos mecanismos do comentário nas variantes impedem a matriz vazia.
- Sem interface de usuário: acessibilidade e E2E não se aplicam.
- Risco: o teste depende de `ACOES_DO_CORPUS` e `FAMILIAS_DE_RECUSA`; se o corpus encolher, o piso derruba o teste em vez de passar vazio.
