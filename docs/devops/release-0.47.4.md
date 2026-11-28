---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.4
branch: melhoria/v0474-release-0474
commit: f198cfbd8261eb15acee8adbb95709484f524097
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-17
---
# Review de devops: release-0.47.4

## Achados

## Detalhes
Aprovado. Entre a v0.47.3 (que é a `main`, `cacbdf06`) e este head, `.github/` muda só em `ci.yml` (`git diff --stat v0.47.3 HEAD -- .github/`: 1 arquivo, 190 inserções, 35 remoções, vindas do #615, E2.270 e E2.489). `release.yml`, `catraca.yml` e `dependabot.yml` não mudam. Não há mudança em `Dockerfile*`, `compose*` nem IaC.

- Mudança no `ci.yml`: a suíte passa de 3 para 5 partes por Python (matriz `parte: [1, 2, 3, 4, 5]`, `--parte "$PARTE/5"`). Na develop, a checagem rápida vira 5 partes por Python, com teto de pulados em job próprio e os agregadores `rapida` e `rapida-quatorze` de nome fixo. Entra o passo `scripts/falhas-no-resumo.py` (`python3 -I`, só informação no resumo, sem rede). `set -o pipefail` mantém o status da suíte atrás do `tee`.
- Segurança do pipeline: `permissions: contents: read` nos jobs novos; ações novas fixadas por SHA com a tag em comentário; sem `pull_request_target`, sem segredo novo; `timeout-minutes` em todos os jobs (18 ocorrências no arquivo; 15 nas partes, 5 nos agregadores e nos tetos). Os agregadores `rapida*` usam `always()` e só leem `needs.*.result`, sem checkout nem código da branch, e exigem `success` nas partes e no teto (pulado ou cancelado reprova; J11). O download de artefatos é só do run corrente, com `retention-days: 1`.
- Sem `continue-on-error`, `[skip ci]` ou check afrouxado (grep no `.github/workflows/`) (R-VERIFY).
- Checks exigidos: os nomes dos jobs de parte mudam de "parte K/3" para "parte K/5". Os agregadores (`bateria`, `bateria (python 3.14)`, `checagem rápida (push na develop)` e a versão 3.14) mantêm o nome. Se a proteção de branch exige algum check de parte pelo nome, o dono precisa ajustar (R-CONFORMIDADE); não alterei nada por `gh api`.
- Promoção: `main` está na v0.47.3 e `homolog` e `develop` estão adiante. A versão dos manifestos é 0.47.4 e a entrada `[0.47.4]` está no topo do `CHANGELOG.md`, abaixo de `[Não publicado]` vazio. A promoção segue develop, homolog, main pelo `tech-lead`, e o merge na `main` é do dono (R-FLUXO, R-MAIN).
- `release.yml`: dispara em push na `main`; o job `testes` tem `contents: read`; o job que publica tem `needs: testes` e `contents: write` só para tag e release. Ele cria `v0.47.4` apenas se a tag ainda não existir, com as notas do `CHANGELOG.md`, depois do merge do dono. Nenhum workflow escreve na `main` antes disso.
- Ferramentas: `git diff`, `grep`; `actionlint` e `shellcheck` não estão no PATH, lacuna registrada. A validade do YAML fica com o CI do PR.

## Custo e rollback
Sem recurso pago novo (R-CUSTO). O CI roda mais jobs mais curtos em paralelo (5 partes por Python), então os minutos totais sobem um pouco; medir na checagem de tempo da release (`gh run list`). Volta: reverter o commit de versão na `develop` antes da promoção; depois da release, reimplantar a tag anterior (v0.47.3).

O Revisar-sha passou de 2539b54f (que só tem parecer) para f198cfbd (commit da versão); o conteúdo revisado é o mesmo.
