---
tipo: review
contrato: 1
pedido: v046
branch: melhoria/v046-fechar-lote
commit: 0b6e6834be6a9df4cdaf5438675b6fb82874f068
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v046 (E6.2, melhoria/v046-fechar-lote)

Diff revisado: `8b5a44d5..0be84795` (7 commits), lido por `git show` numa worktree destacada do revisor. Classe C (`forge-check pr --previo`: sensível da catraca `bin/forge-doutor`). A revisora não fez a entrega.

## Achados
- A1 (recomendado) bin/forge-testes:118 · a regra de bin/forge-doutor no MAPA não leva a test_doutor_branch_atrasada: `--listar bin/forge-doutor` dá 5 módulos sem ele (a mutação do autor usa essa lista); o `--afetados` o acha pela citação. Acrescente-o aqui e em tests/test_testes_tocados.py:55 (resolvido)
- A2 (recomendado) bin/forge-fechar:659 · `>/dev/null` joga fora a saída do `forge-check movimento`, que dá o motivo da recusa no stdout (coluna fora do KANBAN.md, atributo inválido): o aviso só traz o comando. Mande a saída ao stderr ou ao log com `gravar_linha`
- A3 (recomendado) bin/forge-fechar:1047 · guarda sem mutante (AR-1) e ramo sem teste (AR-2): o motivo `head <sha7>` do PR já MERGED não tem teste com --cartao; também sem mutante as guardas `shift 2 || die` de --cartao e --quadro (:88, :89)
- A4 (recomendado) bin/forge-fechar:538 · o `git worktree prune` do repositório inteiro agora roda em todo fechamento, não só depois da remoção que falhou: o registro de uma worktree com o diretório fora da vista desta sessão também sai. Diga isso no doc ou use `--expire`
- A5 (recomendado) bin/forge-fechar:3 · pendente: SP1 (subida por um comando e um brief) estava no Entregar da E6.1 e não tem commit; o Histórico (12:50) diz que depende do gerador em bin/forge-check. Fica para uma etapa própria

## Sondas

## Parecer
**Aprovado.** Sem defeito provado; os cinco achados são recomendados e não devolvem a entrega (`R-REVIEW`).

O que mudou e confere com o pedido (E6, lote por arquivo, DECISÃO DO DONO de 12/11 11:06): um commit por item com o teste dele. 49f20c41 é CONFERENTE-PR-ABERTO-CEDO (frase em `docs/fechamento-integrador.md` com invariante e motivo em `tests/config.json`, `R-FLUXO`). e6d205d5 é WORKTREE-PRUNE-SANDBOX (`podar_orfaos` também depois da remoção que deu certo, e o registro dos metadados presos sem pendência). 6633b0b6 é FECHAR-MOVE-CARTAO (`--cartao`/`--quadro` validados antes do passo 1; o movimento roda só depois do merge provado, no passo 6 e no `--limpar`; já em Pronto não grava; falha vira código 3 com o comando escapado por `%q`). e34c25fa é ATUALIZAR-BRANCH-ATRASADA. f0c8724e, 79f8a4bd e 0be84795 trazem mutantes, testes de ramo e pesos. SP1 ficou fora (A5).

**bin/forge-doutor fora da lista de arquivos do brief: cabe no item.** ATUALIZAR-BRANCH-ATRASADA é por definição um comportamento do `forge doutor` (a decisão Q4 escolheu mostrar o cherry-pick no doutor), e não há como entregar o item sem tocar o arquivo. A mudança é pequena (17+1 linhas): uma função só de leitura local (`git show`, `git log`, `merge-base --is-ancestor`, sem fetch nem rede, então vale também no `--rapido`), que falha para o lado de não adivinhar (rc diferente de 1 ou develop ilegível devolvem None e voltam ao conselho de sempre). `forge-check sobreposicao` não mostra outra branch em `bin/forge-doutor`; as sobreposições da branch são só em `tests/config.json` (com `maq-i7-ambiente` e `prepush-projeto-fila`), resolvidas na fila de integração.

