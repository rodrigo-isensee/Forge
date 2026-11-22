---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-quarentena-fechar
commit: e77f3543f1844065aa66c90e6c1ba3123e66e55c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E114.3, QUARENTENA-DIGITO-ASCII e FECHAR-SEM-AUTO-MERGE)

Revisão completa única, no head `e77f3543` contra a base `b0895f6c` (diff inteiro de `bin/`, `docs/fechamento-integrador.md`, `changelog.d/`, testes e mutantes).

## Gatilhos
Gatilhos: controle de merge do integrador (bypass do ruleset pela conta do dono), validador de autorização do dono na quarentena de teste.

## Veredito por escrito: a mudança só aperta
- **Sem caminho de merge automático no `bin/forge-fechar`:** `grep -c -- '--auto' bin/forge-fechar` dá 0. O único `gh pr merge` é `mesclar_direto` (`bin/forge-fechar:891`), sem `--auto` e sem `--admin`, preso ao head por `--match-head-commit`; os dois chamadores (passo 6, `:1598`; P6, `:1246`) vêm logo depois de `checks_do_head_verdes` (`:1592` e `:1245`). O `--armar` morre no parser (`:117`, código 1, nada feito); `--armar=1` cai em "opção desconhecida" (`:128`). Saiu o `exit 4` de PR armado e o atalho que pulava a espera do passo 4.
- **Check pendente não passa:** `checks_do_head_verdes` (`:864-884`) julga a execução mais recente de cada nome de `CHECKS_EXIGIDOS` (constante `readonly`, `:96`, a catraca incluída); só `completed/success` sai do laço; `completed/*` fora de success para; pendente ou ausente espera e relê tudo; prazo esgotado para sem mesclar; leitura que falha para. Antes, o P6 mesclava com `--auto` sem conferir check nenhum (com o bypass, na hora); agora confere. No passo 6 o requisito final é o mesmo de antes (todos em success), só troca "para" por "espera e relê".
- **Quarentena:** `OK_DO_DONO` (`bin/forge_quarentena.py:28`) aceita só `[0-9]`, sempre com `fullmatch` (`:89`, `:103`). A irmã `DATA` (`:27`) ainda usa `\d`, mas a data com dígito não ASCII cai no `fromisoformat` e vira `None` (erro), falha fechada; não é achado.

Nada afrouxa: nenhuma checagem saiu sem uma igual ou mais forte no lugar.

## Achados
- A1 (recomendado) bin/forge-fechar:1245 · P6 lê os check-runs do sha da marca, que traz os do push na develop (bateria e bateria (python 3.14) em skipped, ci.yml:577 e :857); antes de o CI do PR criá-los, para por "terminou em skipped": falha fechada, mas falsa; contar só a execução do evento do PR
- A2 (recomendado) bin/forge-fechar:1590 · a espera nova de checks_do_head_verdes (até --espera) vem depois da releitura do PR por nome (:1590) e do 6a/6b (:1571-1575): a janela documentada de PR novo do mesmo head e de base andando cresce; esperar os checks antes do 6a e da releitura, ou refazê-los depois
- A3 (recomendado) bin/forge-fechar:1245 · no P6 só CHECKS_EXIGIDOS é conferido; os obrigatórios extras do ruleset da homolog (ler_exigidos_do_destino, :545) não, e o merge direto da conta do dono passa pelo bypass; ler os exigidos da homolog e conferi-los no P6
- A4 (recomendado) scripts/promover-homolog.py:341 · fora do forge-fechar sobra merge automático: o script imprime gh pr merge develop --auto e docs/promocao-integrador.md:18 manda o tech-lead armá-lo; contraria a ordem do dono (nunca merge automático); trocar por merge direto depois dos checks verdes
- A5 (recomendado) docs/fechamento-integrador.md:28 · texto velho: "Com --armar, a linha do --limpar impressa leva --cartao", e bin/forge-check:1469 cita "armar o auto-merge"; o --armar agora recusa; remover as duas menções

## Sondas

