---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-brief-sonda-escrita
commit: 61ab461ec3cbc099baf4c24aa7dc7e7803427dbf
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-28
---
# Review: v0481, E45.58 (BRIEF-SONDA-ESCRITA, #952), 1.ª rodada completa

## Escopo lido
Diff `b414714c..61ab461e`: `bin/forge-check` (28 linhas), `bin/forge-testes` (1), `tests/test_brief_sonda_escrita.py`, `tests/mutantes/v0481-brief-sonda-escrita.json`, `tests/mutantes/v0433-integracao-4.json` (I62), `changelog.d/v0481-brief-sonda-escrita.md`.

## Verificação
- ci: 61ab461ec3cbc099baf4c24aa7dc7e7803427dbf verde (`gh pr checks 952`: suíte 1/5 a 5/5, instalação, passos, verificações longas, teto de pulados e árvore já provada verdes; só `bateria (pareceres)`, `bateria` e `catraca` vermelhos, à espera dos pareceres e do rótulo)
- teste novo: `python3 -m unittest tests.test_brief_sonda_escrita`: 4 testes, OK.
- mutantes: `bin/forge-mutante --conferir --base b414714c`: trechos no lugar; M5 e M7 rodados aqui: morreram (o autor registrou M1 a M7 mortos).
- tamanho (H1): cerca de 21 linhas de código em `bin/forge-check` e 1 em `bin/forge-testes`, um comportamento só; dentro do teto.

## Parecer
Aprovado.

- Barreira de escrita: `sem_entrada_de_sonda` (bin/forge-check:9055) tira só o grupo 4 de `SONDA_NO_ENTREGAR` (a entrada entre `grave no corpus da branch:` e ` · espera: `); a marca e o resto da linha seguem em `caminhos_do_entregar`, e toda linha fora do formato fica intacta. A exceção só liga com `--ref` e `Volta-de:` (bin/forge-check:9141), a mesma condição em que `avaliar_brief` chama `conferir_volta` (bin/forge-check:9436). O teste da linha comum com `.git/hooks/reference-transaction` prova que a barreira segue para as outras linhas, e o de sem `--ref`/sem `Volta-de:` prova que nada muda fora da volta conferida.
- Falha fechada: em `conferir_volta`, todo retorno antes do novo laço (Volta-de fora do formato, anterior ilegível ou diferente, `--ref` que não é commit, erro dos pareceres) reprova; o laço novo (bin/forge-check:4921-4924) exige par igual em (tipo, id, entrada) para cada sonda do Entregar, o que fecha o furo da segunda S3 com outra entrada (a conferência por pertença da linha 4917 aceitava). Assim, entrada tirada da escrita sempre é uma entrada lida do parecer da ref.
- Guardas do diff: cada linha de guarda tem o seu mutante (M1 a M7) e teste de comportamento do ramo de falha; os testes chamam o `forge-check` pelo fixture de `test_volta_por_delta`, sem ler o texto da fonte.
- Fora da lista do brief: o `bin/forge-testes` (mapa `FORGE_CHECK`, cobrado por `test_testes_tocados`) e o `de`/`para` do I62 (cobrado por `test_forge_mutante.ConferirTodas`, AR-12) são consequência mecânica da mudança; sem eles a suíte fica vermelha. O I62 continua negando o mesmo ramo, só com o argumento novo.
- O PR traz o critério de reversão e o fragmento do changelog; nenhuma regra protegida é afrouxada.
