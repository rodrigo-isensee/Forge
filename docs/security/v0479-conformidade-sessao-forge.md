---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: 29cbd24dc696ec318b4a53eb9322f46f149ae713
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: travas do conformidade na sessão do Forge, revalidação (v0478 E51.10, parecer E51.12)

Volta por delta (`R-REVIEW`): a rodada anterior (E51.8, `commit: d235846`, aprovado) está no git. Delta lido: `forge-check parecer delta` de `d235846..29cbd24`. No domínio: `hooks/conformidade.py` (marca `trava=TRAVA_OPACA` nas recusas do alias, `pr edit` em `GH_FORA_DAS_TRAVAS`, `toca_uma_trava` com heredoc e here-string, `texto_reavaliado`), `docs/hooks.md` (item "Travas na sessão do Forge"), 15 fixtures `e51-*`/`rverify-fp-*` novas e `tests/test_hooks.py`. Fora do domínio: o fragmento do changelog e três `tests/mutantes/*.json`.

Gatilhos: hook de conformidade (controle que analisa comando), R-MAIN, R-VERIFY, R-FLUXO (push para a integração, tag v*).

## Achados
- A1 (bloqueante) hooks/conformidade.py:3842 · a releitura pelo valor só olha um nível: shell ou `eval` dentro do texto reavaliado fica livre. `bash -c 'bash -c "B=develop; git push origin \$B"'` recusava em d235846 e agora sai 0 (regressão); `eval 'bash <<< "git push origin main"'` sai 0 na sessão e 2 no projeto.

## Detalhe dos achados
**A1.** `toca_uma_trava` (hooks/conformidade.py:3809-3846) chama a si mesma com `nivel=1`. Nesse nível, as duas condições de shell (3842 e 3844) exigem `not nivel`: o `bash -c`, o `eval` e o `bash <<<` de dentro não são lidos, e o comando simples cai em `return False`. Antes do delta, a palavra com `$` virava `"$"` e a releitura recusava (opaca). Agora `texto_reavaliado` (3849) devolve o valor, e o `$B` só aparece no 2.º nível, que não é lido.

Caminho de ataque: um agente na sessão do Forge (clone ou `wt/*`), por erro ou por instrução injetada, aninha um shell e envia direto para `main`, para `develop` ou com `--force`. O projeto recusa a mesma linha. Severidade alta: é a trava de `R-MAIN`/`R-VERIFY` que some na sessão do Forge (o `pre-push` local e a proteção do GitHub seguem como outra camada).

Correção mínima: no nível 1, o `eval` ou um shell (`SHELLS`) com texto a reavaliar (argumento depois do programa ou here-string) devolve `True`, fechando na dúvida. Outra saída é a recursão seguir até o limite de profundidade que a guarda já usa. Somar fixtures `e51-*` com as quatro sondas abaixo e um mutante que tira a condição. Dono: `dev`.

## Sondas
Hook desta cópia, pela `Fixture`/`rodar` de `tests/test_hooks.py`. Sessão do Forge: `forge: false`, `plugin.json` do Forge, `CLAUDE_PROJECT_DIR` na raiz, papel `forge:dev`, cwd em `~/.forge-contrib/wt/x`. "Projeto" é a mesma fixture com `.forge/versao`.
- S1 · `bash -c 'bash -c "B=develop; git push origin \$B"'` · espera: 2 (era 2 em d235846; projeto 2) · obtido: 0
- S2 · `eval 'bash <<< "git push origin main"'` · espera: 2 (projeto 2) · obtido: 0
- S3 · `bash <<< 'bash <<< "git push origin develop"'` · espera: 2 (projeto 2) · obtido: 0
- S4 · `bash -c 'bash <<< "git push --force origin x"'` · espera: 2 (projeto 2) · obtido: 0

## O que foi conferido
- **Alias e `-c` como trava (A1 do review E51.7):** corrigido. As cinco recusas do alias levam `trava=TRAVA_OPACA` (2630, 2637, 2640, 2647, 2753). `git -c alias.p=push p origin develop` e `... melhoria/x` recusam no clone e em `wt/*`; em d235846 saíam 0.
- **Here-string de shell (A1 do QA E51.9):** corrigido no 1.º nível. Recusam no clone e em `wt/*`: `bash <<<` com push para `develop`, para `HEAD:develop`, com `$B`, com `--force`, com `--no-verify` (zsh), com alias na linha, com crase escapada, sem espaço (`bash<<<'…'`), com escapes, por `env` e por `/bin/bash`. Também recusam o heredoc de shell com `$B` e `cat <<'X' | bash`.
- **Leitura pelo valor no 1.º nível:** `bash -c` e `eval` com `$B` e com `$(echo git)` recusam. `bash -c 'bash -c "git push origin develop"'` (literal) recusa pela guarda base. O caminho aberto está só no 2.º nível (A1).
- **Corpus legítimo, livre:** `git log|status`, `bash -c 'git log -1'`, `bash <<< 'git status'`, `bash <<< 'echo oi'`, `cat <<< '…push…'`, `gh pr edit 12 --body|--add-label`, `gh pr edit 3 --title "$(git log …)"`, `git commit -m "$(cat <<'EOF' …)"`, `python3 - <<'EOF'`, `echo "$(git rev-parse HEAD)"`, `git push origin melhoria/x`.
- **Teste novo:** `python3 -m unittest tests.test_hooks.HookSessaoDoForge.test_travas_do_conformidade` nesta cópia: OK (40 fixtures). A suíte inteira roda só no CI. A branch não tem PR nem execução de CI (`gh run list` vazio): quem mescla confere.

## Fora do achado (sem caminho novo de ganho)
- `python3 - <<'X'` ou `perl - <<'X'` com `os.system('git push origin develop')` sai 0 na sessão (escolha do delta) e 2 no projeto. Mas `python3 -c "…subprocess.run(['git','push',…])"` já sai 0 nos dois, então a sessão não ganha poder novo. É a lacuna antiga do interpretador, registrada na rodada anterior.
- `N=1; gh pr edit $N --base main` sai 0 na sessão e 2 (opaca) no projeto. Trocar a base não mescla, e o merge segue barrado por `R-MAIN`.
- `bash <<< 'git tag v9.9.9'`, `git tag -d` e `git branch -D develop` no here-string saem 0 na sessão e no projeto: a guarda base só lê o here-string pelo `CRITICO`. A tag local só pesa ao ser enviada, e o envio recusa. Vai como melhoria ao Jarvis, junto das lacunas de substituição já registradas.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e sondas locais (`sonda_e5112.py` e `sonda_d235.py` no scratchpad da sessão; a segunda roda sobre o `git archive` de d235846). Faltaram no PATH: gitleaks, semgrep e zizmor (o delta não toca segredo nem workflow).
