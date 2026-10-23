---
tipo: revisao-seguranca
contrato: 1
pedido: lote-forge-fechar
branch: melhoria/lote-forge-fechar
commit: e5ef160da1bfd40a598d8f49e6f7ca5d13c5301a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: lote-forge-fechar

Escopo: `git diff 1008338..e5ef160` (C1 c2ed46b, C2 c1eaef9, C3 e5ef160): `bin/forge-fechar`, `docs/fechamento-integrador.md`, `tests/test_fechar.py` e o fragmento do changelog. Leitura do script inteiro em e5ef160, não só do diff.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `bin/forge-fechar` conduz o merge na `develop` e o passo 7 e o `--limpar` apagam worktree, branch local e branch remota. Log em arquivo com possível credencial na saída do `gh` e do `git`. Sem chamada de rede nova, sem dependência nova, sem custo (`R-CUSTO`).

## Achados

## Detalhe dos achados
Não há achado bloqueante. Conferi os pontos do brief.

**Apagar só com prova de merge.**
- `--limpar` exige PR `MERGED` com base `develop` para a branch (bin/forge-fechar:285-288); erro de leitura do `gh` ou lista sem `MERGED` para antes de qualquer `git` que apaga (falha fechada; coberto por `test_c3_limpar_sem_prova_de_pr_merged_recusa_e_nao_apaga_nada`, que também prova que PR aberto e PR mesclado na `main` não contam).
- Branch local e remota só somem se o sha é um head de PR mesclado ou já é ancestral da base (`sha_confere`, bin/forge-fechar:182-188, usado em :216 e :233). PR de fork com o mesmo nome de branch não abre caminho: o sha tem de ser igual ao head mesclado, logo o conteúdo já entrou. Base local desatualizada só torna a checagem mais conservadora.
- `main`, `develop` e `homolog` continuam recusados antes de tudo (bin/forge-fechar:53), também no `--limpar` (teste `test_c3_limpar_continua_recusando_main_develop_homolog_e_dry_run_nao_apaga`). O push de apagar usa `refs/heads/<ref>` explícito (:236), sem ambiguidade com tag.
- Nada força: `git worktree remove` sem a opção que força (:201), `git branch -D` só depois do `sha_confere`, `git push --delete` sem lease nem força; o `git worktree prune` só roda com o diretório ausente (:203). `test_script_nunca_usa_force_no_verify_nem_rotulo` segue valendo.
- Passo 7 do fluxo normal: `merged_heads` é o head conferido no passo 2 e preso ao merge por `--match-head-commit` (:421, :433).

**Log.**
- Pasta: `FORGE_FECHAR_LOG_DIR`, senão `$XDG_RUNTIME_DIR` gravável, senão `${TMPDIR:-/tmp}/forge-fechar-logs-<uid>` (:120-126); recusa link simbólico antes e depois do `mkdir` com `umask 077`, dono diferente e modo diferente de 700 (:127-131). Num `/tmp` compartilhado, outro usuário que crie a pasta antes é barrado pelo `-O`, e com o diretório nosso e o bit sticky ninguém o troca depois da checagem. Arquivo por `mktemp` com `umask 077` (600, criação exclusiva); o nome do pedido passa por `tr -c 'A-Za-z0-9._-'` (:134), sem travessia de caminho.
- Retenção (:133): `find -maxdepth 1 -type f -user <uid> -name 'forge-fechar-*.log' -mtime +14 -delete`; sem seguir link, só na pasta própria.
- Máscara (:138-148), sondada em cópia em `$TMPDIR` com valores sintéticos: `GH_TOKEN=`, `ghp_`/`ghs_`/`github_pat_`, `x-access-token:<x>@` na URL, `Authorization:`, `Bearer`, `?access_token=` saem mascarados; `token inválido` fica intacto. A tela recebe o texto original, como antes da entrega.
- `fim: código <n>` sai pelo trap (:169-179), com o código real (inclusive 3).

**Recomendações (não bloqueiam; dono: tech-lead, teste: qa-engineer).**
- R1 (baixa) bin/forge-fechar:197-216: a worktree é removida antes de conferir o sha da branch. No `--limpar` com um PR antigo `MERGED` e a branch reaproveitada com commit novo, a worktree limpa some; os commits ficam (a branch fica pendente), mas os arquivos ignorados pelo git (por exemplo um `.env` local) são apagados por `git worktree remove` sem força (sondado em repositório descartável). Correção mínima: conferir o `sha_confere` da branch local antes de remover a worktree e deixar a worktree pendente quando ele falha. Esforço P.
- R2 (baixa) bin/forge-fechar:226-236: entre o `ls-remote` e o `push --delete` corre a suíte do pre-push (minutos). Um push novo nessa janela seria apagado no remoto (o autor ainda tem o commit local). Branch já mesclada não deveria receber push, por isso é baixa. Correção possível: lease preso ao sha lido no push de apagar, se o pre-push e o teste `test_script_nunca_usa_force_no_verify_nem_rotulo` o admitirem; senão, reler o `ls-remote` logo antes. Esforço P.
- R3 (baixa) tests/test_fechar.py: não há teste que prove que a branch local ou a remota com commit depois do merge não é apagada (o aviso "tem commit que não foi mesclado" de :217 e :234 não aparece nos testes). É o controle central do C3; vale um teste por parte, para o `qa-engineer`.
- R4 (informativa) bin/forge-fechar:140 e :145: chave JSON com hífen (`"x-api-key": "<valor>"`) e JWT solto não são mascarados. Sem caminho realista hoje (`gh`, `git` e `forge-check` não imprimem isso), e o próprio doc diz que a máscara é a segunda barreira, atrás da pasta 700.
- R5 (informativa) bin/forge-fechar:196 e :204: o `awk` lê o caminho da worktree pelo segundo campo; caminho com espaço sai truncado. As worktrees do Forge ficam em `~/.forge-contrib/wt/`, sem espaço; ler o resto da linha evita a dúvida.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, sondas da máscara e do `git worktree remove` em `$TMPDIR`. Faltaram no PATH (lacuna, nada instalado): `gitleaks`, `shellcheck`, `semgrep`, `zizmor`, `osv-scanner`; o shellcheck roda no CI da fábrica.
