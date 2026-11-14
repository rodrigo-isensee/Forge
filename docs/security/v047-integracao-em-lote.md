---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-integracao-em-lote
commit: c6b0b788c2815bbdf130a43d2a47eb2bbe6818ed
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-14
---
# Review de segurança: v047 (lote do forge-fechar: INTEGRACAO-EM-LOTE, RELEASE-EM-1H, FECHAR-ESPERA-CI-DEVELOP)

## Gatilhos
`R-SEGURANCA`: controle de integração e de promoção (`bin/forge-fechar`, que mescla na `develop` e agora abre e mescla PR para a `homolog`), texto da `R-FLUXO`. Intervalo revisado: `origin/develop...c6b0b788` (base f4b0c2ae), 20 arquivos.

## Achados
- A1 (bloqueante) bin/forge-fechar:980 · --promover abre o PR promocao/<versão> -> homolog, mas o passo "Nada pula degrau" do CI (job bateria) só aceita head develop para a homolog e a catraca só reconhece (develop, homolog) como promoção: o CI exigido fica vermelho e a promoção nunca mescla (R-FLUXO, RELEASE-EM-1H).
- A2 (recomendado) bin/forge-fechar:954 · o P5 lê os PRs de promocao/<versão> sem isCrossRepository: PR de fork com o mesmo nome de branch conta como aberto (dois abertos param a promoção) ou é retomado; o passo 3 e o 6 já recusam fork, o P5 deveria filtrar igual.
- A3 (recomendado) bin/forge-fechar:106 · --item-de-lote é aceito fora do --lote e pula o 6b e o passo 8 (FECHAR-ESPERA-CI-DEVELOP); o texto diz que é só do --lote, mas nada o impede: recuse-o sem uma marca que só o fechar_lote põe no ambiente do filho.

## Sondas
- S1 · BASE=homolog HEAD_REF=promocao/0.47.1 e o corpo do passo "Nada pula degrau" de .github/workflows/ci.yml:507-511 · espera: ok para a promoção pela marca · obtido: "PR para homolog só a partir da develop (veio de promocao/0.47.1)." rc=1

## Detalhe dos achados
**A1 (bloqueante, defeito provado; severidade média como controle: a promoção falha fechada, mas a correção natural mexe num degrau protegido).** Evidência: `bin/forge-fechar:964-980` cria `promocao/<versão>` no sha da marca e abre o PR para a `homolog`; `.github/workflows/ci.yml:502-511` (passo "Nada pula degrau", dentro do job `bateria`, de que o agregador `bateria`, check exigido `CI/bateria`, depende em `ci.yml:669`) só aceita `HEAD_REF=develop` com base `homolog` (sonda S1); `tests/catraca.py:1527` `PROMOCOES = {("develop", "homolog"), ("homolog", "main")}` e `eh_promocao` (`tests/catraca.py:1236`) não reconhecem o par novo, então o PR também não ganha o tratamento de promoção (árvore provada, pareceres da release). O `--auto` nunca mescla e o P6 morre no prazo; o requisito da diretriz 27 ("promova exatamente o commit da marca") não é entregue. Os testes (`tests/test_fechar_lote.py:315-343`) usam `gh` falso e não veem o CI. Caminho de risco: a saída prática, com a release parada, é afrouxar o degrau às pressas (aceitar qualquer head para a `homolog`), o que abre a `homolog` a branch que não passou pela `develop`. Correção mínima, num só PR com review de segurança: (1) `ci.yml`, passo "Nada pula degrau": para base `homolog`, aceitar `develop` ou `promocao/X.Y.Z` (forma exata `^promocao/[0-9]{1,4}\.[0-9]{1,4}\.[0-9]{1,4}$`), este só com o head do próprio repositório (`github.event.pull_request.head.repo.full_name == github.repository`) e com o sha do head ancestral de `origin/develop` (`git merge-base --is-ancestor`, depois do fetch da develop); base `main` sem mudança; (2) `tests/catraca.py`: `eh_promocao` reconhece o par (`promocao/X.Y.Z`, `homolog`) nas mesmas condições (mesmo repositório e head na develop); (3) teste do degrau com `promocao/0.9.0` aceito, `promocao/x` e `melhoria/y` recusados, e head fora da develop recusado. Alternativa sem mexer no CI: tirar o `--promover` desta entrega (as funções e a opção, como manda a seção de volta de `docs/fechamento-integrador.md`) e levá-lo junto com o ajuste do degrau. Esforço M. Donos: `devops-engineer` (workflow, enviado pelo dono por falta do escopo `workflow` no token), `tech-lead` (catraca e script).

**A2 (recomendado, baixa).** Evidência: `bin/forge-fechar:954-960` (`gh pr list --head "$ramo"` sem `isCrossRepository`), comparado com `bin/forge-fechar:1142-1156` e `:1290-1294`, que recusam fork. Caminho: quem tem conta no GitHub abre, de um fork, um PR com a branch `promocao/<versão>` para a `homolog`; com o PR legítimo aberto, o P5 conta dois e para (atraso da release), ou o P5 retoma o PR do fork se o head dele tiver o sha da marca (conteúdo igual, preso por `--match-head-commit`, então sem ganho de conteúdo). Correção mínima: pedir `isCrossRepository` no `--json` do P5 e descartar as linhas `true` antes de contar abertos e procurar o MERGED. Esforço P. Dono: `tech-lead`.

**A3 (recomendado, baixa).** Evidência: `bin/forge-fechar:106` aceita `--item-de-lote` em qualquer chamada; `:1284` e `:1009` pulam o 6b e o passo 8 com ele. Caminho: um agente com pressa fecha um item com `--item-de-lote` e mescla com a `develop` vermelha, sem acompanhar o CI do merge: é exatamente o incidente que motivou o cartão. Não é fronteira de confiança (o `tech-lead` tem `gh pr merge` direto), por isso recomendação. Correção mínima: o `fechar_lote` exporta uma marca só para o filho (por exemplo `FORGE_FECHAR_LOTE_PAI=<pid do pai>`) e o script recusa `--item-de-lote` sem ela, com teste do recuso. Esforço P. Dono: `tech-lead`.

Sem achado no resto: `--lote` valida o pedido por expressão fixa, a branch por `git check-ref-format --branch` e recusa `main`, `develop`, `homolog` e repetição; o filho recebe argumentos em vetor, sem `eval`; o sha lido da saída do item é filtrado para 40 ou 64 hex; o comando de reversão é só impresso, montado de shas filtrados; a versão do `plugin.json` passa por expressão de dígitos antes de virar nome de ramo; `FORGE_FECHAR_ITEM` só vale com `FORGE_FECHAR_TESTE=1`, como os outros falsos; o único `gh pr merge` (`mesclar_auto`) segue com `--auto` e `--match-head-commit`, sem `--admin`; nada toca a `main`. `esperar_ci` não trata lista vazia como verde e separa cancelado de vermelho; no P3, cancelado segue com aviso e o CI exigido do PR decide.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Sem PR aberto para a branch, não há CI no head: a suíte inteira fica para o CI do PR. Rodado aqui: `python3 -m unittest tests.test_fechar_lote` (50 testes, OK) e `shellcheck bin/forge-fechar` (rc 0). Faltam no ambiente: gitleaks, zizmor, actionlint e Semgrep (nenhum workflow mudou nesta entrega; a correção do A1 muda e pede zizmor e actionlint no CI).
