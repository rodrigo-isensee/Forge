---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-conformidade-trilha
commit: 0f4facab2db2b2aa60107dfdfac9cad6f9814560
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E63.10, revalidação da trilha CONFORMIDADE-SEGURANCA do `hooks/conformidade.py`, head 0f4facab)

Revalidação (H3, `R-REVIEW`) do parecer reprovado no head e48a2e60 (A1 bloqueante, A2 recomendado). Li só o delta de
`forge-check parecer delta docs/reviews/v0479-conformidade-trilha.md`: intervalo `e48a2e60..0f4facab`, domínio "código e
testes", `hooks/conformidade.py`, `docs/hooks.md`, `docs/hooks-fixtures.md`, o fragmento do changelog, 27 fixtures novas
(`cpb-*`, `idx-autocorrect-*`, `sub-pipe-bash-*`, `sub-sessao-forge-pipe-bash-*`, `sub-shell-entrada-de-arquivo-*`), os
mutantes `-10` a `-12` (e ajustes nos `-3`, `-6`, `-8` e no principal) e a prova do custo do corpus. Fora desse domínio
nada foi relido.

## O que li no delta
- A1 (meu): `sem_copia_de_wt` (`hooks/conformidade.py:3821`) troca por NUL cada caminho literal e absoluto (`~`, `$HOME`
  ou `/`) de uma cópia de `wt/`, pelo caminho real, antes do `CONTROLE_NO_TEXTO`; é lista positiva: qualquer sinal de subida
  ou montagem (`..` também partido por aspas, crase, chave, escape, `cd -`, `dirname`...) ou `$` fora de `TMPDIR`, `HOME`
  e do nome só atribuído a uma cópia devolve o texto intacto. `controle_no_texto` (`:3921`) aplica isso só ao padrão largo.
  Contraprovas no corpus: `cpb-dev-wt-subida-ponto-ponto`, `-nome-de-fora`, `-read-reatribui`, `-substituicao`,
  `-fora-do-contrib` e `cpb-dev-continuacao-pedidos` recusam.
- A2 (meu): resolvido por limite declarado em `docs/hooks.md:56` ("rode a leitura fora daquela pasta ou com a saída num
  caminho literal") com a contraprova `cpb-tech-lead-pasta-do-controle-ls-briefs-tmpdir-bloqueia`.
- A12 da segurança: `entrada_de_arquivo` (`:4075`) só libera o shell com a última redireção da entrada para um arquivo
  comum (nenhum segmento `dev`, `proc`, `fd`, `..`, `stdin`, último não numérico); A13: `help.autocorrect` em `-c` e no
  `git config` (também com `--worktree`) entra como o alias. Legível, comentário com a origem de cada guarda.

## Sondas de caso legítimo (hook do 0f4facab contra o do e48a2e60, mesma fixture montada)
Roteiro `~/.forge-contrib/wt/tl-e6310/sondas.py`, saída em `~/.forge-contrib/wt/tl-e6310/sondas.txt`: 44 linhas, tech-lead,
clone do Forge com `HOME` e `~/.forge-contrib` montados, pasta corrente no projeto, em `wt/x` ou na pasta de controle.
- **passaram a liberar** (rc 2 → 0): S1, S1 com caminho absoluto, S2, `cd $HOME/.forge-contrib/wt/x && sed … > $TMPDIR/e.txt`,
  `cd ~/.forge-contrib/wt/x && cat docs/pedidos/v1.md | head -40 > $TMPDIR/e.txt`,
  `cd ~/.forge-contrib/wt/x && git diff --stat > $TMPDIR/s.txt; ls docs/pedidos docs/briefs`;
- **nenhuma passou a recusar**. Iguais (rc 0 nos dois): leitura do pedido e do brief do clone e de `~/.forge-contrib/docs/`,
  `forge-check parecer delta`/`proximo` com saída em `wt/`, `git pull --rebase … && git push …`, o envio com log e `rc=` e a
  espera da `esperar-estado`, a suíte por nome com saída em `wt/`, rodar e ler o oráculo, `git reset --hard`, `git stage`,
  `xargs git diff`, `bash -n`/`env bash`/`. venv/bin/activate` antes do push, `printf … | bash`, `git --git-dir`,
  `bash < scripts/x.sh` (com e sem push), `bash < ~/x.sh` e `< /root/x.sh` com push, `git config --get help.autocorrect`,
  `git -c color.ui=never log`, `git config --worktree user.name`;
- iguais (rc 2 nos dois, já recusavam no e48a2e60, mensagem "`$X` com ação crítica"): S3 (agora limite declarado) e o
  shell com a entrada por variável antes do push (`bash < $TMPDIR/x.sh`, `< "$HOME/x.sh"`, `s=…; bash < $s`,
  `bash scripts/x.sh < $TMPDIR/in.txt`).

## Ferramentas (citadas, não refeitas)
- Testes do domínio, por nome, no head 0f4facab: `HookSessaoDoForge.test_travas_do_conformidade`,
  `Hooks.test_fixtures_da_substituicao_no_projeto`, `test_fixtures_do_controle_so_jarvis`,
  `test_fixtures_da_escrita_no_indice` → `Ran 4 tests in 17.264s OK`.
- `bin/forge-mutante --processos 1 --ids X1,X3 tests/mutantes/v0479-conformidade-trilha-10.json` →
  `X1 · morreu · hooks/conformidade.py:3827`, `X3 · morreu · hooks/conformidade.py:3833`.
- Suíte inteira: sem PR, sem run de CI na branch (`gh run list` vazio); não rerrodada aqui.

## Sondas
- S1 · tech-lead, cwd do projeto: `cd ~/.forge-contrib/wt/x && sed -n 1,5p docs/pedidos/v1.md > $TMPDIR/e.txt` · espera: rc 0 · obtido: rc 0 (e48a2e60: rc 2)
- S2 · tech-lead, cwd ~/.forge-contrib/wt/x: `f=~/.forge-contrib/wt/r.txt; grep -c x docs/pedidos/v1.md > $f` · espera: rc 0 · obtido: rc 0 (e48a2e60: rc 2)
- S3 · tech-lead, cwd ~/.forge-contrib: `ls docs/briefs > $TMPDIR/b.txt` · espera: rc 2, limite declarado em docs/hooks.md:56 · obtido: rc 2

## Parecer
Aprovado no head 0f4facab. O A1 está fechado: a leitura de rotina do pedido do clone a partir do `cd` para a cópia de `wt/`
volta a passar (S1, S2 e mais três variantes), por lista positiva que mantém recusadas as subidas e montagens do caminho
(fixtures `cpb-dev-wt-*`), e os mutantes das duas guardas centrais morrem. O A2 virou limite declarado com contraprova. Nas 44
linhas de rotina comparadas com o hook do e48a2e60, nenhum caso legítimo passou a recusar; as guardas novas do A12 e do A13
não mudam o resultado de nenhuma linha de rotina sondada.
