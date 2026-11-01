---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.31.0
branch: melhoria/release-0.31.0
commit: 0e67326671c6c1e9b42785920d44e5a7b6300dde
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-01
---
# Review de segurança: release-0.31.0

Escopo: a leva da 0.31.0 contra a main, `git diff 6f8e238...0e67326` (24 commits da develop até `91d6cc1` mais o commit de release `0e67326`). Li o diff de código inteiro dos controles (`hooks/_comum.py`, `hooks/conformidade.py`, `hooks/parecer.py`, `.githooks/pre-push`, `bin/forge-check`, `bin/forge-fechar`, `scripts/suite-paralela.py`) e os achados em aberto dos pareceres de segurança de cada PR (`docs/security/heredoc-rapido.md`, `impl-fechar-c.md`, `impl-forge-check-a.md`, `impl-furo-hook-a.md`, `impl-n-ci.md`, `impl-pre-push.md`, `teto-heredoc.md`). Cada PR já teve parecer de segurança próprio, todos aprovados. Este parecer julga o conjunto e não refaz o que eles provaram.

## Gatilhos
`R-SEGURANCA`: controles do Forge (hooks `conformidade` e `parecer`, `.githooks/pre-push`, `bin/forge-check`, `bin/forge-fechar`, guarda da suíte em `scripts/suite-paralela.py`). A leva não toca `.github/`, `Dockerfile`, compose nem IaC: `git diff --name-only 6f8e238...0e67326 | grep -E '^\.github/|Dockerfile|compose|\.tf$|helm|k8s'` sai sem linha (rc 1). A suposição do pedido sobre devops confere.

## Achados
- A1 (recomendado) hooks/conformidade.py:140 · A3 do merge cobre `-c` e `git config`, mas a config do merge vinda do ambiente passa: `GIT_CONFIG_COUNT/KEY_0/VALUE_0`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_GLOBAL=<arquivo>` e `git --config-env=` antes do `git merge` na develop saem 0 (sonda). Dimensão nova da matriz: ambiente.
- A2 (recomendado) hooks/conformidade.py:69 · seguem em cartão o A1 e o A2 do parecer impl-furo-hook-a (forge-check por find -exec, xargs, glob, chaves, stdin ou cópia; `--t` com nome opaco). Todos gravam o pedido sem o jarvis por contorno deliberado, a mesma classe do N6 já aceito; nenhum afrouxa portão de merge.
- A3 (recomendado) .githooks/pre-push:22 · a trava comum em $HOME/.forge-contrib aceita a pasta-mãe por `-e` ou `-L`; a subpasta forge-<uid> é conferida (dona, não link, sem escrita alheia), então não há caminho de outro usuário. Só documentar em docs/hooks.md junto do A1 do review da leva.

## Detalhe dos achados
**A1, recomendado.** Evidência: `hooks/conformidade.py:140` (`CONFIG_DO_MERGE`) é consultado só em `git -c` e em `git config`; as variáveis de ambiente do git não passam por ele. Sondas pelo harness de fixtures (`Fixture`/`rodar` de `tests/test_hooks.py`, papel tech-lead, na develop, sobre a fixture `merge-flag-squash-bloqueia`), todas com saída 0 no `conformidade`: `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=branch.develop.mergeoptions GIT_CONFIG_VALUE_0=--squash git merge feature/x`; a mesma com `export …;` antes; `GIT_CONFIG_PARAMETERS="'branch.develop.mergeoptions'='--squash'" git merge feature/x`; `GIT_CONFIG_GLOBAL=/tmp/c git merge feature/x`; `git --config-env=branch.develop.mergeoptions=V git merge feature/x`. Contraprovas que saem 2: `--squash`, `-Xours`, `--no-ff --no-commit`, `-n -s ours`, `--strat ours`, `git -c pull.twohead=ours pull`. O code review da leva achou o mesmo (A3 dele) com as duas primeiras formas; aqui entram `GIT_CONFIG_PARAMETERS` e `GIT_CONFIG_GLOBAL` para o cartão sair com a família inteira. Caminho: só deliberado. A sessão escolhe pôr `-s ours` ou `--squash` no ambiente para mesclar na develop local descartando o que o review leu. O efeito fica na cópia local: o envio direto para a develop é barrado pelo pre-push e pelo `conformidade` (`R-MAIN`, `R-FLUXO`), e o merge real da integração passa pelo `gh pr merge --match-head-commit` do `forge-fechar`, que o `parecer` confere. Severidade baixa. Correção mínima: no `git` da integração, recusar o merge ou pull quando a linha (ou um `export` anterior) define qualquer um de `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_*`, `GIT_CONFIG_VALUE_*`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG` ou a opção global `--config-env`; fixtures de bloqueio para cada uma e uma de libera sem variável. Esforço P. Dono: tech-lead. Já está no item N1 do pedido impl-furo-hook-a, que vai ao dono.

