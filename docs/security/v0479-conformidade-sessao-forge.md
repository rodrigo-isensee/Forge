---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-sessao-forge
commit: b22efaae57691ca4bc95d62eda389f75b60e6869
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: travas do conformidade na sessão do Forge, revalidação (v0478 E51.22, parecer E51.24)

Volta por delta (`R-REVIEW`): a rodada anterior (E51.20, `commit: bc38552`, aprovado com A2 recomendado) está no git. Delta lido: `forge-check parecer delta` de `bc38552..b22efaa`. No domínio: `hooks/conformidade.py` (`PREFIXOS_DA_FONTE` e `na_posicao_de_programa` em 3811-3817, condição em 3858 e docstring de `toca_uma_trava`), `docs/hooks.md` (item "Travas na sessão do Forge") e 4 fixtures `e51-*` novas. Fora do domínio: o fragmento do changelog e `tests/mutantes/v0479-conformidade-sessao-forge-{6,7}.json`.

Gatilhos: hook de conformidade (controle que analisa comando), R-MAIN, R-VERIFY, R-FLUXO (push para a integração, tag v*).

## Estado dos achados anteriores
- **A2 (E51.20): corrigido.** No nível 1, `source`/`.` na posição de programa (1.ª palavra depois de `ANTES_DO_PROGRAMA` e das atribuições, ou depois só de `builtin`/`command` e das opções deles) é trava com ou sem here-string (`hooks/conformidade.py:3858`); o `.` argumento (`find .`) segue fora. S4 da rodada anterior agora sai 2 (S1 abaixo). Prova de que o pipe é lido, no bash real: `echo 'echo LEU-PIPE' | bash -c 'source /dev/stdin'` e `| bash -c 'builtin . /dev/stdin'` imprimem o texto.

## Sondas
- S1 · `bash -c 'echo "git push origin main" | source /dev/stdin'` (wt) · espera: 2 · obtido: 2 (era 0 em bc38552; projeto: 2)
- S2 · `bash -c 'echo "git push origin main" | . /dev/stdin'` (wt) · espera: 2 · obtido: 2 (era 0)
- S3 · `eval 'echo "git push origin main" | source /dev/stdin'` (wt) · espera: 2 · obtido: 2 (era 0)
- S4 · `bash -c 'echo "git push origin main" | builtin -- source /dev/stdin'` (wt) · espera: 2 · obtido: 2 (era 0)
- S5 · `bash -c 'echo x | find . -path "*docs/reviews*"'` (wt) · espera: 0 · obtido: 0

## O que foi conferido
- **Variantes da família (todas 0→2 na sessão, 2 no projeto):** `builtin .`, `builtin source`, `command source`, `command -p . /dev/fd/0` dentro de `eval`, `{ source /dev/stdin; }`, `( source … )`, `if source …; then`, `! source`, `time source`, `X=1 source`, `\source`, `"source"`, `so""urce`, `builtin builtin source`, `command command .`, `source -- /dev/stdin`, `/proc/self/fd/0`, `|&`, `while read l; do source /dev/stdin; done`, `> f; source f`, `source <(…)`, e o mesmo dentro de `bash <<<` e de `sh -c`.
- **O item só aperta, no total** (confirmação escrita para o rótulo do E51, decisão do dono das 19:09): comparei a sessão (`wt/*`) em bc38552 (`git archive`) e em b22efaa sobre 81 entradas distintas (as das rodadas E51.16 e E51.20, as variantes acima e o corpus legítimo). Nenhuma passou de 2 para 0; as 29 mudanças são todas 0→2, e cada uma executa um push crítico (para `main`/`develop` ou com `--force`) pelo `source`/`.` lendo o pipe, arquivo ou `<(…)` no texto reavaliado. A condição nova em 3858 só soma um `or` a uma recusa já existente, no nível 1, que só é lido quando a guarda base já deu recusa opaca; nada foi retirado. Somado às rodadas E51.16 e E51.20 (onde as únicas 2→0 eram `eval <<< …`, que não executa nada), nenhuma recusa de `R-MAIN`, `R-VERIFY` ou do alvo opaco que proteja um ato some.
- **Corpus legítimo, livre na sessão:** `bash -c 'echo x | . ~/.bashrc'`, `bash -c 'echo x | source ~/.bashrc'`, `bash -c 'echo x | source ./env.sh; git status'`, `bash -c 'source ~/.bashrc; git log -1'`, `bash -c '. ./x.sh; git status'`, `bash -c 'git log | source /dev/stdin'`, `bash -c 'find . -name "*.md" | head -1'`, `bash -c 'ls . | grep x'`, `bash -c 'cp a . && git status'`, `bash -c 'echo x | command -v .'`, `git push origin melhoria/x`. O `source`/`.` como programa só vira trava quando a linha já tem recusa opaca com ação crítica; sem ela, passa.
- **Teste novo:** `python3 -m unittest tests.test_hooks.HookSessaoDoForge` nesta cópia: OK (2 testes; 59 fixtures `e51-*`). A suíte inteira roda só no CI; a branch não tem PR nem execução de CI (`gh pr list` e `gh run list` vazios): quem mescla confere o CI verde.

## Fora do achado (lacuna da guarda base, também no projeto)
- Sem mudança: o shell ou o `source` que lê o pipe no nível 0 (`echo 'git push origin main' | source /dev/stdin`) sai 0 no projeto e na sessão; registrado em `docs/hooks.md` (cartão CONFORMIDADE-SUBSTITUICAO-NO-PROJETO).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do delta e sondas locais pela `Fixture`/`rodar` de `tests/test_hooks.py` sobre as duas árvores. Faltaram no PATH: gitleaks, semgrep e zizmor (o delta não toca segredo nem workflow).
