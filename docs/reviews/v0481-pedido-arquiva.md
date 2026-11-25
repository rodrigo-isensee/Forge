---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-pedido-arquiva
commit: 2c61be46e408759ced4ab72cbe2509bd3643a048
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E9.14, #874, pedido que se arquiva sozinho antes do teto, por delta)

Delta lido: `git diff 8b312446..2c61be46` (volta E9.13), e `forge-check parecer delta` deste parecer: "revalida: sim (bin/forge-check mudou depois do parecer)". Domínio código e testes: `bin/forge-check` (4 linhas), `tests/test_brief_tamanho.py` (2 testes novos), as specs `v0481-pedido-arquiva-3/-5/-6/-7.json` e as de outros pedidos realinhadas (`est-m12-gerar` M3, `v0474-h1-ferramenta-3` M16, `v0479-ae4-ordens` M5 e `-2` M16), e o fragmento do changelog. Os pareceres de QA e segurança e este arquivo no delta são da rodada anterior, não do item.

## Parecer
Aprovado. Nada que barrava no 8b312446 deixa de barrar no 2c61be46:

- `ENTREGUE_DA_ETAPA` (bin/forge-check:8061) só aperta: o lookahead passa a `(?![\w?-])`, e `entregue-se`/`Entregue-a` não fecham mais; `entregue - falta o PR` (hífen com espaço) segue fechando, com teste. Fecha o A1 recomendado do parecer anterior. Nenhuma linha `entregue-` nos pedidos da develop, então nenhum fechamento real some.
- O arquivo e a linha de `## Etapas arquivadas` (bin/forge-check:8127 e 8137) passam o nome do pedido por `caminho_impresso` (= `sem_controle`): só tira caractere de controle; para nome comum o texto é igual. O `i` → `j` na compreensão (8133) é só nome, sem efeito.
- Teste novo `test_parecer_ponto_e_virgula_e_segunda_etapa_cortam_o_entregue`: um caso por corte (`.md=`, `;`, 2ª etapa), e `test_entregue_com_hifen_nao_fecha` com o caso positivo do hífen solto. Os dois comportamentais, sobre `etapa_entregue_na_linha`.
- Mutantes realinhados de outros pedidos mantêm a mesma guarda: o `de` ficou mais longo só para voltar a ser único, e cada um aponta a linha original (M3 em 5128 `_ler_regular`, e não a cópia nova em 8098; M16 em 9861, o `# PEDIDO-TETO-BRIEF`, e não a cópia em 9852; ordens M5 em 5322 e M16 em 8357, com o texto que a branch trocou para `ids_de_etapa`). O `para` de cada um troca o mesmo pedaço de antes.
- M40 a M48 só acompanham o texto novo da regex; M49 é o mutante novo do hífen.

Ferramentas (rodadas aqui no 2c61be46): `tests.test_brief_tamanho` e `tests.test_forge_tamanho`, 49 testes, OK; `bin/forge-mutante --processos 1`: M21, M23, M24 (-3), M38 (-5) e M40 a M49 (-6, -7) morreram todos; `tests.test_forge_mutante -k ConferirTodas` (4) e `tests.test_forge -k SaidaSanitizada` (10), OK. O `forge-mutante --conferir --todas` ainda lista 26 trechos repetidos, todos de specs de outros pedidos que já repetem na base 8d7914bc e na develop; nenhum é deste item.

- ci: #874 no 2c61be46, as 10 partes da suíte (3.12 e 3.14), passos, verificações longas, instalação, teto de pulados e árvore já provada na develop estão verdes. Vermelhos que não são do código: `bateria (pareceres)` (pareceres ainda no head antigo) e `catraca` (R-CONFORMIDADE: muda `bin/forge-check`, pede o rótulo `afrouxa-regra` do dono depois do último push; os 3 avisos de valor esperado trocado em `tests/test_forge_tamanho.py` são a troca de 90% para 80% do pedido, já revisada).

Medida do item: o delta tem 4 linhas em `bin/`; a branch segue abaixo do teto de 150, um comportamento.
