---
tipo: review
contrato: 1
pedido: versao-035
branch: melhoria/push-parecer-ja-no-remoto
commit: d2460c939f3aaab22345a5f97675051e1bc7a7e6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-06
---
# Review: versao-035 (E3, PUSH-PARECER-JA-NO-REMOTO)

## Achados
- A1 (bloqueante) .githooks/pre-push:207 · resolvido em 445803b: o hook consulta $2 (a URL do envio, que segue a pushurl) nas duas chamadas (207 e 296); o caso "pushurl sem o commit, url com ele (A1)" do teste roda a suíte e cai se o hook voltar a usar $1
- A2 (bloqueante) tests/test_pre_push_ja_no_remoto.py:47 · resolvido em 445803b: decisão M14: 150 linhas de código e teste (hook 31+1, teste 118+0), dentro do teto; o teste virou tabela sem perder os casos C-1, C-5, T-5, T-6, C-10 e a fila
- A3 (recomendado) .githooks/pre-push:197 · o ls-remote sobre a URL de $2 aplica url.insteadOf, e o git já passou a URL com pushInsteadOf; divergência entre as duas reescritas fica como residual a registrar no corpo do PR (afrouxa-regra), junto do A10 do modelo de ameaças

## Parecer
Aprovado. Revalidação por delta do parecer reprovado em 6643960 (head revisado então: 72bf750), feita por outra instância do tech-lead (a de 6643960 não existe mais nesta sessão).

Delta lido (`forge-check delta --parecer docs/reviews/push-parecer-ja-no-remoto.md`, intervalo 72bf750..d2460c9): `.githooks/pre-push` 183-186, 189, 192, 197, 207 e 296; `changelog.d/push-parecer-ja-no-remoto.md`:2; `docs/hooks.md`:115; `tests/test_pre_push_ja_no_remoto.py` inteiro (+83 -173, lido de 1 a 118). Já lido no parecer anterior e fora do delta: o resto de `ja_no_remoto` (recusas, `refs/heads/*`, tudo ou nada, `GIT_TERMINAL_PROMPT=0`, `timeout 20`, `sha_valido`, `cat-file -e` e `merge-base --is-ancestor`), a posição depois das recusas e do PREPUSH-DELETE e a segunda consulta depois de `fila_sair`.

A1: `ja_no_remoto` recebe o destino em `destino="${1:-}"` e as duas chamadas passam `"${2:-}"`; a recusa de vazio e de `-*` segue sobre o destino. Comentário, `docs/hooks.md` e fragmento do changelog dizem "o destino do push (a URL de envio, que segue a pushurl)". Mutante conferido: com as duas chamadas trocadas de volta para `"${1:-}"` numa cópia no scratchpad, o teste cai em 5 subtestes, entre eles "pushurl sem o commit, url com ele (A1)"; no head, verde.

A2: `git diff --numstat --no-renames origin/develop...HEAD` (merge-base d9b26bb, a Base-sha): `.githooks/pre-push` 31+1, `tests/test_pre_push_ja_no_remoto.py` 118+0, total 150, dentro do teto; `docs/hooks.md`, `changelog.d/` e o parecer ficam fora. Um comportamento só (o pulo, nas duas consultas). Conferi que a tabela mantém a matriz anterior: igual, ancestral, duas refs, sha não ancestral, destino inexistente, `-x`, credencial com terminal de controle, lento (C-1, menos de 24 s), casamento pela cauda, ref nova, objeto ausente (C-1), misto com ref nova, tag e remoção, `--suite` e `--status` (C-5, T-5), stdin vazio (T-6), não fast-forward, main, homolog e develop, nenhuma trava ou prova na pasta depois do pulo (C-8, T-1), variáveis `FORGE_*` no ambiente e leitura estática da função e das chamadas (C-10), e o teste da fila (destino ganha a ref na espera, senha e trava soltas, C-7).

A3 segue recomendação, não devolve.

Ferramentas: `python3 -m unittest tests.test_pre_push_ja_no_remoto` no head d2460c9: 2 testes, OK (24,6 s). `bin/forge-testes --listar`: suíte completa (`.githooks/pre-push sem mapa`); não a rodei (D-5): o push de d2460c9 a rodou. `shellcheck` não está instalado neste ambiente: segue pendência da regra de ferramenta. Segurança: o parecer da E2.5 (`docs/security/push-parecer-ja-no-remoto.md`) ainda não existe nesta branch; a correção do A1 é o cartão para ele conferir, e não refiz a análise de segurança.
