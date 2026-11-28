---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-brief-sonda-escrita
commit: 68d498057dfd8d376cc63ac4f326b99293656adb
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v0481, E45.61 (BRIEF-SONDA-ESCRITA, #952), delta da volta 1

## Escopo lido
Delta lido: `forge-check parecer delta docs/reviews/v0481-brief-sonda-escrita.md`, intervalo `61ab461e..68d49805`, domínio: `bin/forge-check`, `changelog.d/v0481-brief-sonda-escrita.md`, `tests/mutantes/v0433-integracao-4.json`, `tests/mutantes/v0481-brief-sonda-escrita.json`, `tests/mutantes/v0481-brief-sonda-escrita-2.json`, `tests/test_brief_sonda_escrita.py`. Fora dele (pareceres de QA e segurança) nada foi relido.

## Verificação
- ci: 68d498057dfd8d376cc63ac4f326b99293656adb verde
- run CI 46109255587 do `68d49805`: suíte 1/5 a 5/5, teto de pulados, instalação, passos, python 3.14, verificações longas e árvore já provada verdes; só `bateria (pareceres)`, `bateria` e `catraca` vermelhos, à espera dos pareceres.
- teste do item: `python3 -m unittest tests.test_brief_sonda_escrita`: 7 testes, OK.
- mutantes: `bin/forge-mutante --conferir --base 61ab461e`: trechos no lugar; `--cobertura --base 61ab461e`: toda condição nova coberta por mutante declarado; M8 e M11 rodados aqui: morreram (bin/forge-check:4856 e 4866).
- tamanho (H1): o delta tem cerca de 40 linhas novas e 16 trocadas em `bin/forge-check`; o item inteiro fica perto de 60 linhas de código, um comportamento só; dentro do teto.

## Parecer
Aprovado.

- A1 da segurança corrigido: `sondas_do_pedido` (bin/forge-check:4853) só aceita sonda de parecer com `pedido == pedido_id` e sem `problemas`, o mesmo filtro que a conferência da recomendação incluída já usava; o `lidas` da `conferir_volta` (bin/forge-check:4943) e a isenção da escrita usam essa mesma função, então os dois lados não divergem mais.
- A mudança maior se justifica: com só o `lidas` filtrado, a S1 reprovava pela linha `volta:`, mas a entrada continuava fora da barreira e o `escrita: barrada` sumia, ou seja, a isenção dependia de outra conferência reprovar na mesma execução. Agora a isenção é por linha: só sai da escrita a sonda cujo (tipo, id, entrada) foi relido da `--ref` (bin/forge-check:9082). Isso fecha a isenção por construção, e o teste da S1 afirma as duas linhas (`escrita: barrada` e `volta: ... não está nos pareceres lidos`).
- Nada afrouxou: a condição antiga (`--ref` e `^Volta-de:` frouxo) virou `VOLTA_DE` no formato estrito mais `sha_do_commit` válido mais leitura sem erro (bin/forge-check:4862-4866); qualquer falha devolve conjunto vazio e a entrada segue barrada (teste de `--ref` sem commit e de `--parecer` fora da ref). A `conferir_volta` segue rodando e reprovando como antes; `pareceres_da_ref` é extração sem mudança de lógica (o I62 só troca o argumento).
- Guardas do diff: cada linha de guarda nova tem mutante (M1 a M4 e M7 refeitos; M8 a M13 em `-2.json`, já que o primeiro arquivo tem 7) e teste do ramo de falha pelo fixture `BriefDeVolta`, sem ler a fonte.
- O fragmento do changelog cita a restrição nova.
