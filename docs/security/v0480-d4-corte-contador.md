---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-d4-corte-contador
commit: bf598d2f872df03c42fc799367453eea98b558e9
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança: v0478 (E174.21, PR #869, D4 corte pelo contador)

## Gatilhos
Gatilhos: controle do Forge (bin/forge-fechar, fluxo de branches e promoção), automação que abre PR para a main e promove para a homolog.

## Resumo
Escopo lido: `git diff aabc476c..bf598d2f` (bin/forge-fechar, docs/fechamento-integrador.md, changelog.d, tests/test_fechar_corte.py, test_fechar_laco.py, mutantes e pesos). Primeira rodada nesta branch, sem parecer anterior.

**Veredito sobre o controle: neutro** (não afrouxa nem aperta portão nenhum). O `--corte` só automatiza o que a ordem permanente do dono de 24/11 07:41 manda (cortar a 20 itens, promover com tudo verde, abrir o PR da main; a main continua do dono) e o que `R-FLUXO` já dava ao `tech-lead`:
- **Nunca mescla na main:** nas linhas acrescentadas não há `pr merge`, `--auto`, a opção de administrador, `--force`, `--no-verify` nem `gh api` (contagem 0 no diff). Na main, a única ação é `gh pr create --base main --head homolog` (bin/forge-fechar:1502), aberto e não mesclado. O merge do script segue só por `mesclar_direto` (bin/forge-fechar:1001, `--match-head-commit`, recusa base main), sem mudança.
- **Promoção para a homolog:** V2 chama o `--promover` já existente (bin/forge-fechar:1495), com os mesmos portões P1 a P6 (sha na develop, `--conferir-ref`, CI verde, check-runs exigidos, merge direto preso ao sha, nunca automático), já revisados em `docs/security/v0480-promover-sem-auto.md`. Código diferente de 0 e 3 encerra o corte.
- **Marca:** V5 grava numa worktree temporária sobre a origin/develop e envia só `melhoria/marca-<X.Y.Z>`, com a versão vinda da regex numérica estrita (sem injeção no nome do ramo nem no título), push sem força (corrida com ramo existente falha, fail-closed) e o PR em rascunho para a develop, que segue pareceres e o `--laco`. Ramo já no origin, ou leitura do `ls-remote` que falha, não faz nada.
- **Leituras que falham param** (V1 fetch, versões ilegíveis, `pr list`, contador) e homolog à frente da develop para (sort -V). `--corte` recusa as opções de item, `--promover`, `--lote` e `--laco` juntos. `FORGE_FECHAR_ITEM` e `FORGE_GH` só valem com `FORGE_FECHAR_TESTE=1` (bin/forge-fechar:240-250, sem mudança).
- **`--laco` com rc 0** roda o `--corte` no fim (bin/forge-fechar:1359); em `--dry-run`, só imprime.

Verificação: tests/test_fechar_corte.py rodado no head (unittest): 17 testes, OK (inclui dry-run sem ação, leituras que falham, PR da main aberto espera o dono, PR da main uma vez só, homolog à frente para).

CI do PR #869 no head bf598d2f (execução 45478706012): **vermelho**, fora do domínio de segurança. Falham `test_fechar.Fechar.test_fechar_sem_a_e_b_ou_c_solto` (o padrão `a && b || c` em bin/forge-fechar:1484; o comportamento ali é fail-closed, o defeito é de estilo da guarda) e `test_reval_delta.Guarda.test_caminho_de_texto_so_e_citado_como_a_lista_conhece` (tests/test_fechar_corte.py citado em README.md sem a lista). São do `tech-lead`/autor; a correção toca bin/forge-fechar, então este parecer volta por delta no head novo (`R-REVIEW`).

## Achados
- A1 (recomendado) bin/forge-fechar:1491 · V2 acha a marca com `git log -1 -G` sem `--first-parent`: merge commit na develop (como o #795) expõe o commit interno do ramo, e o --promover levaria um sha fora da cadeia. Use `--first-parent` e confira o assunto `chore(release): marca da <v_dev>`.
- A2 (recomendado) bin/forge-fechar:1499 · V3 abre o PR homolog -> main só com `v_hom != v_main`, sem conferir a ordem: com a main à frente da homolog (anomalia), abriria PR de versão mais velha para a main. Pare como no V1 (sort -V), com 'confira à mão'.
- A3 (recomendado) tests/test_fechar_corte.py:136 · Nenhum teste do --corte afirma que o registro do gh falso não tem `pr merge` nem `--auto` em caminho nenhum; acrescente essa asserção ao teste da promoção e ao do PR da main, para o requisito 'nunca mescla na main' ter guarda própria.

## Sondas

## Detalhe dos achados
- **A1** · severidade baixa · caminho: só com merge commit na develop (ADR 0012 manda squash; o #795 mostra que já ocorreu). P1 aceita o sha por ser ancestral, e a premissa E31.10 do `forge-check pr --base homolog` tende a recusar na catraca (fail-closed), então o efeito realista é parar, não promover o errado. Correção: `git log -1 --first-parent --format=%H -G'"version"' ...` e conferir o assunto. Esforço P. Dono: autor do D4.
- **A2** · severidade baixa · o merge na main é só do dono, então o dano é um PR enganoso. Correção: `sort -V` entre `v_main` e `v_hom` e `die` se a main estiver à frente. Esforço P. Dono: autor do D4.
- **A3** · severidade baixa · sem caminho de ataque hoje; é a guarda de regressão do requisito do brief. Esforço P. Dono: `qa-engineer` ou autor.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática do diff, grep nas linhas acrescentadas, teste novo rodado localmente, logs dos jobs do CI lidos pelo `gh` (só leitura). gitleaks, zizmor, actionlint e semgrep não estão no PATH (lacuna; o diff não toca workflow nem traz credencial).
