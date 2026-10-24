---
tipo: review
contrato: 1
pedido: lote-fechar-031
branch: melhoria/lote-fechar-031
commit: e0e83a414081a2ebdd6290eab36e85c4522b7c67
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-fechar-031

## Achados
- A5 (recomendado) bin/forge-fechar:164 · classe: mensagem de erro que não resolve. O `chmod u=rwx,go=,g-s` tira o setgid, mas não o setuid de diretório: sonda com 4755 e 6777 fica 4700, e o script para pedindo "chmod 700", que também não tira o bit. Raro (setuid em diretório não tem efeito no Linux) e falha fechada; sugestão: `u=rwx,go=,u-s,g-s` e o modo 4755 no subTest.

## Revalidação por delta (rodada 2)
- Parecer anterior: `0728af911db79e4225cf1c9e9c5c43c690e0ba5f` (reprovado, A1 bloqueante; A2 a A4 recomendados), sobre `432a0a7`.
- `forge-check delta --parecer docs/reviews/lote-fechar-031.md` → intervalo `432a0a7..e0e83a4`; delta lido: `bin/forge-fechar` 11, 148, 162, 164, 723-724, 726-728; `docs/fechamento-integrador.md` 39, 52; `tests/test_fechar_log_check.py` 75, 82; `tests/test_fechar_orfao.py` 117-119, 124-128, 144-145, 152-163. Conferido também `git diff 9dae159..e0e83a4` (1d51c56, fe7f29b, e0e83a4): é o mesmo delta, o parecer de segurança não mexeu em código.
- Já lido (rodada 1, fora do delta, não relido): o resto do diff `d150ec8...432a0a7`, incluindo o passo 7 (linhas 350-460), a saída da worktree e o erro de uso `--sem-limpar` com `--limpar`.
- A1 resolvido: o teste agora põe o PR MERGED no head antigo, faz o commit na worktree e roda `--limpar` de dentro dela; chega ao passo 7, espera código 3, `limpeza: remota=ok worktree=pendente branch=pendente`, o aviso "tem commit que não foi mesclado" e nenhum `git worktree remove`. Mutação em cópia (`$TMPDIR/tech-lead-rev-lf031/mut-a1-2`, sem o `elif` da guarda na linha 377): o teste fica vermelho (`FAILED (failures=1)`, resumo diferente do esperado). Volta a verde sem a mutação.
- A2 resolvido para o setgid: `chmod u=rwx,go=,g-s`; sonda 2755, 1755 e 3700 → 700; subTest 0o2755 com máscara 0o7777. Setuid ficou de fora (A5, recomendado).
- A3 resolvido: o comentário da linha 148 diz que o modo é ajustado, alinhado com as linhas 161-162.
- A4 (e R2 da segurança) resolvido: `pendente, rode:` traz primeiro `forge-fechar <pedido> --ref <ref> --limpar` (que confere o sha); `git branch -D` só sai com a branch local existente; teste novo `test_sem_limpar_sem_branch_local_nao_imprime_branch_d_e_poe_o_limpar_primeiro` e o teste antigo conferem a ordem. Cabeçalho (linha 11) e `docs/fechamento-integrador.md` (linhas 39 e 52) dizem o mesmo que o código.

## Conferências pedidas
- `chmod`: continua depois de `[ ! -L ]`, `mkdir -p`, `[ -d ] && [ ! -L ]` e `[ -O ]` (fora do delta, já lido); link, outro dono e não diretório seguem recusados, cobertos em `test_fechar_log_check.py`. TOCTOU é o R1 da segurança, em cartão (decisão técnica do Jarvis no pedido).
- De dentro da worktree: passo 7 sai para a principal e fecha com 0 (teste da rodada 1); com commit não mesclado, agora com teste que chega ao passo 7 (A1).
- `--sem-limpar`: código 3, limpeza pendente impressa com o `--limpar` primeiro, erro de uso com `--limpar` (teste da rodada 1).
- `logdir` relativo absolutizado: sem mudança no delta; o lugar do log é o mesmo (rodada 1).
- `docs/engineering/achados-recorrentes.md` (PA-7): sem itens; nenhum se aplica.
- Testes: `python3 -m unittest tests.test_fechar tests.test_fechar_log_check tests.test_fechar_orfao` → `Ran 96 tests in 54.941s`, `OK`. Suíte completa, shellcheck e validação do plugin ficam com o pre-push e o CI (regras "ferramenta"), não refeitas.
- Commits do delta: Conventional Commits em português, um por achado. `R-NEUTRO` e `R-CUSTO`: nada novo.

## Parecer
Aprovado. O bloqueante A1 está resolvido e o teste falha sem a guarda; A2 a A4 entraram. Fica o A5, recomendado (setuid em diretório), para um cartão ou para a próxima mexida no trecho.
