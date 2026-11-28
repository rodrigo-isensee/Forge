---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-agentes-caiu-em-finito
commit: c838a467219922cc11c89680dc0aed730bebc0ef
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E53.2 e revalidação E53.6 (AGENTES-CAIU-EM-FINITO)

Diff revisado: `5ccac0bf..81408618` (6 arquivos, +129 -14; código em `hooks/agentes.py`, +19 linhas, dentro do teto H1).

## Achados
- A1 (recomendado) hooks/agentes.py:564 · a docstring de `lapides_vigentes` não diz que o `desde` não finito lança `EstadoIlegivel`; a de `autores_vigentes` (677) já diz. Alinhar no próximo toque.
- A2 (recomendado) tests/mutantes/v0479-agentes-caiu-em-finito.json:1 · M5 e M6 (e o M19 editado de trava-agente-morto-3) morrem por erro (TypeError no item "x"), não por asserção; um teste que afirme o item fora da forma ignorado sem erro fecha o ramo.

## Parecer
Aprovado. Faz o que a E53 pede: `lapides_vigentes` e `autores_vigentes` passam o `desde` por `caiu_em_finito` antes da subtração e lançam `EstadoIlegivel`, que `principal` (hooks/agentes.py:1309) converte em recusa do disparo sem regravar o estado, igual ao `interrompidos_vigentes` da BP3-S3. Reuso do auxiliar existente, sem mecanismo novo. A lista `agentes` não precisa da mesma guarda: `vigentes` já mantém o registro quando `dentro_do_prazo` levanta (falha para o lado seguro); conferido com `dentro_do_prazo({"desde": 10**400})` → OverflowError, capturado em `vigentes`.

Testes: borda com `10**400`, `-(10**400)`, `inf`, `-inf`, `nan` nas duas funções, prazo finito e disparo pelo hook recusado com o arquivo intacto. Rodados aqui: `tests.test_agentes_interrompidos` (29 testes, OK); `bin/forge-mutante` da spec nova M1-M6 todos mortos; `--cobertura --base 5ccac0bf` com as 6 linhas de guarda cobertas; specs editadas: M19 de trava-agente-morto-3 e M1-M8 de v047-h2-autor-fica mortos. Suíte inteira: fica no CI do PR (sem PR nesta etapa; o PQ do autor na E53.1, conferido pelo Jarvis em 14:10).

Regras: `R-REVIEW` (dois achados só recomendados, viram cartão depois do merge), `R-NEUTRO` sem termo de projeto, fragmento `changelog.d/` presente.

## Revalidação E53.6 (head c838a467)
Delta lido: `forge-check parecer delta` em `81408618..c838a467`; no domínio só `tests/test_agentes_interrompidos.py` (+4 -1, commit E53.5 do QA). O `principal` do teste de disparo passa a ficar num `try` que converte `OverflowError` em `self.fail`, para o defeito da base falhar por asserção e não por erro. Rodado aqui: o teste no head passa (módulo inteiro, 29 testes OK); com `hooks/agentes.py` da base `5ccac0bf`, as duas subtests falham com `AssertionError: OverflowError escapou de principal`. Sem código de produção no delta; A1 e A2 seguem recomendados. Aprovado no head c838a467.
