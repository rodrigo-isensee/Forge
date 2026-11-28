---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-h2-retomado-conflito
commit: 83d3b07d479ddc5ade6c4fdffc331aea7602e845
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478 (E92.6, revalidação do H2-RETOMADO-CONFLITO)

Revalidação por delta (R-REVIEW). A rodada anterior (head `a98c1a53`, reprovado com A1) fica no git. Base `fb3b670b`, head `83d3b07d`. A janela A5 fica fora por decisão.

Gatilhos: hook de controle do R-TETO (reserva de escrita por branch), registro no erros.log.

## Delta lido
`forge-check parecer delta` no intervalo `a98c1a53..83d3b07d`: no domínio, `hooks/agentes.py` (ramo do retomado tardio no `iniciar`, 1303-1310, e a linha do cabeçalho), `docs/hooks.md` (`expiracao_horas`) e as três fixtures `tests/hooks/agentes/autor-retomado-tardio-*.json` (uma nova, `...branch-mista`). Fora do domínio: fragmento do changelog, `docs/hooks-fixtures.md`, mutantes.

Já lido e sem mudança desde a rodada anterior: `sem_controle` e o corte de 80 caracteres na linha do erros.log, a saída antecipada do `iniciar` quando o id já está em `agentes`, reserva vencida e de parecer fora de `ocupadas`.

## Achados anteriores
- A1 (bloqueante): corrigido. `hooks/agentes.py:1309` grava o retomado com `escrita` inteira, como na base; `git diff fb3b670b..83d3b07d -- hooks/agentes.py` mostra só a soma da linha `H2-RETOMADO-CONFLITO ... segue com <tomadas>` ao erros.log quando há `tomadas`, sem mudar o registro, o código de saída nem a recusa. A fixture `...branch-tomada-avisa` agora espera rc 2 ("ocupada por forge:software-engineer") depois do `SubagentStop` da reserva viva.

## Só aperta
Base x head pelas mesmas três fixtures do head (harness de `tests/test_hooks.py`, `executar_fixture`, árvores por `git archive` em TMPDIR próprio): código, stderr e estado iguais nos dois lados; a única diferença é a linha nova no erros.log (no head, as três falham só se o esperado omite `erros_log`, porque a linha a mais aparece; na base, falham só se o esperado a exige). Ganho de observabilidade sem afrouxar nada. Bate com a sonda de 5 passos do autor (`/root/.forge-contrib/wt/e925-saida/sondas.txt`, `head-novo` igual à base).

## Sondas
- S1 · fixture ...branch-tomada-avisa do head (viva B, início de A, fim de B, Agent em a) · espera: rc 2 "ocupada por forge:software-engineer" e linha "segue com" · obtido: head ok; base ok sem o erros_log (rc 2, mesmo stderr)
- S2 · `...branch-mista` e `...reserva-viva-vale` nos dois lados · espera: mesmo código e stderr · obtido: iguais; diferença só a linha do erros.log

## Riscos aceitos e ferramentas
Nenhum risco aceito. Suíte inteira não rodada (CI do PR); rodadas só as sondas acima. Ferramentas externas de varredura não se aplicam.
