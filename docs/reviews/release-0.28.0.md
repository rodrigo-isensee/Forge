---
tipo: review
contrato: 1
pedido: release-0.28.0
branch: melhoria/release-0.28.0
commit: 450d7fa27e133cddbafd9ce09f19f63548f86a31
parecer: aprovado
revisor: forge:tech-lead (outra instância, E2.1)
data: 2026-10-21
---
# Review: release 0.28.0

Escopo: o que a main recebe, `git diff 5e9b234 450d7fa` (159 arquivos): a leva #257 a #274 (18 squashes na develop até `8b047d4`) e o commit da release `450d7fa`. O revisor não é o autor do fechamento (D-ETAPAS-INST). Conferência só com `git show`/`git diff` e numa cópia própria em `$TMPDIR`, sem trocar o HEAD da worktree.

Veredito sobre `450d7fa`: **APROVADO**, sem achados que bloqueiem.

## Achados

## O que foi conferido
1. **Versão.** `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` passam de 0.27.0 para 0.28.0. Minor, pelo SemVer do `CLAUDE.md` e pela ADR 0005 (item 6): nenhum formato de arquivo de projeto quebra. O `!` do #270 marca o afrouxamento da F6 (com o rótulo `afrouxa-regra` do dono), não quebra para os projetos; o precedente dos `feat!` de 2026-10-12 também saiu como minor (0.10.0).
2. **Changelog (ADR 0006).** Os 18 fragmentos de `changelog.d/` (lidos em `8b047d4`) somem no `450d7fa` e a pasta fica vazia. A seção `## [0.28.0] - 2026-10-21` fica logo abaixo de `## [Não publicado]` (vazia) e traz **20 linhas** (8 Adicionado, 9 Alterado, 3 Corrigido), cada uma igual, byte a byte, à do fragmento: 16 fragmentos de uma linha, `modelos-no-forge` com duas (MODELOS-NO-FORGE em Alterado, MODELO-SEGURANCA-DERIVA em Corrigido) e `regra-lote-por-arquivo` com duas. Nenhum PR ficou de fora. O commit da release só toca os dois `plugin.json`, o `CHANGELOG.md` e os 18 fragmentos.
3. **O código mesclado é o código revisado.** Para cada um dos 18 squashes, o commit citado em `docs/reviews/<pedido>.md` comparado com o squash, nos arquivos do PR fora das pastas de parecer: 17 sem diferença; no #271 (`160f370` × `82c11c0`) o `bin/forge-check` difere só pelo #262, que já estava na develop, e o patch da branch é igual ao do squash linha a linha. Os 18 pareceres de review e de QA estão `aprovado`; segurança presente e aprovada nos 14 com gatilho; os 4 sem parecer de segurança (#257, #258, #266, #271) registram "sem gatilho" no review ou no QA.
4. **Controles do Forge.** Os PRs que tocaram arquivo protegido (#259, #267, #269, #270, #274) têm o rótulo `afrouxa-regra` (`gh pr view`). `tests/config.json` só ganha invariantes (#260, #268), nenhum some. `docs/regras/R-DECISAO.md` (#273) acrescenta texto.
5. **Interação entre PRs nos mesmos arquivos.**
   - `hooks/conformidade.py` e `hooks/_comum.py` (#269 e depois #270): a exceção de leitura da F6 (`so_leitura`) usa a leitura única `leituras()` do #269 e recusa qualquer `#`, `$`, crase e várias linhas antes de ler, então não há caminho em que as duas mudanças divirjam sobre o comentário. O parecer do #270 (`2e1e712`) já foi dado sobre a develop com o #269.
   - `bin/forge-fechar` (#261, #265, #274): o laço do `--esperar-rotulo` roda dentro do log do #265 (a saída do laço vai ao registrador) e termina na `limpar_entrega` única do #274; `docs/fechamento-integrador.md` descreve os três juntos (opções, passo 5, passo 7, `--limpar`, log e código 3).
   - `.githooks/pre-push` (#267) e os testes que entraram depois: nenhum teste novo da leva lê o conteúdo real de `docs/{reviews,security,qa,devops}` fora das classes do caminho curto; o único (`test_modelos_citados`, #272) lê `_modelo.md`, que pelo próprio pre-push roda a suíte inteira. O push de limpeza do `forge-fechar` (apagar ref) cai na suíte inteira, como o doc diz.
   - `bin/forge-testes` (#266): a lista `FORGE_CHECK` inclui `test_erros_no_brief` (#262) e `CONTEUDO` inclui `test_modelos_citados` (#272); o `MapaDoForgeCheck` confere a lista contra os arquivos.
6. **Testes**, numa cópia de `450d7fa` em `$TMPDIR`: `test_changelog`, `test_testes_tocados`, `test_pre_push_parecer`, `test_fechar` e `test_modelos_citados` (160 testes, OK, 1 skip); `test_hooks` e `test_guarda_conferente` (57, OK); `test_forge` (418, OK). A suíte inteira sobre `450d7fa` é a evidência do E1.1 no pedido (1338 OK, `validar-plugin` ok); o CI repete no PR.
7. **Regras.** R-NEUTRO e R-CUSTO: nada de projeto nem serviço pago na leva (testes de neutralidade verdes). R-VERIFY: nenhum push forçado. R-FLUXO: a release parte de `8b047d4`, a develop revisada; a main `5e9b234` não é ancestral (merges homolog → main por merge commit), por isso o diff de árvores é o que se revisa, como o pedido registra.

## Recomendações (não bloqueiam)
- R1 · O Histórico do pedido diz "18 fragmentos juntados em 16 linhas: 8 Adicionado, 6 Alterado, 2 Corrigido"; o `CHANGELOG.md` tem 20 linhas (8, 9 e 3). O changelog está certo; vale corrigir a contagem no pedido para o resumo do PR homolog → main não herdar o número errado.
- R2 · Cerca de metade das linhas da seção não termina em ponto final, herdado dos fragmentos. Cosmético; não vale mexer na release por isso.
- R3 · Os pareceres de segurança e devops desta release (E2.2, E2.3) são do papel deles e não foram refeitos aqui.
