---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-teto-fora-desenho
commit: a660a3182eaef7eb7dd64efe30bde1381b2339ce
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 · desenho TETO-FORA-DO-GIT, 2ª volta (E159.6, PR #842)

Review por delta do head a660a318 (2ª volta E159.5), base develop 789fc141. Delta lido por `forge-check parecer delta docs/reviews/v0480-teto-fora-desenho.md`: intervalo `604f8c56..a660a318`, no domínio só `docs/propostas/teto-fora-do-git.md` (9 linhas a mais, 8 a menos). Classe T, só texto: sem código, guarda nem mutante. Testes dos arquivos tocados: `test_clareza` e `test_changelog`, 100 testes, OK; a suíte inteira fica no CI do PR. Instância que não escreveu a volta. Decisões do dono conferidas em `docs/pedidos/v0478.md` ("b: o teto vai para um arquivo fora do controle de versão"; "a, com cartão para provar no sandbox real", citado em :90).

## Achados
- A7 (recomendado) docs/propostas/teto-fora-do-git.md:40 · "na cópia principal e na worktree vinculada, o mesmo que o hook lê; noutra pasta, um arquivo que o hook não lê" omite o clone em `.forge/wt/<item>`, que pelo corte de :38 e pela C1 (h) de :49 também grava na cópia principal; a medida (2) de :68 omite a worktree vinculada. Alinhe as três listas.

## Sondas
- S2 · `diretorio_comum(<este clone em ~/.forge-contrib/wt>)` no head a660a318 · espera: o `.git` do próprio clone, pela :38 nova (valor informativo) · obtido: `/workspaces/.forge-contrib/wt/v0480-teto-fora-desenho-rev/.git`
- S3 · `diretorio_comum(<s>/wt)`, `wt/.git` = `gitdir: <s>/evil/.git/worktrees/w`, `gitdir` de volta e `commondir` `../..` · espera: `<s>/evil/.git`, pelo caso de abuso de :80 · obtido: `<s>/evil/.git`
- S4 · `diretorio_comum("/workspaces/Forge")` (a raiz da sessão, âncora do hook) · espera: `/workspaces/Forge/.git` · obtido: `/workspaces/Forge/.git`

## Conferência pedida no brief
- **A5 (clone):** fechado. A linha falsa saiu; :38 diz que o clone fora de `.forge/wt/` tem o `.git` próprio e lê outro arquivo, e o S2 rodado de novo dá exatamente isso. O clone dentro de `.forge/wt/` é tratado pelo corte do caminho, como o `bin/forge-copia:36-45`, e a C1 (h) pede a prova.
- **A6 (`.git` forjado coerente):** fechado. :80 descreve o S3 como caso de abuso com o resultado que a sonda dá (o script lê `<x>/.forge/limites.json`), e o valor do script é rebaixado a informativo (:40, C1 (j)); quem barra é o hook pela `raiz_declarada()` (:37). Conferi a âncora do hook: o `.git` da raiz, pasta ou arquivo de worktree, é recusado a escrita para todo papel (`hooks/conformidade.json:40` e `:43`), então o subagente não forja o `.git` da raiz da sessão; S4 confirma a leitura na raiz.
- **C1 e medida (2):** reescritos de acordo: (d) restrito ao hook, (f) restrito à cópia principal, (h) cobre worktree e clone em `.forge/wt/`, (j) novo; a medida (2) tira de fora as outras pastas.

## Parecer
Aprovado. A 2ª volta fecha A5 e A6 pelo caminho sugerido no parecer anterior (scripts informativos, hook como autoridade), e as sondas S2 e S3 rodadas de novo batem com o texto novo. O A7 é de consistência de texto e vira cartão.
