---
tipo: revisao-devops
contrato: 1
pedido: ci-postinstall-cli
branch: melhoria/ci-postinstall-cli
commit: 84f9e3860f8e70521fd31b8e691187ee58e373ec
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-20
---
# Review de devops: ci-postinstall-cli

## Parecer
Aprovado. Revisor: outra instância do devops-engineer, distinta da autora do conserto (D-ETAPAS-INST). O diff de `.github/` contra a base 0f480c8 é uma linha, em `.github/workflows/ci.yml` (passo "Claude Code CLI"): o comando de instalação global do CLI, na versão 2.1.296, passa a ganhar a liberação de script só desse pacote.

Conferido:
- A versão continua fixa em 2.1.296 (sem `latest`), e a liberação de script libera o script de instalação só do pacote nomeado, que é o que baixa o binário nativo; nenhuma outra dependência ganha permissão de rodar script.
- Nenhum passo da bateria saiu nem ficou condicional: o diff não toca nenhuma outra linha, e o `if:` do passo é o mesmo (`!cancelled() && steps.gate.outputs.pesada == 'true'`). Nada de `continue-on-error`, `[skip ci]` ou teste pulado (`R-VERIFY`); `claude plugin validate . --strict` e `tests/e2e-instalacao.sh` seguem depois do passo.
- Permissões, ações fixadas por SHA, `concurrency` e `timeout-minutes` não mudam; a entrada é literal, sem interpolação de dado não confiável.
- Tempo: o mesmo pacote e a mesma versão, com o binário nativo agora de fato baixado (o run verde anterior já registrava 2 pacotes); a diferença é de segundos, sem passo novo. O job não cresce de forma mensurável.

Ferramentas: `actionlint`, `shellcheck` e `zizmor` não estão no PATH deste ambiente (lacuna registrada); a prova é a bateria do PR, que roda `actionlint` e `zizmor` no próprio CI. Não reproduzi a instalação localmente (sandbox sem o runner).

## Achados
(nenhum bloqueante)

## Custo e rollback
Custo: nenhum (`R-CUSTO`); runner gratuito, sem serviço, cache ou artefato novo, e minutos de CI iguais. Rollback: reverter o commit da linha em `ci.yml` (volta ao comando anterior). O workflow só vai ao remoto por quem tem o escopo, e a mudança em `.github/` exige o rótulo `afrouxa-regra` do dono no PR.
