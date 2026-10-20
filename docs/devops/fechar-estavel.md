---
tipo: revisao-devops
contrato: 1
pedido: fechar-estavel
branch: melhoria/fechar-estavel
commit: 6a1f2b3fee83ca24ea8ba1e24da2ea2f7e97ef0d
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-20
---
# Review de devops: fechar-estavel

## Parecer
Aprovado. A única mudança em `.github/` é uma linha em `.github/pull_request_template.md`; nenhum workflow, permissão ou segredo foi tocado. Ferramentas: `git diff` entre ef71b3c e 6a1f2b3, `bash -n bin/forge-fechar` (sintaxe ok). Faltaram no ambiente: `shellcheck` e `actionlint` (lacuna registrada; o CI do PR roda o shellcheck). Sem Dockerfile, compose ou IaC na entrega.

## Achados
(nenhum bloqueante)

## Detalhe dos achados
- Modelo de PR: o diff em `.github/` tem uma linha acrescentada, o item do rótulo `afrouxa-regra`, desmarcado (`- [ ]`). Não altera item existente. Não é afrouxamento de regra: só lembra o autor de pedir o rótulo ao dono (`R-CONFORMIDADE`).
- Pausa e repetição (`bin/forge-fechar`, `FORGE_FECHAR_PAUSA`): o script roda na máquina de quem fecha, não em runner; não há minuto de CI nem serviço cobrado (`R-CUSTO`). Cada operação repetível faz no máximo 3 tentativas com pausa padrão de 3 s (cerca de 6 s de espera no pior caso); o laço de checks do passo 4 conta no máximo 3 falhas seguidas de leitura e continua limitado por `espera`. Nenhum laço é infinito. Recomendação não bloqueante: `FORGE_FECHAR_PAUSA` não tem teto, mas a validação numérica já recusa valor inválido e o ajuste é do próprio usuário.
- Repetição só em operação idempotente (leituras e `push --delete` da limpeza). Push de código, criação de PR, `pr ready` e merge não se repetem; nada de `--force` nem `--no-verify` (`R-VERIFY`). Nada escreve na `main` (`R-MAIN`).

## O que esperar no PR
A catraca (`tests/catraca.py`) pede o rótulo `afrouxa-regra` do dono porque a mudança toca `.github/`. O tech-lead deve avisar o dono; o autor não aplica o rótulo. O fragmento `changelog.d/fechar-estavel.md` já existe e a versão não é alterada no PR.

## Custo e rollback
Custo: zero em minutos de CI e em recursos novos (`R-CUSTO`). Rollback: reverter o commit da branch (o item do modelo de PR e o script voltam ao estado anterior); não há migração nem estado externo.
