---
tipo: revisao-seguranca
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-custo
commit: 5a397c61c3be84a131d0ec14e824bcc4575263ab
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0475-ci-custo (revalidação por delta)

Escopo: delta `ae44f02b..5a397c61` lido por `forge-check parecer delta` (pedido v0474, E3.227). O delta é o merge da `develop` (`791d94e8`) com conflito de texto em `skills/ci-cd/SKILL.md`, seção "Tempo e dependências". Já lido: o resto da branch, no parecer do `ae44f02b` (fica no git).

## Gatilhos
Gatilhos: CI/CD (workflow-modelo copiado para todo projeto novo).

## Achados
- A4 (recomendado) tests/test_forge.py:791 · O lookbehind `(?<!\$)` deixa passar marcador escrito após `$` (`${{SOBRA}}`); nenhum modelo tem hoje marcador assim. Fechar com `\$\{\{[A-Z_]+\}\}` como segundo padrão, se quiser.

## Detalhe
Resolução do conflito (`git show --remerge-diff 5a397c61`): `skills/ci-cd/SKILL.md:56-57` mantém as duas linhas, o apontador da branch para `ci-de-projeto-privado.md` e a regra da `develop` (`forge-cota-ci`, rc 1 acima de 80%, sem pedir escopo quando falta permissão); nada do checklist de workflow (itens 1 a 10) nem do texto movido foi perdido. A regra nova reforça `R-CUSTO` e o menor privilégio do token. `bin/forge-testes` e `tests/test_forge.py` no delta só trazem o lado da `develop`; em relação à `develop`, a branch segue com as mesmas mudanças (`test_modelo_ci` em `LEITORES_DE_TEXTO` e na regra de `forge-(init|novo-projeto)`). A1-A3 seguem resolvidos; A4 segue aberto como recomendação (código inalterado, sem caminho de ataque).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Rodados: `python3 -I tests/catraca.py --base origin/develop` (rc 0); `python3 -m unittest tests.test_modelo_ci tests.test_metricas_texto tests.test_ambiente_git tests.test_testes_tocados` (203 testes, OK, 1 skip). CI do PR #651: a bateria completa fica com ele; na leitura, a bateria de pareceres vermelha por falta deste parecer no head e a de passos em andamento. Ferramentas ausentes no PATH (lacuna, nada instalado): `zizmor`, `actionlint`, `gitleaks`.
