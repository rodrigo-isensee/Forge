---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: ae44f02bec60f2ab2f38aa677f9289bdd158ec0a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0475-ci-custo (revalidação por delta)

Escopo: delta `7c7f6c42..ae44f02b` lido por `forge-check parecer delta` (pedido v0474, E3.191). No domínio: `skills/ci-cd/SKILL.md` (a seção "CI de projeto privado: minutos" sai para arquivo de apoio, mais retoques de redação) e `skills/ci-cd/ci-de-projeto-privado.md` (novo). Fora do domínio, lidos pelo foco do brief: `tests/test_modelo_ci.py:185-188` e `tests/mutantes/v0475-ci-custo-2.json` (M17, M18, M22). O modelo `templates/projeto/.github/workflows/ci.yml` não mudou no delta. Rodadas anteriores ficam no git.

## Gatilhos
Gatilhos: CI/CD (workflow-modelo copiado para todo projeto novo).

## Achados
- A4 (recomendado) tests/test_forge.py:791 · O lookbehind `(?<!\$)` deixa passar marcador escrito após `$` (`${{SOBRA}}`, S4 da rodada anterior); nenhum modelo tem hoje marcador assim. Fechar com `\$\{\{[A-Z_]+\}\}` como segundo padrão, se quiser.

## Detalhe
O texto movido é idêntico ao da seção removida (comparado com `git show 7c7f6c42:skills/ci-cd/SKILL.md`; só mudam o nível do título e a linha em branco final): seguem `--no-renames` (A1-A3 da rodada inicial, resolvidos), o agregador `ci` e o grupo de `concurrency` por número de PR. `skills/ci-cd/SKILL.md:56` aponta o arquivo novo. Os retoques do checklist (itens 1 e 10, "Rápido e barato", PR de release, simulação de merge) mantêm o sentido de cada controle: `permissions:` mínimas, `actionlint`/`shellcheck` sem instalar, nada de aprovar check vermelho (`R-CONFORMIDADE`). Os mutantes M17, M18 e M22 passam a mutar o arquivo novo, e o teste exige que `SKILL.md` cite `ci-de-projeto-privado.md`: a guarda segue no texto que ensina. A4 segue aberto como recomendação (sem caminho de ataque; o código dele não mudou).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: `python3 -I tests/catraca.py --base origin/develop` (rc 0); `python3 -m unittest tests.test_modelo_ci tests.test_metricas_texto tests.test_ambiente_git` (41 testes, OK). Sem PR aberto, sem CI a citar: a suíte inteira fica com o CI do PR. Ferramentas ausentes no PATH (lacuna, nada instalado): `zizmor`, `actionlint`, `gitleaks`.
