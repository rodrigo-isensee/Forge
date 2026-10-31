---
tipo: revisao-seguranca
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c1
commit: f38de40811c8b2b8bde7c24104acb6db4ab4c02c
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-fechar-c (branch c1)

Diff lido: `234dbe0..f38de40` (bin/forge-fechar, tests/test_fechar_r1_worktree.py, docs/fechamento-integrador.md, changelog.d/impl-fechar-c-c1.md). Também relidos inteiros, no commit revisado, `limpar_entrega`, `sha_confere`, `remoto_exato` e o bloco do `--sem-limpar`.

**Item entregue:** E1 do pedido, FECHAR-R1-WORKTREE com o C1-2 do modelo de ameaças (`docs/security/ameacas/fechar-c.md`, SEC-FECHARC-2).

**M14 (agents/tech-lead.md:19):** um comportamento só (a pendência por commit sem merge imprime leitura, não comando que apaga, em toda a família: `limpar_entrega` e `--sem-limpar`). Código e teste: 192 linhas (48+7 em `bin/forge-fechar`, 137 no teste), acima do teto; nenhum arquivo em `hooks/` nem em `PROTEGIDOS` (`tests/catraca.py:43-45`), então a exceção vale, já aceita no review do tech-lead; o PR precisa levar a linha `teto: excedido, 192 linhas, <motivo>` no corpo. Cumpre, com essa condição no PR.

## Gatilhos
`R-SEGURANCA`: controles do Forge (`bin/forge-fechar` conduz o merge e imprime e roda remoções; está em `SENSIVEIS`).

## Achados

## Detalhe dos achados
Conferência dos controles do modelo de ameaças:
- C1-1: a local decide por `sha_local` (`bin/forge-fechar:396`), a remota por `sha_remoto`, com a leitura própria em `rem_leitura` (`:506`); local mesclada com remota sem merge imprime leitura só para a remota.
- C1-2: com commit sem merge, nenhuma linha traz `git worktree remove`, `git branch -D` ou `git push origin --delete` para a ref: aviso de quem está na worktree principal (`:408-409`), pendência da worktree (`:445-448`), da branch (`:488-490`), da remota (`:527-528`) e o `--sem-limpar` (`:818-831`), que relê o sha local e o remoto e, se a leitura remota falha, imprime só um comentário, sem comando. Falha fechada.
- C1-3: `leitura_sem_merge` (`:382-384`) imprime só um comentário e `git log --oneline`, com os argumentos em `printf '%q'`, a ref por `refs/heads/` e a remota pelo sha lido do servidor; sem `&&`, `;` nem `|`.
- Casos de abuso AB-C1-1 a AB-C1-7 cobertos em `tests/test_fechar_r1_worktree.py`, com asserções de ausência (discriminam). Rodados aqui: `test_fechar_r1_worktree`, `test_fechar_sha_arvore` e `test_fechar_orfao`, 27 testes OK.
- Informativo, sem achado: o comentário de `:815` ainda diz que os comandos soltos não conferem nada; agora o bloco relê o sha. É texto, não comportamento.

Sem caminho de ataque novo: a mudança só troca linhas impressas que apagam por linhas de leitura; nada passa a executar.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e do script, testes da suíte. Faltaram no PATH: `shellcheck`, `gitleaks` e `semgrep` (lacuna; o CI roda o shellcheck).
