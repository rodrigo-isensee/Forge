---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-d6-resto
commit: 9a708f86cf6018f09145073a52ce0e7480d9649a
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Code review: hook salvar grava e envia ao parar (D6 parte a; v0481 E11.2, PR #877)

Revisado: `bbbe2d88..9a708f86` (um commit, `feat(hooks)`), 15 arquivos, `hooks/salvar.py` com 132 linhas (dentro do teto H1, um comportamento). Parecer anterior da branch: nenhum.

## Achados
- A1 (bloqueante) hooks/salvar.py:24 · O git do hook, fora do sandbox, lê o .git/config da cópia, que o agente grava de dentro dele: filtro clean, core.sshCommand e gpg.program rodam código do agente (S1), contra a regra 4 da emenda. Sugestão: não agir com chave local fora de uma lista de permitidas.
- A2 (bloqueante) hooks/salvar.py:24 · `core.hooksPath=/dev/null` troca o caminho dos hooks, o que o R-VERIFY veda sem exceção; o PR só declara o afrouxamento da ADR 0003 item 2. Falta a exceção escrita em docs/regras/R-LIMITES.md e o destaque do R-VERIFY no título, para a decisão do dono.
- A3 (recomendado) hooks/salvar.py:22 · Prazos somados: até 6 chamadas de 10 s mais o envio de 40 s, 100 s contra os 60 s do hooks.json; o Claude Code mata o hook depois do commit e antes do log. Sugestão: prazo global único, descontado a cada chamada.

## Sondas
- S1 · sonda_filtro.py: cópia com `filter.x.clean = sh -c 'touch MARCA; cat'` no .git/config e `* filter=x` no .gitattributes, depois `salvar.git_da_copia(copia, "add", "-A", "--", "hooks/x.py")` · espera: MARCA ausente (nada do agente roda fora do sandbox) · obtido: rc=0 marca_criada=True

## Parecer
**Reprovado**, por A1 e A2.

**A1, segurança com gatilho.** A emenda (regra 4) justifica desligar os hooks do git porque eles são código do agente rodando fora do sandbox; o mesmo vale para o `.git/config` da cópia, que o sandbox deixa gravar nas cópias em `~/.forge-contrib/wt/` (este review gravou o `remote.origin.url` da própria cópia de dentro do sandbox). O `-c core.hooksPath` e o `-c core.fsmonitor` fecham dois caminhos de uma classe aberta: `filter.<x>.clean`/`process` (rodam no `git add`, provado em S1), `core.sshCommand` e `url.*.insteadOf` (no `push`), `commit.gpgsign` com `gpg.program` (no `commit`), `credential.helper`, `include.path`/`includeIf`, `protocol.ext.allow`. Sugestão: antes de qualquer outra chamada, ler `git config --local --list --name-only` (leitura, sem executar nada) e não agir se aparecer chave fora de uma lista de permitidas (`core.repositoryformatversion`, `core.filemode`, `core.bare`, `core.logallrefupdates`, `remote.origin.url`, `remote.origin.fetch`, `branch.*.remote`, `branch.*.merge`, `user.name`, `user.email`), com teste de comportamento do ramo de recusa e mutante declarado. Cabe ao `security-engineer` confirmar o alcance no parecer dele; este achado cita a sonda, sem refazer o parecer de segurança.

**A2, resposta à pergunta do brief: sim, conflita com o R-VERIFY.** O texto do R-VERIFY (`docs/regras/R-LIMITES.md`) veda desativar ou trocar o `core.hooksPath`, sem exceção; o argumento da emenda ("não é o `--no-verify` de um agente, o agente não escolhe") muda quem decide, não o efeito: os hooks do git não rodam no commit e no envio. Consequência concreta nos projetos: um `pre-commit` de varredura de segredos ou lint do projeto não roda sobre o commit WIP, que vai ao remoto; no Forge, as checagens baratas do `.githooks/pre-push` (ENVIO-LEVE) ficam de fora, e só a guarda das branches de integração é reposta no hook. O desenho em si é defensável (rodar o código do agente fora do sandbox é pior), mas é um segundo afrouxamento: precisa da exceção escrita no R-VERIFY, do destaque no título do PR ao lado do da ADR 0003 e da mesma decisão do dono. Com A1 e A2 resolvidos, o item fica pronto para essa decisão.

**O que está correto.** O escopo é respeitado com `--only` e `--literal-pathspecs`, arquivo exato não vale como prefixo; nunca age em `main`, `master`, `develop` ou `homolog` (`INTEGRACAO` de `_comum.py`), nem com cópia em outra branch, brief de parecer, dois briefs, duas cópias, cópia fora da pasta, conflito no índice ou mesclagem, rebase, cherry-pick e revert em andamento; o envio é `refs/heads/<b>:refs/heads/<b>` sem `+` (a `BRANCH_VALIDA` exige primeiro caractere alfanumérico) e o remoto que andou é recusado sem `--force` (teste `test_envio_recusado_sem_force_fica_no_log`). As `GIT_*` herdadas saem e o git não pede senha. A ADR traz "Por que o existente não basta", critério de reversão e medida com dono e prazo; os dois invariantes de teste afrouxados estão listados e nenhum trecho de `invariantes` sai.

**Verificadores.** Rodei a classe nova: `python3 -m unittest tests.test_hooks.SalvarAoParar`, 23 testes, OK. Suíte inteira: CI do PR #877 no head `9a708f86`, com as partes concluídas verdes e a parte 1/5 do Python 3.14 pendente na leitura; não rerrodei o SHA. Mutantes declarados em `tests/mutantes/v0481-d6-resto*.json` (4 arquivos): citados, não refeitos.
