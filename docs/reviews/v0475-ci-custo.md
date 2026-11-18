---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: ae44f02bec60f2ab2f38aa677f9289bdd158ec0a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.190, melhoria/v0475-ci-custo), revalidação

## Achados
- A5 (recomendado) tests/test_modelo_ci.py:1 · tamanho (M14): 207 linhas contadas contra a base (`tests/test_modelo_ci.py` 198, `bin/forge-testes` 4, `tests/test_forge.py` 3, `tests/test_reval_delta.py` 2), um comportamento; o corpo do PR traz `teto: excedido, 207 linhas, <motivo>`.

## Parecer
Aprovado (`R-REVIEW`). Delta lido: `forge-check parecer delta docs/reviews/v0475-ci-custo.md`, intervalo 7c7f6c42..ae44f02b, domínio código e testes (`skills/ci-cd/SKILL.md`, `skills/ci-cd/ci-de-projeto-privado.md`, `tests/mutantes/v0475-ci-custo-2.json`, `tests/test_modelo_ci.py`).

- **Texto movido:** a seção "CI de projeto privado: minutos" sai da `SKILL.md` e vai, igual, para `skills/ci-cd/ci-de-projeto-privado.md` (diff entre a seção antiga e o arquivo novo: só a linha em branco final e o nível do título). A `SKILL.md` aponta para o arquivo em "Tempo e dependências"; os outros ajustes da `SKILL.md` são encurtamento de redação, sem mudar regra.
- **Teste:** `test_skill_aponta_para_o_modelo_e_explica_o_porque` afirma o ponteiro na `SKILL.md` e lê o conteúdo no arquivo novo; não passa no vazio se o arquivo sumir (o `read_text` falha).
- **Mutantes M17, M18 e M22:** apontam ao arquivo novo e morrem no head.

Ferramentas e provas, rodadas só no diff, no ae44f02b:
- `python3 -m unittest tests.test_metricas_texto tests.test_orcamento_instrucao tests.test_modelo_ci`: `Ran 29 tests ... OK`.
- `python3 -I tests/catraca.py --base origin/develop`: rc=0.
- `bin/forge-mutante --processos 1 tests/mutantes/v0475-ci-custo-2.json`: `M17 · morreu`, `M18 · morreu`, `M22 · morreu`, rc=0.
- CI: a suíte completa fica no CI do PR #651, obrigatório para o merge.
