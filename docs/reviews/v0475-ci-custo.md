---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: 5a397c61c3be84a131d0ec14e824bcc4575263ab
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.226, melhoria/v0475-ci-custo), revalidação do merge da develop

## Achados
- A5 (recomendado) tests/test_modelo_ci.py:1 · tamanho (M14): 207 linhas contadas contra a base (`tests/test_modelo_ci.py` 198, `bin/forge-testes` 4, `tests/test_forge.py` 3, `tests/test_reval_delta.py` 2), um comportamento; o corpo do PR traz `teto: excedido, 207 linhas, <motivo>`.

## Parecer
Aprovado (`R-REVIEW`). Delta lido: `forge-check parecer delta docs/reviews/v0475-ci-custo.md`, intervalo ae44f02b..5a397c61 (merge da `develop` 791d94e8), domínio código e testes (`bin/forge-testes`, `skills/ci-cd/SKILL.md`, `tests/test_forge.py`).

- **Conflito resolvido:** `git show --remerge-diff 5a397c61` mostra conflito só em `skills/ci-cd/SKILL.md`, "Tempo e dependências". A resolução mantém as duas regras: o ponteiro `CI privado: ci-de-projeto-privado.md` (desta branch) e a linha da `develop` com `forge-cota-ci` (rc 1 acima de 80%); a linha antiga de medição, que a `develop` já substituiu, sai. Nenhuma regra perdida.
- **`bin/forge-testes` e `tests/test_forge.py`:** só o que veio da `develop`, entrado sem conflito; o lado desta branch nesses arquivos segue igual (`git diff 791d94e8 5a397c61 --stat`: 4 e 3 linhas, as mesmas do parecer anterior).

Ferramentas e provas, no 5a397c61:
- `python3 -m unittest tests.test_metricas_texto tests.test_modelo_ci tests.test_cota_ci`: `Ran 47 tests ... OK`.
- `python3 -I tests/catraca.py --base origin/develop`: rc=0.
- CI: a suíte completa fica no CI do PR #651, obrigatório para o merge.
