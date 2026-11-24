---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: 14c7e31ede621eff8a7b3d3f63044f05bb9ab115
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478, G1.2 sozinho, volta por delta (E140.22)

Revalidação no head ca6cf392. O código revisado é o 14c7e31e, que é o head sem os commits de parecer. A rodada anterior aprovou 55a57bde e fica no git (df05b806).

Gatilhos: controles do Forge (`docs/regras/`), `PROTEGIDOS` (`bin/forge-check`).

## Delta lido
`forge-check parecer delta` cobre 55a57bde..ca6cf392. No domínio, só `tests/test_parecer_fora_do_delta.py` mudou. O resto do intervalo são pareceres (`docs/{qa,reviews,security}/v0480-g1-2-delta.md`). Depois de 14c7e31e, só `docs/reviews/v0480-g1-2-delta.md` mudou. O `bin/forge-check` continua igual ao da rodada anterior.
- `tests/test_parecer_fora_do_delta.py:101-103`: `test_recomendado_fora_do_delta_passa` agora põe o bloqueante repetido A1 ao lado do recomendado A2. Antes, o parecer sem bloqueante saía na guarda de `bin/forge-check:4182-4183` e o laço de `:4191-4205` nem rodava. Agora o laço chega ao recomendado, e o teste confere que ele não é recusado. A asserção continua `[]` e nenhum caso foi removido nem afrouxado.

## Classificação
O delta **só aperta**. A sonda local trabalhou numa cópia em `$TMPDIR` do `bin` e do `tests` de ca6cf392. Ela tirou a condição `a["gravidade"] != "bloqueante"` do laço de `fora_do_delta`, o que faz o recomendado fora do delta ser recusado. Com esse mutante, o teste novo falha (`FAILED (failures=1)`), e o teste de 55a57bde passa (`OK`). O código de produção não mudou, e nenhum caminho de ataque novo surge. A classificação do item inteiro continua a da rodada anterior: afrouxa, por ordem do dono, no G1.2. Achados anteriores: nenhum.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A branch está sem PR, e a suíte inteira fica para o CI. Rodei localmente só o arquivo tocado, `tests.test_parecer_fora_do_delta`: 29 testes, OK. Ferramentas usadas: git, o `forge-check` do head e uma sonda de mutação local, que só leu numa cópia temporária. Não fiz varredura externa nem instalei ferramenta.
