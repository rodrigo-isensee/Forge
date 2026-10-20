---
tipo: review
contrato: 1
pedido: release-0.26.0
branch: melhoria/release-0.26.0
commit: 998fdd5115212ef7ad892c0874574d859f60703c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-20
---
# Review: release 0.26.0

Escopo: fechamento da versão `a4d2eac..998fdd5` (base a4d2eac72109c51fbad75252986182e8f98bee1f) e a leva `74e5bb7..a4d2eac` (#242 a #245). O revisor não é o autor do fechamento (D-ETAPAS-INST). Conferência feita só com git e `gh pr view`, sem trocar o HEAD da worktree.

Veredito sobre `998fdd5`: **APROVADO**, sem achados que bloqueiem.

## Achados

## O que foi conferido
1. **Versão.** `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` passam de 0.25.0 para 0.26.0; minor, conforme o SemVer do `CLAUDE.md` (nenhuma entrega quebra os projetos).
2. **Arquivos do fechamento.** `git diff --stat a4d2eac 998fdd5`: 7 arquivos, os dois `plugin.json`, o `CHANGELOG.md` e a remoção dos quatro fragmentos (`changelog.d/s-16.md`, `fechar-estavel.md`, `catraca-endurecer.md`, `conf-correcao.md`). Nenhum outro arquivo mudou.
3. **Seção [0.26.0].** Entrada `## [0.26.0] - 2026-10-20` logo abaixo de `## [Não publicado]` (que fica vazia), com as quatro entregas: três em `### Alterado` (CATRACA-ENDURECER, CONF-CORRECAO, S-16) e uma em `### Corrigido` (FECHAR-ESTAVEL). Comparei linha a linha com os fragmentos apagados: o texto de cada um entrou byte a byte, sem perda.
4. **Pareceres da leva.** Review (`docs/reviews/`) e QA (`docs/qa/`) de S-16 (`eb16bb2`), FECHAR-ESTAVEL (`6a1f2b3`), CATRACA-ENDURECER (`fb5028e`) e CONF-CORRECAO (`568757c`) estão com `parecer: aprovado`, e nenhum traz linha `(bloqueante)` em `## Achados`. CATRACA-ENDURECER e CONF-CORRECAO tiveram uma volta (review reprovado, depois revalidação por delta aprovada sobre o commit citado). Segurança das quatro e devops de S-16 e FECHAR-ESTAVEL presentes em `docs/security/` e `docs/devops/`; o parecer de cada um é do respectivo papel (E2.2, E2.3), não refeito aqui.
5. **#244 e #245: o que mudou depois do parecer.** Os dois PRs terminam num merge da develop (`1f2b66a` e `73313ae`, segundo pai `bd8b696`, o #243), posterior ao commit revisado.
   - #244: `git log --no-merges fb5028e..1f2b66a` traz só o #243 (`bd8b696`) da develop; os arquivos fora de `docs/(reviews|security|qa)/` alterados depois do parecer são só os do #243 (`.github/pull_request_template.md`, `bin/forge-fechar`, `changelog.d/fechar-estavel.md`, `docs/devops/fechar-estavel.md`, `docs/fechamento-integrador.md`, `tests/test_fechar.py`).
   - #245: o commit revisado tem base `74e5bb7`, então o merge trouxe o #242 (`ef71b3c`) e o #243 (`bd8b696`); além dos arquivos do #243, mudaram depois do parecer os do #242 (`changelog.d/s-16.md`, `docs/adr/0008-governanca-de-contribuicoes.md`, `tests/catraca.py`, `tests/test_catraca.py`). Ver R1.
   - Nos dois, nenhum arquivo do próprio PR mudou entre o commit revisado e o head, salvo os próprios pareceres (`docs/reviews/` e `docs/security/` da revalidação); não há interseção entre os arquivos do PR e os que vieram da develop, logo o patch revisado é o mesmo (`commit_vale`). O tree do head do #245 é idêntico ao do squash `7556bca`.
6. **#242 e #243, por completude.** #243: nada fora dos pareceres mudou entre `6a1f2b3` e o head `f167487`. #242: os arquivos do PR não mudaram entre `eb16bb2` e o head `71de242`; o que mudou veio da develop (#234 a #239, já na 0.25.0).
7. **Regras.** R-NEUTRO, R-CUSTO e R-VERIFY: o fechamento só toca versão e changelog, sem custo nem termo de projeto. ADR 0006: fragmentos juntados pela release e apagados.

## Detalhe dos achados
- R1 (recomendado, não bloqueia) · O brief afirma que, nos #244 e #245, os arquivos que mudaram depois do parecer são só os do #243. Vale para o #244; no #245 vieram também os do #242. O efeito é nulo (nenhum arquivo do #245 se sobrepõe aos do #242, e o #242 tem seus próprios pareceres aprovados), mas a premissa do brief estava incompleta; quem escreve o brief da próxima release confere a base do commit revisado de cada PR com `git merge-base`.
