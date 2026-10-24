---
tipo: review
contrato: 1
pedido: lote-atualizar
branch: melhoria/lote-atualizar
commit: 1776e2dcdad82e4f9ae0e2bf69612993988875c5
parecer: aprovado
revisor: forge:tech-lead (instância de review, LOTE-ATUALIZAR-REV E1.1, rodada 3)
data: 2026-10-23
---
# Review: lote-atualizar (rodada 3, voltas 2 e 3)

Escopo: delta `6ecddee..1776e2d` (commits `a8ee390` e `1776e2d`), só `tests/test_atualizar.py` (`bin/` sem mudança). O parecer da rodada 2 (aprovado, com o A5 recomendado) é a base; o que não está no delta fica como "já lido".

## Achados
- A6 (recomendado) tests/test_atualizar.py:446 · o ramo "Não consegui desfazer" do handler de EOF/Ctrl-C (bin/forge-atualizar:118-120) segue sem teste: os novos conferem só que a mensagem NÃO sai quando o abort funciona. Num toque futuro, force a falha do abort (`index.lock`) com `na_pergunta=KeyboardInterrupt()` e confira a mensagem e a repassagem

## Parecer
**Aprovado.** O A5, no que pedia (ramo do `merge --abort` com a mesclagem aberta sem teste), está resolvido. Resta só o A6, recomendado, que não bloqueia.

### A5: resolvido
`integrar_com_erro_depois_do_commit(na_pergunta=...)` faz a falha vir na pergunta ao dono, com a mesclagem aberta e sem commit. Três testes novos (erro, Ctrl-C, EOF) conferem: `trazidos` não chamado, ausência de `MERGE_HEAD`, `HEAD == antes`, árvore limpa, mensagem ("Desfiz a mesclagem" no erro comum; silêncio em Ctrl-C/EOF, que repassam a exceção, verificada por `assertIsInstance`) e ausência de "Não consegui desfazer".

### Prova de que falham sem o ramo
Sonda em `$TMPDIR/tech-lead-loteatualizar3/` (cópia do head, `HOME` isolado): com o código do head, `AtualizarComDevelopQueAvancou` dá 20 OK. Trocando `git merge --abort` por `pass` em `desfazer_mesclagem`, falham 6: os 3 testes novos, mais `test_conflito_em_forge_versao_recusado_pelo_dono_desfaz_a_mesclagem` e `test_versao_da_develop_fora_do_formato_...` (os dois valores). Os testes provam o caso.

### Ferramentas
Sem regras de ferramenta para este diff; a bateria fica com o pre-push e o CI. Rodei só `tests.test_atualizar`.

### Fora deste parecer
Segurança (E2.1) e QA (E3.1) ficam com os seus papéis.
