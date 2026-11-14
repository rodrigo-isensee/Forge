---
tipo: revisao-devops
contrato: 1
pedido: v047
branch: melhoria/v047-integracao-em-lote
commit: c6b0b788c2815bbdf130a43d2a47eb2bbe6818ed
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-14
---
# Review de devops: v047 (integracao-em-lote, E1.240)

## Achados

## Detalhes
Aprovado. O intervalo origin/develop...c6b0b788 não toca `.github/`, `Dockerfile*`, `compose*` nem IaC; o parecer cobre a mecânica de entrega em `bin/forge-fechar` (espera do CI da develop, `--lote`, `--promover`).
- R-MAIN: `--promover` fixa a base em `homolog` e o merge automático (`--auto --merge --match-head-commit`) só vale para o PR da homolog; a `main` segue só com o dono. A mensagem final apenas imprime o comando do tech-lead.
- R-VERIFY: nenhum `--force`, `--no-verify` nem check ignorado; CI cancelado ou vermelho para o fluxo (código 5), exceto o cancelado na promoção, que avisa e deixa o CI do PR decidir.
- R-CONFORMIDADE: nada altera proteção de branch, rulesets ou segredos; só `gh pr merge`, `gh run list` e push/delete de `promocao/<versão>`.
- R-CUSTO: sem runner, serviço ou artefato novos; a espera usa `gh run list` (leituras), sem minutos de CI adicionais.
- Reversão do lote impressa com os merges em ordem inversa; a lista termina em espaço, então `&&` fica separado.
- Ferramentas: `shellcheck bin/forge-fechar` rc=0. `actionlint` ausente do PATH (sem workflow no intervalo, sem efeito).

## Custo e rollback
Sem minutos de CI nem recursos novos (`R-CUSTO`). Volta: reverter os commits da branch na `develop` (`git revert`); o script não cria estado fora do ramo `promocao/<versão>`, apagado ao fim.
