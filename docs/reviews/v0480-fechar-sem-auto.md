---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-sem-auto
commit: a34b33bf1bd6a4e2e726846eb68fd0e397e5196f
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 (E171.8, PR #855, FECHAR-NUNCA-AUTO, revalidação por delta)

## Parecer
Aprovado. Esta é a revalidação por delta da volta E171.7. Li só a saída de `forge-check parecer delta` (intervalo f5143cea..c89d29eb). No domínio deste parecer, o delta toca só `bin/forge-testes` e `tests/mutantes/v0478-fechar-checks.json`, com 5 linhas de cada lado. O resto do intervalo são os pareceres de segurança e de QA, que ficam fora do meu domínio.

- A1 fechado. O `de` do FCK-M5 agora traz `falta_q="check obrigatório"` e casa só a linha 948 de `bin/forge-fechar`. O do FCK-M6 segue o texto novo da linha 961 (`o $falta_q $falta do head`). `test_forge_mutante.ConferirTodas` passou aqui. `bin/forge-mutante --ids FCK-M5,FCK-M6` deu "morreu" para os dois (948 e 961).
- A2 fechado. `test_fechar_sem_auto` entrou na tupla de `bin/forge-fechar` em `bin/forge-testes`, e `test_testes_tocados.MapaCobreOQueOsTestesLeem` passou aqui.
- A3 e A4 seguem recomendados e viram cartão depois do merge. A volta não mexeu em `bin/forge-fechar`, então o mérito aprovado no parecer anterior continua valendo.

Testes rodados aqui, com ambiente limpo: ConferirTodas, MapaCobreOQueOsTestesLeem, `tests.test_fechar_checks_do_head` e `tests.test_fechar_sem_auto`, 31 OK. No CI do PR em c89d29eb (a34b33bf mais o parecer do QA), as suítes 3.12 e 3.14, nas partes de 1/5 a 5/5, estão verdes, e também a catraca, a instalação e o teto de pulados. Só `bateria (pareceres)` e o agregado `bateria` estão vermelhos, como se espera antes de fechar os pareceres.
