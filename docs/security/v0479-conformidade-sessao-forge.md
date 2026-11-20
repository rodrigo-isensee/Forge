---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: bc385524277c69f47a6cb0f7ed5d37cee5706626
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: travas do conformidade na sessão do Forge, revalidação (v0478 E51.18, parecer E51.20)

Volta por delta (`R-REVIEW`): a rodada anterior (E51.16, `commit: a554e34`, aprovado com A1 recomendado) está no git. Delta lido: `forge-check parecer delta` de `a554e34..bc38552`. No domínio: `hooks/conformidade.py` (`FONTES` em 3810, `toca_uma_trava` 3847-3857 e docstring), `docs/hooks.md` (item "Travas na sessão do Forge"), 7 fixtures `e51-*` novas e `tests/test_hooks.py`. Fora do domínio: o fragmento do changelog e `tests/mutantes/v0479-conformidade-sessao-forge-{4,5,6}.json`.

Gatilhos: hook de conformidade (controle que analisa comando), R-MAIN, R-VERIFY, R-FLUXO (push para a integração, tag v*).

## Achados
- A2 (recomendado) hooks/conformidade.py:3851 · No nível 1, `source`/`.` só é trava com here-string: `bash -c 'echo "git push origin main" | source /dev/stdin'` (também `. /dev/stdin`, `builtin source` e dentro de `eval '…'`) sai 0 na sessão e 2 no projeto; o `source /dev/stdin` lê o pipe.

## Estado dos achados anteriores
- **A1 (E51.16): corrigido em parte; o que resta é o A2.** `source`/`.` com here-string no nível 0 e no 1 e o shell que lê um pipe dentro do texto reavaliado agora recusam (saída 2) no clone, em `wt/*` e no projeto: S1, S2 e S3 abaixo, mais `--force`/`--no-verify` por `source`, `builtin source`, `command source`, `. /dev/fd/0 <<<`, `<<<"…"` sem espaço, `| sh`, `| bash -s`, `source <<<` dentro de `bash -c`, de `eval` e de `bash <<<`. Ficou de fora o `source`/`.` lendo o pipe no nível 1 (A2), que a correção mínima do A1 cobria ("tratar `source` e `.` como `SHELLS` no nível 1").

## Detalhe dos achados
**A2.** Evidência: `hooks/conformidade.py:3851` exige `aqui` (here-string) para o `source`/`.` no nível 1, mas o `source /dev/stdin` (e `/dev/fd/0`) executa também o que chega por pipe; a guarda base recusa a linha como opaca (`bash -c` com ação crítica) e a sessão a solta porque `toca_uma_trava` devolve `False`. Prova de que o pipe é lido: `echo 'echo LEU2' | bash -c 'source /dev/stdin'` imprime `LEU2`.

Caminho de ataque: agente na sessão do Forge envia direto para `main`/`develop`, ou com `--force`/`--no-verify`, por `bash -c 'echo "…" | source /dev/stdin'`. Severidade baixa: `echo 'git push origin main' | source /dev/stdin` no nível 0 já sai 0 no projeto e na sessão (lacuna da guarda base, abaixo), e o `pre-push` local e a proteção do GitHub seguem como outra camada. Por isso é `recomendado`; volta ao autor e é corrigido antes do merge.

Correção mínima: no nível 1, `source`/`.` na posição de programa (a 1.ª palavra depois de `ANTES_DO_PROGRAMA`, ou depois de `builtin`/`command`) é trava com ou sem here-string, como o shell em 3847 (fecha na dúvida); o `.` como argumento (`find .`) segue fora. Fixture `e51-wt-push-pipe-para-source-aninhado-bloqueia` com `bash -c 'echo "git push origin main" | source /dev/stdin'`; a `e51-wt-ponto-aninhado-libera` continua livre. Esforço P. Dono: `dev`.

## Sondas
- S1 · `source /dev/stdin <<< 'git push origin develop'` (wt) · espera: 2 · obtido: 2 (era 0 em a554e34)
- S2 · `. /dev/stdin <<< 'git push origin develop'` (wt) · espera: 2 · obtido: 2 (era 0)
- S3 · `bash -c 'echo "B=develop; git push origin \$B" | bash'` (wt) · espera: 2 · obtido: 2 (era 0)
- S4 · `bash -c 'echo "git push origin main" | source /dev/stdin'` (wt) · espera: 2 · obtido: 0 (projeto: 2)
- S5 · `bash -c 'eval <<< "git push origin main"'` (wt) · espera: 0 (o eval não lê a entrada) · obtido: 0 (era 2 em a554e34)

## O que foi conferido
- **Eval com here-string fora do nível 1 (3849):** não afrouxa. O `eval` sem argumento não lê a entrada: `bash -c 'eval <<< "echo LEU"; echo fim'` imprime só `fim`. As três entradas que passaram de 2 para 0 (`bash -c 'eval <<< "…"'`, com `\$B`, e `eval 'eval <<< "…"'`) não executam nada. O `eval` com argumento (`eval "$(cat)" <<< …`, `eval $(echo git push …)`) segue trava; `bash -c 'echo … | eval'` sai 0 na sessão e também não executa.
- **O item só aperta, no total** (para o rótulo da catraca): comparei a sessão (`wt/*`) em a554e34 e em bc38552 sobre 54 entradas (as do A1, as do A2, o corpus legítimo e os casos de `eval`). Todas as mudanças são 0→2 em entradas que executam uma trava, exceto as três de `eval <<< …` acima, 2→0 em entradas inócuas. As condições novas em 3847 e 3851 só somam recusas no nível 1, que só é lido quando a guarda base já deu recusa opaca; a 3849 tira só o caso que não executa. Nenhuma recusa de `R-MAIN`, `R-VERIFY` ou do alvo opaco que proteja um ato some.
- **Corpus legítimo, livre na sessão e no projeto:** `source /dev/stdin <<< 'git log -1'`, `. /dev/stdin <<< 'git status'`, `bash -c 'find . -name "*.md" | head -1'`, `bash -c 'source ~/.bashrc; git log -1'`, `bash -c '. ./x.sh; git status'`, `bash -c 'git log | head'`, `bash -c 'ls | bash'`, `bash -c 'cat x | sh'`, `bash -c 'eval'`, `git push origin melhoria/x`, `bash -c 'echo x | . ~/.bashrc'`.
- **Teste novo:** `python3 -m unittest tests.test_hooks.HookSessaoDoForge` nesta cópia: OK (2 testes; 55 fixtures `e51-*`). A suíte inteira roda só no CI; a branch não tem PR nem execução de CI (`gh pr list` e `gh run list` vazios): quem mescla confere o CI verde.

## Fora do achado (lacuna da guarda base, também no projeto)
- Sem mudança desde E51.16, agora registrada em `docs/hooks.md` (cartão CONFORMIDADE-SUBSTITUICAO-NO-PROJETO): o shell ou o `source` que lê o comando de um pipe, de arquivo ou de `<(…)` no nível 0 não é lido (`echo 'git push origin main' | source /dev/stdin` e `| bash` saem 0 no projeto e na sessão).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e sondas locais pela `Fixture`/`rodar` de `tests/test_hooks.py` (`sonda_e5120.py`, e `sonda_old.py` sobre o `git archive` de a554e34 para a comparação). Faltaram no PATH: gitleaks, semgrep e zizmor (o delta não toca segredo nem workflow).
