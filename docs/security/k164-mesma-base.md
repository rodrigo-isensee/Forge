---
tipo: revisao-seguranca
contrato: 1
pedido: k164-mesma-base
branch: melhoria/k164-mesma-base
commit: 6fa601f6afa9cd7319d133ec5e753ef1133b80fa
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: k164-mesma-base

Escopo: `git diff 8c07b44..6fa601f` (item E1 do pedido): `bin/forge-check` (função `base_do_delta`, `pr_da_cli` passa a usá-la), `hooks/parecer.py` (o hook lê a mesma base e passa a chamar `cmd_pr` com ela), 3 fixtures de `tests/hooks/parecer/`, spec de mutação, fragmento e o parecer do review.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `hooks/parecer.py` e `bin/forge-check` são PROTEGIDOS e formam o portão de pareceres (hook local e `forge-check pr`).

## Achados
- A1 (recomendado) hooks/parecer.py:374 · O hook deixa o modo estrito e usa o merge simulado com refs/remotes/origin/<base>, ref local que update-ref move. Sem ganho novo (refs/heads da integração já se movem), mas vale fixture e nota no modelo de ameaças.

## Detalhe dos achados
**A1 (informativa; esforço P; dono: tech-lead).** Evidência: `hooks/parecer.py:374` chama `fc.base_do_delta`, que em `bin/forge-check:616` resolve `refs/remotes/origin/<base>` antes da local; `hooks/parecer.py:383` passa essa base ao `cmd_pr`. Antes, o hook chamava `cmd_pr` sem base (estrito sempre), premissa citada no E4 de `docs/security/forge-check-lote.md`; o R3 daquele parecer já registrava que a remota é ref local. Caminho de ataque: um agente autor muda código depois do parecer, cria um commit lateral com a mesma mudança, aponta `refs/remotes/origin/develop` para ele (`git update-ref`, não barrado em `hooks/conformidade.py:1189`, que só barra `-d`), mescla esse commit na branch e o hook do `git merge` na integração aceita o parecer antigo. Ganho real nulo: o mesmo agente já pode mover `refs/heads/develop` direto e pular o hook de merge; no Forge a catraca recalcula com a base do evento do PR (`tests/catraca.py:1149`) e o pre-push barra o envio direto à integração. Correção mínima: registrar no modelo de ameaças que o hook confia na ref remota local e, opcional, uma fixture com a remota movida para um commit lateral.

## Verificação
- Guarda da base fora do fluxo (`bin/forge-check:613`): só `develop`, `homolog`, `main` (com ou sem um `origin/`) entram no merge simulado; `refs/heads/develop`, `origin/origin/develop`, `master` ou nome qualquer voltam a `(None, None)`, modo estrito. Presa pela fixture `pr-base-fora-do-fluxo-continua-estrita-bloqueia` e pelo mutante M4 (morto, conforme o review).
- Head contido na base: `(None, aviso)`; o hook descarta o aviso e segue estrito. Falha fechada.
- Isenção de QA: com base `None` (fluxo `master`, base inexistente), `base_da_entrega` cai em `BASES` e, sem nenhuma, devolve diff vazio, que `isencoes_do_diff` (`bin/forge-check:553`) não isenta. Fica mais estrito que o anterior (que comparava com o sha local); a lacuna R2 do pedido (projeto só em `master`) é anterior e fica fora.
- Caminho `git merge` (`hooks/parecer.py:447`): a base passa a ser o nome da integração atual, lido pela remota; local adiante da remota não encolhe o delta (a remota vem na frente).
- Injeção de argumento: a base que chega ao git é nome fixo de `BASES_DO_FLUXO`; o `ref` só chega depois de `existe()` (`rev-parse --verify`). Nada novo impresso: o aviso usa sha abreviado e nome da lista fixa.
- `tests.test_hooks.Hooks.test_fixtures` rodado neste review na worktree em 6fa601f: OK, rc=0.
- M14 (`agents/tech-lead.md:19`): cumpre. `git diff --numstat --no-renames 8c07b44 6fa601f` dá 35 linhas de código (`bin/forge-check` 21+7, `hooks/parecer.py` 3+4); fixtures, spec, fragmento e pareceres ficam fora. Um comportamento: a base do delta compartilhada; o intervalo a-b está em `melhoria/k164-intervalo`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: git, python3 e a suíte de fixtures do hook. `gitleaks`, `semgrep`, `osv-scanner`, `zizmor` e `actionlint` sem objeto (o diff não traz dependência, workflow nem segredo) e não usados.
