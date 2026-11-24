---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: 4182040651ad42a57cd8d047c4684946efbf659d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478, G1.2 sozinho, volta por delta (E140.5)

Revalidação depois do merge da develop (216413c9) no head 41820406. A rodada anterior aprovou bdd44bc0 e fica no git (1a0cf4db, 7202a7a7).

Gatilhos: controles do Forge (`docs/regras/`), `PROTEGIDOS` (`bin/forge-check`).

## Delta lido
`forge-check parecer delta` (bdd44bc0..41820406, sem o que veio da base) aponta `bin/forge-check` e `bin/forge-testes` no domínio.
- `bin/forge-check:10652-10656` e `:10899-10900`: o subcomando `autorizacao gravar` e o `pedido_existe`. Vêm da develop (#810, G1.2a), com parecer próprio aprovado em `docs/security/v0479-sieg-g1-gravar.md`. Este item não tocou nessas linhas.
- `bin/forge-testes:160`: a resolução do merge mantém os dois nomes, `test_autorizacao_gravar` (develop) e `test_parecer_fora_do_delta` (branch). Nenhum teste saiu da lista.
- O patch da branch sobre a develop (`216413c9..41820406`) em `bin/`, `agents/`, `docs/regras/`, `skills/` e nos dois testes do item é igual, linha a linha, ao patch aprovado (`5cff9f6a..bdd44bc0`). A única diferença é a linha de `forge-testes` citada acima. O mecanismo do G1.2 não mudou e não mudou de lugar: `LARGURA_DA_FAIXA` em `:4121`, `parecer_anterior` em `:4129`, `trechos_do_delta` em `:4142` e `fora_do_delta` em `:4150`.

## Classificação
É a mesma da rodada anterior: **afrouxa**. Um bloqueante novo fora do delta, que não repete a rodada anterior, passa a ser recomendado e vira cartão. Na segurança, ele só bloqueia com `explorável: S<n>` e a sonda (`bin/forge-check:4150-4176`, `docs/regras/R-SEGURANCA.md`). É isso que o dono mandou no G1. O merge não aperta nem afrouxa mais nada. O risco residual de `parecer_anterior` continua igual e sem achado.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A branch está sem PR, e a suíte inteira fica para o CI do PR. Rodei localmente só os testes dos arquivos tocados, `test_parecer_fora_do_delta` e `test_testes_tocados`: 217 testes, OK, 1 pulado. Ferramentas usadas: git e o `forge-check` do head. Nenhuma varredura externa e nenhuma ferramenta instalada.
