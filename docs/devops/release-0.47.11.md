---
tipo: revisao-devops
contrato: 1
pedido: release-0.47.11
branch: melhoria/v0479-release-04711
commit: 45b77250141751c88bac5fd7e4b5f3b109256748
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-20
---
# Review de devops: release 0.47.11 inteira (v0478, E42.5)

Head `fe752d14` (marca da 0.47.11 sobre a develop em `119aed79`). Cobre `git diff v0.47.10..fe752d14` (24 arquivos) e a junção dos itens (`META85` e a sonda S1 do relógio), cada um já integrado com os próprios pareceres.

Aprovado, sem achados. Nada em `.github/`, `Dockerfile*`, `compose*` ou IaC mudou: o gatilho de devops não se aplica ao conteúdo; o parecer cobre a mecânica da release.

## Detalhes
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em `"version": "0.47.11"`; `.claude-plugin/marketplace.json` não tem campo de versão. `origin/main` está em 0.47.10 (a versão sobe).
- CHANGELOG: `[Não publicado]` vazio; uma entrada `## [0.47.11] - 2026-11-20` em português (Adicionado, Corrigido) acima da `[0.47.10]`.
- `changelog.d/` só com `README.md`: os dois fragmentos foram apagados no commit da marca (`bin/forge-changelog conferir-release`: ok).
- Delta da marca: `git diff --name-only HEAD~1 HEAD` lista só os dois manifestos, `CHANGELOG.md` e os dois fragmentos removidos.
- Promoção: `scripts/promover-homolog.py --conferir-ref fe752d14857633363b9da383eeeb9321ff67b7fe` (o passo 1c do `bin/forge-fechar`) reconhece a marca: `versão: homolog 0.47.10 | develop 0.47.11`, `CHANGELOG: entrada [0.47.11] presente, [Não publicado] vazio, changelog.d/ sem fragmentos`, `pareceres: 6 arquivo(s) da promoção, todos aprovados`. Ele sai com falha só por motivos que não são da mecânica da marca e se resolvem no fluxo: faltam os pareceres de review, QA e segurança do pedido `release-0.47.11` (este devops é o meu) e o teto de tamanho.
- Teto para o corpo do PR: a ferramenta calcula 155 linhas de código na leva, acima de 150; o corpo do PR `homolog` -> `main` (do `tech-lead`) leva `teto: excedido, 155 linhas, <motivo>` com essa contagem exata.
- Suíte: a local falha por ambiente (sandbox: `/proc` e `gh`); a prova é o check-run `bateria` do CI do PR no mesmo sha (não é achado).
- Ferramentas: `actionlint`, `shellcheck` e `docker build` sem objeto (nenhum arquivo de pipeline ou container mudou).

## Custo e rollback
Nenhum minuto de CI novo além do run do PR; nenhum recurso novo (`R-CUSTO`). Rollback: reimplantar a tag `v0.47.10`; a versão não traz migração.

## Revalidação (head 45b77250, delta a14d6c80..45b77250)
Entrou a quarentena da sonda S1 (#708) pela `develop`, mais a marca atualizada (`chore(release): inclui a quarentena da S1 (#708)`). Continua aprovado, sem achados.
- Delta: 14 arquivos (`CHANGELOG.md` com 2 linhas em Corrigido, `tests/config.json`, `tests/quarentenas.py`, `tests/test_catraca.py`, `tests/test_hooks.py`, mutantes e pareceres do #708). Nada em `.github/`, `Dockerfile*`, `compose*` nem IaC. `forge-check parecer delta docs/devops/release-0.47.11.md` (fe752d14..45b77250): "delta: nenhum arquivo do domínio mudou" (o `tests/config.json` veio da base, `develop`, com os pareceres do #708).
- `tests/config.json`: `teto_pulados` de 1 para 2 (única linha), com o teste `TetoDaQuarentena` que reprova se o teto passar de 1 mais as quarentenas abertas; a mesma entrada do CHANGELOG manda devolver a 1 no PR que tirar a quarentena. É afrouxamento declarado e com decisão do dono de 19/11; não é defeito de pipeline e não cria custo (`R-CUSTO`).
- Versão: `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.47.11; `## [0.47.11] - 2026-11-20` em português, `[Não publicado]` vazio; `changelog.d/` só com `README.md` (`bin/forge-changelog conferir-release`: ok).
- `scripts/promover-homolog.py --conferir-ref 45b77250141751c88bac5fd7e4b5f3b109256748`: `versão: homolog 0.47.10 | develop 0.47.11`, `CHANGELOG: entrada [0.47.11] presente`, `pareceres: 17 arquivo(s) da promoção, todos aprovados`. Pendências fora do devops: pareceres de review, QA e segurança de `release-0.47.11` desatualizados por `tests/config.json` (cada papel revalida o seu) e o teto de tamanho.
- Teto para o corpo do PR: a contagem **não mudou**, segue 155 linhas de código na leva; o corpo leva `teto: excedido, 155 linhas, <motivo>`.
- Suíte: a local falha por ambiente (sandbox: `/proc` e `gh`); a prova é o check-run `bateria` do CI do PR no mesmo sha.
