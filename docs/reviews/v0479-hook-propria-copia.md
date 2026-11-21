---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-hook-propria-copia
commit: bde062d7d009f4d2670967a03f5d05fb507fbc43
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E88.8, HOOK-AGENTE-FORA-DA-PROPRIA-COPIA), revalidação

Revalidação (H3, `R-REVIEW`): delta lido por `forge-check parecer delta`, intervalo `4ee59dfc..bde062d7`, no domínio `hooks/copia.py`, `tests/test_copia.py`, 9 fixtures novas em `tests/hooks/copia/`, 7 arquivos de mutantes, `docs/hooks.md`, `docs/hooks-fixtures.md` (gerado) e o fragmento do changelog. Nada fora do delta foi relido.

Verificado (rodado nesta cópia, TMPDIR novo por `mktemp -d`):
- `python3 -m unittest tests.test_copia`: 16 testes OK (inclui as 27 fixtures da pasta `copia` pelo executor do `test_hooks`).
- `python3 -m unittest -k test_hooks_json tests.test_hooks`: 1 teste OK.
- Suíte inteira: fica com o CI do PR (`R-REVIEW`), sem rerrodar aqui.

## Achados anteriores
- A1 (bloqueante): corrigido. `leitura()` (`hooks/copia.py:72-77`) separa as formas de leitura de `tag`, `branch`, `stash`, `apply`, `symbolic-ref` e `worktree`, com a fixture `libera-git-leitura-na-raiz` e os casos de `test_git_que_so_le`; S1 a S3 refeitas liberam.
- A2 (recomendado): corrigido. `env`, `timeout`, `command`, o caminho do git, `GIT_DIR=`, `--git-dir`, `--work-tree` e a barra antes da quebra viram alvo (`hooks/copia.py:53`, `:80-103`, `:119-123`); S5 a S7 recusam.

Pontos novos julgados sem achado:
- Sem varrer `wt/`: `worktrees()` lê só `git worktree list --porcelain` (ambiente sem `GIT_*`, `timeout=5`) e tira a raiz; `copia_do_alvo()` lê o HEAD só do clone de primeiro nível citado pelo alvo (`head_de`, só disco). O custo por chamada fica limitado ao número de alvos.
- Clones em `.forge/wt/` do projeto contam como cópia: a base entra junto de `~/.forge-contrib/wt/` (`hooks/copia.py:191`); como fica dentro da raiz, a ordem importa e está certa (cópia antes da regra da raiz, `:227-231`). As fixtures `libera-clone-do-projeto-em-forge-wt` e `recusa-clone-alheio-em-forge-wt` cobrem os dois ramos.
- A falsa leitura por argumento com nome `list`/`show` (S8, S9) é o A8 da segurança no mesmo head; não repito o achado.

## Achados
- A3 (recomendado) hooks/copia.py:1 · H1: 255 linhas de código (copia.py 237, hooks.json 12, forge-testes 6) contra 150; não cumpre o critério (cortar não deixa a suíte vermelha). Corte possível sem perder guarda: prefixos, apelido e `GIT_DIR` (`:28-31`, `:80-98`, `:119-123`) em item próprio. Teto excedido vai ao dono pelo Jarvis.

## Sondas
- S1 · fixture copia (reserva `escrita: melhoria/x`, worktree nela), `git tag -l` na raiz · espera: 0 · obtido: 0
- S2 · mesma fixture, `git stash list` · espera: 0 · obtido: 0
- S3 · mesma fixture, `git apply --check x.patch` · espera: 0 · obtido: 0
- S4 · mesma fixture, `git log > /dev/null` (controle) · espera: 0 · obtido: 0
- S5 · mesma fixture, `env git commit -m x` na raiz · espera: 2 · obtido: 2, R-CONFORMIDADE
- S6 · mesma fixture, `GIT_DIR=.git git commit -m x` · espera: 2 · obtido: 2, R-CONFORMIDADE
- S7 · mesma fixture, `git -C . \` com quebra e `commit -m x` · espera: 2 · obtido: 2, R-CONFORMIDADE
- S8 · mesma fixture, `git stash push -- list` · espera: 2 · obtido: 0 (A8 da segurança)
- S9 · mesma fixture, `git worktree add ../novo list` · espera: 2 · obtido: 0 (A8 da segurança)
- S10 · mesma fixture, `cd ../wt && git commit -m x` (a própria cópia) · espera: 0 · obtido: 0

## Parecer
Aprovado. Os dois achados do head 4ee59dfc estão corrigidos e provados por fixture e por sonda; a leitura do HEAD ficou restrita ao clone citado e às worktrees do `git`, e os clones de `.forge/wt/` contam como cópia sem abrir brecha na raiz.

Tamanho (H1): o item passou de 177 linhas no primeiro head para 255 porque a volta única absorveu os recomendados dos três portões (A2 deste review; A2, A3 e A4 da segurança; A1 e A2 do QA), que pela `R-REVIEW` iriam a cartão. O mínimo que fecha os bloqueantes (núcleo, leitura do A1 deste review, raiz nunca própria do A1 da segurança) passa de 150 por si; o corte limpo que resta é tirar a leitura de prefixos, apelido e `GIT_DIR` (cerca de 35 linhas) para um item seguinte, com as fixtures dela. Desfazer agora custa outra volta dos três portões e tira guardas já provadas; não bloqueio, mas o PR não pode levar `teto: excedido` com o motivo da H1, porque ele não se cumpre: a decisão de aceitar o excesso ou cortar é do dono (`R-DECISAO`).
