---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0478-guardas-parecer
commit: 56bb90b555cc63d4f035dd27d0d35a6541e3647a
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-18
---
# Review de segurança: v0478 (guardas do hook `parecer`, E3.13, revalidação)

Volta por delta. Rodada anterior: `commit c41f7fe5`, no git (E3.8). Delta lido (`forge-check parecer delta`, `c41f7fe5..56bb90b5`): no domínio, `hooks/parecer.py` (`GH_REPO` em `SENSIVEIS`, `REPO_INCERTO`, `repo_indicado`, a recusa em `pasta_do_gh` e as três chamadas em `conferir`), 4 fixtures `incidente-r-copia-alheia-*-gh-repo-*` e `tests/test_hooks_parecer_repo.py` (19 para 23). Fora do domínio, não relido: changelog, `docs/hooks-fixtures.md` e `tests/mutantes/*`.

## Gatilhos
Gatilhos: hook de controle (`hooks/parecer.py`) que guarda o portão de parecer de todos os projetos e do Forge.

## Achados
- A5 (bloqueante) hooks/parecer.py:605 · Fechado nas formas S6 a S9, segue aberto por `source`/`.`: na cópia alheia, `source env.sh; gh pr ready feature/x` (env.sh com `export GH_REPO=<dono>/<forge>`) dá 0, e o PR do Forge sai do rascunho sem parecer (S10, S11).
- A6 (recomendado) hooks/parecer.py:908 · `remotos` lê só `remote.*.url` cru: na cópia alheia com `remote.origin.gh-resolved <dono>/<forge>` ou `url.<forge>.insteadOf <alheio>`, o gh age no Forge e `gh pr ready feature/x` dá 0 (S12, S13).

## Sondas
- S10 · cwd={tmp}/alheio (remoto outro/coisa, `env.sh` = `export GH_REPO=dono/forge`), sessão no clone dono/forge, sem parecer: `source env.sh; gh pr ready feature/x` · espera: código 2 (R-REVIEW) · obtido: código 0
- S11 · mesmo cenário: `. ./env.sh && gh pr ready feature/x` · espera: código 2 · obtido: código 0
- S12 · cwd={tmp}/alheio com `git config remote.origin.gh-resolved dono/forge` (feito antes, ou na mesma linha): `gh pr ready feature/x` · espera: código 2 · obtido: código 0
- S13 · cwd={tmp}/alheio com `git config url.git@github.com:dono/forge.git.insteadOf git@github.com:outro/coisa.git`: `gh pr ready feature/x` · espera: código 2 · obtido: código 0

## Estado dos achados anteriores
- **A5 (bloqueante): fechado nas formas da rodada, aberto pela variante `source`.** S6 a S9 refeitas no head dão 2 com a mensagem nova. Vizinhas que também dão 2: fora de cópia de trabalho, `typeset -x`, `set -a; GH_REPO=...`, `export --`, `read GH_REPO <<<`, `printf -v GH_REPO`, `eval export ...` e `eval "export ..."`, quebra de linha em vez de `;`, subshell `( )`, grupo `{ }`, `bash -c`, `sh -c`, `xargs`, `command`, `env`, `gh pr create` e `-R outro/coisa` com GH_REPO exportado. Com `source` ou `.`, o arquivo lido define o GH_REPO, mas `mexidas_na_linha` só pega o nome das palavras da linha (S10, S11). Fora de cópia de trabalho, `source` dá 2 pela falha fechada de antes.
- **A1 a A4:** fechados na rodada anterior. Não há delta que os toque.
- Corpus de legítimos: cópia alheia sem repositório indicado (0), `gh pr view` com GH_REPO exportado (0), clone da sessão com GH_REPO exportado confere o parecer (2 sem parecer, como antes), `GH_REPO=` no prefixo (2 sem parecer). Muda: `gh pr ready --undo` com GH_REPO exportado fora do clone passa a dar 2. É falso positivo raro, aceitável na falha fechada.

## Detalhe dos achados
**A5 (alta, bloqueante), variante `source`.** Evidência: `hooks/parecer.py:605-606`. Para `source` e `.` (que estão em `LE_VARIAVEL`), o hook junta às mexidas só os argumentos (`env.sh`), nunca o que o arquivo define. Assim `repo_indicado` (`hooks/parecer.py:923`) recebe `mexidas` sem GH_REPO e a cópia alheia volta a liberar. Caminho de ataque, o mesmo do A5: depois da recusa, o agente grava `env.sh` pelo Write numa pasta com `git init` e roda `source env.sh; gh pr ready <branch>`, ou `gh pr merge`. Correção mínima: em `mexidas_na_linha`, `source` e `.` contam como se mexessem em todos os `SENSIVEIS` (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`, `HOME`, `CDPATH`, `GH_REPO`, `GH_CONFIG_DIR`, `XDG_CONFIG_HOME`), porque o arquivo pode definir qualquer um deles. Também serve recusar `source` e `.` na chamada com gh pr como já se faz com `eval`. Fixtures novas: S10 e S11 com recusa. Esforço P. Dono: tech-lead.

**A6 (média, recomendado).** Evidência: `hooks/parecer.py:906-909`. `remotos` lê `git config --get-regexp ^remote\..*\.url$`, a URL crua. O gh decide o repositório de outra forma. Primeiro, pelo `remote.<n>.gh-resolved` com `dono/repo`: provado sem rede, numa cópia com remoto `outro/coisa` e `gh-resolved dono/forge`, `gh repo set-default --view` (gh 2.105.0) imprime `dono/forge`. Segundo, pela URL depois do `insteadOf`, a que `git remote -v` mostra: provado, o remoto `outro/coisa` aparece como `dono/forge`. O `gh pr ready` não rodou contra o GitHub. Fica como recomendado por proporcionalidade: escrever `gh-resolved` com `dono/repo` ou `insteadOf` à mão é menos natural que `export`, e o `gh repo set-default` grava `base` num remoto existente. Correção mínima: `remotos` junta `git ls-remote --get-url <remoto>` de cada remoto (aplica o `insteadOf`) e os valores de `remote.*.gh-resolved` que não são `base`. Fixtures S12 e S13. Esforço P. Dono: tech-lead.

## Riscos aceitos e ferramentas
Nenhum risco aceito. As sondas rodaram com o lançador da suíte (`tests/test_hooks.py`: `Fixture.montar`, `rodar`, `montar_proc`), por um script local fora do repositório. Base: a fixture `incidente-r-copia-alheia-ready-r-bloqueia.json`, variando o cwd, o comando e a configuração do git da cópia alheia. Teste rodado: `python3 -m unittest tests.test_hooks_parecer_repo` (OK, 5 testes). A suíte inteira roda no CI, e este head não tem CI (o brief diz "sem suíte local"). Lacuna: `gitleaks` e `semgrep` não estão no PATH. O delta não traz segredo nem dependência.
