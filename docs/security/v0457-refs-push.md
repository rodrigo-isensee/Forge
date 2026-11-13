---
tipo: revisao-seguranca
contrato: 1
pedido: v0457
branch: melhoria/v0457-refs-push
commit: b12f6d9be42f4b3b5f00bce51be535b567207483
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-12
---
# Review de segurança: v0457 E9.7 (3b, política de refs PREPUSH-REFS, PR #506)

Diff revisado: `8b5a44d5..b12f6d9b` de `melhoria/v0457-refs-push` (13 arquivos), lido numa worktree destacada própria.

## Gatilhos
`R-SEGURANCA`: hook de envio (controle que analisa entrada, as linhas de refs que o git passa no stdin) no Forge e no modelo de projeto; o PR leva o rótulo `afrouxa-regra` (posto pelo dono), porque o item 3 muda a PREPUSH-DELETE e a regra de uma branch por envio passa a valer para as pessoas nos projetos (aceito pelo dono, ORDEM DO DONO de 2026-11-12 13:50).

## Parecer
**Origem dos hooks (decisão 4a, `R-CONFORMIDADE`).** O commit `3d4a884f` toca só `.githooks/pre-push` e `templates/projeto/.githooks/pre-push` (+22 linhas cada). Aplicado o patch `/root/.forge-contrib/patches/refs-push.patch` sobre `3d4a884f^` numa worktree descartável, `git diff 3d4a884f` deu 0 linhas: o commit traz exatamente o patch do dono e nada mais. Nenhum commit seguinte (`82053063..b12f6d9b`) toca os dois hooks.

**A política contra as ameaças da D2** (`docs/security/ameacas/v0457-hook-shell-pipe.md`, parte P), no laço `while read` (`.githooks/pre-push:141`, política em :168-188; `templates/projeto/.githooks/pre-push:6`, política em :31-51), igual nos dois:
- **Ref fora de `refs/heads/` e `refs/tags/`** (P2, P3 e o espelho): lista positiva `refs/heads/?*|refs/tags/?*` (não lista negativa, AR-3); `refs/heads/` vazio, `HEAD`, `refs/tagsX/`, `refs/notes/`, `refs/remotes/` e `refs/pull/` recusam, inclusive na remoção.
- **Refspec com `:`** (`HEAD:refs/notes/x`, `HEAD:refs/heads/a HEAD:refs/heads/b`, `:` matching): o hook julga a ref remota que o git já resolveu, então a sintaxe não importa; destino fora recusa pelo item 1, duas branches pelo item 2.
- **`--all`, `--branches`, `--mirror`** (P1, P2): mais de uma `refs/heads/*` com código recusa; os testes de envio real (`EnvioDeVerdade`) provam a recusa sem o remoto mudar.
- **Remoção em massa** (P2, P5): mais de uma remoção por envio recusa, branch ou tag; `--prune` com curinga recusa sem apagar nada no remoto (teste `test_prune_com_curinga_nao_apaga_em_massa`).
- **Falha fechada:** cada recusa é `exit 1` dentro do laço, que lê o stdin direto (sem pipe, então o `exit` sai do hook); os contadores começam em 0 na linha anterior ao laço e não vêm do ambiente (sonda com `refs_branches=-5` exportado recusa igual); linha curta (sem ref remota) recusa pelo item 1; campo a mais vai para o sha remoto e recusa na checagem de fast-forward. A mensagem de recusa não sugere `--no-verify`, `--force` nem gravar e rodar arquivo.
- **Corpus de legítimos** (L-6, L-7): uma branch, uma branch com tags, uma remoção sozinha e uma branch com tags e uma remoção passam pela política (testes `test_uma_remocao_passa`, `test_branch_com_tags_e_uma_remocao_nao_recusa_pela_politica`, `test_uma_branch_por_envio_passa`). Os 6 módulos ajustados trocam a segunda branch por tag ou passam a esperar a recusa, sem afrouxar outra asserção.

