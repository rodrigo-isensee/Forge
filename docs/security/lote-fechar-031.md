---
tipo: revisao-seguranca
contrato: 1
pedido: lote-fechar-031
branch: melhoria/lote-fechar-031
commit: 432a0a7934fe72373e8dd476e8238d6a3a58ec39
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-24
---
# Review de segurança: lote-fechar-031

Escopo: `git diff d150ec8...432a0a7` (E1 e4034d3, E2 a3d00bd, E3 364143e, fragmento 432a0a7): `bin/forge-fechar`, `docs/fechamento-integrador.md`, `tests/test_fechar.py`, `tests/test_fechar_log_check.py`, `tests/test_fechar_orfao.py` e `changelog.d/lote-fechar-031.md`. Li a função `limpar_entrega` inteira e o fluxo dos passos 6 e 7 em 432a0a7, não só o diff. Sondas em pasta descartável de `$TMPDIR` (repositório, `HOME`, `gh` e `forge-check` falsos do próprio harness de `tests/test_fechar.py`).

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `bin/forge-fechar` conduz o merge na `develop`, e o passo 7 e o `--limpar` apagam worktree, branch local e branch remota. E1 muda a permissão de um caminho do sistema de arquivos (`chmod`); E2 troca o diretório de trabalho antes de apagar; E3 é um modo novo que sai depois do merge. Sem rede nova, sem dependência nova, sem custo (`R-CUSTO`).

## Achados

## Detalhe dos achados
Não há achado bloqueante. Duas recomendações (R1, R2), baixas, ficam abaixo; nenhuma tem caminho de ataque realista com as pastas padrão.

**E1, `chmod 700` da pasta do log (bin/forge-fechar:156-166; checagens em :157-162).**
- Link, outro dono e não diretório continuam recusados antes do `chmod`. Sondas: pasta 755 do usuário vira 700 com aviso (rc 0); link para pasta do usuário, link para `/`, arquivo comum e `/` (outro dono) saem com rc 1 e o modo do alvo não muda; pasta com setgid (2755) vira 2700 no `chmod 700` e o script recusa na releitura (falha fechada).
- O caminho relativo agora vira absoluto (:156), o que mantém o log no mesmo lugar depois do `cd` do passo 7.
- R1 (recomendado, baixa): há TOCTOU entre a checagem `-L`/`-O`/`stat` (:157-162) e o `chmod 700 "$logdir"` (:163), e o `chmod` do GNU segue link. Sonda determinística (um `stat` falso no PATH troca a pasta por um link para um arquivo do usuário entre a leitura do modo e o `chmod`): o arquivo-alvo passou de 644 para 700 e o script saiu com rc 1 na releitura. Caminho de ataque: exige escrita na pasta-pai do log por outro usuário. Com as pastas padrão não existe: `$XDG_RUNTIME_DIR` é 700 do usuário e `${TMPDIR:-/tmp}/forge-fechar-logs-<uid>` fica em `/tmp` com sticky bit, onde outro usuário não renomeia a entrada; corrida sem atalho (150 rodadas contra um trocador em laço, 246 mil trocas) não acertou nenhuma vez. Só aparece com `FORGE_FECHAR_LOG_DIR` dentro de pasta de outro usuário, e o ganho é trocar para 700 o modo de um arquivo do próprio usuário (o kernel recusa `chmod` em arquivo de outro dono; como root, o ganho seria maior, mas o script não é rodado como root). Correção mínima: só ajustar o modo quando a pasta-pai é do próprio usuário (ou tem sticky bit), e recusar como antes nos outros casos; ou fazer o ajuste por descritor (`open` com `O_DIRECTORY|O_NOFOLLOW`, `fstat` do dono e `fchmod`). Esforço P. Dono: `tech-lead`.

