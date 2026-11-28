---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: d38537ee5176cd9cc587a6158fc6662e99dd6bb5
parecer: aprovado
escopo: incremental
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-27
---
# QA: v0481 (E47.13, #948, espera amarela, delta da volta 2)

Delta `054d4103..d38537ee` (só `tests/test_catraca.py`, `tests/test_ci_local.py` e a spec `tests/mutantes/v0481-espera-amarela-5.json`) contra os meus A1-A4 da 1.ª rodada, que fecharam. Clone de revisão `/root/.forge-contrib/wt/v0481-espera-amarela-qa-engineer-2`; logs em `/root/.forge-contrib/wt/qa-v0481-volta2/`. Sem produção no delta, sem `docs/ux`. A 1.ª rodada (CE-1 a CE-6, M1-M25) segue valendo: não mudou no domínio.

- ci: d38537ee5176cd9cc587a6158fc6662e99dd6bb5 verde
  - Run CI `46092864322` do `Revisar-sha`: verdes `árvore já provada na develop`, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação (python 3.14)`, `teto de pulados` e as 5 partes da suíte 3.12; falham só `bateria (pareceres)` e `bateria` (esperam os pareceres, fora da conta, G3). O check `catraca` e seu job interno `catraca (conferência)` seguem vermelhos no head pelo rótulo do dono ausente (R-CONFORMIDADE, `[afrouxa-regra` no título), como na 1.ª rodada. Os descendentes só tocam `docs/security/` e `docs/reviews/`.

## Fechamento dos achados

| Achado | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| A1 (Q1) CLI `--modo pareceres`, reprovado sem arquivo sensível, rc 1 | `EsperaNaoEVermelho.test_reprovado_sem_arquivo_sensivel_sai_1` | parecer reprovado sem arquivo sensível | fechou: M26 e Q1 morrem |
| A1 (Q2) QA reprovado, review e segurança aprovados, arquivo sensível, rc 1 | `test_qa_reprovado_com_review_aprovado_e_arquivo_sensivel_sai_1` | cmd_pr sem achado | fechou: M27 e Q2 morrem |
| A2 (Q3) `sem parecer da branch` sai 3; vizinhos não casam | `test_so_parecer_de_outra_branch_sai_3`, `test_linha_sem_parecer_da_branch_e_o_vizinho` | `branchx`, espaço duplo, `parecer conferido` | fechou: M28 e Q3 morrem |
| A3 (Q5) rc 1 com `gh` `nenhum` ou `failure` não grava espera | `EsperaAmarelaNosWorkflows.test_espera_grava_o_sufixo_...` (subTest por estado, nos dois workflows) | rc 1 com a API respondendo | fechou: M29, M30 e Q5 morrem |
| A4 `--vermelho` dá veredito nos 3 de `EsperaAmarelaNosWorkflows` | `job()`, `agregador()` e `fim_do_passo` com asserção explícita | job ou passo ausente na base | fechou: os 3 viram `prova (asserção)` |

## Vermelho antes do verde (`bin/forge-testes --vermelho 319a968d --modulos test_catraca,test_ci_local`, rc=0)

```
vermelho: base=319a968df760 head=d38537ee5176 módulos=test_catraca,test_ci_local (restrito por --modulos)
contagem: não prova (passa na base)=498; prova (API ausente)=12; prova (asserção)=7
EsperaNaoEVermelho.test_linha_sem_parecer_da_branch_e_o_vizinho · prova (API ausente)
EsperaNaoEVermelho.test_so_parecer_de_outra_branch_sai_3 · prova (API ausente)
EsperaAmarelaNosWorkflows (3 testes) · B=falha · prova (asserção)
```

`test_reprovado_sem_arquivo_sensivel_sai_1` e `test_qa_reprovado_com_review_aprovado_e_arquivo_sensivel_sai_1` passam na base de propósito (guardas negativas: o comportamento vermelho já existia); quem as prova são M26/M27 e Q1/Q2. Nenhum sem veredito.

## Mutantes (rc=0 nas duas)

```
forge-mutante tests/mutantes/v0481-espera-amarela-5.json (rev=d38537ee5176)
M26 · morreu · tests/catraca.py:2149
M27 · morreu · tests/catraca.py:2157
M28 · morreu · tests/catraca.py:156
M29 · morreu · .github/workflows/catraca.yml:58
M30 · morreu · .github/workflows/ci.yml:618
rc=0
forge-mutante qa-mut.json (Q1-Q7, lista do QA, rev=d38537ee5176)
Q1 · morreu · tests/catraca.py:2149
Q2 · morreu · tests/catraca.py:2157
Q3 · morreu · tests/catraca.py:156
Q4 · morreu · tests/catraca.py:2326
Q5 · morreu · .github/workflows/catraca.yml:58
Q6 · morreu · .github/workflows/catraca.yml:74
Q7 · morreu · .github/workflows/ci.yml:619
rc=0
```

Sem sobrevivente. As specs 1-4 (M1-M25) não mudaram no delta.

## Outras observações
- Acessibilidade e E2E de navegador: n/a (workflow e script de catraca, sem tela).
- Bugs em `docs/qa/bugs/`: nenhum. O D2 local em `tests/test_pre_push_trava.py:610` falha na base e já foi corrigido na develop (#949); não é do delta.
