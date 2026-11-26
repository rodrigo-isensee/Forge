---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/marca-0.47.19
commit: 9487d956120b90e783ef1462fcfe83c2b1df7230
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-26
---
# Review de segurança: marca da 0.47.19 (#905, v0481 E12.25; classe C)

Gatilhos: nenhum de código. A marca de release passa pela segurança por exigência do processo (classe C).

Neutro: a marca não muda código, hook, workflow nem regra. Só junta o texto do changelog e sobe a versão. Nada aperta e nada afrouxa.

## Escopo lido
Diff `cc4376fe..9487d956`: 13 arquivos. Três foram modificados (`.claude-plugin/plugin.json`, `dev/.claude-plugin/plugin.json` e `CHANGELOG.md`) e dez apagados, todos em `changelog.d/`. Nenhum arquivo de código, hook, workflow, teste ou agente foi tocado. A catraca da base (`cc4376fe`), rodada como no CI (script da base, cwd no head, `--base cc4376fe`), sai 0, sem violação nem aviso.

## Conferências
- **Release reproduzida:** num clone temporário em `cc4376fe`, `bin/forge-changelog release 0.47.19 2026-11-26` gera uma árvore cujo `git diff --cached 9487d956` é vazio (0 linhas). Os dez arquivos de `changelog.d/` apagados, o `CHANGELOG.md` e os dois `plugin.json` saem idênticos aos da marca.
- **Fragmentos:** os 10 fragmentos (`v0481-catraca-avisos`, `-ci-descendente-parecer`, `-copia-base-fechada`, `-d6-resto`, `-docs-ok`, `-fechar-dryrun-branch`, `-g4-f1-aviso`, `-limpar-clone-parecer`, `-pedido-arquiva` e `-perfil-fifo`, este com duas linhas) estão linha a linha na seção `## [0.47.19] - 2026-11-26` (`CHANGELOG.md:7-21`), cada um na seção `###` de origem: Adicionado 4, Alterado 2 e Corrigido 5. Em `changelog.d/` sobra só o `README.md`. `bin/forge-changelog conferir-release` dá `ok` e `tests.test_changelog` roda 91 testes, OK.
- **Versão:** `0.47.19` em `.claude-plugin/plugin.json:3` e em `dev/.claude-plugin/plugin.json:3` (ESCOPO+ E12.22), igual a `CHANGELOG.md:7`. A seção nova fica logo abaixo de `[Não publicado]` e acima da 0.47.18 (`CHANGELOG.md:23`). A `origin/main` está em `52dc3dcd`, com `0.47.18`.
- **Data:** o commit é de 2026-11-26T07:39:54-03:00. O dia local e o dia UTC são os dois 2026-11-26.
- **Corpo do #905:** a linha `teto: excedido, 522 linhas, marca de versão` está presente. Eu a reproduzi com as funções do próprio `forge-check`, como faz o `medir_a_marca` do `forge-fechar` (`origin/main...9487d956`, três pontos, base comum `b224ee09`): total 522, acima do teto, classe C. O corpo lista os três pareceres `release-0.47.19`. O corte com 10 itens, abaixo de 20, segue a ordem fixa do dono de 25/11 07:52 citada no corpo; o `forge-fechar --corte` ainda não a conhece (cartão AUTORIZACOES-FIXAS, E14.52), e os passos do V5 foram feitos à mão. O diff não toca `tests/config.json`, então o `teto_versao` e os configs não mudaram.
- **Segredos:** nenhum padrão de token, chave ou chave privada nas linhas acrescentadas.
- **CI do head `9487d956`:** runs 45803496622 (CI) e 45803496653 (Catraca), `headSha` conferido, os dois `success`. Todos os checks que contam estão em `pass`: as dez partes da suíte (3.12 e 3.14), `bateria`, `bateria (pareceres)`, `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `catraca`, `instalação`, os dois tetos de pulados e `árvore já provada na develop`. Nenhum vermelho. Os 7 jobs que só rodam em push na develop saíram pulados. O CI de push da develop em `cc4376fe` (run 45750622760) está verde.
- ci: 9487d956120b90e783ef1462fcfe83c2b1df7230 verde

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas ausentes do PATH: `gitleaks`, `osv-scanner`, `semgrep`, `zizmor`, `actionlint` e `trivy` (lacuna). O delta não toca workflow nem dependência, e a busca de segredos foi feita por padrões.
