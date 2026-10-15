---
tipo: revisao-devops
contrato: 1
pedido: ci-local
branch: melhoria/ci-local
commit: 68b3aec3c05e4f52f0ddcb156ab72cb2ab87dd25
parecer: aprovado
revisor: forge:devops-engineer
data: 2026-10-14
---
# Review de devops: ci-local

Parecer de autor (o devops escreveu o script); exige review independente do tech-lead (`R-REVIEW`).

## Parecer
Aprovado, com as lacunas abaixo. `scripts/ci-local <PR> [--publicar]` lê os `run:` de `ci.yml` e `catraca.yml` do PR, roda numa worktree temporária no sha da cabeça, com `env` do passo e `RUNNER_TEMP` próprio por job. Nenhuma lógica do CI foi copiada. Só biblioteca padrão.

Volta 2 (re-review B3, N1, N2): passos sem `shell:` voltaram a `bash -e {0}` como o GitHub (o pipefail da volta 1 era engano meu e do revisor); `shell: bash` declarado usa `-eo pipefail`. `if:` com `github.*` desconhecido ou aninhado demais vira "sem suporte" com aviso, sem `RecursionError`. Testes de regressão vermelhos antes, verdes depois; suíte 587 OK.

Execução real sobre o PR #121 (develop -> homolog), sem `--publicar`: testes estruturais OK (556), shellcheck OK, validação do plugin OK, instalação ponta a ponta OK, fluxo de promoção OK, segredos OK, pareceres OK, catraca FALHOU (legítimo: `bin/forge-check` mudou e falta o rótulo `afrouxa-regra` do dono, igual ao CI real), `workflows` PULADO (sem actionlint/zizmor), `versão e changelog` e `pr-texto` PULADOS (`if` não se aplica a base homolog). Bug achado e corrigido na execução: jobs `pareceres` e `catraca` criavam o mesmo `$RUNNER_TEMP/base`; agora cada job tem subpasta (teste de regressão).

Ferramentas: shellcheck sem achado novo (o script é Python; não há shell tocado); actionlint e zizmor ausentes no PATH.

Volta 3 (parecer de segurança, A1, A2, C1, D): PR de fork recusado (`isCrossRepository`), salvo `--confiar` com aviso; passos com ambiente mínimo por lista branca; `ci.yml`/`catraca.yml` symlink conta como ausente; `--publicar` recusa PR que altera `.github/workflows/` ou `tests/catraca.py`, e o texto diz que o status é autodeclarado. Testes de regressão vermelhos antes (6 falhas e 3 erros), verdes depois; suíte 597 OK. Fora desta volta (recomendados A3 e C2): token dedicado de escopo fino, `start_new_session`/`killpg`.

Volta 4 (D1 do re-review de segurança): o portão D agora usa `git diff --name-only --no-renames -z`, que traz o nome antigo e o novo (renomear `tests/catraca.py` é recusado), e é falha fechada: se o `git diff` sair com rc diferente de 0, o `--publicar` é recusado em vez de seguir com lista vazia. Testes de regressão (renomear a catraca, `git diff` que falha, PR que só altera o README) vermelhos antes (3 erros), verdes depois; suíte 600 OK e validação do plugin OK. Fora: A3 e C2, e o `--publicar` real não foi executado.
Volta 5 (CL-01 e C2, do QA): INT e TERM viram uma exceção que sobe até o `finally` do `main`, que remove a worktree e a pasta temporária (segundo sinal ignorado durante a limpeza); rc 130 e 143 e uma linha "interrompido", sem traceback. Cada passo roda em grupo de processos próprio (`start_new_session`) e o grupo inteiro é morto na interrupção ou no timeout, então não sobram netos. Testes de regressão com processo filho real e sinal (`SinalTest`) vermelhos antes (1 falha, 1 erro), verdes depois; suíte 602 OK, validação do plugin OK. Fora: A3 e `--publicar` real.

## O que fica de fora
- Job `workflows` (actionlint, zizmor): o CI os baixa; local só rodam se instalados, e o job é não obrigatório.
- Merge-base no lugar do primeiro pai do merge commit do GitHub: a base dos jobs de diff pode diferir quando a base avançou depois do PR.
- `if:` avaliado por avaliador próprio (sem `eval`), só no subconjunto `github.*`, literais, ==, !=, &&, ||, parênteses; fora dele o job fica "pulado por falta de suporte", com aviso, e conta como falha se for obrigatório.
- Os passos rodam como o GitHub os roda: sem `shell:`, `bash -e {0}` (sem pipefail); com `shell: bash`, `bash --noprofile --norc -eo pipefail {0}`.
- `if:` com contexto `github.*` desconhecido ou aninhado demais deixa o job "pulado por falta de suporte", com aviso.
- **Os testes rodam sobre a cabeça do PR, não sobre o merge com a base** (o CI testa o merge commit). Atualize a branch com a base (`git merge origin/<base>`) antes de rodar.
- Chaves que o leitor ignora geram aviso: `env:` de workflow e de job, `defaults`, `working-directory`, `shell`, `continue-on-error`. Também há aviso se sobrar `HEAD^`/`HEAD~` no passo depois da troca de `git rev-parse HEAD^1`, se o `gh auth token` falhar e se o PR não estiver `OPEN`.
- Passos de preparo (instalação global de CLI, `curl`, `wget`) são ignorados; vale o que há no PATH. Ferramenta ausente em job obrigatório vira `failure`.
- O status `ci-local` é **autodeclarado**: não prova que a bateria rodou (quem tem escrita publica `success` com uma chamada à API), usa os workflows do próprio PR e mede a cabeça sem o merge com a base; não substitui o CI nem a revisão. Por isso `--publicar` recusa PR que altera `.github/workflows/` ou `tests/catraca.py`. Torná-lo check exigido é decisão do dono (`R-CONFORMIDADE`).
- Workflow (`ci.yml`, `catraca.yml`) que seja symlink conta como ausente (falha se obrigatório).

## Segurança (gatilho `R-SEGURANCA` para o security-engineer)
O script executa localmente os `run:` e o código da cabeça do PR, com os privilégios de quem o roda: é o equivalente local de `pull_request_target` com checkout da cabeça. O que protege de fato é o portão antes da execução: PR de fork (`isCrossRepository`) é **recusado**, salvo `--confiar` explícito, que imprime aviso de exposição da credencial; em PR do mesmo repositório, só quem tem escrita controla a branch. O que roda depois é redução de vazamento acidental, não defesa: os passos recebem ambiente mínimo por lista branca (`PATH`, `HOME`, `USER`, `LOGNAME`, `SHELL`, `LANG`, `LC_*`, `TERM`, `TMPDIR`, `TZ`, `GITHUB_REPOSITORY`, mais `RUNNER_TEMP`, `GITHUB_STEP_SUMMARY`, `CI` e o `env:` do passo), mas o PR escreve os próprios `env:` e o `gh` ainda lê a credencial em disco sob `HOME`. Outras mitigações: `if:` sem `eval`, worktree temporária, timeout de 30 min por passo. Limitações conhecidas: processos em segundo plano e ganchos gravados no `.git` comum sobrevivem à limpeza; o token entregue tem o escopo do usuário, maior que o `contents: read` do CI. Rode só sobre PR de autor confiável.

## Custo e rollback
Custo zero (`R-CUSTO`): roda na máquina local, sem serviço pago e sem minutos de Actions. Rollback: reverter os dois commits; nada em `.github/`.
