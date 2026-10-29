---
tipo: review
contrato: 1
pedido: hk3-parecer-pasta
branch: melhoria/hk3-parecer-pasta
commit: 94ea85b06b8cdc8645d38e61b98df4bed9899858
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: o hook parecer resolve a pasta do git só quando ela é literal (HK3-PARECER, PR A, E1 e E3)

Escopo: rodada 7. Revalida por delta o parecer `e967301`, que aprovou o merge `d81e848`, e cobre os dois commits que vieram depois dele:
- `bb6eec4`, que traz a develop `7a9d23c` (pais `e967301` e `7a9d23c`);
- `94ea85b`, que ajusta um teste.

O brief manda ler `e967301..94ea85b`. O `bin/forge-check delta --parecer docs/reviews/hk3-parecer-pasta.md` dá `d81e848..94ea85b`, que tem o mesmo código. São 27 arquivos, e quase todos vêm da develop (`4afeec7` LOTE-PREPUSH-PARECER e `7a9d23c` AQ1-FORGE-CHECK), que já passaram pelos portões nos próprios PRs. Este review lê só o que o PR A decidiu nesse delta:
- `git merge-tree --write-tree e967301 7a9d23c`: o único conflito é `docs/engineering/achados-recorrentes.md`;
- `git diff <árvore do merge automático> bb6eec4`: a única diferença é a resolução desse conflito (+2 -6, só as marcas e as linhas AR). Nenhum outro arquivo foi tocado à mão;
- `git diff e967301 94ea85b -- hooks/ bin/forge-testes tests/test_hooks_parecer_pasta.py tests/test_testes_tocados.py tests/hooks/parecer/ changelog.d/hk3-parecer-pasta.md`: vazio. O código do PR A não mudou;
- `94ea85b`: uma linha em `tests/test_erros_no_brief.py:541`.

O que a resolução faz:
- as linhas AR-1 a AR-6 da develop ficam como estão;
- a `mascara-do-shell-esconde-codigo`, que era a AR-1 da branch, já é a AR-6 da develop e não se repete;
- as duas classes do PR A viram AR-7 (`pasta-do-git-diferente-do-bash`, `hooks/parecer.py:257`) e AR-8 (`cd-escondido-por-involucro`, `hooks/parecer.py:224`), com o texto, a contagem e a linha citada de antes.

Isso é o que pede a decisão técnica de 2026-10-29 07:30. São 8 linhas, abaixo do teto de 20.

O que muda em `94ea85b`: o teste `test_aq1_o_arquivo_do_forge_traz_as_linhas_ar_da_proposta` antes exigia a lista exata dos 6 tipos e agora exige que as 6 primeiras linhas sejam as da proposta. A segunda asserção ainda passa todas as linhas por `fc.problemas_dos_achados`. Isso confere o formato de cada uma, o slug da classe e o teto de 20 linhas. O teste continua vermelho se as linhas da proposta sumirem, mudarem de ordem ou perderem o formato, e só deixa de fixar o total. Isso é o que pede a decisão técnica de 2026-10-29 08:05.

Ficou como "já lido": todo o código do PR A (`hooks/parecer.py`, `bin/forge-testes`, `tests/test_hooks_parecer_pasta.py`, `tests/test_testes_tocados.py`, `changelog.d/hk3-parecer-pasta.md`, fixtures e mutantes das rodadas 1 a 6) e o conteúdo da develop `7a9d23c`.

Veredito: **aprovado**. O merge é o merge automático mais a resolução das linhas AR, e o ajuste do teste é o menor possível. Não há regressão do que `e967301` aprovou.

## Ferramentas (citadas, não refeitas)
- `python3 -m unittest tests.test_erros_no_brief tests.test_hooks_parecer_pasta tests.test_testes_tocados` em `94ea85b`: `Ran 124 tests in 25.012s` / `OK`.
- `bin/forge-check docs`: sem saída, rc 0.
- `tests/config.json`: o PR A não mexe nele.
- Teto M14 (`git diff --numstat --no-renames origin/develop...HEAD`, com `origin/develop` = `7a9d23c`): 265 linhas de código e teste, abaixo de 400:
  - `bin/forge-testes`: 5
  - `hooks/parecer.py`: 222
  - `tests/test_erros_no_brief.py`: 2
  - `tests/test_hooks_parecer_pasta.py`: 34
  - `tests/test_testes_tocados.py`: 2

  As 263 linhas da rodada 6 mais as 2 de `94ea85b`. Há uma classe só em `hooks/` (a pasta do git), com corpus próprio. Ok.
- Achados recorrentes (PA-7): conferi as 8 linhas. A AR-7 e a AR-8 são as antigas AR-2 e AR-3 do PR A, com a numeração nova do merge. A AR-8 fica com `vezes: 3`. O que sobra da classe é o A6, que é recomendado e igual na base. Nenhuma classe se repetiu neste delta, então nenhuma linha AR mudou.

## Revalidação
O delta não tem código do PR A. As sondas da rodada 5 não foram refeitas, porque o `hooks/parecer.py` é o mesmo byte a byte. O que poderia regredir:
- a interação com o que a develop trouxe: o pre-push, o `bin/forge-check` e os testes de `forge-check brief` e dos achados;
- a lista de módulos do `bin/forge-testes`, com o módulo novo `tests/test_pre_push_parecer_curto.py` da develop.

Os 124 testes do item, verdes em `94ea85b`, cobrem isso, e a suíte inteira fica para o CI do PR.

## Achados
- A4 (recomendado) hooks/parecer.py:567 · gh pr create, ready e merge com pasta desconhecida (pushd, cd fora do nível de cima) são julgados pela pasta da sessão; o merge e o pull recusam, o gh não; sem mudança desde a rodada 1
- A6 (recomendado) hooks/parecer.py:161 · `builtin cd`, `command cd` e `if builtin cd` mudam a pasta do shell sem o hook ver o `cd` (rc=0, igual na base); mesma classe do A8 da segurança (AR-8)

## Parecer
Aprovado. O merge da develop `7a9d23c` só resolveu o conflito das linhas AR, e resolveu como a decisão de 07:30 pede: AR-1 a AR-6 da develop, e AR-7 e AR-8 do PR A. O `94ea85b` ajusta o teste do arquivo AR para exigir as 6 linhas da proposta nas primeiras posições, sem fixar o total. O hook do PR A não mudou, os testes do item estão verdes e o teto ficou em 265 linhas. O A4 e o A6 continuam como recomendações e ficam como estão (decisão técnica de 2026-10-28 11:49). As citações AR deste parecer seguem a numeração nova. A renumeração a cada merge é o assunto do cartão AR-CONFLITO.
