---
tipo: review
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: d81e8488e6bb5510a7bda4a7115d4f502f9c4c0e
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: o hook parecer resolve a pasta do git só quando ela é literal (HK3-PARECER, PR A, E1 e E3)

Escopo: rodada 6. É a revalidação por delta do parecer `e8481c1`, que aprovou `79d0f6f`, sobre o merge `d81e848` (pais `913e748`, o último parecer do PR A, e `3b94791`, a develop). O brief manda ler `913e748511c1eb7182beb2e12746fea245e45707..d81e8488e6bb5510a7bda4a7115d4f502f9c4c0e`, e o `bin/forge-check delta --parecer docs/reviews/hk3-parecer-pasta.md` dá `79d0f6f..d81e848`, que tem o mesmo código. Esse delta traz 60 arquivos, mas todos vêm da develop `3b94791`, que já passou pelos portões nos próprios PRs. O que este review lê é só o que o merge decidiu:
- `git merge-tree --write-tree 913e748 3b94791`: o único conflito é `docs/engineering/achados-recorrentes.md`;
- `git diff <árvore do merge automático> d81e848`: a única diferença é a resolução desse conflito. Nenhum outro arquivo foi tocado à mão;
- `git diff 913e748 d81e848 -- hooks/parecer.py`: vazio. O hook do PR A não mudou, e a develop não mexe nele.

A resolução mantém as três linhas, cada uma com o seu número: a AR-1 da develop (`mascara-do-shell-esconde-codigo`, `bin/forge-mutante:404`) e as duas do PR A, que viraram AR-2 (`pasta-do-git-diferente-do-bash`, `hooks/parecer.py:257`) e AR-3 (`cd-escondido-por-involucro`, `hooks/parecer.py:224`). O texto, as contagens e as linhas citadas são os mesmos de antes, e o `hooks/parecer.py` não mudou, então as citações continuam certas. Ficou como "já lido": todo o código do PR A (`hooks/parecer.py`, `bin/forge-testes`, `tests/test_hooks_parecer_pasta.py`, `tests/test_testes_tocados.py`, `changelog.d/hk3-parecer-pasta.md`, fixtures e mutantes das rodadas 1 a 5) e o conteúdo da develop.

Veredito: **aprovado**. O merge é o merge automático mais a resolução das linhas AR. Não há regressão do que `e8481c1` aprovou.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_hooks_parecer_pasta tests.test_testes_tocados` em `d81e848`: `Ran 82 tests in 20.489s` / `OK`. Rodei de novo porque a develop mexe em `tests/test_hooks.py` e em `tests/config.json`, e o corpus do PR A depende deles.
- Pre-push do autor no envio de `d81e848`: 2196 OK, e o `forge-mutante` deu 79 mutantes mortos (histórico do pedido, 2026-10-28 21:32). O CI do PR roda a suíte inteira.
- `bin/forge-check docs`: sem saída, rc 0.
- `tests/config.json`: o PR A não mexe nele. A mudança que aparece no delta é da develop.
- Teto M14 (`git diff --numstat --no-renames 3b94791...d81e848`): 263 linhas de código e teste (`bin/forge-testes` 5, `hooks/parecer.py` 222, `tests/test_hooks_parecer_pasta.py` 34, `tests/test_testes_tocados.py` 2), abaixo de 400. É o mesmo número da rodada 5. Há uma classe só em `hooks/` (a pasta do git), com corpus próprio. Ok.
- Achados recorrentes (PA-7): conferi as três linhas. A AR-2 (`pasta-do-git-diferente-do-bash`) e a AR-3 (`cd-escondido-por-involucro`) são as antigas AR-1 e AR-2 do PR A, com a numeração nova do merge. A AR-3 fica com `vezes: 3`. O que sobra da classe é o A6, que é recomendado e igual na base. A AR-1 da develop (`mascara-do-shell-esconde-codigo`) não aparece no PR A. Nenhuma classe se repetiu neste delta, então nenhuma linha AR mudou.

## Revalidação
O delta não tem código do PR A. As sondas da rodada 5 (`$TMPDIR/tech-lead-hk3-parecer-pasta/sonda5/`) não foram refeitas, porque o `hooks/parecer.py` é o mesmo byte a byte (`git diff 913e748 d81e848 -- hooks/parecer.py` vazio). O que poderia regredir é a interação com o que a develop trouxe nos testes (`tests/test_hooks.py`, `tests/config.json`, `tests/apoio_volta_unica.py`). Os 82 testes do item verdes em `d81e848` cobrem isso, e a suíte inteira fica para o CI do PR.

## Achados
- A4 (recomendado) hooks/parecer.py:567 · gh pr create, ready e merge com pasta desconhecida (pushd, cd fora do nível de cima) são julgados pela pasta da sessão; o merge e o pull recusam, o gh não; sem mudança desde a rodada 1
- A6 (recomendado) hooks/parecer.py:161 · `builtin cd`, `command cd` e `if builtin cd` mudam a pasta do shell sem o hook ver o `cd` (rc=0, igual na base); mesma classe do A8 da segurança (AR-3)

## Parecer
Aprovado. O merge da develop `3b94791` só resolveu o conflito das linhas AR, e resolveu certo: as três linhas ficaram, cada uma com o seu número. O hook do PR A não mudou, os testes do item estão verdes no merge e o teto continua em 263 linhas. O A4 e o A6 continuam como recomendações e ficam como estão (decisão técnica de 2026-10-28 11:49). A renumeração das AR a cada merge é o assunto do cartão AR-CONFLITO.
