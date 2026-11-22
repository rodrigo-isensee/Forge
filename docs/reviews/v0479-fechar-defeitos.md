---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-fechar-defeitos
commit: e6c1fe8a2e054a09261612232fcb6fd4bb97f780
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E75.7, melhoria/v0479-fechar-defeitos)

Revalidação (H3, R-REVIEW) do parecer 06ac3ef8 (reprovado no 5d383ebf por A1 e A2). Delta lido: `forge-check parecer delta`, intervalo `5d383ebf..e6c1fe8a`, no domínio `bin/forge-fechar`, `changelog.d/v0479-fechar-defeitos.md`, `tests/mutantes/v0478-fechar-6a.json`, `tests/mutantes/v0478-fechar-checks.json`, `tests/mutantes/v0478-fechar-checks-2.json`, `tests/test_fechar.py`, `tests/test_fechar_base_andou.py`, `tests/test_fechar_checks_do_head.py`. Nada fora do delta foi relido.

## Sondas
- S1 · check-runs filter=latest do head 9441c447 (PR 745) no awk da linha 872 · espera: os três exigidos completed/success · obtido: os três completed/success (catraca id 136879394213 success vence id 136879303871 cancelled)

## Parecer
Aprovado.

- A1 (resolvido): `checks_do_head_verdes` julga, por nome exato de `CHECKS_EXIGIDOS`, só a execução de id maior; a forma real do PR 745 passa (S1) e a execução mais nova com falha recusa mesmo com a velha verde, nas duas ordens da resposta.
- A2 (resolvido): `test_rotulo_aplicado_catraca_velha_cancelled_e_nova_verde_mescla` fixa a forma real nas duas ordens; o falso de `gh api` em `test_fechar.py` confere o caminho e o `--jq` exatos do script e, por padrão, devolve a catraca cancelled ao lado da verde.
- `--armar` (A1 da segurança): recusa a execução mais recente já terminada fora de success (failure, cancelled, timed_out) e arma com ela rodando ou ausente; mensagem própria nos dois ramos.
- 6a (A2 da segurança): a guarda `local_base != srv` depois da busca tem mutante (F6A-M4) e teste do ramo de falha com a develop andando de novo.
- Guardas mudadas com um mutante por linha (FCK-M2 a FCK-M9, F6A-M4); changelog coerente com o comportamento.

Verificações: `bash -n bin/forge-fechar` ok; `bin/forge-testes` com test_fechar, test_forge_fechar, test_fechar_base_andou, test_fechar_checks_do_head e test_fechar_auto_merge: 205 testes, OK (1 pulado); `bin/forge-mutante --ids FCK-M2,FCK-M4,FCK-M5`: os três morreram. Suíte inteira fica no CI do PR.
