---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v047-h4-atualiza-branch
commit: ecc079920274ff207f217372c8708bef6e990899
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v047-h4-atualiza-branch (E2.689, H4 no head ea5c12c8)

Escopo: `git diff 73a0ab81...ea5c12c8` (bin/forge-fechar, tests/test_fechar_base_andou.py, 3 JSON de mutantes, fragmento). 154 linhas de código e teste (51 + 103), um comportamento só.

## Achados
- A1 (bloqueante) docs/fechamento-integrador.md:20 · o passo 2b ainda diz "O fechamento não traz a base (E8)" e "segue, sem merge, sem commit e sem envio"; o H4 passa a commitar e enviar em melhoria/*. Doc afetada sem atualizar na entrega (definição de pronto); reescreva o 2b (merge, envio, recomeço com --trazida, E8 só fora de melhoria/*)
- A2 (recomendado) docs/protecao-de-branch.md:21 · "a branch traz a base uma vez, no fim, antes do pedido de merge": cite que o forge-fechar a traz sozinho sem conflito (H4), para a regra de proteção continuar explicada
- A3 (recomendado) bin/forge-fechar:798 · no recomeço logo após o push, o gh pr list pode ainda dar o headRefOid antigo do PR aberto e o passo 3 para (falha fechada; rodar de novo resolve). Avalie reler o head do PR por alguns segundos ou dizer na mensagem que basta repetir
- A4 (recomendado) bin/forge-fechar:1 · 154 linhas passam da orientação de 150 (M14): o corpo do PR traz `teto: excedido, 154 linhas, <motivo>`

## Sondas
- S1 · grep -n 'sem merge, sem commit e sem envio' docs/fechamento-integrador.md · espera: nenhuma linha (o 2b agora commita e envia) · obtido: linha 20

## R-FLUXO e R-VERIFY
Só mantém ou aperta. O envio é `git push origin <sha>:refs/heads/<branch>` sem `--force` nem `--no-verify`, fast-forward (o merge tem o head do servidor como primeiro pai), e passa pelo pre-push, que decide pela ref remota (`.githooks/pre-push:141`). Só roda em `melhoria/*`, só com `merge-tree` limpo, uma vez por cadeia (`--trazida`); conflito ou falha de leitura param e devolvem ao agente, como antes. A base entra na hora do merge (`R-FLUXO`), com o pedido do dono (E2.664). A cadeia recomeça inteira no head novo: `forge-check pr` (o parecer vale pelo diff efetivo sobre a base, que o merge limpo não muda), 1c, PR e merge presos ao head novo. O `update-ref` exige o valor antigo e a worktree só anda por `--ff-only` limpa.

## Verificações
- Teste novo: `python3 -m unittest tests.test_fechar_base_andou` com ambiente limpo: 37 testes, OK (75,7 s).
- Guardas novas: 12 mutantes declarados (8 em `tests/mutantes/v047-h4-atualiza-branch.json`, 4 em `-2.json`), um por linha de guarda, cada um com teste do ramo de falha; os 2 remapeados (`mp1311-fechar-cartao-2`, `v0456-e8b`) apontam para testes H4 equivalentes. A mutação é do autor (V2), sem rerrodar.
- Suíte: só no CI do PR, não rerrodada.

## Revalidação (head 80679f19)
Delta lido por `forge-check parecer delta`: só `docs/fechamento-integrador.md` (passo 2b reescrito: merge, envio sem force nem pular o pre-push, recomeço com `--trazida`, E8 só fora de `melhoria/*`) e `docs/protecao-de-branch.md:21` (cita o H4). A1 e A2 resolvidos; S1 reexecutada: 0 linhas. A3 e A4 seguem recomendados, sem devolver. Código inalterado desde ea5c12c8.

## Revalidação (head ecc07992, E1.46)
Delta lido por `forge-check parecer delta` (80679f19..ecc07992, sem o que veio da develop): só `bin/forge-fechar:789` (`[ -d "$arvore_lock" ]` vira `test -d "$arvore_lock"`, mesma semântica) e o `de` do M6 em `tests/mutantes/v047-h4-atualiza-branch.json`, alinhado à linha nova. As junções da develop pelo passo 2b (f1e1ac05, 80dd1720) têm `git show --remerge-diff` vazio: merge limpo, sem resolução que mude o patch. Conferido: todo `de` dos JSON de mutantes que miram `bin/forge-fechar` aparece uma vez só na fonte (o L3 de `lote-0307-a.json` volta a casar só a linha 1186). CI do PR 633 no head ecc07992: as 5 partes da suíte e o teto de pulados verdes; `bateria (pareceres)` vermelha só por este parecer preso a 80679f19 (`commit: desatualizado`). A3 e A4 seguem recomendados.

## Parecer
Aprovado no head ecc07992 (antes, em 80679f19). Antes reprovado só por A1: o código está correto, testado e dentro de `R-FLUXO`/`R-VERIFY`, mas o documento de operação do fechamento descreve o oposto do que o passo 2b passa a fazer. A2 a A4 não devolvem. Na volta, a revalidação é pelo delta (só a doc).
