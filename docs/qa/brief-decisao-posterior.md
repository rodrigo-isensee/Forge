---
tipo: qa
contrato: 1
pedido: versao-035
branch: melhoria/brief-decisao-posterior
commit: 90a57d43ad227effc0c2f5938743f0ca4f4cedeb
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: BRIEF-DECISAO-POSTERIOR (E5 da versao-035)

Escopo: `d9b26bb...90a57d4` (`bin/forge-check`, `bin/forge-testes`, `tests/test_decisao_aprovacao_raiz.py`, `tests/test_testes_tocados.py`, fragmento de changelog). Depois de 90a57d4 a branch traz só os pareceres de review (7f5a1dc) e segurança (bf8bae6), sem código. Sem UX nem API: o contrato é o do E5 (desenho da versao-035 e modelo de ameaças, C-1 a C-9; o C-10 é do PR) e a decisão do dono de 15:20.

suite: reusa
A suíte inteira não foi rodada de novo (R-QA, decisão do dono de 14:59): vale como minha a execução do pre-push sobre a árvore 90a57d4, `/tmp/push-e5.log.2`: `Ran 2618 tests in 1761.259s (2 processos)`, `OK (skipped=30)`, `push_rc=0`. Os commits depois dele são só pareceres.

## Achados
- A1 (recomendado) tests/test_decisao_aprovacao_raiz.py:70 · mutante Q5 sobreviveu (raiz do brief lida mesmo fora de docs/briefs) e faltam os abusos 6, 11 e 12 do modelo de ameaças; guarda correta no código, sem teste. Sugestão: três subcasos em arquivo de teste próprio (o atual está no teto de 85 linhas)
- A2 (recomendado) tests/mutantes:1 · sem spec de mutação do E5 gravada (a do pn4 não cobre coluna 2, ordem nem link); sugestão: gravar as sete linhas Q1 a Q7 usadas aqui como tests/mutantes/brief-decisao-posterior.json

## Critério → teste → resultado
| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Decisão posterior à aprovação não reprova o brief em voo (dono, 15:20), quadro só na raiz do brief com `--raiz` no clone | `test_quadro_so_na_raiz_do_brief_vale_com_raiz_no_clone` | quadro fora da `--raiz`; rc 0 com aviso | passou (vermelho na base) |
| C-2 aprovação vale só com o pedido na coluna 2 | `test_linha_aprovado_vale_so_com_o_pedido_na_coluna_2` | caixa diferente vale; `outro`, `exemplo-x`, `exemplo.md` não | passou (vermelho na base) |
| C-1, C-3 sem aprovação válida ou retrodatada, tudo segue cobrado (rc 1, sem aviso) | `test_no_clone_sem_aprovacao_ou_retrodatada_segue_cobrada` | `reprovado`; hora um minuto antes do brief | passou (passa na base: guarda de regressão da fronteira, sem vermelho) |
| C-4 primeiro quadro da ordem decide, sem somar o seguinte | `test_primeiro_quadro_decide_sem_somar_o_seguinte` | quadro do brief reprovado, o do clone aprovado | passou (vermelho na base) |
| C-5 quadro link (arquivo ou `docs/kanban`) não vale e não cai no seguinte | `test_quadro_que_e_link_nao_vale_e_nao_cai_no_seguinte` | link para quadro forjado com quadro bom no clone | passou (vermelho na base) |
| C-6, C-7, C-9 decisão sem hora, modo `entrega`, texto do aviso | `tests.test_decisao_aprovacao` (existente, não tocado) | sem hora; outro modo | passou |
| Contagem do mapa FORGE_CHECK (40 módulos) | `tests.test_testes_tocados` | mínimo de módulos | passou |
| Abusos 6 (`docs` como link), 11 (brief fora de docs/briefs), 12 (brief por link) | nenhum | n/a | lacuna: A1 |

## Cenários e resultado real
- Módulos tocados, `python3 -m unittest tests.test_decisao_aprovacao_raiz tests.test_decisao_aprovacao tests.test_testes_tocados`: `Ran 98 tests in 61.742s`, `OK`.
- Vermelho antes do verde, `bin/forge-testes --vermelho d9b26bb3e6b11e7d45c8b7ed81c7da7a8a325503 --modulos test_decisao_aprovacao_raiz`, rc 0:
  `vermelho: base=d9b26bb3e6b1 head=bf8bae6180f7 módulos=test_decisao_aprovacao_raiz (restrito por --modulos)`;
  `revertidos à base: bin/forge-check, bin/forge-testes, changelog.d/brief-decisao-posterior.md, docs/reviews/..., docs/security/...`;
  `contagem: não prova (passa na base)=1; prova (asserção)=4`. Conferido por conta própria com o `bin/forge-check` da base sobre a árvore 90a57d4: 7 falhas em 5 testes (as 4 acima, mais as subcasos `outro`, `exemplo-x`, `exemplo.md`, `conferencias.md` e `kanban`). A execução com o mapa inteiro (40 módulos) não terminou na janela (fila e carga); a restrita ao módulo novo basta, porque o teste novo é o único que prova a regra.
- Mutação (R-QA), `bin/forge-mutante` sobre a spec do QA (fora do repositório; ver A2), em `bin/forge-check`, rev bf8bae6:
  `Q1 · morreu · :5180` (coluna 2) · `Q2 · sobreviveu · :5174` · `Q3 · morreu · :5174` (ordem) · `Q4 · morreu · :5175` (link, `docs/kanban`) · `Q5 · sobreviveu · :5173` · `Q6 · sobreviveu · :5258` · `Q7 · morreu · :5182` (mtime).
  - Q2 (tirar a raiz do brief da busca): equivalente nos testes, não no código. O ambiente do teste põe o HOME no `~/.forge-contrib`, que está em RAIZES_DE_BRIEF e acha o mesmo quadro; a diferença só existe para brief em raiz fora das três, que é o alargamento já descrito no A1 da segurança (recomendado, sem ganho ao atacante).
  - Q6 (`pedido_id` ausente dá None): equivalente hoje, porque `avaliar_brief` é o único chamador com `brief` e sempre passa o id; os outros chamadores não passam `brief`. É defesa em profundidade, sem comportamento observável.
  - Q5 (guarda de docs/briefs): lacuna real de teste, sem defeito no código (a leitura do diff confere a guarda); ficou como A1 recomendado, junto dos abusos 6, 11 e 12 que a segurança me atribuiu. Não adicionei teste: o commit pedido para este parecer é o 90a57d4 e teste novo exigiria commit próprio antes do parecer.
- Linhas de guarda mudadas no diff e mutante: `:5173` Q5 e Q2, `:5174` Q3, `:5175` Q4, `:5180` Q1, `:5182` Q7 (inalterada, mantida como controle), `:5258` Q6. Todas têm mutante.

## Bugs
Nenhum aberto. Sem acessibilidade nem E2E (ferramenta de linha de comando).

## Resultado
Aprovado: o E5 afrouxa só o que o dono autorizou às 15:20 (brief já aprovado, linha do pedido certo, hora posterior ao `mtime`, primeiro quadro válido), falha fechada, e o teste novo falha na base em 4 de 5 casos. Sem bloqueio; A1 e A2 recomendados.
