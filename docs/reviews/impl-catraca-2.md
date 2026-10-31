---
tipo: review
contrato: 1
pedido: impl-catraca-2
branch: melhoria/impl-catraca-2-c2
commit: 886b70ab3fed3a4463a05de914e89776efa16ebd
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Review: impl-catraca-2 (branch c2)

## Achados

## Parecer
Aprovado. A branch entrega o item E2 do pedido (S16-TESTE-CHAVES, C2 do desenho com as correções do modelo de ameaças). Diff lido: `234dbe0..886b70a`, dois commits (`87e7fc6` teste, `886b70a` fragmento).

M14 (`agents/tech-lead.md:19`): 70 linhas contadas (`git diff --numstat --no-renames 234dbe0 886b70a`: `tests/test_catraca.py` 69+1; o fragmento `changelog.d/` fica fora), abaixo de 150. Um comportamento só (o rótulo de PR mesclado não cobre violação de chave do config). Não toca `hooks/` nem `PROTEGIDOS`.

Conferido contra o modelo de ameaças (`docs/security/ameacas/catraca-2.md`, 3.2):
- C2-1: a tabela `CHAVES_DO_CONFIG` (`tests/test_catraca.py:1858-1876`) tem as 15 formas, cada uma com o texto da regra; o caso de `termos_proibidos_hash` ajusta a base com uma entrada, como o modelo exige.
- C2-2: `test_toda_forma_de_violacao_de_chave_tem_um_caso` (`:2076`) conta as chamadas a `msg(` em `regras_de_config` e `regra_termos_proibidos` pela árvore de sintaxe e exige igualdade com a tabela, mais um piso de 15 e nomes sem repetição.
- C2-3: `refaz_o_pr_10_com_config` (`:2042`) mantém no PR #10 a mudança em `tests/catraca.py` e no workflow, e o `pede()` confere rc 1 e "mudança em".
- C2-4: rodei a mutação "filtrar o `None` de `arquivos`" no lugar da guarda (`tests/catraca.py:1017-1018`), numa cópia em `$TMPDIR`: 14 das 15 formas caem por rc 0 com "liberada(s) pelo rótulo", não por traceback. A que segue verde é `custo_permitido novo` (`:1875`), porque a violação de custo nunca chega ao caminho do PR mesclado (o `custo` vem antes); o subteste continua útil como guarda desse outro controle. Não é defeito.
- C2-5: a docstring do teste antigo passa a dizer só o que ele cobre, sem perder asserção.
- C2-6 (recomendado no modelo, não exigido pelo pedido): não há caso de chave na classe do squash. Fica como recomendação para uma próxima mexida; não devolve.

Regras ferramenta: rodei `python3 -m unittest tests.test_catraca.RotuloDePrMesclado tests.test_ambiente_git` no head revisado: 40 testes, OK. A suíte completa fica com o CI do PR e o pre-push. Segurança: parecer próprio do `security-engineer` (E1.3), não refeito aqui.
