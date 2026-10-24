---
tipo: review
contrato: 1
pedido: lote-atualizar
branch: melhoria/lote-atualizar
commit: f1cf78c075ff3f24400ca680944d6dae76d5b493
parecer: reprovado
revisor: forge:tech-lead (instância de review, LOTE-ATUALIZAR-REV E1.1)
data: 2026-10-23
---
# Review: lote-atualizar

Escopo: `db55859..f1cf78c` (base db55859529da47652babded81461d2b0500ef79f), 5 commits, 3 arquivos (`bin/forge-atualizar`, `tests/test_atualizar.py`, `changelog.d/lote-atualizar.md`). Primeira rodada; o revisor não é o autor.

## Achados
- A1 (bloqueante) tests/test_atualizar.py:418 · classe teste-que-não-prova: integrar_develop roda no processo com o os.environ do executor, não com self.env; sem identidade git no HOME a mesclagem falha sem conflito e o teste passa no código antigo (1644a1a). Isole o ambiente e afirme que o conflito foi resolvido e que trazidos foi chamado
- A2 (recomendado) bin/forge-atualizar:129 · o código de saída do merge --abort e do checkout -B não é lido; se falhar, a mensagem "Desfiz a mesclagem" volta a mentir, que é o defeito do F4-A9. Leia o código e, se falhar, diga o estado real e o comando para desfazer à mão
- A3 (recomendado) bin/forge-atualizar:131 · o comentário diz "a árvore estava limpa", mas nada garante isso; o checkout -B preserva mudança local e arquivo não rastreado (sonda abaixo). Troque por "o checkout sem -f leva as mudanças locais junto; só some o commit da mesclagem"
- A4 (recomendado) ~/.forge-contrib/docs/pedidos/LOTE-ATUALIZAR.md:9 · o E1 do pedido diz "diz a verdade (a mesclagem ficou feita) e não manda desfazer", e o código desfaz a mesclagem. Registre no pedido a decisão técnica de desfazer, que é a opção mais segura e casa com o comentário do except

## Parecer
**Reprovado**, por um bloqueante (A1). A correção em si está certa; o que não prova nada é o teste.

### O que foi conferido e está certo
- `desfazer_mesclagem` (bin/forge-atualizar:126): com `MERGE_HEAD`, aborta; sem ele e com `HEAD != antes`, volta a branch `forge/upgrade-<nova>` ao commit de antes. Só roda quando a branch atual é a do upgrade (a guarda da linha 106), e entre o `merge` e o `except` o único commit possível é o `commit --no-edit` da resolução. Por isso o que some é só o commit criado pelo próprio comando (e ele continua no reflog).
- O `checkout -q -B <branch> <antes>` não apaga trabalho do projeto. Sonda em `$TMPDIR/tech-lead-loteatualizar/sonda`: com um arquivo rastreado modificado e um não rastreado antes do merge, depois de merge, conflito, `--ours`, commit e `checkout -B`, o `HEAD` volta para `antes`, o `git status` mostra ` M a` e `?? untr`, e o conteúdo sujo de `a` continua lá. Sem `-f`, o checkout recusa em vez de sobrescrever. Os arquivos trazidos pela develop saem, e isso é o desfazer. O `reset --hard` do `dfc40b4` era destrutivo e o `f1cf78c` o trocou com razão. Não é preciso pôr `-B` na lista do `test_nao_usa_comandos_destrutivos`.
- Ctrl-C ou EOF durante o `commit` ou o `trazidos`: o mesmo `desfazer_mesclagem` cobre os dois estados (com e sem `MERGE_HEAD`).
- O `ignore_patterns("__pycache__")` aparece só em `tests/test_atualizar.py:127`, no `copytree` do `publicar`. O código de produção não muda.
- O fragmento `changelog.d/lote-atualizar.md` descreve o que o código faz: desfaz de verdade depois do commit e o teste deixa de copiar `__pycache__`.
- Commits: Conventional Commits em português, com o teste vermelho antes da correção. O segundo commit de correção já foi aceito pelo Jarvis (DECISÃO TÉCNICA no pedido).

### A1 em detalhe (bloqueante, classe teste-que-não-prova)
O teste carrega o módulo e chama `modulo.integrar_develop` no próprio processo. O `git()` do módulo herda o `os.environ` do executor, não o `self.env` do `setUp` (que tira os `GIT_*` e aponta `HOME` e `GIT_CONFIG_GLOBAL` para a pasta temporária). Evidência, com o teste do `1644a1a` (código antigo) num `git archive` em `$TMPDIR/tech-lead-loteatualizar/red`:
- `HOME` sem `.gitconfig`: **OK** (deveria falhar). A saída capturada é "deu conflito em: (arquivos). Desfiz a mesclagem", porque o `merge` falha por falta de identidade, sem conflito, e o `assertEqual(HEAD, antes)` passa sem que o cenário tenha sido exercitado.
- `HOME` com `user.name` e `user.email`: **FAILED** (`d857582 != ebfdf6c`), que é o vermelho certo.
- No head `f1cf78c`, `tests.test_atualizar` dá 74 OK nos dois ambientes. Ou seja, no ambiente sem identidade o teste não distingue o código antigo do novo.

Além do ambiente sem identidade, o mesmo vazamento faz o teste depender de qualquer `GIT_*` do executor (por exemplo, dentro de um hook) e do gitconfig global do usuário.

Sugestão: envolver a chamada em `mock.patch.dict(os.environ, self.env, clear=True)` e afirmar que o cenário aconteceu: `assertIn("Conflito resolvido", saida.getvalue())` e que o mock de `trazidos` foi chamado uma vez. Depois disso, o vermelho do `1644a1a` tem de falhar sem depender do HOME de quem roda.

### Ferramentas
Não há `docs/engineering/praticas.md` com regras de ferramenta para este diff. A bateria fica com o pre-push e o CI, que eu não refaço. Rodei só `tests.test_atualizar` no head: 74 OK.

### Fora deste parecer
Segurança (E2.1) e QA (E3.1) ficam com os seus papéis.
