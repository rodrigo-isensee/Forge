---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/lote-cilista-v2
commit: 6f7a9d1a5d629c350ee2411712a9b5c26a25f0bd
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-04
---
# Review de segurança: lote-cilista-v2

## Gatilhos
R-SEGURANCA: controles do Forge (tests/test_ci_local.py, trava de ordem do lint do CI).

## Achados
- A1 (bloqueante) tests/test_ci_local.py:44 · o analisador por linha não vê âncora e merge YAML (&a, <<: *a): um passo antes do lint herda shell que executa código da branch e a trava passa; sonda reproduzida

## Detalhe dos achados
Fechados da rodada anterior, conferidos nas variantes do teste: A5 (lista positiva de env por chave exata, em qualquer recuo, inline, com aspas) e A6 (CHAVES_DO_LINT reprova continue-on-error e working-directory). Os 53 testes do arquivo passam.

A1: evidência tests/test_ci_local.py (ENV_QUE_EXECUTA e passos_da_bateria, leitura por linha). Sonda: no checkout da bateria, uma chave extra `x: &a {shell: "bash scripts/x.sh {0}"}` e, no gate, `<<: *a`; passos_antes_do_lint_fora_da_lista devolve [] (o hash do run do gate não cobre o shell herdado). O GitHub Actions aceita âncoras desde 2025. Quem: autor de PR que edita o ci.yml sem tocar o teste; ganha execução de código da branch antes do actionlint e do zizmor, o que a trava existe para impedir. Severidade média. Correção mínima: reprovar no arquivo inteiro qualquer âncora, alias ou chave de merge (em ENV_QUE_EXECUTA, `(^|[\s:{,])[&*][A-Za-z_]` e a chave `<<`) e acrescentar uma variante às sondas. Esforço P, dono: autor do lote.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Análise estática; sonda local em Python fora da árvore; zizmor, actionlint e gitleaks não rodados.
