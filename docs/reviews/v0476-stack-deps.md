---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0476-stack-deps
commit: 95605e662d55742e4af9b64e640878ea0bfa085b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-18
---
# Review: v0474 (E3.247, item E3.245, `forge-copia --instalar` com lockfile e sem credencial)

## Achados
- A5 (recomendado) bin/forge-copia:48 · código e teste somam agora 205 linhas (52+4 em `bin/forge-copia`, 149 no teste), acima da orientação de 150 (M14). O corpo do PR leva `teto: excedido, 205 linhas, <motivo>` (instalação e o endurecimento pedido pela segurança no mesmo comportamento).
- A7 (recomendado) bin/forge-copia:50 · a lista tira `GIT_CONFIG_COUNT` e `GIT_CONFIG_KEY_*`/`VALUE_*`, mas não `GIT_CONFIG_PARAMETERS`, a outra via de config injetada do git (`git -c`, que pode levar `http.extraheader` com o token). Acrescentar à lista e ao teste.
- A8 (recomendado) tests/test_forge_copia.py:264 · `test_instalacao_real_so_com_lockfile` repete o que o teste da linha 247 já prova (todo `detecta` contém "lock") e só nega dois nomes; pode sair. O teste da linha 247 percorre `stacks/` sem mínimo de itens (checklist 11), coberto hoje pelo da linha 240.

## Sondas

## Revalidação
Delta lido por `forge-check parecer delta docs/reviews/v0476-stack-deps.md`, intervalo `89f7ef2f..95605e66`: `bin/forge-copia`, os dois `instalar.json` e `pronto.md`, a ADR 0001, o fragmento do changelog, `tests/mutantes/v0476-stack-deps-2.json` e `tests/test_forge_copia.py`. Nada fora disso relido.

- **Achados anteriores:** A1 resolvido por desenho (`detecta` aponta só o lockfile; sem ele avisa e sai 0, documentado no `pronto.md` da stack). A2 resolvido (`detecta` do node é `pnpm-lock.yaml`; sem ele não roda o `--frozen-lockfile`). A3 resolvido (ADR 0001 lista `instalar.json`). A4 resolvido (`assertGreaterEqual(len(stacks), 2)`, `detecta` em lista e argv só de strings). A5 segue, com o número novo. A6 resolvido (spec nova em `v0476-stack-deps-2.json`).
- **Achados da segurança (no 89f7ef2f):** o A1 dela (instalação sem lockfile nem hash) tem resposta no delta: python instala de `requirements.lock` com `--require-hashes --no-deps` e o pacote local com `--no-deps`; node com `--frozen-lockfile`. O A2 dela (ambiente com o token) tem `env=env_sem_credencial()`. O veredito é da segurança (`R-SEGURANCA`); não refaço.
- **Testes:** `python3 -m unittest tests.test_forge_copia tests.test_ambiente_git tests.test_metricas_texto` deu 52 testes OK. O teste de ambiente roda `env` real no comando de instalação e confere a saída (comportamento, não leitura de fonte), mais o teste de que o resto do ambiente permanece.
- **Ferramentas:** `python3 -I tests/catraca.py --base origin/develop` deu rc=0. `bin/forge-mutante tests/mutantes/v0476-stack-deps-2.json` no head 95605e66: M1 a M14 morreram, um por guarda ou item da lista.
- **Neutralidade (`R-NEUTRO`, ADR 0001):** `pnpm`, `pip` e os lockfiles só em `stacks/` e na ADR; `bin/forge-copia` cita só nomes de variáveis de credencial, sem linguagem.
- **Suíte:** a suíte inteira fica para o CI do PR.

## Parecer
Aprovado, sem bloqueante (`R-REVIEW`).