**E2, saída da worktree antes da limpeza (bin/forge-fechar:359-376).**
- O alvo da remoção (`arvore`, casado por `$2==b` exato com `refs/heads/<ref>`), o `sha_local` e `merged_heads` são lidos antes do `cd`; o `cd` só muda de onde os comandos rodam, no mesmo repositório (mesmo diretório comum), e a remoção segue presa a `sha_confere` e sem a opção que força.
- A principal é a primeira entrada de `git worktree list --porcelain`; o `cd` só ocorre se ela existe, é diretório e resolve (`pwd -P`) para outro lugar que não a atual. Sondas: (a) branch na principal e script rodado de outra worktree: a principal não é removida (o git recusa remover a principal), worktree e branch ficam pendentes, rc 3; (b) branch na principal e script rodado de dentro dela: fica pendente com o aviso, sem `cd`; (c) nome parecido (`melhoria/x-2` com worktree própria, mesmo sha): só `melhoria/x` sai, `melhoria/x-2` local, remota e worktree ficam, `develop` intacta, rc 0.
- `main`, `master`, `develop` e `homolog` continuam recusados antes de qualquer chamada (bin/forge-fechar:60), sem, com `--limpar` e com `--sem-limpar` (sonda: rc 1 e zero chamadas nas 12 combinações).
- Fora do delta, só registro: em sistema de arquivos sem diferença de maiúsculas (macOS), um `--ref Main` com ref solta poderia alcançar a `main` local no `git branch -D`; a recusa de :60 compara o texto exato. Hoje a remoção ainda exige PR `MERGED` desse head e `sha_confere`, então fica como observação para um cartão futuro, não achado deste pedido.

**E3, `--sem-limpar` (bin/forge-fechar:59, :718-726).**
- Não pula guarda do merge: o bloco está depois do passo 6 e de todas as conferências de `MERGED`, head, base e commit de merge. Sondas: o `forge-check pr` roda no sha e o merge sai com `--match-head-commit <sha>`; check vermelho para antes do merge (rc 1, nenhuma chamada de `pr merge`); `--limpar` junto é erro de uso antes de qualquer chamada; com `--dry-run` só descreve. Não executa nenhum comando de limpeza (testado em `test_sem_limpar_mescla_pula_o_passo_7_imprime_os_comandos_e_sai_com_3`).
- Os nomes impressos passam por `printf '%q'` e o `ref` já passou por `git check-ref-format --branch`; não há injeção de comando no texto impresso.
- R2 (recomendado, baixa): os comandos impressos (:722-723) trazem `git branch -D` e `git push origin --delete` sem a conferência de sha que a `limpar_entrega` faz e que a exceção da `R-VERIFY` exige (head remoto igual ao `headRefOid` do PR). Se a branch ganhar commit depois do merge (nome reaproveitado, commit local não enviado) e alguém rodar esses comandos à mão, perde-se o commit sem a confirmação que a `R-VERIFY` pede. Não há atacante: é risco de integridade por operação manual; o próprio texto oferece o caminho seguro (`--limpar`), que confere o sha. Correção mínima: imprimir só o `forge-fechar <pedido> --ref <ref> --limpar` como comando, ou marcar os comandos crus como "só se o sha ainda for <sha mesclado>" com o sha. Esforço P. Dono: `tech-lead`.

**`R-VERIFY` no código.** Nenhuma linha nova usa `--force`, `-f`, `--force-with-lease` nem `--no-verify`.

## Riscos aceitos e ferramentas
Sem risco aceito. Ferramentas: `shellcheck` (nada novo no delta; os três avisos que acusa, em :476, :493 e :500, são do passo 2b, anterior a este pedido), as sondas acima e `python3 -m unittest tests.test_fechar tests.test_fechar_log_check tests.test_fechar_orfao` (95 testes, OK). Faltaram no PATH: `gitleaks`, `semgrep`, `zizmor`, `osv-scanner` (não instalados; o delta não traz segredo, dependência nem workflow). Não consegui provar no sandbox o `EPERM` do `chmod` em arquivo de outro dono (o `/etc` é só leitura e a sonda devolveu `EROFS`); vale a regra do kernel, que só deixa o dono ou o root trocar o modo.
