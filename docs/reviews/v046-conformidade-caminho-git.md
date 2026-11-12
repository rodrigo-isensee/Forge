---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/conformidade-caminho-git
commit: 22187bae11aba23d2e8fe705b6302647d7a34134
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E20.7, conformidade-caminho-git)

## Escopo lido
`git diff 8b5a44d5..22187bae` (Base-sha 8b5a44d5): 2 commits (06fa3baf fix, 22187bae test), 25 arquivos. Código e teste que contam (M14): `hooks/conformidade.py` +31/-1 e `tests/test_hook_git_comum.py` +33, 65 linhas, abaixo da orientação de 150; fixtures, spec de mutantes, índice e fragmento ficam fora. Uma classe de comportamento em `hooks/` (escrita pelo Bash com prefixo opaco antes de nome do `.git`), com corpus próprio `gitcomum-*` (10 recusam, 10 liberam). Revisão de instância que não fez a entrega, numa worktree destacada minha.

## Achados
- A1 (recomendado) hooks/conformidade.py:974 · falso positivo provado: `echo a > "$TMPDIR/logs/run.log"`, `cp x "$R/modules/vpc/main.tf"` e `echo a > "$TMPDIR/forge/x.log"` recusam rc 2 com a mensagem de .git/; falha fechada, saída pelo caminho literal; a mensagem não diz que o prefixo opaco foi lido como .git
- A2 (recomendado) hooks/conformidade.py:1154 · o limite declarado na entrega cita `$(pwd)/hooks/x`, mas esta linha troca `$(pwd)` por `$PWD`, que `expandir` resolve: a sonda `cp x "$(pwd)/hooks/novo.py"` sai rc 0; o caso real é `$(git rev-parse --show-toplevel)/hooks/x`; corrigir o texto do limite no PR

## Sondas

## Parecer
**Aprovado no domínio do review**, no head 22187bae. O item não entra na `develop` com este head: a segurança (E20.8, `docs/security/v046-conformidade-caminho-git.md`, fd4ad995) reprovou com A1 a A3 bloqueantes (resto vazio depois do opaco, `${d%…}`, crase sem aspas). Cito e não refaço (`R-SEGURANCA`); a volta do autor reabre este parecer por delta.

Checklist de leitura sobre o diff:
1. Faz o que a E20.6 pede: as sondas S1 e S2 da E20.4 viraram fixtures que recusam (`gitcomum-s1-subst-comum-forge-bloqueia`, `gitcomum-s2-variavel-forge-bloqueia`), e os comandos de git comuns seguem livres (`gitcomum-git-commit/fetch/worktree-add-libera`). Nada além do pedido.
2. Desenho: `resto_no_git` só soma um alvo a `alvos_da_escrita`; as regras `.git/…` existentes decidem. Não cria regra nova nem afrouxa nenhuma. Na dúvida recusa, coerente com a docstring da linha 939.
3. Legível; nomes dizem o que fazem; `NOMES_DO_GIT` comentado com a origem (E20.6).
4. Tipos e erros: `max(fins)` só depois do `if not fins`; `os.listdir(comum)` só com `comum` resolvido.
7. Testes: módulo próprio `tests/test_hook_git_comum.py` com mínimo de 20 itens (`minimo`) e os dois lados afirmados (item 11 do checklist). Rodei: 20 fixtures OK.
9. Commits Conventional em português, um por mudança.
10. Sem mecanismo novo de processo.

Guardas do diff e mutantes (cito, sem refazer): linhas de guarda mudadas 959, 969, 971, 974, 981, 982 e o padrão da 325; a spec `tests/mutantes/v046-conformidade-caminho-git.json` declara G1 a G7, um por linha, e o QA (E20.9) registra os 7 mortos. O QA anota que G3 morre por `ValueError` em `max([])`, não pela regra; concordo que é equivalente na prática.

Falso positivo declarado (pedido do brief): existe, mas é estreito e não trava fluxo comum do time. Procurei nos 3144 registros de sessão desta máquina escritas com `$TMPDIR`, `$(mktemp …)` ou `$(git rev-parse --show-toplevel)` seguidos de `logs`, `config`, `forge`, `hooks`, `info`, `index`, `refs`, `objects` ou `modules`: só aparecem nas sondas dos portões de hoje; o time grava logs em caminho literal (skill `esperar-estado`) e `$TMPDIR/hooks.out` ou `$TMPDIR/forge.log` não casam (o nome tem de ser a primeira parte inteira). `$(pwd)/…` não é afetado (A2). Nos projetos, `config/` e `modules/` na raiz são comuns, mas o falso positivo só ocorre com prefixo opaco não resolvido; Write e Edit não passam por aqui. Por isso A1 fica recomendado; com a volta da segurança, vale tirar `$TMPDIR` e `$(mktemp …)` do alcance, como a segurança sugere no A7 dela.

`bin/forge-testes` e o módulo novo: `--listar --base 8b5a44d5` dá "suíte completa (tests/hooks/conformidade/gitcomum-crase-forge-bloqueia.json sem mapa)". É de propósito: o comentário de `bin/forge-testes:157-159` deixa fixtures sem regra no `MAPA` para o plano manual, e o pre-push tira fixtures e specs do plano (`TESTE_DO_DIFF`, linha 686), ficando com `hooks/conformidade.py` (regra `hooks/.*` → `test_hooks`, que roda as 20 `gitcomum-*` no corpus inteiro) e com o próprio `tests/test_hook_git_comum.py`, que roda por estar no diff. Pôr o módulo novo na regra `hooks/.*` só duplicaria as fixtures que `test_hooks` já roda; não é preciso mudar o mapa.
