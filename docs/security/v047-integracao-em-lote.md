---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-integracao-em-lote
commit: 13cb874d23ef51f505f3dfcb3248c78c6ffea22c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (lote do forge-fechar: INTEGRACAO-EM-LOTE, RELEASE-EM-1H, FECHAR-ESPERA-CI-DEVELOP)

## Gatilhos
`R-SEGURANCA`: controle de integração e de promoção (`bin/forge-fechar`), o passo "Nada pula degrau" do CI (`R-FLUXO`), a catraca (`tests/catraca.py`) e o `scripts/arvore-testada.py` (pulo da suíte). Revalidação por delta `c6b0b788..13cb874d` (`forge-check parecer delta`): no domínio, `.github/workflows/ci.yml`, `bin/forge-fechar`, `scripts/arvore-testada.py`, `tests/catraca.py` e os testes de controle `tests/test_catraca_promocao.py`, `tests/test_fechar.py`, `tests/test_fechar_lote.py`.

## Achados

## Sondas

## Detalhe dos achados
Os três achados da rodada anterior (parecer em `c6b0b788`) estão resolvidos no head `13cb874d`.

**A1 (era bloqueante): resolvido.** O passo "Nada pula degrau" (`.github/workflows/ci.yml:506-520`) passou a rodar o modo `degrau` da catraca a partir de uma worktree de `refs/remotes/origin/develop` (`python3 -I`, o código da develop protegida, nunca o do PR), com `HEAD_SHA`, `HEAD_REPO` e `BASE_REPO` vindos do evento. Para PR com base `homolog` ou `main`, o passo `Gate` só deixa de rodar a bateria pesada com base `develop` (`ci.yml:451`), então nenhum código da branch roda antes do degrau nesses PRs; o checkout com `fetch-depth: 0` traz a develop e o head. A tabela única `PROMOCOES` (`tests/catraca.py:1530-1532`) aceita `develop` e `promocao/X.Y.Z` (`re.fullmatch`, dígitos ASCII) para a `homolog` e só `homolog` para a `main`; a linha de `promocao/` exige o sha do head ancestral da develop do servidor (`git merge-base --is-ancestor --end-of-options`), e `violacoes_do_degrau` exige o head do próprio repositório, falhando fechado com `BASE_REPO` vazio. `eh_promocao`, o modo `pareceres` e o `scripts/arvore-testada.py` leem a mesma tabela; no `arvore-testada`, falha ao carregar a catraca sai com rc diferente de 0 e a suíte roda inteira (falha fechada). No `bin/forge-fechar`, a versão lida do `plugin.json` só vira nome de ramo depois de `par_de_promocao` conferir o par na mesma tabela. Sondas no modo `degrau` (rc 0 aceita, outro rc recusa): `promocao/0.47.1` com head na develop, do próprio repositório, aceito; o mesmo com head fora da develop (13cb874d), de fork, `promocao/x`, `promocao/0.47.1` com quebra de linha no fim, `melhoria/y` para a homolog, `develop` para a main, `HEAD_REPO` vazio, `--head --` e `--head --all`, todos recusados; `homolog -> main` e `develop -> homolog` aceitos; base `develop` não é degrau (passa).

**A2 (era recomendado): resolvido.** O P5 pede `isCrossRepository` e descarta as linhas que não são `false` antes de contar abertos e procurar o MERGED (`bin/forge-fechar:980-983`), como o passo 3 e o 6.

**A3 (era recomendado): resolvido.** `--item-de-lote` é recusado sem `FORGE_FECHAR_LOTE_PAI` igual ao `$PPID` (`bin/forge-fechar:144-146`); o `fechar_lote` o põe só no ambiente do filho, com `exec` dentro da substituição (o pai do filho é o próprio script). Sondado: sem a marca e com marca errada, recusado. Residual informativo: quem roda o script pode forjar a marca (o próprio PID e `exec`); como já registrado, não é fronteira de confiança (o `tech-lead` tem `gh pr merge` direto), é trava contra o uso por engano, e cumpre isso.

Sem achado novo no delta: o CI do lote passou a acompanhar o topo da develop lido no servidor (`remoto_exato`), com recuo para o último merge lido e aviso; o comando de reversão continua só impresso, de shas filtrados.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem PR aberto para a branch, não há CI no head: a suíte inteira, o actionlint e o zizmor (o workflow mudou) ficam para o CI do PR, que os roda antes de todo código da branch. Rodado aqui no head `13cb874d`: `python3 -m unittest tests.test_catraca_promocao tests.test_fechar_lote tests.test_arvore_testada` (89 testes, OK), `shellcheck bin/forge-fechar` (rc 0) e as sondas do modo `degrau` e do `--item-de-lote` acima. Faltam no ambiente: gitleaks, zizmor, actionlint e Semgrep.