## Detalhe dos achados
- **A1** · evidência: `bin/forge-fechar:867` lê `commits/<sha>/check-runs?filter=latest` sem filtrar o evento; `.github/workflows/ci.yml:577` e `:858` pulam `bateria (python 3.14)` e `bateria` no push na develop. Leitura do código e dos workflows, não observado no servidor (sem acesso ao `gh` neste ambiente). Caminho de ataque: nenhum; o efeito é parar a promoção sem motivo (disponibilidade), nunca mesclar. Severidade baixa. Correção mínima: descartar check-run cujo check suite não é do evento `pull_request` do PR (ou ler os checks pelo `gh pr checks <n>`, como no passo 4) e tratar o que sobrar como ausente; manter "terminada fora de success para" para a execução do PR. Esforço P. Dono: autor da branch (devops-engineer/tech-lead do fechar).
- **A2** · evidência: ordem `:1571` (6a), `:1574` (6b), `:1590` (releitura por nome), `:1592` (espera dos checks), `:1598` (merge). Caminho: durante uma espera longa (re-execução de check), a develop anda ou outro PR do mesmo head aparece; o `--match-head-commit` segura o head, não a base nem o PR. Severidade baixa (o passo 4 já esperou os checks; a espera do passo 6 é rara). Correção mínima: mover `checks_do_head_verdes 6` para antes do `passo "6a"`, ou repetir 6a, 6b e a releitura por nome depois dela. Esforço P. Dono: autor da branch.
- **A3** · evidência: `:1245` chama só `checks_do_head_verdes P6`; `ler_exigidos_do_destino` (`:545`) roda só no caminho do item (`:1463`). Caminho: o dono põe um check obrigatório a mais no ruleset da homolog; o P6 mescla pela conta com bypass sem ele. Não é regressão (antes o `--auto` com bypass mesclava sem nada). Severidade baixa. Correção mínima: no P6, ler os exigidos da homolog e esperar cada um como os de `CHECKS_EXIGIDOS`. Esforço P/M. Dono: autor da branch.
- **A4** · evidência: `scripts/promover-homolog.py:341` (`comando_merge` com `--auto`), `:18` e `:334` (texto), `docs/promocao-integrador.md:18`. Caminho: o tech-lead segue o processo e arma o merge automático da develop para a homolog; com a conta do dono no bypass, o GitHub mescla na hora com check vermelho ou pendente (o mesmo motivo que o próprio forge-fechar registra em `:858-860`). Fora do diff desta branch; registrado porque a ordem do dono vale para qualquer PR. Severidade média. Correção mínima: o script imprime o merge direto (`gh pr merge develop --merge --match-head-commit <sha>`) só com os checks verdes, e o doc diz "mescle com tudo verde, nunca automático"; pode virar item próprio se o dono preferir. Esforço P. Dono: devops-engineer (script) e tech-lead (doc).
- **A5** · evidência: `docs/fechamento-integrador.md:28`, `bin/forge-check:1469` (comentário). Caminho: nenhum (texto); induz quem lê a tentar o `--armar`. Severidade informativa. Correção mínima: apagar as duas menções. Esforço P. Dono: autor da branch.

## Provas executadas
- `bin/forge-fechar v0478 --ref melhoria/x --armar` → rc 1, mensagem de recusa com o comando certo; `--armar=1` → "opção desconhecida".
- `OK_DO_DONO.fullmatch` sobre `A-1`, `A-١`, `A-1\n`, `Ａ-1`, `A-²` → só `A-1` passa.
- `python3 -m unittest tests.test_forge_quarentena tests.test_fechar_auto_merge tests.test_fechar_checks_do_head` → 45 testes, OK (inclui pendente que espera e relê, pendente no fim do prazo sem merge, falha terminada sem esperar). O P6 tem teste próprio de pendente no prazo (`tests/test_fechar_lote.py:552`). A suíte inteira fica para o CI do PR, que o passo 4 do forge-fechar exige; o brief pede sem suíte local.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, grep, execução local do script e dos testes afetados. Sem acesso ao `gh` (configuração bloqueada pelo sandbox): a semântica dos check-runs de push com `skipped` (A1) vem dos workflows, não do servidor.
