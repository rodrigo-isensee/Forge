---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: a554e34536490ff7af78000f76b67a1652f6e840
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: travas do conformidade na sessão do Forge, revalidação (v0478 E51.14, parecer E51.16)

Volta por delta (`R-REVIEW`): a rodada anterior (E51.12, `commit: 29cbd24`, reprovado com A1) está no git. Delta lido: `forge-check parecer delta` de `29cbd24..a554e34`. No domínio: `hooks/conformidade.py` (`toca_uma_trava`, nova condição em 3842 e docstring), `docs/hooks.md` (item "Travas na sessão do Forge", "um nível só"), 8 fixtures `e51-*` novas e `tests/test_hooks.py` (piso 48). Fora do domínio: o fragmento do changelog e `tests/mutantes/v0479-conformidade-sessao-forge-5.json`.

Gatilhos: hook de conformidade (controle que analisa comando), R-MAIN, R-VERIFY, R-FLUXO (push para a integração, tag v*).

## Achados
- A1 (recomendado) hooks/conformidade.py:3847 · `source /dev/stdin <<< 'git push origin develop'` (e `.`) sai 0 na sessão e 2 no projeto: só `SHELLS` relê o here-string. `bash -c 'echo "B=develop; git push origin \$B" | bash'` sai 0 (era 2 em d235846); `echo … | bash` puro já sai 0 nos dois.

## Detalhe dos achados
**A1.** Evidência: `toca_uma_trava` (hooks/conformidade.py:3842 e 3847) só trata como texto reavaliado o argumento e o here-string de `eval` e de `SHELLS` (hooks/_comum.py:2137). O `source` e o `.` com `/dev/stdin` e here-string executam o texto, mas caem fora; a guarda base recusa a linha como opaca (`heredoc` com ação crítica) e a sessão a solta porque `toca_uma_trava` devolve `False`. Também o shell sem argumento que lê de um pipe dentro do texto reavaliado (`… | bash`) não é lido no nível 1: em d235846 a palavra com `$` virava opaca e recusava.

Caminho de ataque: agente na sessão do Forge envia direto para `develop`, `main` ou com `--force`/`--no-verify` por `source /dev/stdin <<< '…'`. Severidade baixa: não há ganho novo, porque `echo 'git push origin main' | bash` sai 0 no projeto e na sessão (lacuna da guarda base, abaixo), e o `pre-push` local e a proteção do GitHub seguem como outra camada. Por isso é `recomendado`, não bloqueante; volta ao autor e é corrigido antes do merge.

Correção mínima: em `toca_uma_trava`, tratar `source` e `.` como `SHELLS` no here-string (linha 3847) e no nível 1 (linha 3842); e, no nível 1, um shell de `SHELLS` sem argumento (lê a entrada) também fecha na dúvida. Fixtures `e51-*` com as entradas do A1 e com `source /dev/stdin <<< 'git log -1'` (livre). Esforço P. Dono: `dev`.

## O que foi conferido
- **A1 anterior (shell ou `eval` aninhado):** corrigido. As quatro sondas da rodada E51.12 recusam no clone, em `wt/*` e no projeto (saída 2): S1 `bash -c 'bash -c "B=develop; git push origin \$B"'`, S2 `eval 'bash <<< "git push origin main"'`, S3 `bash <<< 'bash <<< "git push origin develop"'`, S4 `bash -c 'bash <<< "git push --force origin x"'`. Viraram as fixtures `e51-wt-push-*-aninhado-*` e `e51-wt-push-force-bash-c-here-string-bloqueia`.
- **Outras formas de aninhamento, todas 2 nos três lugares:** `eval` em `eval`, `eval` em `bash -c`, `zsh -c` em `sh -c`, shell aninhado por `env`, `timeout`, `command`, `exec`, `/bin/bash` e `busybox sh`, três níveis de `bash -c`, heredoc de shell dentro de `bash -c` e o inverso, here-string dentro de heredoc, `bash /dev/stdin <<<` dentro de `bash -c`, `xargs … bash -c`, função, `F=--force` aninhado, alias aninhado e `git tag` aninhado.
- **Corpus legítimo, livre na sessão:** `bash -c 'bash -c "git log -1"'`, `bash -c 'bash -c "git status"'`, `bash -c 'git log -1'`, `bash <<< 'git status'`, `cat <<< 'git push origin develop'`, `git push origin melhoria/x`, `bash -c 'for f in a b; do bash -c "echo $f"; done'`, `eval 'echo oi'`, `git commit -m "$(cat <<'EOF' …)"`. O fecho do 2.º nível só age quando a guarda base já deu recusa opaca, então a leitura aninhada não vira falso positivo.
- **Teste novo:** `python3 -m unittest tests.test_hooks.HookSessaoDoForge` nesta cópia: OK (2 testes, 48 fixtures de conformidade). A suíte inteira roda só no CI; a branch não tem PR nem execução de CI (`gh run list` e `gh pr list` vazios): quem mescla confere o CI verde.

## Fora do achado (lacuna da guarda base, também no projeto)
- O shell que lê o comando de um pipe ou de substituição de processo não é lido: `echo 'git push origin develop' | bash`, `bash <(echo git push origin develop)`, `bash < <(…)` e `source <(…)` saem 0 no projeto e na sessão. Não é deste delta nem da sessão do Forge; vai como melhoria ao Jarvis (dimensão nova da matriz: "entrada do shell por pipe ou por `<(…)`").

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e sondas locais pela `Fixture`/`rodar` de `tests/test_hooks.py` (`sonda_e5116.py`, e `sonda_d235.py` sobre o `git archive` de d235846 para a comparação). Faltaram no PATH: gitleaks, semgrep e zizmor (o delta não toca segredo nem workflow).
