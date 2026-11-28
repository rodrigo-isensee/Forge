---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-espera-amarela
commit: d38537ee5176cd9cc587a6158fc6662e99dd6bb5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-27
---
# Review: v0481 (E47.14, #948, espera amarela, delta da volta 2)

Delta lido `bc60149c..d38537ee` (commit `d38537ee` do E47.11, mais os pareceres de QA `e3cee390` e `7f3f8242`), no clone de revisão `/root/.forge-contrib/wt/v0481-espera-amarela-tech-lead-5`. Delta lido pela ferramenta: `forge-check parecer delta docs/reviews/v0481-espera-amarela.md` · `revalida: sim (desatualizado: tests/mutantes/v0481-espera-amarela-5.json mudou depois do parecer; ... é do domínio do parecer de review)`. A rodada anterior (E47.7, head `054d4103`, aprovado) fica no histórico do git.

## CI e ferramentas (citadas, não refeitas)
- ci: d38537ee5176cd9cc587a6158fc6662e99dd6bb5 verde
- Check-runs do `d38537ee` (runs `46092864476` e `46092944625`): suíte 3.12 (5/5), `bateria (passos)`, `bateria (python 3.14)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `teto de pulados (python 3.12)` e `árvore já provada na develop` verdes. Vermelhos que esperam: `bateria (pareceres)` e `bateria` (pareceres) e `catraca (conferência)` com `catraca` (log do job `140817794173`: só R-CONFORMIDADE sem o rótulo `afrouxa-regra` em `catraca.yml`, `ci.yml` e `tests/catraca.py`, script da base sem o rc 3, como na rodada anterior). O head `625750dd` acima dele só traz `docs/security/`.
- Produção: `git diff --stat bc60149c..d38537ee -- . ':!tests' ':!docs'` vazio, e `tests/catraca.py` fora do diff; nenhuma linha de controle mudou. Teto (H1) segue em 123 linhas.
- Testes do diff, à mão: `test_catraca.EsperaNaoEVermelho` e `test_ci_local.EsperaAmarelaNosWorkflows` · 19 testes, OK.
- Mutantes: `bin/forge-mutante --processos 1 tests/mutantes/v0481-espera-amarela-5.json` · M26 (`catraca.py:2149`), M27 (`:2157`), M28 (`:156`), M29 (`catraca.yml:58`) e M30 (`ci.yml:618`) morreram, os Q1, Q2, Q3 e Q5 do QA.

## Leitura do delta
1. A1 do QA: os dois testes novos dirigem o CLI `--modo pareceres` em subprocesso; um sem arquivo sensível (ramo `not tocados`) e outro com `hooks/` e review e segurança aprovados e QA reprovado, que chega ao ramo `pedidos and not achados` (a ausência de `R-REVIEW` na saída prova o ramo). Os dois exigem rc 1 e a ausência de `catraca: espera`.
2. A2 do QA: `sem parecer da branch` sai 3 pelo CLI, e o teste do padrão afirma o caso positivo e três vizinhos (`branchx`, o vazio com espaço duplo que o M28 criaria, e `conferido`), cada um em `subTest`.
3. A3 do QA: o rc 1 do script agora roda com o `gh` respondendo `nenhum` e `failure`, nos dois workflows, e exige rc 1 sem `espera=`; o caso antigo com o `gh` saindo 9 ficou, então nada perdeu força.
4. A4 do QA: o desempacotamento por tupla virou `job()`/`agregador()` com `assertIn` e `assertEqual(len(...), 1)`; mesma força, e a base agora reprova por asserção, não por erro. As asserções existentes sobre o nome do agregador, `pernas`, `always()` e o passo da catraca seguem iguais.
5. Commit em Conventional Commits em português, com pedido e etapa; a spec `-5` tem 5 mutantes, abaixo do teto de 8, um por linha de guarda apontada pelo QA.

## Parecer
Aprovado no `d38537ee`. Os A1 a A4 do QA estão fechados com teste de comportamento que dirige o ramo certo, os mutantes Q1, Q2, Q3 e Q5 morrem, nenhum teste existente perdeu força e nenhuma linha de produção mudou. O vermelho do D2 local em `tests/test_pre_push_trava.py:610` fica fora do delta (corrigido na develop, #949).
