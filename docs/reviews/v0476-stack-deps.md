---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: f10912559b0561216f157059b9828099c5ee463e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.268, item E3.264, `forge-copia --instalar` com ambiente sem credencial por padrão de nome)

## Achados
- A5 (recomendado) bin/forge-copia:48 · código e teste somam 211 linhas (54+4 em `bin/forge-copia`, 153 no teste), acima da orientação de 150 (M14). O corpo do PR leva `teto: excedido, 211 linhas, <motivo>`.

## Revalidação
Delta lido por `forge-check parecer delta docs/reviews/v0476-stack-deps.md`, intervalo `ecfc40c3..f1091255`: `bin/forge-copia`, `stacks/node-react/pronto.md` e `tests/mutantes/v0476-stack-deps-2.json`. Nada fora disso relido.

- **Achados anteriores:** A9 resolvido (os quatro `*_TOKEN` saíram de `fora`, M2 e M3 saíram da spec 2; o M1 da spec 3 cobre o padrão `TOKEN` e morre). A10 resolvido (o `pronto.md` da stack node diz que a instalação roda sem as variáveis com `TOKEN`, `SECRET` ou `PASSWORD`, como `NPM_TOKEN`). A5 segue, recomendado.
- **Testes:** `python3 -m unittest tests.test_forge_copia tests.test_metricas_texto` deu 32 testes OK.
- **Ferramentas:** `python3 -I tests/catraca.py --base origin/develop` deu rc=0. `bin/forge-mutante tests/mutantes/v0476-stack-deps-2.json`: M1 e M4 a M14 morreram. `bin/forge-mutante tests/mutantes/v0476-stack-deps-3.json`: M1 a M5 morreram.
- **Segurança:** a lista fixa menor não muda o efeito (o padrão cobre os nomes tirados); o veredito é da segurança (`R-SEGURANCA`).
- **Suíte:** a suíte inteira fica para o CI do PR.

## Parecer
Aprovado: A9 e A10 resolvidos no delta; resta só A5, recomendado (`R-REVIEW`).
