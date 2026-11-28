---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-quarentena-fechar
commit: 3820b48415ae762ca859e669431b50fc84b18e03
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-22
---
# Review de segurança: v0478 (E114.6, revalidação da volta única)

Revalidação por delta no head `3820b484`. A rodada anterior (E114.3, head `e77f3543`, aprovado com recomendações) fica no git.

Gatilhos: controle de merge do integrador (bypass do ruleset pela conta do dono).

## Delta lido
`forge-check parecer delta` no intervalo `e77f3543..3820b484`. No domínio: `bin/forge-fechar`, `docs/fechamento-integrador.md`, `tests/test_fechar.py`, `tests/test_fechar_checks_do_head.py`, `tests/test_fechar_lote.py`. Fora do domínio (não relidos): `changelog.d/`, `tests/mutantes/*.json`, `tests/test_forge_fechar.py`. Relidos também os pontos de chamada que o delta toca: `ler_exigidos_do_destino` (`bin/forge-fechar:545`), `conferir_base_no_merge` (`:1003`) e a inicialização de `inicio` (`:1484`).

## Achados
- A1 (recomendado) bin/forge-fechar:874 · corrigido: a execução em skipped sai do awk antes de escolher a mais recente; o exigido só em skipped fica ausente e espera até o prazo, sem mesclar (falha fechada)
- A2 (recomendado) bin/forge-fechar:1604 · corrigido: depois da espera dos checks, ler_pr_antes_do_merge (base, fork, head, número pelo nome) e conferir_base_no_merge rodam de novo, logo antes do ready e do merge
- A3 (recomendado) bin/forge-fechar:1264 · corrigido: o P6 chama ler_exigidos_do_destino com alvo=homolog (:1197) e checks_do_head_verdes itera exigidos, não só CHECKS_EXIGIDOS
- A4 (recomendado) scripts/promover-homolog.py:341 · aberto, fora do delta e do escopo desta volta: o script ainda imprime gh pr merge develop --auto e docs/promocao-integrador.md:18 manda armá-lo; vira cartão para devops-engineer e tech-lead
- A5 (recomendado) docs/fechamento-integrador.md:28 · corrigido no doc; sobra o comentário bin/forge-check:1469 ("armar o auto-merge"), sem efeito em execução e fora do delta; vira cartão informativo

## Sondas

## Detalhe
- **A1:** `bin/forge-fechar:874` filtra `$4 != "skipped"`; `neutral` e as demais conclusões fora de `success` continuam parando (mais estrito que o GitHub, falha fechada). Testes: `test_skipped_nao_conta_nem_com_id_maior` (`tests/test_fechar_checks_do_head.py`) e `test_bateria_skipped_do_push_nao_para_e_exigido_da_homolog_conta` (`tests/test_fechar_lote.py`).
- **A2:** ordem nova `:1592` (6a), `:1598` (releitura), `:1602` (espera), `:1604-1605` (releitura do PR e da base), ready, merge. Sobra a janela entre a última leitura e o merge, documentada em `:895-898`; o `--match-head-commit` prende o head. Teste: `test_pr_que_muda_de_base_na_espera_dos_checks_nao_mescla`.
- **A3:** `:1264-1265`. A leitura do ruleset que falha cai no piso `CHECKS_EXIGIDOS` (desenho de E3.45, `:542-544`), o mesmo do passo 4; não é regressão (antes o P6 conferia só o piso). Teste: o exigido `lint` da homolog sem check-run para o P6.
- **Prazo único (A3 do review):** `checks_do_head_verdes 6 "$inicio"` usa o `inicio` do passo 4 (`:1484`), sempre definido quando `ja_mesclado=0`, o único caminho que chega à `:1602`. Encurta a espera, nunca a afrouxa.
- **A4 e A5 (resto):** cartões, como pede a regra de achado fora do delta; nenhum dá caminho de merge sem check no `forge-fechar`.

Nada afrouxa: as três mudanças só acrescentam conferência ou encurtam prazo.

## Provas executadas
- `bash -n bin/forge-fechar`: sintaxe OK.
- `python3 -m unittest test_fechar_checks_do_head test_fechar_lote.Promover test_fechar_auto_merge` (em `tests/`): 48 testes, OK (inclui os testes novos de A1, A2, A3 e do prazo único).
- A suíte inteira fica para o CI do PR, que o passo 4 do `forge-fechar` exige; o brief pede sem suíte local.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e execução local dos testes afetados; sem acesso ao `gh` no sandbox (a semântica de `skipped` vem dos workflows e dos dublês dos testes).
