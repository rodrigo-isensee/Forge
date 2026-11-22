---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-seg-quarentena-fechar
commit: 3820b48415ae762ca859e669431b50fc84b18e03
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-22
---
# Review: v0478 (E114.7, branch melhoria/v0480-seg-quarentena-fechar)

Revalidação da volta única (H3, `R-REVIEW`) no head 3820b484, sobre o aprovado em e77f3543 (E114.2). Um commit de código (3820b484, E114.5): `bin/forge-fechar` +38/-23, um comportamento (a conferência dos check-runs antes do merge, no passo 6 e no P6). Dentro do teto H1.

## Achados
- A1 (recomendado) bin/forge-fechar:1602 · o prazo do passo 6 conta do `inicio` do passo 4, então a espera do 6b (`--espera-ci`, até 3600 s) também o consome; com checks já verdes no passo 4 não muda nada, mas um exigido ausente no passo 6 para sem espera. Dizer no doc que o 6b entra na conta.

## Parecer
**Aprovado.** O delta fecha o que a volta pediu:
- `skipped` não conta (`:874`): nem verde nem falha; exigido só em `skipped` fica ausente e espera (A1 da segurança).
- Os exigidos do ruleset ou da proteção do destino entram na conferência (`exigidos`, `:872`), lidos no passo 4 (`:1483`) e, no P6, para a `homolog` (`:1264`) (A3 da segurança).
- `ler_pr_antes_do_merge` extraída sem mudar as guardas e chamada de novo, com `conferir_base_no_merge`, depois da espera dos checks (`:1603-1604`) (A2 da segurança). PR que vira MERGED na espera cai no caminho já existente (`estado_do_pr` depois do merge que erra).
- O prazo do passo 6 deixa de recomeçar (`ini="$2"`, `:867`): fecha o A3 do meu parecer anterior; o A1 anterior (doc do `--armar`) também saiu (`docs/fechamento-integrador.md:82`).

O A2 anterior (`bin/forge-check:1469`, comentário com "armar o auto-merge") segue fora do delta: vira cartão depois do merge.

Guardas e mutantes (V2): cada guarda mudada tem mutante (VU1 a VU5 em `tests/mutantes/v0480-seg-quarentena-fechar.json`; FCK-M3, M4 e M7 atualizados em `v0478-fechar-checks.json`) e teste do ramo de falha por comportamento (skipped com id maior, exigido a mais ausente, base que muda na espera, prazo único). O falso do `gh` em `tests/test_fechar.py` para o ruleset falha sem o arquivo (404), tão estrito quanto o script (item 12).

Delta lido: `forge-check parecer delta docs/reviews/v0480-seg-quarentena-fechar.md`, intervalo `e77f3543..3820b484`, 9 arquivos no domínio (`bin/forge-fechar`, changelog, `docs/fechamento-integrador.md`, 2 specs de mutante, 4 testes); os pareceres de QA e segurança ficam fora do domínio.

Rodado aqui, sem a suíte inteira (fica no CI do PR): `python3 -m unittest tests.test_fechar_checks_do_head tests.test_fechar_lote.Promover` deu `Ran 40 tests ... OK`; `bin/forge-mutante tests/mutantes/v0480-seg-quarentena-fechar.json` deu os 7 mutantes `morreu` (QD1, FS1, VU1 a VU5).
