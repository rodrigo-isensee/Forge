---
tipo: revisao-devops
contrato: 1
pedido: develop-vermelha-ci-local
branch: melhoria/ci-local-jobs-consolidados
commit: 5d623443be6f7acab6a401fbfecaa988b428341c
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-15
---
# Review de devops: ci-local-jobs-consolidados

## Parecer
Aprovado, sem achado bloqueante. O #138 consolidou o `ci.yml` em `rapida` e `bateria`; o job `workflows` (único não obrigatório) virou dois passos da `bateria`, e o teste que fixava os ids antigos quebrou a develop.

## Conferências
- **Não afrouxa:** `NAO_OBRIGATORIOS` agora é vazio, então `rapida`, `bateria` e `catraca` são todos obrigatórios; só os passos cujas ferramentas ausentes são todas de `FERRAMENTAS_OPCIONAIS` (`actionlint`, `zizmor`) são pulados, com `AVISO` em stderr. Passo que mistura opcional e obrigatória (ex.: `actionlint` e `shellcheck`) continua inteiro, e a ausência de `shellcheck` ou `claude` segue virando `failure` (teste de regressão cobre).
- **Leitura dos workflows:** `ler_jobs` não mudou; o teste agora exige os ids `rapida`, `bateria`, `catraca` e que a `bateria` ainda traga unittest, shellcheck, actionlint, zizmor, `claude plugin validate`, e2e-instalacao, conferência de changelog, fluxo de promoção e `verificar-contribuicao` (guarda contra passo sumir na consolidação).
- Os passos `curl` de baixar actionlint/zizmor continuam ignorados como preparo; o regex de ferramenta exige o comando em posição de comando, então não casa com `actionlint.tgz`.
- Não torna o `ci-local` check exigido (decisão do dono, A); nada em `.github/` mudou.

## Execução
- `env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests` (load average 1,05 antes): 653 testes, OK.
- `scripts/validar-plugin.sh`: Validation passed.
- actionlint e zizmor ausentes no PATH (lacuna, irrelevante: nenhum workflow mudou).

## Observações (informativas)
- Um passo opcional pulado reduz a cobertura local sem reprovar; é o mesmo comportamento do antigo job `workflows`, agora por passo, e o CI continua rodando os dois.
- O texto do docstring ficou com linha longa; estilo apenas.