**A2, recomendado.** Evidência e sondas no parecer `docs/security/impl-furo-hook-a.md` (A1 e A2); no HEAD da leva, `hooks/conformidade.py:69-80` não mudou depois daquele parecer. Caminho deliberado, severidade média pelo ativo (registro de decisão do dono), baixa pela probabilidade. Correção mínima e dono como lá (tech-lead, esforço M e P).

**A3, recomendado.** Evidência: `.githooks/pre-push:22-27`. A pasta-mãe `$HOME/.forge-contrib` é escolhida se existe ou é link, sem conferir dona nem modo; a trava fica na subpasta `forge-<uid>`, que é recusada se é link, se não é do próprio usuário ou se tem escrita de grupo ou de outros (`:43-50`). Só o próprio usuário cria entradas no `$HOME`, então trocar a pasta-mãe por um link exige já ter a conta. Sem caminho de ataque realista: informativo. As provas `.verde` e `.dirigida` seguem na pasta de cada lado (`trava_arquivo criar legado`, `:198`); sem pasta conferida, `verde` e `dirigida` ficam vazios, o `anotar` não grava e o `tem_prova` não acha prova: falha fechada, roda tudo. Correção mínima: a linha de `docs/hooks.md` sobre a pasta da trava cita `$HOME/.forge-contrib` e a conferência da subpasta, no mesmo cartão de docs do A1 do review da leva. Esforço P. Dono: tech-lead.

**Conferências sem achado (o conjunto):**
- `hooks/parecer.py:261-287` (lançadores, PARECER-LANCADOR): sondas com saída 2 sem parecer para `nice`, `command`, `exec`, `stdbuf -o0`, `nohup`, `setsid`, `env -i`, `time`, `sudo -u`, pipe com `cat`; recusa como lançador não lido para `ionice`, `busybox`, `find -execdir`, `xargs`. O `cd` atrás de lançador não muda a pasta lida.
- `hooks/conformidade.py` A5 (rótulo `afrouxa-regra`): valor por variável, substituição, opção sem valor no fim, `xargs`, `alias` do shell e do `gh`, escape `\u` no `gh api` exigem o dono; o escape malformado conta como ilegível (falha fechada).
- `hooks/conformidade.py` `git_config`: `set`/`unset` do git 2.46, `--`, `--comment`, `--value` e `--worktree` com chave de merge barram; a dica não sugere `--worktree` para as chaves do merge.
- `.githooks/pre-push`: `--status` sai 2 em todo erro de conferência (não vira "livre"); o texto da trava segue filtrado pelo C-14 (já na main), o que fecha o A1 do parecer impl-pre-push; o `ns` gravado só tem dígitos.
- `bin/forge-check`: `caminho_do_pedido` só expande `~/` pelo HOME, procura caminho relativo só dentro de `docs/pedidos` com `realpath` (`dentro_da_raiz`); `mesmo_pedido` aceita caminho só absoluto e por `realpath`; o E4 em modo estrito reprova quando o git falha, em vez de filtrar para nada.
- `bin/forge-fechar`: commit não mesclado (local ou remoto, pelo sha relido) imprime leitura escapada por `%q`, nunca comando que apaga; o `--dry-run` só lê a ref local; a promoção de execução da Catraca a "velha" exige uma leitura do rótulo ausente, e a velha nunca libera o merge sozinha (a nova decide).
- `scripts/suite-paralela.py`: o resumo do CI sai depois do veredito, só nomes de unidade e números, e qualquer erro dele vira linha no stderr sem mudar o código de saída; `conferir_trava` não mudou.
- Testes: nenhum invariante sai de `tests/config.json` (fora do diff); as mudanças em testes existentes só endurecem (HOME isolado nos testes da trava, leitura do rótulo um passo depois) ou trocam nomes de função.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas locais pelo harness de fixtures da própria worktree (nenhuma contra repositório real, rede ou produção). `gitleaks`, `semgrep`, `osv-scanner`, `zizmor`, `actionlint` e `shellcheck` não estão no PATH (lacuna registrada; o diff não traz segredo, dependência nem workflow; o shellcheck roda no CI e nos QA de cada PR).
