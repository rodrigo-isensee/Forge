---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-release-04716-anexo
commit: 51fc24a74534d3ba419d2f7f08c9ae307aa07347
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (anexo da 0.47.16, E167.9)

Escopo: `git diff --name-status 5f1c6e97 51fc24a7` toca 12 arquivos, só metadado de versão: `CHANGELOG.md` (12 linhas novas na seção `[0.47.16]`, nenhuma removida) e a remoção dos 11 fragmentos `changelog.d/v0480-*.md` juntados (#805, #812, #839, #843, #844, #845, #846, #847, #848, #851, #853). Nenhum código, hook, `bin/`, `scripts/`, `.githooks/`, `.github/`, teste, `tests/config.json` nem manifesto; os dois `plugin.json` seguem em `0.47.16`.

Gatilhos: nenhum

## Detalhe dos achados
Sem achados.

- **Leitura.** As 12 linhas novas são texto que descreve itens já revisados na origem (conferência de cada um em `docs/security/release-0.47.16.md`); sem segredo (busca por padrões de token e chave nas linhas novas: 0) nem comando novo. As duas linhas que afrouxam regra dizem isso no próprio texto: o hook `ordens` ("afrouxa o item 1" da ADR 0003) e a revalidação só no delta (bloqueante novo fora do delta vira recomendado e cartão).
- **Conferência.** `bin/forge-changelog conferir-release`: `ok: changelog.d/ sem fragmentos pendentes`; `python3 -m unittest tests.test_changelog`: 91 testes, OK.

## Riscos aceitos e ferramentas
Sem riscos aceitos. Revisão estática com git. gitleaks, osv-scanner, semgrep, zizmor e actionlint fora do PATH (lacuna registrada; o diff é só texto de versão, lido por inteiro). Suíte não rodada localmente (o brief pede só os testes dos arquivos tocados); vale o CI do PR de promoção.
