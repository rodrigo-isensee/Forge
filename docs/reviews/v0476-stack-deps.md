---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: 8727471d9fdde8d6e9bf04edb75a3c8a91adf9ba
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.305, item E3.264, `forge-copia --instalar` depois da junção com o MP6)

## Achados
- A5 (recomendado) bin/forge-copia:48 · código e teste somam mais de 150 linhas (M14). O corpo do PR leva `teto: excedido, <n> linhas, <motivo>`.

## Revalidação
Delta lido por `forge-check parecer delta docs/reviews/v0476-stack-deps.md`, intervalo `f1091255..8727471d`, sem o que veio da base: `bin/forge-copia`, `tests/test_forge.py` e `tests/test_forge_copia.py`. A resolução da junção 8e21fb07 foi lida por `git show --remerge-diff 8e21fb07`. Nada fora disso relido.

- **f8f7e6c5 (E3.298):** `instalar.json` entra na forma do pacote de stack em `tests/test_forge.py` e precisa ser JSON válido; a forma da lista fica com `tests/test_forge_copia.py`.
- **8e21fb07 (junção):** conflito só no docstring de `bin/forge-copia` e nos imports e no fim de `tests/test_forge_copia.py`. Ficaram os dois lados: a classe `Instalar` e a classe `Disco`, os imports `io` e `json`. No `main`, a recusa por disco vem antes do `git worktree add` e do `git clone`, e o `instalar(real)` só roda depois da cópia criada; a linha de saída do docstring segue com "1 git ou instalação falhou". O resto do bloco no delta (o `MAQUINAS` de `tests/test_forge.py`, a classe `Disco`) é da base, sem mudança na junção.
- **8727471d:** o pacote falso de `Instalar` copia o `bin/forge_disco.py` ao lado do `forge-copia`; sem ele, o import novo falha na raiz temporária.
- **Achados anteriores:** A5 segue, recomendado.
- **Testes:** `python3 -m unittest tests.test_forge_copia tests.test_forge.PacotesDeStack tests.test_ambiente_git` deu 60 testes OK.
- **Ferramentas:** `python3 -I tests/catraca.py --base origin/develop` deu rc=0, sem guarda nova no delta.
- **Suíte:** a suíte inteira fica para o CI do PR.

## Parecer
Aprovado: a junção manteve a instalação e a recusa por disco na ordem certa; resta só A5, recomendado (`R-REVIEW`).
