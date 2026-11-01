---
tipo: review
contrato: 1
pedido: release-0.31.0
branch: melhoria/release-0.31.0
commit: 0e67326671c6c1e9b42785920d44e5a7b6300dde
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-01
---
# Review: release-0.31.0

Escopo: a leva da 0.31.0 contra a main, `git diff 6f8e238...0e67326` (24 commits da develop até `91d6cc1`, PRs #391, #393, #396 e #403 a #423, todos `MERGED` na develop, mais o commit de release `0e67326`), 162 arquivos, +6515 −261. Li o diff de código inteiro (`hooks/_comum.py`, `hooks/conformidade.py`, `hooks/parecer.py`, `.githooks/pre-push`, `bin/forge-check`, `bin/forge-fechar`, `scripts/suite-paralela.py`), os textos de `docs/hooks.md`, `docs/fechamento-integrador.md` e `.claude/CLAUDE.md`, e corpus, fixtures, specs de mutante e `tests/pesos-d4.json` pela lista. Cada PR já teve review, QA e, com gatilho, segurança próprios; o commit de release tem review e QA em `docs/reviews/release-0.31.md` e `docs/qa/release-0.31.md`. Este parecer julga o conjunto, sem refazer o que eles provaram.

## Achados
- A1 (recomendado) docs/hooks.md:117 · texto antigo: o `--status` ainda diz só saídas 0 e 1 (a c2 trouxe a 2) e que sandbox e terminal não se enxergam (a c4 pôs a trava em ~/.forge-contrib); a linha 115 lista só XDG, TMPDIR e /tmp. Cartão de docs; classe AR-9, que volta a 3 no próximo PR de processo.
- A2 (recomendado) CONTRIBUTING.md:12 · o CLAUDE.md passou a `.githooks/pre-push --suite`, mas CONTRIBUTING.md:12, skills/contribuir-com-o-forge/SKILL.md:39 e .github/pull_request_template.md:14 seguem com `unittest discover`; alinhar no mesmo cartão do A1 (o modelo de PR é do devops).
- A3 (recomendado) hooks/conformidade.py:140 · a A3 cobre `-c` e `git config`, mas `GIT_CONFIG_COUNT/KEY_0/VALUE_0=` e `git --config-env=branch.develop.mergeoptions=X` antes do merge na develop saem 0 (testei no hook). Classe já no item N1 do pedido impl-furo-hook-a, que vai ao dono.
- A4 (recomendado) hooks/conformidade.py:72 · seguem em cartão os A2 e A3 do review impl-furo-hook-a e o A1 da segurança (forge-check opaco com `--t`, `find -exec forge-check`, `xargs forge-check`); todos falham para o lado de gravar o pedido sem o jarvis, sem afrouxar portão de merge.
- A5 (recomendado) .githooks/pre-push:198 · seguem os A2 a A4 do review impl-pre-push (stderr de "recusada" na prova legada, spec de mutação da pasta comum, `assertIn(codigo,(1,2))` que já pode ser 2) e os A2 e A3 da segurança; nenhum muda o portão.
- A6 (recomendado) bin/forge-fechar:383 · seguem o A1 do review impl-fechar-c (`ler | grep -qx` sob pipefail conta rótulo presente como ausente; só atrasa) e, nos pareceres heredoc-rapido, teto-heredoc e impl-n-ci, as recomendações de teste e comentário; nenhuma com defeito provado.
- A7 (recomendado) .githooks/pre-push:17 · o título do PR #418 (e do commit 2270356 na develop) traz o caminho absoluto da pasta pessoal, expandido pelo shell; o código e o CHANGELOG usam `$HOME`. Só histórico, sem conserto sem reescrever; vale escrever `$HOME` entre aspas simples nos títulos.

## Parecer
Aprovado. Nenhum defeito provado, requisito descumprido nem achado de segurança com gatilho no conjunto; os sete achados são recomendações de texto, de processo ou já rastreadas em cartão e não devolvem (`R-REVIEW`).

- **Release (0e67326):** versão 0.31.0 em `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` (0.30.8 → 0.31.0, minor: há `feat` na leva, #408 e #412, e nada quebra os projetos). A seção `[0.31.0] - 2026-11-01` tem 24 entradas (3 Alterado, 21 Corrigido), uma por PR; `[Não publicado]` vazio e `changelog.d/` ausente. `scripts/conferir-release.py --base origin/main`: rc 0, `ok: changelog.d/ sem fragmentos pendentes`, `versão base: 0.30.8 | versão da release: 0.31.0`. A reprodução byte a byte pelo `bin/forge-changelog release` está no parecer `release-0.31`.
- **Escopo (P-CORTE-031 = A):** os itens em andamento (IMPL-FURO-HOOK-A a1 a a5, IMPL-FECHAR-C c1 a c4, IMPL-PRE-PUSH c1 a c5, IMPL-N-CI c1 a c3, IMPL-FORGE-CHECK-A, HEREDOC-RAPIDO passos 1 e 2, CLAUDE-MD-SUITE) mais o TETO-HEREDOC (#414). Nenhum item da 0.32 (heredoc-comentario, heredoc-donos) está no diff.
- **Coerência entre PRs:** o `parecer` passa a ler o comando atrás de lançadores pela mesma `separar_lancadores` do `conformidade` (A2); testei `nice`, `timeout -k`, `env --block-signal`, `stdbuf --output=L`, `time --append` (bloqueiam sem parecer) e `xargs --process-slot-var`, `xargs --eof=E`, `sudo --chroot` (recusados como lançador não lido). As flags de merge da A3 recusam `--squash`, `-Xours`, `-nsours`, `--no-co` e `--squash` depois da branch, e liberam `--no-ff`. A marca curta `__fh` (HEREDOC-RAPIDO) tem fonte única (`marca`, `MARCAS`) e todos os usos antigos de `MARCA + r"\d+__"` foram trocados. O `forge-check` E4 em modo estrito (C3) e o `realpath` do Pedido (C2) se compõem com o `base_do_delta` da 0.30.8 sem divergência.
- **Afrouxamentos:** 14 PRs da leva levam o rótulo `afrouxa-regra` (#391, #393, #396, #407, #409, #412, #413, #415, #416, #417, #418, #420, #422, #423; lido do `gh pr view`), todos `MERGED` com a catraca verde. Nenhum invariante sai de `tests/config.json` (o arquivo não está no diff). Os de efeito no portão endurecem: recusa por estratégia de merge, lançador, rótulo vindo de variável, escrita do `forge-check` por papel, subpasta da trava com escrita alheia, `--status` com saída 2 em vez de "livre".
- **Ferramentas citadas, não refeitas:** CI de push na develop em `91d6cc1`: `success` (e nos três commits anteriores); PR #423: `bateria` e `bateria (python 3.14)` pass, `catraca` pass. `python3 -m unittest tests.test_changelog`: OK (46 testes). `bin/forge-check docs`: rc 0. Mutação e shellcheck estão nos QA de cada PR (specs em `tests/mutantes/`) e no CI; o review não os reexecutou.
- **Teto M14:** julgado em cada PR (os pareceres de QA e de segurança registram as contas, todas abaixo de 150 ou divididas por item, como o lote IMPL-FURO-HOOK-A em 5 PRs, uma classe de `hooks/` por PR). A branch `melhoria/release-0.31.0` leva só o commit de release e pareceres: 0 linhas contáveis, um comportamento (fechar a release).
- **Neutralidade e custo:** nenhum termo de projeto ou de stack nos textos novos; o único caminho pessoal está num título de PR (A7), fora dos arquivos. Nada novo consome serviço pago (`R-NEUTRO`, `R-CUSTO`).
- **Devops:** `git diff --name-only 6f8e238...0e67326` não tem `.github/`, `Dockerfile`, compose nem IaC; a suposição do pedido confere e não há etapa de devops. O resumo do CI (IMPL-N-CI) mexe em `scripts/suite-paralela.py` e já tem parecer de devops próprio (`docs/devops/impl-n-ci.md`). Segurança (E1.2) e QA (E1.3) da leva têm etapa própria (`R-SEGURANCA`, `R-QA`).
