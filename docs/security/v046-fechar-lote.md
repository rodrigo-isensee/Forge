---
tipo: revisao-seguranca
contrato: 1
pedido: v046
branch: melhoria/v046-fechar-lote
commit: 2dda228f9517b38e0720c1d65d211934099a8f5d
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-13
---
# Review de segurança: v046 (fechar em lote, E6.3)

Diff `8b5a44d5..0be84795` (7 commits, 4 itens: CONFERENTE-PR-ABERTO-CEDO, WORKTREE-PRUNE-SANDBOX, FECHAR-MOVE-CARTAO, ATUALIZAR-BRANCH-ATRASADA). Lido em worktree destacada própria; testes dos arquivos tocados rodados (24, verdes) e o shellcheck do `bin/forge-fechar` limpo.

## Revalidação por delta (E6.14)
Head 2dda228f. Delta do código da fechar-lote desde 17ae39a3: só a regra do `bin/forge-doutor` no mapa de `bin/forge-testes` (acrescenta `test_doutor_branch_atrasada` à lista) e `tests/test_testes_tocados.py:55` (lista esperada). É dado de seleção de testes, sem execução de entrada, rede, gravação nem remoção; só amplia o que roda, não afrouxa guarda. O 4a2a4293 é merge da develop (domínio de outros pareceres; `forge-check parecer delta` lista a árvore trazida, nada de `bin/forge-fechar` mudou). `tests/test_testes_tocados.py` rodado: 150 testes, OK (1 pulado por /proc do sandbox). CI do PR 525 no head: catraca, árvore provada e instalação verdes; a bateria falha só no passo "Parecer de review ... quando o PR toca código que governa os agentes", que pede pareceres neste head (os de E6.12/E6.14). A1 segue recomendado, sem promoção.

## Revalidação por delta (E6.6)
Head 17ae39a3 (merge da develop a986c292). `forge-check parecer delta` de 0be84795 a 17ae39a3: nenhum arquivo do domínio mudou; só `docs/engineering/achados-recorrentes.md` e `tests/pesos-d4.json` (fora do domínio; este último segue JSON válido). Parecer anterior vale; A1 segue recomendado, sem promoção.

## Gatilhos
`R-SEGURANCA`: controle do Forge que apaga (poda de registros de worktree no passo 7) e grava estado (movimento do quadro) a partir de entrada do autor (`--cartao`, `--quadro`).

## Achados
- A1 (recomendado) bin/forge-fechar:778 · a linha do --dry-run imprime `--raiz $quadro` e `--de <coluna lida do arquivo>` sem printf '%q', ao contrário do aviso da linha 662 e do que docs/fechamento-integrador.md promete para todo comando impresso; quem cola a linha executa `$(` do caminho

## Sondas

## Detalhe dos achados
**A1** · evidência: `bin/forge-fechar:778`; sonda: `--quadro "$TMPDIR/E6.3 q$(id)" --cartao X1 --dry-run` imprime `forge-check movimento X1 --de — --para Pronto --raiz /tmp/claude-0/E6.3 q$(id)` cru. Caminho de ataque: o valor vem do próprio autor (ou da seção do `KANBAN.md`/`historico.md` do quadro dele) e só vira execução se alguém colar a linha; sem ganho de privilégio para terceiro. Severidade: baixa. Correção mínima: `printf '%q'` no `$c`, na coluna e no `$quadro` dessa linha, como na linha 662. Esforço P. Dono: tech-lead (autor da E6.1).

## Respostas ao brief
- **Poda de `.git/worktrees`** (`bin/forge-fechar:538`, `podar_orfaos` em 480): agora roda também depois de um `git worktree remove` bem-sucedido. O `git worktree prune` só tira registro cujo diretório sumiu e respeita worktree trancada (`git worktree lock`); não apaga arquivo de trabalho, commit nem ref, só o índice e o HEAD de uma worktree cujo diretório já não existe. Não há caminho do autor até ela: não recebe argumento. O `meta` (`bin/forge-fechar:525`) é só lido e impresso, nunca apagado. A remoção segue sem a opção que força e depois da prova de merge. Sem achado.
- **Movimento do quadro** (`bin/forge-fechar:651-668`): o ID passa pela forma ancorada `^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$` (linha 127; sondado: `-x`, `a/b`, quebra de linha, `a;id` e `../x` recusados) antes do passo 1; os argumentos vão ao `forge-check` como vetor, sem shell. O `forge-check movimento` só acrescenta ao `historico.md`, tira `|` e caracteres de controle, valida `--de`/`--para` contra as colunas do `KANBAN.md` e recusa link simbólico; nada se apaga. `--quadro` escolhe só em que quadro (com `KANBAN.md`) a linha é acrescentada, o que o autor já faz com o `forge-check movimento` à mão: sem elevação. Só roda com merge provado (passo 6 ou `--limpar` com PR `MERGED` na develop); a escolha de qual cartão mover é do autor, como no movimento manual (informativo). Movimento que falha vira código 3 e não desfaz nem prende a limpeza.
- **`bin/forge-doutor`** fora da lista de arquivos do brief: cabe no item, porque ATUALIZAR-BRANCH-ATRASADA é literalmente "forge doutor mostra o cherry-pick". Pelo lado da segurança é só leitura local (sem fetch, sem executar o cherry-pick); o sha sai de `git log --format=%H` e vai ao `merge-base --is-ancestor` depois de `--` (sondado: sha vazio ou `--all` dão 128, que a função trata como "não conferi").
- **CONFERENTE-PR-ABERTO-CEDO**: só texto e invariante novo em `tests/config.json` (acrescenta, não afrouxa).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: shellcheck (limpo, nível warning). Lacunas: gitleaks e semgrep não estão no PATH (rodam no CI).
