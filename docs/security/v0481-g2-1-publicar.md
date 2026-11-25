---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-g2-1-publicar
commit: 841c14dcdc209c0cb1375caba6b11bcc0d4b155f
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-25
---
# Review de segurança: v0481 (E6.24, #878, G2.1 `forge-check parecer publicar`), volta por delta

Revalidação por delta da rodada aprovada em c78bfe22 (E6.20; texto no git). Delta lido: `forge-check parecer delta` deste arquivo até 841c14dc e `git diff c78bfe22..841c14dc` (no domínio: `hooks/conformidade.py`, `tests/test_hooks.py` e as 3 fixtures novas `contrib-publicar-*`; fora: changelog e `tests/mutantes/v0481-g2-1-publicar-6.json`, lido também). Veredito: o A1 do review E6.18 está fechado (a última `--raiz` vale, como no argparse), mas a troca da primeira pela última `--raiz` abre um caso que barrava em c78bfe22 e hoje libera (A1 abaixo). Não é "só aperta ou neutro".

Gatilhos: controles-do-forge, autorizacao, ci-cd.

## Achados
- A1 (bloqueante) hooks/conformidade.py:1386 · ultima_raiz lê também as palavras depois de `--`, que o argparse trata como o posicional `arquivo`: `forge-check --raiz <clone do Forge> parecer publicar -- --raiz=x/.forge/pareceres/v1/review.md` barrava em c78bfe22 e libera em 841c14dc (S1). Correção: parar o laço em `--`.

### A1, detalhe
- Evidência: `hooks/conformidade.py:1383-1391` (`ultima_raiz`) varre todas as palavras; `:2577` usa o resultado como alvo. No `forge-check` real (`bin/forge-check:10729-10735`), depois de `--` a palavra `--raiz=...` é o `arquivo`, e a raiz continua a do Forge: rodei `python3 bin/forge-check --raiz <cópia> parecer publicar -- --raiz=x/.forge/pareceres/v1/review.md` e a recusa cita `--raiz=x/.forge/pareceres/v1/review.md` como o arquivo (rc 1 só porque o arquivo não existe).
- Caminho de ataque: agente na sessão de projeto quer publicar no PR do Forge (R-CONTRIB). Põe o parecer em `<clone do Forge>/--raiz=x/.forge/pareceres/<pedido>/<tipo>.md` (o regex `(?:^|/)\.forge/pareceres/...` de `bin/forge-check:3752` casa) e roda a linha acima; o hook resolve a raiz `x/...` na pasta do projeto e libera. Exige o arquivo no clone do Forge e o registro de autoria; probabilidade baixa, impacto: a trava R-CONTRIB do publicar volta a ser contornável num caso que c78bfe22 barrava. Severidade média; bloqueia por ser regressão de controle provada, pedida no brief ("nada que barra hoje deixa de barrar").
- Correção mínima (dono: o autor do item, E6.21): em `ultima_raiz`, `if a == "--": break` antes dos dois testes, e uma fixture V0481-PUBLICAR com a linha da S1 esperando código 2 `R-CONTRIB`, mais o mutante do `break`. Conferi aqui, numa cópia por `git archive`: com o `break`, a S1 barra e as 8 fixtures V0481-PUBLICAR passam.
- O mesmo `--` também enganava a `parecer.opcao` de c78bfe22 quando não havia `--raiz` antes (`forge-check parecer publicar -- --raiz=...` na pasta do Forge); o `break` fecha os dois.

## Sondas
- S1 · fixture conformidade, sessão de projeto, `forge-check --raiz ~/.forge-contrib/proj parecer publicar -- --raiz=x/.forge/pareceres/v1/review.md` · espera: código 2 R-CONTRIB · obtido: 841c14dc código 0; c78bfe22 código 2

## Achados anteriores e A1 do review E6.18
- A1 do review E6.18 (duas `--raiz`, vale a última): fechado. Sonda S2 (`--raiz .` antes e `--raiz=<clone do Forge>` depois do subcomando): c78bfe22 código 0, 841c14dc código 2. As fixtures novas (`-duas-raiz-a-ultima-no-forge-bloqueia`, `-raiz-depois-do-subcomando-no-forge-bloqueia`, `-duas-raiz-a-ultima-no-projeto-libera`) cobrem S1 e S2 do review e o caso inverso.
- Sem abreviação de `--raiz` que contorne: todo prefixo dela é prefixo de `--raiz-pedidos` (ambíguo no argparse), como na rodada anterior. `--raiz` sem valor no fim é pulada e vale a anterior, como no argparse (que recusa a linha).
- A1 e A2 da E6.16: seguem corrigido e resolvido (nada no delta toca `bin/forge_pareceres.py` nem `bin/forge-check`).

## Mutantes
M34, M35 e M36 mortos aqui contra `tests.test_hooks.Hooks.test_fixtures_do_publicar` (3, 1 e 2 falhas); a fixture da S1 não existe e o `break` proposto ainda não tem mutante.

## Suíte e CI
Sem CI no head 841c14dc: o #878 está `CONFLICTING` (a develop andou 29 commits) e nenhum run do `pull_request` saiu para esse sha; o último run é de 3f42827f. Sem `- ci:` por isso. Rodei aqui `test_fixtures_do_publicar` (OK no head, 8 fixtures), os mutantes e as sondas; a suíte inteira fica para o CI depois do rebase.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` ausentes do PATH: lacuna registrada, nada instalado (`R-CUSTO`). Revisão estática; nenhuma chamada de escrita à API.
