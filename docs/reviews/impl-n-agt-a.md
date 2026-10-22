---
tipo: review
contrato: 1
pedido: impl-n-agt-a
branch: melhoria/impl-n-agt-a
commit: 535cd9a19c7108d19eea600226df1e06898a0f37
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-22
---
# Review: impl-n-agt-a

Escopo: os 4 commits da branch sobre a base `38c5824` (56fca85 AGT-1, 494ad20 AGT-2, 5d13ce6 fragmento, 18fb796 parecer de segurança) e o merge `535cd9a` da `develop` (`af79bef`). O pedido de origem se perdeu; o escopo é o que dizem os commits e `changelog.d/impl-n-agt-a.md` (retomada RET-AGT-A). São 8 arquivos, +505/−16.

## Achados

## Parecer
**Aprovado.**

**Merge da `develop`.** Sem conflito: o diff combinado de `535cd9a` é vazio e `git diff af79bef 535cd9a` tem o mesmo stat do diff da branch sobre a base (8 arquivos, +505/−16), ou seja, o patch não mudou. A resolução **não pede nova olhada de segurança**: o parecer de `docs/security/impl-n-agt-a.md` (commit `5d13ce6`) cobre o mesmo patch; `18fb796` só acrescenta esse parecer.

**O que a entrega faz (checklist 1, 2).**
- AGT-1: o hook `agentes` passa a rodar no clone do Forge e nas worktrees (`hooks/agentes.py:334`, `clone_do_forge=True`), com o estado em `<diretório comum do git>/forge/run/` (`fixar_estado_do_clone`, `:190-201`), porque no clone `.forge` é arquivo. `arquivo_de_estado` dá ao `forge-check fila` o mesmo caminho (`bin/forge-check`, `agentes_vigentes`); sem diretório comum, cai no caminho antigo, que falha para lista vazia, como antes. `registrar_erro` usa o `_run` já fixado, então o `erros.log` do clone vai para a mesma pasta.
- AGT-2: `hash_do_brief_diverge` recalcula o sha256 do arquivo do cabeçalho e bloqueia por `R-BRIEF` se não bater. Só o cabeçalho conta, com exatamente uma `Arquivo:` e uma `Brief-sha256:`. A leitura (`ler_brief`) é fechada: `realpath` sob `docs/briefs/`, arquivo regular por `lstat` e `fstat`, `O_NONBLOCK|O_NOFOLLOW`, teto de 256 KiB, o mesmo do `forge-check brief mensagem`.
- Regras preservadas: `R-TETO` não se abre com `FORGE_GUARDA_ABERTA` (teste próprio), `hooks_desligados` não vale no clone (documentado), erro interno do hook segue liberando (ADR 0003), e só a mensagem ao conferente passa a bloquear por erro de leitura, como a regra pede. `tests/config.json` não foi tocado. Sem dependência nova, sem rede, sem custo (`R-CUSTO`), sem termo de projeto (`R-NEUTRO`).
- Documentação na mesma entrega: `docs/hooks.md` (tabela e "Estado e expiração"), docstrings e fragmento de changelog.

**Legibilidade, erros, testes (checklist 3, 4, 7, 11).** Funções pequenas e com nome claro. Exceções capturadas com motivo comentado (`RuntimeError` sem HOME). `tests/test_agentes_clone.py` (11 casos: teto no clone e na worktree, soma entre as duas, 0700 e `.gitignore`, duplicado, `erros.log`, guarda aberta, `forge-check fila`) e `tests/test_agentes_hash_brief.py` (19 casos: hash relativo e absoluto, brief editado, entrega, outro agente, inexistente, atalho e `..` para fora, dispositivo, FIFO sem travar, 256 KiB no limite e acima, cabeçalho duplicado, corpo e segundo bloco). O parecer de segurança registra que 27 dos 30 testes novos falham com o código da base. `test_guarda_conferente.py` foi ajustado para o hash real e continua cobrindo só a forma; o comentário de `test_passa_mensagem_com_varios_blocos` explica por que o segundo bloco, com hash falso, passa.

**Commits (checklist 9).** Conventional Commits em português, um por mudança coerente, com o ID do pedido. O merge é `git merge --no-edit`, sem rebase.

**Saída das ferramentas.** Na worktree, sobre `535cd9a`: `scripts/validar-plugin.sh` deu `Validation passed`, rc 0. `python3 -m unittest discover -s tests` rodou 1624 testes, com 4 falhas e rc 1: `test_pre_push_shellcheck.test_shellcheck_no_hook` (SC2329 em `.githooks/pre-push:243`, aviso do shellcheck local), `test_hooks.test_erro_interno_com_lista_de_permissao_falha_fechado` e as fixtures `conformidade/contrib-falha-fechada-pela-raiz-cwd-{home,wt}-bloqueia`. As 4 falham igual na `develop` pura (`af79bef`, worktree destacada, os mesmos 5 testes). Estão em arquivos que a branch não toca. São do ambiente local (sandbox e versão do shellcheck), não desta entrega; o CI do PR decide. Não refaço o que as ferramentas decidem.

**Recomendações (não bloqueiam; ficam como cartão para o Jarvis):**
- R1 · `hooks/agentes.py:229`. A raiz de brief fora do clone é `~/.forge-contrib/docs/briefs/`, a convenção documentada (`docs/hooks.md:35`, `bin/forge-check:960`). Hoje, nesta retomada, os briefs estão em `~/.forge-contrib/forge/docs/briefs/`, que não é aceita nem pelo hook nem pelo `forge-check`. Antes da entrega, o hook nem rodava no clone. Depois da release, uma mensagem ao `forge:conferente` lançada do `~/Forge` com o brief nessa pasta passa a ser bloqueada por `R-BRIEF`. O código está certo frente ao contrato documentado. O que se corrige é o arranjo local, voltando os briefs para `~/.forge-contrib/docs/briefs/`, ou um pedido que decida a raiz. O Jarvis deve saber disso antes da release.
- R2 · `hooks/agentes.py:197`. O mesmo R1 do parecer de segurança: um `chmod 0o700` depois do `mkdir` fecha a pasta `run/` que já exista mais aberta. Esforço P.
- R3. Os R2 e R3 do parecer de segurança (config do clone lida de `.forge/config.json` da worktree; o `vigia` sobre `agentes.json`, o C2) ficam para o lote b, como ele propõe.
