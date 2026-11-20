---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-pv-b3-pre-push
commit: cb4f48b5e4bcad520fec12b58109c6b6ca30290a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 (E57.47, PR-VERDE B3, patch do `.githooks/pre-push`, head cb4f48b5)

Revalidação pelo delta (H3, `R-REVIEW`): `forge-check parecer delta docs/reviews/v0479-pv-b3-pre-push.md`, intervalo 081067f0..cb4f48b5, domínio "código e testes"; no domínio só `docs/engineering/v0479-pv-b3-pre-push.patch` e `docs/engineering/v0479-pv-b3-pre-push.md` (volta da segurança, E57.43). Lido só esse delta; o resto vale do parecer anterior (head 081067f0). O patch não foi aplicado na branch (D6).

## Ferramentas citadas (sem refazer)
- Suíte: só no CI do PR (`R-REVIEW`); não rerrodada aqui.
- `git apply --stat`/`--check` do patch sobre o `.githooks/pre-push` da base 20bbbd8d (blob f9443600): só `.githooks/pre-push`, 38 inserções, aplica; resultado f54dabe, igual ao índice do patch; `bash -n`: ok.
- `shellcheck`: fora do PATH nesta estação (o CI confere quando o patch entrar).
- Tamanho (H1): 38 linhas de shell acrescentadas, um comportamento: dentro do teto.

## Leitura do delta
- A guarda nova `case "$prazo" in ''|*[!0-9]*)` recusa o envio antes de rodar a conferência e esvazia a lista; `timeout --` fecha a porta do `--help`. Falha fechada mantida.
- A nota agora diz o que o A1 anterior apontou (exceção do intérprete sai 1 e cai na mensagem de registro desatualizado) e o roteiro de aplicar fixa o commit revisado e confere pelo `--stat`.

## Achados
- A1 (recomendado) docs/engineering/v0479-pv-b3-pre-push.patch:32 · Segue do parecer anterior: exceção do intérprete sai 1 e mostra "registro desatualizado"; a nota já documenta, a mensagem ainda engana. Cartão depois do merge.
- A2 (recomendado) docs/engineering/v0479-pv-b3-pre-push.patch:10 · Segue: "em segundos" contra 34 a 45 s medidos (meta R3 p95 < 20 s); cartão para cortar ou paralelizar o grupo mais lento de REGISTROS.
- A3 (recomendado) docs/engineering/v0479-pv-b3-pre-push.patch:19 · Segue e cresce: a guarda do prazo é mais uma sem teste de comportamento nem spec em tests/mutantes/; o PR de aplicação do dono leva os 6 casos da nota como teste.
- A4 (recomendado) docs/engineering/v0479-pv-b3-pre-push.patch:17 · `FORGE_REGISTROS_PRAZO=0` passa a guarda e o `timeout` do GNU trata 0 como sem prazo: a conferência roda sem teto. Não pula nada; vale citar na nota ou exigir prazo maior que 0.
- A5 (recomendado) docs/engineering/v0479-pv-b3-pre-push.patch:1 · Commit 322749ff com mensagem "wip patch" fora do Conventional Commits; o merge por squash o apaga, senão reescreva na integração.

## Sondas
- S1 · cópia na base 20bbbd8d com o patch aplicado, remoto bare vazio, ambiente limpo, `FORGE_REGISTROS_PRAZO=--help` · espera: recusa sem rodar a conferência · obtido: "FORGE_REGISTROS_PRAZO deve ser um número de segundos inteiro (veio '--help')", rc 1
- S2 · idem com `FORGE_REGISTROS_PRAZO=5x` · espera: recusa · obtido: mesma mensagem, rc 1

## Parecer
Aprovado no head cb4f48b5. A correção da segurança fecha a porta do `--help` sem afrouxar nada, o patch continua aditivo e aplica limpo na base. A1 a A5 viram cartão depois do merge.