**Tamanho:** 429 linhas contadas (`git diff --numstat --no-renames 8b5a44d5..0be84795`, bin 105, tests/*.py 320, tests/config.json 4), quatro comportamentos. O lote por arquivo foi decisão do dono; o corpo do PR precisa trazer `teto: excedido, 429 linhas, lote por arquivo da E6 (decisão do dono de 12/11 11:06), 320 delas de teste`.

**Ferramentas (citadas, não refeitas):** `shellcheck bin/forge-fechar` rc=0. `bin/forge-mutante --cobertura --base 8b5a44d5`: as três guardas Python de `bin/forge-doutor` (:141, :146, :160) estão cobertas por D1, D2 e D3; `bin/forge-fechar` (shell) fica fora da análise da catraca, e as guardas dele foram conferidas à mão contra C1 a C9 e P1 a P5 (A3 lista o que falta). São 17 mutantes ao todo, em três specs, todas abaixo de 8 por arquivo.

**Testes dos arquivos tocados** (`bin/forge-testes tests/<m>.py`, um por vez): test_doutor_branch_atrasada 6 OK, test_fechar_move_cartao 12 OK, test_fechar_prune_sandbox 3 OK, test_fechar_forge_check_real 3 OK. A suíte inteira fica com o CI do PR.

**Checklist de leitura:** os falsos de `git` e `forge-check` (`GIT_META_PRESA`, `CHECK`) não afrouxam a regra do script: o `git` falso chama o anterior e só recria a pasta, e o movimento real é provado em `test_fechar_forge_check_real`. O subprocesso do `forge-check` real usa `-I`. A coluna lida do histórico segue a forma que o `cmd_movimento` grava (só linha com hora ISO, `$5` = Para), e o teste com a linha "lixo" prova o filtro. O ID do cartão tem lista positiva e vai ao `awk -v` sem barra invertida. Não achei código morto nem TODO.

## Revalidação por delta (head 17ae39a3)
Delta lido por `forge-check parecer delta docs/reviews/v046-fechar-lote.md` (intervalo `0be84795..17ae39a3`, sem o que veio da base): só `tests/pesos-d4.json` (e a linha AR-13 de `docs/engineering/achados-recorrentes.md`, vinda da develop). O merge da develop `a986c292` teve um conflito, em `tests/pesos-d4.json`. A resolução confere: `git diff a986c292 HEAD -- tests/pesos-d4.json` traz só as três chaves da branch (`test_doutor_branch_atrasada` 5.0, `test_fechar_move_cartao` 16.0, `test_fechar_prune_sandbox` 7.2); o JSON é válido, ordenado, e todo módulo `tests/test_*.py` tem peso. `forge-testes tests/test_pesos_teto.py` e `tests/test_suite_partes.py` OK. Nenhum código de `bin/` mudou, então os achados A1 a A5 (recomendados) seguem como estavam; nenhum bloqueante. Parecer mantido: aprovado.

## Revalidação por delta (head 2dda228f)
Delta lido por `forge-check parecer delta docs/reviews/v046-fechar-lote.md` (intervalo `17ae39a3..2dda228f`, sem o que veio da base): só `bin/forge-testes` e `tests/test_testes_tocados.py`. O commit da branch é um só, 2dda228f (E6.12); o resto do intervalo vem do merge da develop `4a2a4293`. A regra de `bin/forge-doutor` no MAPA ganhou `test_doutor_branch_atrasada` e a lista esperada de `tests/test_testes_tocados.py:55` acompanha: `bin/forge-testes --listar bin/forge-doutor` agora dá `test_atualizar, test_doutor, test_doutor_branch_atrasada, test_doutor_custo, test_doutor_protecao_gh, test_doutor_relogio, test_forge, test_medidas_m14b, test_novo_projeto, test_qa_doutor_f8`. O A1 está resolvido; a nova varredura `test_modulos_que_rodam_o_forge_doutor_estao_na_regra_dele` segue válida. `forge-testes tests/test_testes_tocados.py` 150 OK (1 pulado) e `tests/test_doutor_branch_atrasada.py` 6 OK; a suíte inteira fica com o CI do PR 525. Os achados A2 a A5 (recomendados) seguem como estavam; nenhum bloqueante. Parecer mantido: aprovado.

## Revalidação por delta (head 0b6e6834)
Delta lido por `forge-check parecer delta docs/reviews/v046-fechar-lote.md` (intervalo `2dda228f..0b6e6834`, sem o que veio da base): só `tests/config.json`, vindo da junção com a develop `b19a5a94` (PRs 524, 528 e 529: o invariante e o motivo de `agents/agile-coach.md`, diretriz 20). O commit da branch no intervalo é o merge `0b6e6834` (E6.17) e os pareceres do QA e da segurança; nada de código da fechar-lote mudou: `git diff --stat 2dda228f HEAD` sobre `bin/forge-fechar`, `bin/forge-doutor`, `bin/forge-testes`, `tests/test_fechar_*.py`, `tests/test_doutor_branch_atrasada.py` e `tests/pesos-d4.json` não traz nenhum arquivo deles (só os mutantes do PR 524, vindos da base). `tests/config.json` segue JSON válido. `forge-testes tests/test_fechar_move_cartao.py tests/test_testes_tocados.py` 162 OK (1 pulado); o CI do PR 525 está verde nos checks concluídos. Os achados A2 a A5 (recomendados) seguem como estavam; nenhum bloqueante. Parecer mantido: aprovado.
