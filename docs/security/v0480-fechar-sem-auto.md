---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-sem-auto
commit: a34b33bf1bd6a4e2e726846eb68fd0e397e5196f
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança por delta: v0478 (E171.10, PR #855)

Rodada anterior: `reprovado` no head `f5143cea` (commit `a264f9e2`, no git), com A1 bloqueante. Esta volta lê só o delta `f5143cea..a34b33bf`.

Gatilhos: portão de merge (FECHAR-NUNCA-AUTO, FECHAR-SEM-AUTO-MERGE), fluxo de branches (R-FLUXO), variável de ambiente que solta um controle.

## Delta lido
- `tests/mutantes/v0478-fechar-checks.json` (FCK-M5, FCK-M6): o `de` de FCK-M5 agora casa só o laço dos exigidos (`falta_q="check obrigatório"`, `bin/forge-fechar:948`), sem ambiguidade com o laço novo (`:956`); FCK-M6 casa o texto novo do `die` do prazo (`o $falta_q $falta do head`, `:961`). O `forge-check parecer delta` marca o arquivo como fora do domínio, mas ele é a prova de mutante da guarda do merge e foi o objeto do A1: lido.
- `bin/forge-testes:218`: o mapa de `bin/forge-fechar` passa a listar `test_fechar_sem_auto`. Só acrescenta teste ao que roda quando o arquivo muda; não tira nenhum.
- `bin/forge-fechar`: sem mudança no delta (`git diff --stat f5143cea a34b33bf -- bin/forge-fechar` vazio). A leitura da rodada anterior (todo check-run do head, recusa de cópia velha, variável dupla, sem `--auto`) segue valendo sobre o mesmo código.

## Achados anteriores
- A1 (bloqueante): **fechado**. FCK-M5 morre em `bin/forge-fechar:948` e FCK-M6 em `:961` (`bin/forge-mutante tests/mutantes/v0478-fechar-checks.json --ids FCK-M5,FCK-M6` no head `a34b33bf`); `tests.test_forge_mutante.ConferirTodas` OK (4 testes).

## Direção da mudança
Por escrito: o delta **só aperta ou é neutro**. Os mutantes devolvem a prova da guarda "pendente não conta como verde" e "pendente no fim do prazo para, sem merge" (aperta); o mapa do `forge-testes` amplia os testes do arquivo tocado (aperta). Nenhum caminho que recusava passa a mesclar.

## Provas
- Testes dos arquivos tocados no head `a34b33bf`: `tests.test_testes_tocados`, `tests.test_fechar_sem_auto`, `tests.test_fechar_checks_do_head`, 220 testes OK (1 skip preexistente).
- Suíte inteira: CI do PR #855, execução 45413593544, sobre `c89d29eb` (mesma árvore de código de `a34b33bf`, só `docs/qa/` a mais): as dez partes da suíte, as baterias de passos e verificações longas, a instalação e o teto de pulados verdes; a única falha é `bateria (pareceres)`, pela falta de pareceres aprovados (R-REVIEW e R-SEGURANCA), que este parecer resolve no que toca à segurança.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e o `forge-mutante` local, sem rede além da leitura do CI. Varredura de segredo e SAST não se aplicam ao delta; as ferramentas de varredura não estão no PATH deste ambiente (lacuna registrada).
