---
tipo: revisao-seguranca
contrato: 1
pedido: v0481
branch: melhoria/v0481-fechar-ci-topo
commit: 58852bf22fd6dcd4912d14b65813f701995cb38e
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-24
---
# Review de segurança por delta: v0481 (E13.13, #880, forge-fechar: CI do topo, branch criada do servidor, cópia certa)

## Gatilhos
Gatilhos: controle do fluxo de merge (portões do `forge-fechar`, R-FLUXO), CI da develop, guardas de mutação e catraca (R-CONFORMIDADE).

## Delta lido
`git diff dd2fcada..58852bf2` (volta única E13.10): `bin/forge-fechar` (+13/-2), as specs `mp1311-fechar-cartao.json`, `v047-integracao-em-lote-3.json`, `v0481-fechar-ci-topo.json` e a nova `v0481-fechar-ci-topo-2.json` (M9 a M12), `tests/test_fechar_ci_topo.py`, `tests/test_fechar_sha_conferido.py`, `docs/fechamento-integrador.md` e o fragmento do changelog. Já lido e não relido: o resto do #880 em dd2fcada (parecer anterior, no git).

## Achados anteriores
- A1 (bloqueante, resolvido): IL-M21 e M2 alinhados à fonte; os dois mutantes morrem (S2) e o `ConferirTodas` que o CI roda passa (S1).
- A2 (bloqueante, resolvido): o nome `test_commit_que_falta_aqui_pede_o_fetch` voltou (tests/test_fechar_sha_conferido.py:122) e a spec M5 o cita; catraca local limpa (S3) e a do CI verde no head (run 45530565279).

## Sondas
- S1 · bin/forge-mutante --conferir --todas, aqui e na árvore da base d49accf8 · espera: nada de forge-fechar nem das specs do item · obtido: rc 1 com 26 linhas de outras specs, idênticas às da base; ConferirTodas OK
- S2 · bin/forge-mutante nas specs v0481-fechar-ci-topo-2.json, v0481-fechar-ci-topo.json, mp1311-fechar-cartao.json e v047-integracao-em-lote-3.json · espera: todos morrem · obtido: rc 0 nas quatro (M9 a M12, M2 e IL-M21 incluídos)
- S3 · python3 -I tests/catraca.py --modo regras --base d49accf8 --head HEAD --ramo melhoria/v0481-fechar-ci-topo · espera: sem recusa · obtido: rc 0
- S4 · python3 -m unittest tests.test_fechar_ci_topo tests.test_fechar_sha_conferido tests.test_fechar_ref_por_nome · espera: OK · obtido: 26 testes, OK

## Detalhe (só aperta ou neutro)
- **Branch criada desfeita (bin/forge-fechar:444-445, :1670, :1755).** Aperta. O `fim` apaga `refs/heads/$ref` só por `git update-ref -d <ref> <sha criado>`: o valor antigo é exigido, então a branch que andou (outro agente, o 2b) não sai; `$ref` já passou por `check-ref-format --branch`; `branch_criada` nasce vazio (não herda do ambiente) e zera logo depois do passo 2, antes do PR e do merge, então nada depois do passo 3 apaga a branch que o merge e a limpeza usam. A parada antes do passo 3 deixa o servidor como única fonte na rodada seguinte: some o sha velho local e nenhum portão muda. Os itens do lote rodam em processo próprio (`--item-de-lote`), sem `ref` trocado sob o mesmo `branch_criada`.
- **Aviso do vermelho do topo (:1246-1247).** Neutro: só uma linha em stderr; o `ci_st`, o código 5 e a reversão impressa não mudam (M11 e o teste do vermelho do próprio merge provam os dois lados).
- **`--sem-limpar` na cópia principal (:1693).** Neutro em relação à base: a parada FECHAR-COPIA-CERTA nasceu neste mesmo item (dd2fcada) e só protegia o passo 7, que o `--sem-limpar` não roda; o fechamento segue pelos mesmos portões (1, 1c, 2, 2b, 6, 6b, `--match-head-commit`) e termina com código 3, como na develop. `--sem-limpar` é flag explícita, recusada junto com `--limpar` (:204) e nos modos lote, laço e promoção.
- **Specs e testes.** Só realinham o `de`/`para` à fonte e acrescentam mutantes e testes; nenhuma guarda sai. No código e nos controles em volta, só aperta ou neutro.

## Riscos aceitos e ferramentas
Nenhum risco aceito. CI: catraca verde no Revisar-sha (45530565279). A suíte rodou na árvore de código do Revisar-sha em duas execuções que os envios de pareceres (só docs) cancelaram: 45530565296 (58852bf2) e 45531353905 (5624fc6a); juntas, 8 das 10 partes verdes e nenhuma vermelha (faltam 3.12 parte 1 e 3.14 parte 3), mais `bateria (pareceres)` vermelha pelos pareceres presos a commits velhos, que este renova. O CI completo vale no commit deste parecer, que não toca código. gitleaks, zizmor, actionlint, semgrep e shellcheck ausentes no PATH (lacuna; o delta não toca workflow nem segredo).
