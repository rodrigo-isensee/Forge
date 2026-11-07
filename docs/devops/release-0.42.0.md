---
tipo: revisao-devops
contrato: 1
pedido: release-0.42.0
branch: melhoria/release-0.42.0
commit: 7a189d413dce70cf200d74f0a4a29d97fd2d704c
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-07
---
# Review de devops: release-0.42.0 (main a74c752 até 7a189d4)

## Parecer
Aprovado, sem achado bloqueante. Escopo lido: `git diff a74c752 7a189d4` nos arquivos de pipeline, hook de envio e scripts de mecânica (224 arquivos na leva; o resto é código de portão, agentes, skills, testes e docs, fora do foco de devops). Não sou autor de nenhuma parte da leva. O lote 0.35 a 0.42 já tem parecer de devops em `docs/devops/uniao-035-042.md` (develop, head 9e87a91); aqui confirmo que o delta de pipeline da leva é o mesmo e que o commit de release 7a189d4 só soma CHANGELOG, manifestos e remoção de fragmentos.

Superfície: `.github/workflows/` não muda; não há `Dockerfile*`, `compose*`, IaC nem `dependabot.yml` no diff. `.github/` muda só em `.github/pull_request_template.md` (+3 linhas: campo `Rótulo:` e comentário HTML). Manifesto conferido: `.claude-plugin/plugin.json` em 0.42.0.

## Achados
- A1 (recomendado) .github/pull_request_template.md:20 · a leva toca `.github/`; o PR da promoção precisa do rótulo `afrouxa-regra` do dono (catraca) e o corpo do PR `homolog` → `main` traz a saída de `tests/catraca.py --modo rotulados` (skill `ci-cd`, ADR 0008). Avisar o `tech-lead`; não bloqueia.
- A2 (recomendado) .githooks/pre-push:183-205 · `segredo_no_delta` e `ja_no_remoto` leem o script de segredo de `origin/develop`, com falha fechada na recusa; o pulo da suíte vale só para branch já no remoto, nunca para `main`, `homolog`, `develop`, tag ou ref nova. Não afrouxa; conforme.
- A3 (recomendado) scripts/verificar-contribuicao.sh:35-38 · `--no-color` nos `git diff` e marca `forge:ponta` (:6); só endurece o parse. Enquanto a develop não tiver a versão nova, o hook usa a antiga e varre só o HEAD; some após o merge · informativo.
- A4 (recomendado) scripts/arvore-testada.py:1 · este e `scripts/conferir-promocao.py` e `scripts/placar-mutacao.py` são scripts novos de apoio à promoção e à mutação; a lógica de portão é coberta pela suíte e pelos pareceres do tech-lead e do QA · informativo.

## Ferramentas
`shellcheck` rodou em `.githooks/pre-push` e `scripts/verificar-contribuicao.sh`, sem achados. `actionlint` ausente do PATH (lacuna registrada; nenhum workflow muda). `docker build` não se aplica. Nenhum teste rodado nesta etapa (o push de 7a189d4 rodou 1190 testes afetados, OK, 26 pulados).

## Custo e rollback
Sem minutos de CI novos nem recurso pago (`R-CUSTO`): nenhum workflow muda. Rollback: reverter o merge da release na `develop` (`git revert`) e, se já na `main`, reimplantar a tag anterior (v0.34.0); hooks, scripts e manifestos são arquivos versionados, sem migração nem estado fora do repositório.
