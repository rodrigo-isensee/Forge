---
tipo: revisao-devops
contrato: 1
pedido: v047-catraca-hook-por-script
branch: melhoria/v047-catraca-hook-por-script
commit: 66a3a9a4bbcafbd3588f564bd2fc2a81964fe3e6
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-11-15
---
# Review de devops: v047-catraca-hook-por-script

## Achados
- A1 (recomendado) tests/catraca.py:276 · interpretador que não é Python (`bash -x x.sh`) falha fechado: mudar só a opção acusa remoção do hook. Falso positivo seguro, resolve-se com o rótulo; vale registrar no texto da regra se aparecer.

## Detalhes
Aprovado. Classe C pelo gatilho (`tests/catraca.py` é protegido da catraca); a diff não toca `.github/`, `Dockerfile*`, `compose*`, IaC nem `hooks/`. A chave do hook passa de (evento, matcher, command, args sem opção) para (evento, matcher, tipo, interpretador, script). Trocar o script, o tipo (`prompt`), o comando (`true`, `echo`) ou antepor `-c`, `-m`, `/dev/null` remove a chave e barra; opções inócuas do Python e argumentos depois do script não. Sem `-X`/`-W` a falha é fechada. Não há workflow novo, nem permissão, segredo, cache ou ação de terceiros novos.

Revalidado no head 66a3a9a4 (delta 40faab23..66a3a9a4 sem arquivo do domínio; mudaram só `tests/catraca.py`, testes, corpus e mutantes do item): 10 testes OK nas mesmas duas classes. Antes, em 40faab23: `python3 -m unittest tests.test_catraca.Hooks tests.test_catraca.CorpusDasSondasDeHook` com 8 testes OK; o `hooks/hooks.json` real gera 18 chaves. As sondas S1 a S4, A3 e PR565 do corpus `tests/fixtures/catraca-hooks/sondas.json` dão o esperado. A suíte inteira roda só no CI (não esgotei o tempo local: a classe inteira passou do limite de 100 s). A `develop` avançou 3 commits; a simulação de merge fica para o CI do PR.

Ferramentas: `actionlint`, `shellcheck` e `docker build` não se aplicam (sem workflow, script de shell nem imagem alterados).

## Custo e rollback
Sem minutos de CI novos além da suíte já existente (os testes novos somam cerca de 7 s) e sem recurso pago (`R-CUSTO`). Rollback: reverter o commit do merge; a catraca volta à chave anterior, sem estado nem migração.
