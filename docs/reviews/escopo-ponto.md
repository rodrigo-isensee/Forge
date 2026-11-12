---
tipo: review
contrato: 1
pedido: v0457
branch: melhoria/escopo-ponto
commit: c51ecb4847bcac295a72bf42f0dec8ab44f1538e
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-12
---
# Review: v0457 (E23.41, melhoria/escopo-ponto no c51ecb48)

Revalidação por delta (E23.41), por instância que não fez a entrega. Delta lido: `forge-check parecer delta docs/reviews/escopo-ponto.md`, intervalo ba35957368421e2e1803e48011839eaa83454463..c51ecb4847bcac295a72bf42f0dec8ab44f1538e, no domínio bin/forge-check, changelog.d/escopo-ponto.md, tests/mutantes/v0457-escopo-ponto{,-2,-3,-4}.json, tests/test_conf_escopo.py, tests/test_selo_e_entrega.py. Testes dos arquivos tocados, um módulo por vez: `test_conf_escopo` 16 OK; `test_selo_e_entrega` 62 OK.

## Achados
- A4 (bloqueante) bin/forge-check:2321 · revisao-devops vai à etapa `devops`, que não existe; o brief de portão real do devops é `Etapa: review` e o parecer de devops nunca ancora: regressão da E23.36 (d) (S2); a fixture em tests/test_selo_e_entrega.py:717 a esconde

## Detalhe do A4
A etapa `devops` não está em ETAPAS_DO_GERAR (o `brief selar` a recusa no vocabulário); o brief do portão de devops é `Etapa: review` com Revisar-sha (v0457-devops-engineer-2, E23.16). O teste sela à mão `Etapa: devops`, mais frouxo que a ferramenta. Correção: devops pela etapa `review` com `Agente destino: forge:devops-engineer` (e o review com `forge:tech-lead`, para um não ancorar o outro), fixture com a etapa real e mutante da distinção.

## Sondas
- S1 · test_conf_escopo.PareceresPeloPedido.test_parecer_de_outra_branch_com_o_id_nao_troca_o_slug (docs/reviews/x.md pedido x da melhoria/x, docs/reviews/p1.md pedido p1 da melhoria/outra), merge-integracao · espera: rc 0 e escopo ok · obtido: OK (no ba359573 dava rc 1)
- S2 · ParecerDoPortao com brief de portão selado como o real (`Etapa: review`, Revisar-sha = head) e parecer revisao-devops em docs/devops/x.md com esse commit: · espera: escopo ok (anexo do portão), como no ba359573 · obtido: rc 1, escopo: fora do declarado no brief "docs/devops/x.md"

## Revalidação dos achados anteriores
- A1 resolvido: pedido_dos_pareceres só troca o slug pelo id com `branch:` igual (bin/forge-check:2273); teste do caso misto e M7, M8, M27.
- A2 resolvido, mais estrito que o pedido: o `commit:` precisa ser o Revisar-sha de brief selado do portão da branch e do pedido, e veredito trocado no mesmo `commit:` recusa, com git que falha contando como troca (M19 a M23, M28).
- A3 resolvido pelo teste do S1.
- Conferidos sem achado: merge-base só ancorado em Base-sha de brief selado mais novo que o da entrega (M24 a M26, sonda da ref reescrita virou teste); tipo e parecer do anexo com teste e mutante (M16, M18); VV-3 com o ponto inicial (M1). Mutantes M1 a M28 com specs atualizadas (AR-12 conferido); não achei log do forge-mutante sobre o c51ecb48 em ~/.forge-contrib/wt/ (o escopo-ponto.mutante4.log é anterior à volta): fica com o QA.
- Fora deste PR, por decisão registrada no brief: os filtros L08/G2 também confiam na `origin/develop` local; vira cartão para a versão seguinte, não achado aqui.

## Tamanho (M14)
bin/forge-check (159) e tests/*.py (397): 556 linhas desde o Base-sha. O PR precisa trazer `teto: excedido, 556 linhas, <motivo>`; o motivo (consertos da mesma conferência, volume nos testes dos ramos negativos e das voltas de segurança) basta.

## Parecer
Reprovado por A4: defeito provado (S2) introduzido no delta, que anula para o devops o anexo do portão que a E23.36 (d) entregou. A1, A2 e A3 da rodada anterior estão resolvidos. A segurança das âncoras (anexo e merge-base) fica com o parecer do security-engineer.
