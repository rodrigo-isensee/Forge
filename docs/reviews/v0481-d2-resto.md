---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d2-resto
commit: f1d048fb8051ee5c7a6d152ccc767e6794ea37a6
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0481 (E11.14, #881, D2 `forge-check pronto`, revisão por delta da volta E11.13; classe C)

Delta revisado: `ec5c7040a..f1d048fb8`, a volta única E11.13. São 25 linhas de código a mais e 15 a menos (`bin/forge-check` 5/3, `bin/forge_pronto.py` 20/12), além do teste, das specs e do fragmento. O total da branch continua abaixo do teto H1. Parecer anterior: aprovado em `ec5c7040` com o recomendado A1. O `forge-check parecer delta` pediu nova revisão (`revalida: sim`, `bin/forge-check` mudou), e esta revisão lê só o delta.

## O que foi conferido
- **A1 do parecer anterior foi resolvido.** O `cmd_pronto` agora guarda o `motivo` do `pr_da_branch` e o repassa como `sem_corpo`. Com o gh em erro e sem `--corpo`, a linha do corpo diz `não verificável (<motivo>)` e o resultado é 2. Sem PR, o `pr_da_branch` devolve `({}, None)`: o motivo fica None e o resultado segue 1 ("corpo do PR não conferido"). O PR fechado também segue 1. Com `--corpo`, o motivo nunca é lido.
- **O rc 2 nunca chega ao 0.** O `conferir` devolve `1 if reprovadas else 2 if nao_verificaveis else 0`. O passo que sai 2, inclusive o comando que não abre (o `rodar` devolve 2), vai para `nao_verificaveis`. Qualquer outro código diferente de 0 continua reprovado. Quando há reprovação e não verificável juntos, vence o reprovado (1). O pr-texto da catraca com rc 2 dentro do `tamanho_e_corpo` continua reprovando, o que é o lado mais conservador.
- **Nenhuma checagem foi afrouxada.** O que antes saía 1 por um passo com rc 2 agora sai 2, e o 2 também não passa. O `--help` do subcomando já anunciava "2 não verificável", e o docstring e o fragmento agora dizem o mesmo.
- **Mutantes.** Ids únicos de M1 a M27 nas quatro specs: `-1` tem M1 a M8, `-2` tem M9 a M16, `-3` tem M17, M18, M26 e M27, e `-4` tem M19 a M25. `python3 -I bin/forge-mutante --processos 1` sobre as quatro specs, numa chamada só: 27 de 27 morreram, rc 0. `--cobertura --base ec5c7040a`: rc 0, e toda guarda mudada tem mutante (linhas 58, 62, 63, 64, 74 e 76 do `forge_pronto.py`).
- **Testes (checklist 7, 11, 12).** `python3 -m unittest tests.test_forge_pronto`: 19 OK. Cada ramo novo tem teste de comportamento: passo que sai 2, reprovado que vence, gh em erro sem corpo (com o teto não chamado) e motivo com corpo dado (o teto é conferido). O teste de ponta a ponta usa o gh falso com o nome exato e sai 1, e a mensagem confere o motivo que chega. O rc 2 de ponta a ponta fica provado no `Agregador` e pelo M22.
- **CI:** não rerrodei a suíte. No #881, head `f1d048fb`, a suíte estava pendente, e a `catraca` e a `bateria (pareceres)` estavam vermelhas à espera dos pareceres deste head. O merge depende do CI verde.

## Sondas
- S1 · conferir, passo ok, corpo None, sem_corpo "gh sem rede ou sem acesso" · espera: 2 · obtido: 2, "não verificável em tamanho e corpo do PR"
- S2 · passo sai 2, corpo ok · espera: 2 · obtido: 2
- S3 · um passo sai 2 e outro sai 1 · espera: 1 · obtido: 1, "reprovado em b"
- S4 · sem PR (corpo None, motivo None) · espera: 1 · obtido: 1
- S5 · gh em erro sem corpo e passo que sai 5 · espera: 1 · obtido: 1
- S6 · passo sai 2 e o teto reprova · espera: 1 · obtido: 1
- S7 · comando que não abre · espera: 2 · obtido: 2

## Parecer
Aprovado. A volta faz o que o A1 pedia e nada além disso. O não verificável sai 2 com o motivo, reprovado continua 1, e só sai 0 com tudo passando. Os ids dos mutantes estão únicos, e os 27 morreram numa rodada só.
