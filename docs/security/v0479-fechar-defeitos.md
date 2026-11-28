---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-fechar-defeitos
commit: e6c1fe8a2e054a09261612232fcb6fd4bb97f780
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0478, E75.8 (melhoria/v0479-fechar-defeitos)

Revalidação (volta por delta) do parecer de 71210414 (commit revisado 5d383ebf). Delta lido: `forge-check parecer delta` no intervalo `5d383ebf..e6c1fe8a`; no domínio, `bin/forge-fechar`, `tests/test_fechar.py`, `tests/test_fechar_base_andou.py` e `tests/test_fechar_checks_do_head.py`; os mutantes em `tests/mutantes/` também foram lidos. O resto da rodada anterior (1c, 6a e pareceres) está no git e não mudou.

## Gatilhos
Gatilhos: controle do Forge (`bin/forge-fechar`, portão de checks antes do merge no passo 6).

## Resumo
- **A1 (anterior, recomendado): fechado.** `checks_do_head_verdes "$armar"` passou a rodar também com `--armar` (`bin/forge-fechar:1599`). Ele para quando a execução mais recente de um obrigatório terminou fora de success, antes do `ready` e do `mesclar_auto` (`:875`). Rodando ou ausente, o `--armar` arma. Os textos de `:861-865` e `:1487-1488` agora seguem a premissa real do bypass. Teste: `test_com_armar_e_check_terminado_com_falha_recusa` (failure, cancelled e timed_out, com uma catraca velha verde ao lado).
- **A2 (anterior, recomendado): fechado.** O teste `test_6a_busca_que_traz_outra_base_alem_da_lida_para` faz a develop andar de novo entre o `ls-remote` e a busca, e espera a parada sem merge. O mutante F6A-M4 (`tests/mutantes/v0478-fechar-6a.json`) prende a guarda de `:1002`.
- **Julgamento pela execução de id maior** (`:866-882`): dentro de cada nome de `CHECKS_EXIGIDOS`, o `awk` fica com a linha de maior `id`, sem depender da ordem. O merge direto exige `completed/success` nela, e a falta dela também para. Leitura que falha para (`:868-869`). Nome mais longo continua sem valer pelo exigido.

Confirmação: **não só aperta**. O `--armar` aperta: antes armava com falha terminada, agora recusa. O julgamento por nome afrouxa num caso: com duas execuções do mesmo nome, uma velha que falhou e uma nova verde (re-run, ou a catraca cancelled da troca de rótulo, caso do PR 745), o merge antes era recusado (`test_duplicata_do_exigido_precisa_de_todas_verdes`, removido) e agora passa. Isso corrige uma recusa falsa e não dispensa check. Continuam valendo os dois afrouxamentos do parecer anterior (1c e 6a). Por isso o rótulo `afrouxa-regra` deste PR espera o OK do dono.

Observação sem achado: uma execução nova com o mesmo nome vinda de outro workflow, com id maior e verde, esconderia a falha do obrigatório, porque o casamento é só por nome (a observação anterior sobre `${par#*/}`). No merge direto, o passo 4 confere o par workflow/nome antes. No `--armar` o passo 4 não roda, mas criar ou mudar workflow exige o escopo `workflow`, que o token do bot não tem. Só o dono abre esse caminho, então fica como observação, sem achado. Resíduo já conhecido: com `--armar` e o check ainda rodando, o bypass do dono pode mesclar na hora. Isso fecha só com a retirada do bypass (E5.1, decisão do dono).

Suíte: a branch não tem PR nem CI (`gh pr list` e `gh run list --branch melhoria/v0479-fechar-defeitos` devolvem `[]`). Rodei os testes de abuso: `python3 -m unittest tests.test_fechar_checks_do_head tests.test_fechar_base_andou` deu 52 OK no e6c1fe8a. Sondas de mutante numa cópia em `$TMPDIR`, todas mortas: sem a guarda de `:1002`, o teste novo do 6a falha; com `--armar` sem morrer em `completed/*`, o teste de falha terminada falha; com a primeira linha no lugar do id maior, 6 testes de checks falham.

## Sondas

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática, testes de abuso e sondas de mutante locais. Não rodei `gitleaks` porque o delta não toca segredo nem configuração. Os check-runs reais não foram lidos porque não há PR.
