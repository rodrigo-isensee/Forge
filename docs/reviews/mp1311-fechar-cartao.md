---
tipo: review
contrato: 1
pedido: melhorias-de-projeto-1311
branch: melhoria/mp1311-fechar-cartao
commit: 0884fae230d784f90d6cb0108dfa414ee91707e0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: melhorias-de-projeto-1311 (fechamento: FECHAR-REF-POR-NOME)

## Achados
- A1 (recomendado) tests/test_fechar_ref_por_nome.py:20 · test_dry_run_descreve_o_nome duplica a asserção de tests/test_fechar.py; o M3 só é morto pelo teste de test_fechar.py. Inofensivo.

## Sondas

## Parecer
Aprovado. Classe C, head 0884fae2, instância que não fez a entrega.

- Faz o que o item pede: com a branch local, `forge-check pr` recebe o nome (`ref_check="$ref"`); sem ela, o sha lido do servidor via `remoto_exato` (`bin/forge-fechar` 820-832). O dry-run segue a mesma regra.
- Cadeia do sha conferido intacta: `sha_conferido` lido antes do passo 1, `head_atual` relido depois do passo 1 e no passo 2, `--match-head-commit` no merge; o caminho sem branch local mantém o commit exigido (`cat-file`) e a releitura no servidor. Teste `test_head_que_anda_durante_a_conferencia_ainda_para` cobre o head que anda.
- Guardas do diff: 3 linhas mudadas, 3 mutantes declarados (M1, M2, M3), todos mortos (`bin/forge-mutante tests/mutantes/mp1311-fechar-cartao.json`). Cada ramo tem teste de comportamento.
- Testes rodados aqui (sem PR, só os afetados): test_fechar 99 OK, test_fechar_ref_por_nome 4 OK, test_fechar_sha_conferido 9 OK, test_fechar_base_andou 30 OK. `shellcheck bin/forge-fechar` sem saída.
- Tamanho: bin/forge-fechar 19 linhas e testes dentro da orientação de 150; um comportamento só. Fragmento em `changelog.d/` presente.