**Testes e catraca.** `tests/test_prepush_refs.py`: 20 testes (6 de política e 4 de envio real, para cada hook), ambiente montado do zero (AR-4). Os 16 mutantes de `tests/mutantes/v0457-refs-push.json` e `-2.json` têm o trecho `de` presente no head (AR-12). `test_pre_push_trava.py` tem 217 asserções no head (217 na base, 216 em `82053063`). Nenhum fluxo de CI dispara em push de tag, então tag livre (D2, item 2) não abre caminho de publicação.

**Rodado na máquina, um módulo por vez, no head:** `test_prepush_refs` 20 OK; `test_pre_push_afetados` 36 OK; `test_pre_push_ja_no_remoto` 2 OK; `test_pre_push_parecer` 21 OK; `test_pre_push_segredo` 10 OK; `test_prepush_so_docs` OK (9 pulados pelo sandbox: `/proc` e `chown`, nenhum dos dois ajustados); `test_pre_push_trava` 50 OK (4 pulados pelo sandbox).

**CI do PR #506 (`gh pr checks 506`, run 43288706245, head `b12f6d9b`):** `catraca`, `instalação (python 3.14)` e `árvore já provada na develop` verdes; `bateria (passos)` vermelha só no passo de pareceres (`R-REVIEW`: o PR toca `bin/forge-testes` sem parecer de review aprovado), e por isso `bateria`, `bateria (python 3.14)` vermelhas e as partes da suíte, o teto de pulados e as verificações longas puladas. A bateria completa **ainda não rodou** neste head: o portão dela fica para o CI depois dos pareceres, e o merge (que espera a tag) exige esse CI verde. Isso não muda o veredito de segurança.

**Resíduos (fora deste diff, já declarados na ameaça):** `--no-verify` e `git send-pack` pulam o pre-push (cobertos pelas travas de texto, D3 e `R-VERIFY`); várias tags com código no mesmo envio seguem livres por desenho (D2); uma branch com uma remoção no mesmo envio segue livre (L-7).

**Veredito:** aprovado. Um achado recomendado, pré-existente e sem caminho de ataque pelo git.

## Achados
- A1 (recomendado) .githooks/pre-push:141 · o laço while read dos dois hooks (o do modelo em templates/projeto/.githooks/pre-push:6) ignora a última linha sem quebra de linha; o git sempre a termina, então sem caminho de ataque; endurecer com `|| [ -n "$remote_ref" ]` num próximo patch do dono

## Sondas

## Detalhe dos achados
**A1** · evidência: `.githooks/pre-push:141` e `templates/projeto/.githooks/pre-push:6`; com o stdin `refs/heads/x <sha> refs/heads/a <zero>\nrefs/heads/x <sha> refs/heads/b <zero>` (a segunda linha sem `\n`), os dois hooks não recusam (rc 0), porque o `read` devolve falso na linha final sem terminador; com `\n` no fim, recusam ("mais de uma branch"). · caminho de ataque: nenhum realista; o git escreve cada linha do pre-push com `\n`, e quem chama o hook à mão com stdin próprio não passa por ele para enviar. Comportamento anterior a este diff. · severidade: informativa. · correção mínima: `while read -r _ local_sha remote_ref remote_sha || [ -n "$remote_ref" ]; do` nos dois hooks, com um teste da linha sem terminador. · esforço: P. · dono: `tech-lead` prepara o patch e o teste; o dono aplica (decisão 4a, `R-CONFORMIDADE`).

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum novo neste parecer. A mudança da PREPUSH-DELETE (item 3) e a regra de uma branch por envio para as pessoas nos projetos são decisões do dono (2026-11-10 23:45 e ORDEM DO DONO de 2026-11-12 13:50), com o rótulo `afrouxa-regra` posto por ele.

Ferramentas: o analisador de shell rodou nos dois hooks sem aviso de nível warning ou acima. Faltaram no ambiente o varredor de segredos, os analisadores de workflow e o de dependências (o CI os roda); o diff não toca workflow nem dependência. Lacuna de verificação: as sondas de envio real com `-c remote.origin.mirror=true`, `-c push.default=matching` e o refspec `:` foram barradas pelo hook de conformidade (`R-VERIFY`, prova da suíte) e não foram contornadas; esses caminhos chegam ao hook como as mesmas linhas de refs que `--mirror` e `--all`, cobertas pelos testes de envio real e pelas sondas de stdin.
