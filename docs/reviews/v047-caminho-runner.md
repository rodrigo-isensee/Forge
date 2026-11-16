---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-caminho-runner
commit: 72d2eaa01398a1f9d9713347fe2a9620fa035863
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-13
---
# Review: v047 (E5.22, CAMINHO-PESSOAL-BARRA-RUNNER)

## Achados

## Sondas

## Parecer
Aprovado no head 72d2eaa0 (classe C, 1 linha de código, 2 de teste). A troca de `@` por `@/` em `scripts/verificar-contribuicao.sh:55` devolve a barra que o `/home/runner/` consumia, então `/home/runner/home/<nome>/` e `/home/runner/Users/<nome>/` passam a ser acusados; o home do runner sozinho (`/home/runner/work`) vira `@/work` e continua sem acusar (coberto pelos casos antigos do mesmo teste). A spec antiga `v047-caminho-pessoal.json` (CP-M1 a CP-M3) foi atualizada ao novo `de`, e `v047-caminho-runner.json` traz um mutante (CR-M1) para a guarda alterada. Evidência: `unittest tests.test_forge.VerificarContribuicao` 15 testes OK; `forge-mutante` CR-M1 morreu e CP-M1, CP-M2 e CP-M3 morreram; `shellcheck` limpo. Sem PR aberto; suíte inteira fica no CI. Fragmento de changelog presente. Guardas: 1 linha, 1 mutante.
