---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-hook-propria-copia
commit: 4ee59dfcdf2b82cb10a3c49f8ed6fefdc92113dd
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E88.3, HOOK-AGENTE-FORA-DA-PROPRIA-COPIA)

Escopo: diff `ad3b3b6f..4ee59dfc` (hook `hooks/copia.py`, registro em `hooks/hooks.json`, 18 fixtures em `tests/hooks/copia/`, `tests/test_copia.py`, 4 arquivos de mutantes, limites em `docs/hooks.md`; `docs/indice-forge.md` e `docs/hooks-fixtures.md` são saída de gerador).

Verificado (rodado nesta cópia, TMPDIR novo por `mktemp -d`):
- `python3 -m unittest tests.test_copia`: 11 testes OK (inclui as 18 fixtures pelo executor do `test_hooks`).
- `python3 -m unittest -k test_hooks_json -k test_cada_hook_tem_caso tests.test_hooks`: 2 testes OK.
- Suíte inteira: fica com o CI do PR (`R-REVIEW`), sem rerrodar aqui.

Desenho conferido sem achado: a sessão principal (sem `agent_id`) fica livre; a cópia vem do registro (`escrita` da reserva, `agentes.escritas_do_registro`) cruzada com o HEAD das worktrees e dos clones de `~/.forge-contrib/wt/` (com `realpath`, o que cobre o `~/.forge-contrib` em link simbólico); a pasta de controle fora de `wt/`, as temporárias e `/dev` ficam livres; registro ausente, ilegível ou sem cópia libera e anota no erros.log; `agentes.py` não muda; leitura comum (`git log > /dev/null`, `cat`) passa.

## Achados
- A1 (bloqueante) hooks/copia.py:23 · Subcomando decide sozinho: `git tag -l`, `git stash list` e `git apply --check` (só leem) são recusados na raiz, o cwd padrão do subagente. Fere o contrato de docs/hooks.md ("leitura não conta"). Separe as formas de leitura de tag, stash e apply, com fixture de libera para cada uma.
- A2 (recomendado) hooks/copia.py:55 · `env git commit`, `GIT_DIR=x git commit` e `git -C <dir> \` com quebra de linha antes do subcomando não viram alvo (sonda em processo: `[]`). Não está entre os limites de docs/hooks.md:149; registre lá ou leia o prefixo.

## Sondas
- S1 · fixture copia (reserva com `escrita: melhoria/x`, worktree `wt` nela), comando `git tag -l` no cwd da raiz · espera: código 0 (leitura) · obtido: código 2, "R-CONFORMIDADE: <raiz> fica fora da sua cópia"
- S2 · mesma fixture, comando `git stash list` · espera: código 0 · obtido: código 2, R-CONFORMIDADE
- S3 · mesma fixture, comando `git apply --check x.patch` · espera: código 0 · obtido: código 2, R-CONFORMIDADE
- S4 · mesma fixture, comando `git log > /dev/null` (controle) · espera: código 0 · obtido: código 0

## Parecer
Reprovado por A1. O pedido exige que o hook não trave o time por falso positivo na leitura, e o subagente roda com o cwd na raiz da sessão: um `git tag -l` (fluxo de versão) ou `git stash list` recusado lá é a trava que o desenho quer evitar. Correção pequena em `alvos_do_segmento` (ou `GIT_DE_ESCRITA`): tratar `tag` sem argumento de nome ou com `-l`/`--list`/`--contains`/`--points-at`, `stash list`/`stash show` e `apply --check`/`--stat`/`--numstat` como leitura, com uma fixture `libera-*` por forma e o mutante da guarda nova. A2 vira cartão depois do merge. Na volta, o delta basta (`forge-check parecer delta`).
