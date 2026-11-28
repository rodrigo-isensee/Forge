---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-placar-prometido
commit: d27d69cdee924cacfd4ad969e30ec426ecdf5f1b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E110.12, MEDIR-DE-NOVO-O-PROMETIDO, revalidação do merge da develop)

Delta lido (H3, R-REVIEW) em `forge-check parecer delta docs/reviews/v0480-placar-prometido.md`: intervalo b57a9676..d27d69cd, sem o que veio da develop; no domínio `bin/forge-testes`, `tests/pesos-d4.json` e `tests/test_testes_tocados.py`. O conflito em `tests/test_testes_tocados.py` manteve as duas entradas: `bin/forge-placar` segue com `test_placar_prometido` e `.devcontainer/devcontainer.json` ganha `test_ambiente_recriacao` (da develop, E119.1); o mapa do `bin/forge-testes` e o peso em `tests/pesos-d4.json` batem com o caso, e `tests/test_ambiente_recriacao.py` existe no head. Nada do placar prometido mudou; o parecer de b57a9676 abaixo segue válido.

## Revalidação anterior (E110.6, head b57a9676)

Revalidação da volta única (H3, R-REVIEW) no head b57a9676, pelo delta lido em `forge-check parecer delta docs/reviews/v0480-placar-prometido.md`: intervalo afc7083d..b57a9676, sem o que veio da develop; no domínio `bin/forge-placar`, `bin/forge-testes`, o fragmento do changelog, as duas specs de mutante, `tests/pesos-d4.json` (só do merge da develop, fora do commit b57a9676), `tests/test_placar_prometido.py` e `tests/test_testes_tocados.py`.

O A1 anterior está resolvido: M6 (`if not com`) e M7 (`or PROMETIDO.search("prometido: 0%")`) trocam agora dentro do nó da condição das linhas 594 e 593. O prometido limitado a 6 dígitos inteiros (`\d{1,6}`) impede o `float` de virar `inf` e o `--json` de sair `Infinity`; o que passa disso vira `falta:` com o texto novo, e o M10 guarda o teto. O mapa do `bin/forge-testes` inclui `test_placar_prometido` e o caso do `test_testes_tocados` acompanha.

## Achados
- A2 (recomendado) docs/melhoria-continua.md:17 · o checklist do `forge-placar propostas` aqui e em skills/kanban-metricas/SKILL.md:37 não cita o `prometido: <N>%` (até 6 dígitos) nem a linha `prometido:` nova; só a docstring do script diz como declarar.
- A3 (recomendado) bin/forge-placar:592 · o real sai sem o piso de amostra do `comparar` (`--minimo`, rc 3 inconclusivo): com poucas delegações o `real -60%` aparece como medida firme; marcar `amostra pequena` ao lado.

## Sondas
- S1 · python3 -I tests/catraca.py --modo regras --base 48d6f4b8 (merge-base com a develop) --head b57a9676 --raiz . · espera: rc 0 · obtido: rc 0
- S2 · bin/forge-mutante --cobertura --base 48d6f4b8 · espera: rc 0, toda condição coberta · obtido: rc 0, linhas 586, 593, 594, 595 e 625 cobertas

## Parecer
Aprovado no head d27d69cd: `test_testes_tocados.Mapa` 18 OK no head (rodado de `tests/`). Na volta anterior: ferramentas citadas, sem refazer: `bin/forge-mutante` nas duas specs, 10 de 10 mortos (M1 a M10); `test_placar_prometido` e `test_testes_tocados.Mapa` 32 OK no head, com ambiente limpo. Suíte inteira: fica no CI do PR. A2 e A3 viram cartão depois do merge.
