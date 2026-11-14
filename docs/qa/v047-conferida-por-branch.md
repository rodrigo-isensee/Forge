---
tipo: qa
contrato: 1
pedido: v047
branch: melhoria/v047-conferida-por-branch
commit: 7c91b13d795b743b129ef41f55ab755b5eee4ad2
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-14
---
# QA: v047 (conferida por branch, E1.185; QA E1.196)

## Achados
- A1 (recomendado) tests/test_conferida_por_branch.py:57 · o teste do `desde_da_branch` cai na base por TypeError (assinatura nova), não por asserção, e o `forge-testes --vermelho` sai 2 (sem veredito); as outras 3 provam por asserção. Um teste que chame sem `base_ref` e compare o retorno prova por asserção (R-QA).

## Critério → teste → resultado
O pedido (E1.185) não tem especificação de UX; as obrigações vêm do texto do item: ignorar a conferida já contida na base como Desde, sem perder a da própria branch (CA-1 a CA-4), e a mudança de expectativa dos dois testes de `MergeDaBaseDepoisDoBrief` (CA-5).

| Critério | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| CA-1 conferida de outro item, já na develop, não é o Desde (intervalo do Base-sha, arquivo do outro item fora do escopo) | `ConferidaDeOutroItem.test_conferida_de_a_na_base_nao_e_o_desde_de_b` | conferida ancestral da `origin/develop` e fora do Base-sha | passou; base falha (asserção) |
| CA-2 a conferida da própria branch segue sendo o Desde depois do merge da base | `test_conferida_da_propria_branch_segue_sendo_o_desde` | controle: conferida não ancestral da base | passou; base falha (asserção) |
| CA-3 `entrega --desde <conferida de outro item>` é recusado | `test_forma_antiga_recusa_a_conferida_de_a_como_desde` | `--desde` sobre commit já na base | passou; base falha (asserção) |
| CA-4 o Desde proposto aos briefs é o Base-sha (`desde_da_branch`) | `test_desde_proposto_aos_briefs_e_o_base_sha` | `base_ref` ausente vs presente | passou; base: erro de assinatura (A1) |
| CA-5 expectativa mudada em `MergeDaBaseDepoisDoBrief` (rc 1 a 0 e `intervalo: <Base-sha>..`) | `test_merge_base_sem_ancora_fica_o_base_sha`, `test_head_ja_na_develop_mantem_o_base_sha` | sem âncora; head já na base | passou |

Os dois testes mudados: o rc=1 antigo fixava o defeito (a conferida trazida virava Desde e `agents/outro.md` da develop aparecia fora do escopo); o rc=0 novo com `intervalo: <Base-sha>..` e `assertNotIn("agents/outro.md")` é afirmação mais forte, não afrouxamento. Concordo com o review.

## Cenários e resultado real
- Execução local no head 7c91b13d (código idêntico ao do merge dos pareceres 1e7c183f): `python3 -m unittest tests.test_conferida_por_branch tests.test_selo_e_entrega.MergeDaBaseDepoisDoBrief`: `Ran 12 tests in 379.782s` `OK`.
- Suíte inteira: não rerrodada; vai ao CI do PR (`bateria`), que ainda não existe (brief: sem PR).
- Vermelho (`forge-testes --vermelho 6517ff14 --modulos test_conferida_por_branch --prazo 900`): `vermelho: base=6517ff14034b head=1e7c183f702b`; revertidos à base `bin/forge-check` e os documentos; 3 testes `H=ok · B=falha · prova (asserção)`, 1 `H=ok · B=erro · sem veredito`; `contagem: prova (asserção)=3; sem veredito=1`; rc=2 (A1). A rodada sem `--modulos` não terminou em mais de 25 minutos (suíte completa sob carga) e foi descartada.
- Mutação (`bin/forge-mutante tests/mutantes/v047-conferida-por-branch.json tests/mutantes/v047-conferida-por-branch-2.json --processos 2`): `rev=1e7c183f702b`, CB-M1 a CB-M10 `morreu`, rc=0. Conferi a lista contra o diff: as linhas de guarda mudadas (`ja_na_base`, `desde_valido`, `base_sha_como_desde`, `veredito_do_desde`, `cmd_entrega_conferir`) têm mutante.
- Review A1 (ramo `revisados` sem `ja_na_base`, `bin/forge-check:2186`): confirmo na leitura do diff; é recomendado, fora do escopo do item, sem teste que o exponha.
- Bordas: `base_ref` ausente (`None`) mantém o comportamento antigo (só Base-sha); a ref reescrita só tira candidatas (falha fechada, segundo o review).
- Permissões e acessibilidade: n/a (ferramenta de linha de comando).
