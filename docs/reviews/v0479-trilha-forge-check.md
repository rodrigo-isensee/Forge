---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-trilha-forge-check
commit: a318e97d9cc5012c3481e0027063c4646c559b40
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E91.2 (TRILHA-FORGE-CHECK)

Escopo: 0f4a8221, 6dfb2bde e a318e97d sobre 15936278; 41 linhas em `bin/forge-check` (H1 dentro do teto), um comportamento por commit.

## Achados
- A1 (recomendado) tests/mutantes/v0479-trilha-forge-check-2.json:6 · ids M1..M6 repetem os da spec 1; `forge-mutante` com as duas recusa ("id de mutante repetido entre as specs"). A convenção das `-2` segue a numeração (aq1-forge-check-2: M9..); renumere para M7..M12.
- A2 (recomendado) bin/forge-check:9455 · o PQ novo `forge-check pr v0478 --previo --base develop`, rodado neste clone após o commit do parecer e `git fetch`, sai rc=1 só por 34 `parecer conferido` de commits que o clone não tem (VOLTAS-REVISOR-WT, anterior ao diff); a espera rc=0 não se cumpre no v0478.

## Parecer
Aprovado. As três escolhas do autor se sustentam:

- (a) `--previo` no PQ do K-156: certo. O portão roda o PQ logo depois do próprio commit, com os outros pareceres em paralelo (Z10) ainda ausentes; sem `--previo`, a ausência deles reprovaria todo portão. No `--previo` só a ausência vira aviso; desatualizado, reprovado, forma, `pedido:` e blob do próprio parecer seguem violação (`cmd_pr`), e o `--previo` não grava o resultado para o hook `parecer` (`executar`, `gravar`). O `pr` acha o parecer pelo `pedido:` do frontmatter, então `pr v0478` alcança `docs/reviews/<branch>.md`.
- (b) K-166 recusar: certo. Segue o padrão das `ETAPAS_QUE_RECUSAM`; aviso no stderr do `brief gerar` não chega ao brief selado e seria ignorado. A volta (`--volta`) sai antes da guarda, então não é barrada. Custo medido: `etapas_conferidas` no v0478 real (2723 linhas de Histórico, 491 conferidas) leva 2,8 s por geração, aceitável.
- (c) K-252 só o texto da etapa: certo. No `brief gerar`, o escopo declarado ainda é `PREENCHER`; o texto da etapa é a única fonte legível. A substring `.githooks/` casa com a guarda real (`hooks/conformidade.py:63`, `\.githooks` sem âncora, inclui `templates/projeto/.githooks/`); o falso negativo (etapa que não cita a pasta) cai no bloqueio do próprio hook, que é a trava; a linha é só orientação.

Specs realinhadas: z075 M3 troca o `de` para `"--merge-base", base, ...`; o teste citado roda sem `--base` (padrão `origin/develop`) e o mutante HEAD~1 morre (`forge-mutante ... --ids M3`: "M3 · morreu · bin/forge-check:408"); o modo `--base` novo tem os próprios mutantes (spec -2, M1 a M5). aq1-forge-check M7 não mudou no diff e o trecho segue único (linha 4201; a linha nova do K-166 não tem o `)` final). Nenhuma enfraqueceu.

Verificação: testes da trilha e dos que leem as funções mudadas (test_trilha_forge_check, DocsEstritoNoDelta, test_citacao, VoltaComRecomendacao, test_pre_envio_brief): 63 OK. Mutantes das duas specs, rodadas separadas: 12 de 12 morreram. `forge-mutante --cobertura --base 15936278`: toda guarda do diff coberta; `--conferir`: trechos no lugar. Suíte completa: CI do PR.
