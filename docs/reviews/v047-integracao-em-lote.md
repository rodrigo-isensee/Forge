---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-integracao-em-lote
commit: c6b0b788c2815bbdf130a43d2a47eb2bbe6818ed
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.237, lote do forge-fechar)

Intervalo `origin/develop..c6b0b788` (6 commits da E1.197): INTEGRACAO-EM-LOTE (`--lote`, diretriz 26), FECHAR-ESPERA-CI-DEVELOP (passos 6b e 8, `--espera-ci`, código 5) e RELEASE-EM-1H (`--promover <sha>`, diretriz 27), com o texto em `R-FLUXO`, `agents/tech-lead.md`, `docs/fechamento-integrador.md`, skill `trabalho-em-paralelo` e o modelo de projeto. Revisor: instância que não fez a entrega.

## Achados
- A1 (bloqueante) bin/forge-fechar:980 · --promover abre PR promocao/<versão> -> homolog; o "Nada pula degrau" (ci.yml:509) exige head develop e falha (S1), e catraca.PROMOCOES e arvore-testada não o reconhecem (S2): o PR nunca fica verde e o P6 para (R-FLUXO).
- A2 (recomendado) tests/test_fechar_lote.py:314 · os testes de Promover usam um gh falso que aceita qualquer par head/base; nenhum confronta o par com o degrau do CI e da catraca (checklist 12, falso mais frouxo que o real), o que deixou A1 verde. Um teste que cruze o par com PROMOCOES fecha a classe.
- A3 (recomendado) bin/forge-fechar:908 · o CI do lote é o do último "merge:" lido nas saídas dos itens; item cujo PR já constava MERGED traz um merge antigo, e o CI acompanhado deixa de ser o do topo do lote (cancelado dá código 5 à toa). Sugestão: acompanhar o topo da develop do servidor depois do L3.
- A4 (recomendado) changelog.d/v047-integracao-em-lote.md:2 · pendente: o cartão pede a medida no forge-check metricas (E1.119) e o aviso ao dono com o PR para a main verde (E1.121, ponto 3); nada disso está no diff. Confirme com o Jarvis se fica para outro item e registre no PR.

## Sondas
- S1 · BASE=homolog HEAD_REF=promocao/0.47.1 no passo "Nada pula degrau" de ci.yml:508-511 · espera: ok (o PR da promoção passa) · obtido: "PR para homolog só a partir da develop (veio de promocao/0.47.1)." rc=1
- S2 · catraca.eh_promocao com head promocao/0.47.1 e base homolog no mesmo repo · espera: True · obtido: False (PROMOCOES = develop->homolog, homolog->main)

## Verificadores
- Teste novo: `python3 -m unittest tests.test_fechar_lote` (ambiente limpo) · 50 testes, OK, 162 s. A suíte inteira fica no CI do PR (ainda sem PR; não rerrodada).
- `shellcheck bin/forge-fechar` · rc=0.
- Mutantes declarados: 8 arquivos `tests/mutantes/v047-integracao-em-lote*.json`; a mutação é do autor (V2), não refeita aqui.
- Tamanho (M14): 807 linhas de código e teste (bin e tests/*.py); o corpo do PR precisa de `teto: excedido, 807 linhas, <motivo>` (lote decidido pelo dono por arquivo comum, E1.197).

## Parecer
Reprovado por A1. O lote (L1 a L3, um CI só no último merge, reversão impressa e código 5) e a espera do CI da develop (6b e 8) estão corretos e cobertos pelos testes do ramo de falha; a leitura de `esperar_ci` (sem execução não é verde, cancelado separado de vermelho, prazo vira pendente) confere com a diretriz 26. A promoção pela marca, porém, cria um degrau novo (`promocao/*` -> `homolog`) que o CI e a catraca recusam: em produção o `--promover` nunca mescla, e a meta de 1 h da diretriz 27 não anda. Na volta: ou o PR de promoção sai da `develop` (com a `develop` parada na marca, como na 0.47.0, e `--match-head-commit <marca>`), ou o par entra no degrau do CI, em `PROMOCOES` e no `arvore-testada` com teste e com o parecer do `devops-engineer` (pipeline) e da segurança (catraca). A2 a A4 não devolvem.
