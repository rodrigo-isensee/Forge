---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: ecfc40c355010520c48d15ded98990fe3b66464b
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.257, item E3.253, `forge-copia --instalar` com ambiente sem credencial por padrão de nome)

## Achados
- A9 (bloqueante) bin/forge-copia:50 · com o padrão `TOKEN`, os quatro `*_TOKEN` de `fora` viraram código morto: M2 e M3 da spec `v0476-stack-deps-2.json` sobrevivem (S1). Tirar os quatro da lista e M2/M3 da spec 2 (o M2 da spec 3 cobre).
- A5 (recomendado) bin/forge-copia:48 · código e teste somam agora 211 linhas (54+4 em `bin/forge-copia`, 153 no teste), acima da orientação de 150 (M14). O corpo do PR leva `teto: excedido, 211 linhas, <motivo>`.
- A10 (recomendado) bin/forge-copia:51 · o padrão por substring também tira `NPM_TOKEN` e afins, de que o `pnpm install` precisa com registro privado; dizer no `pronto.md` da stack node que a instalação roda sem essas variáveis.

## Sondas
- S1 · `bin/forge-mutante tests/mutantes/v0476-stack-deps-2.json` no ecfc40c3 · espera: M1 a M14 morrem · obtido: `M2 · sobreviveu · bin/forge-copia:50` e `M3 · sobreviveu · bin/forge-copia:50`; os demais morreram

## Revalidação
Delta lido por `forge-check parecer delta docs/reviews/v0476-stack-deps.md`, intervalo `95605e66..ecfc40c3`: `bin/forge-copia`, o fragmento do changelog, `tests/mutantes/v0476-stack-deps-2.json`, `tests/mutantes/v0476-stack-deps-3.json` e `tests/test_forge_copia.py`. Nada fora disso relido.

- **Achados anteriores:** A7 resolvido (`GIT_CONFIG_PARAMETERS` na lista, com teste de comportamento que roda `env` real). A8 resolvido (o teste repetido saiu). A5 segue, com o número novo.
- **Testes:** `python3 -m unittest tests.test_forge_copia tests.test_ambiente_git` deu 50 testes OK.
- **Ferramentas:** `python3 -I tests/catraca.py --base origin/develop` deu rc=0. `bin/forge-mutante tests/mutantes/v0476-stack-deps-3.json`: M1 a M5 morreram. Spec 2: S1.
- **Segurança:** o padrão por nome atende ao pedido da segurança; o veredito é dela (`R-SEGURANCA`).
- **Suíte:** a suíte inteira fica para o CI do PR.

## Parecer
Reprovado: A9, mutante declarado sobrevivente por guarda morta (`R-REVIEW`).
