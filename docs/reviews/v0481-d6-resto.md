---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 1afd54b5fe5b5a25dd2a96fd490c57469228e9bb
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Code review: hook salvar grava e envia ao parar, volta E11.6 (D6 parte a; v0481 E11.7, PR #877)

Revisado por delta: `9a708f86..1afd54b5` (um commit de código, `fix(hooks)`, E11.6), lido pelo `forge-check parecer delta` (revalida: sim, este parecer barrou). Parecer anterior: reprovado no `9a708f86` por A1 e A2, com A3 recomendado.

## Achados
- A1 (bloqueante) hooks/salvar.py:145 · Branch nova: a varredura vai de HEAD^ a HEAD, mas o push leva todos os commits locais; segredo em commit anterior sai sem varredura (S1). O pre-push usa o merge-base com a develop. Sugestão: base = merge-base com origin/<Base do brief>, com teste e mutante.

## Sondas
- S1 · sonda_branch_nova.py: na cópia, branch melhoria/x sem envio, commit local de docs/b.md com SEGREDO dos testes, depois hooks/x.py mudado no escopo e SubagentStop · espera: não enviado: varredura de segredo · obtido: "melhoria/x 6764af8 1 arquivo(s) enviado", docs/b.md presente no remoto

## Parecer
**Reprovado**, por A1. Os três achados anteriores estão resolvidos; o novo é da própria correção do A2.

**A1 anterior (config da cópia): resolvido.** `config_permitida` lê `git config --local --no-includes --list -z` antes de qualquer outro git na cópia (está no `plano`, antes do `symbolic-ref`), recusa chave fora da lista positiva e exige `remote.origin.url` igual ao da cópia principal. Conferi as bordas: o `--list` devolve seção e nome em minúsculas, então `Filter.X.Clean` não escapa da regex; `include.path`, `includeIf` e `extensions.worktreeConfig` aparecem como chave e são recusados; `branch.<nome>.remote` com URL não alcança nada, porque o envio nomeia `origin`. `XDG_CONFIG_HOME`, `BASH_ENV`, `ENV` e as `GIT_*` saem do ambiente. Minha sonda S1 anterior (filtro clean) virou subteste de `test_config_local_fora_da_lista_nao_age` com mais 10 chaves; rodei a classe e ela passa.

**A2 anterior (R-VERIFY): resolvido.** A exceção está escrita em `docs/regras/R-LIMITES.md` só para o hook `salvar`, "à espera do dono", e o título do PR traz `R-VERIFY core.hooksPath` ao lado da ADR 0003 item 2. A emenda diz o que se perde (o `pre-commit` do projeto) e quem cobre (o CI). Não rastreado fora do commit (`--untracked-files=no`), com teste. **Script do plugin em vez do da origin/develop:** aceito. Os três motivos do PR se sustentam: o agente não grava a pasta do plugin, a `refs/remotes/origin/develop` da cópia é gravável por ele, e nos projetos a develop não tem o script. O script roda com `--no-ext-diff --no-textconv`, sob a config já filtrada. Nos projetos, o padrão "caminho pessoal" do Forge pode segurar um envio legítimo; isso falha fechado (o commit fica na cópia e o motivo vai ao log), então é aceitável.

**A3 anterior (prazo): resolvido.** `FIM` é fixado uma vez por processo e cada `rodar` usa o que resta; com prazo esgotado, `subprocess` levanta `TimeoutExpired` e o `executar` grava a linha no `erros.log`. 50 s cabem nos 60 s do `hooks.json`.

**A1 novo.** A varredura é a reposição do `pre-push` que o `core.hooksPath` vazio desliga, e é o argumento da exceção ao R-VERIFY. Na branch já enviada, a base `origin/<branch>` cobre o delta, e isso está testado. Na branch nova, a base é só `HEAD^`, mas o push leva a branch inteira. O `.githooks/pre-push` usa `merge-base` com a develop nesse caso (linha 222). O teste `test_varredura_vai_da_origin_da_branch` cobre só o ramo da branch já enviada. O caso da branch nova fica sem teste e sem mutante.

**Teto.** `teto: excedido, 182 linhas`, aceito: as três correções fecham bloqueantes do mesmo hook, e nenhum corte fica mesclável sozinho. A correção do A1 deve caber em poucas linhas.

**Verificadores.** Rodei `python3 -m unittest tests.test_hooks.SalvarAoParar` no `1afd54b5`, com ambiente limpo: 31 testes, OK. A sonda S1 roda com `python3 -I`, sobre a fixture da classe. Os mutantes M31 a M39 em `tests/mutantes/v0481-d6-resto-5.json` e `-6.json` são citados, não refeitos. A suíte inteira roda no CI do PR #877, e não rerrodei o SHA. O merge espera também a decisão do dono sobre os dois afrouxamentos.
