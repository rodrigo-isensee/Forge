---
tipo: review
contrato: 1
pedido: t1-conf-escopo
branch: melhoria/t1-conf-escopo
commit: b9426d8b35215c985c91ced3d571e61504876346
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-29
---
# Review: t1-conf-escopo (lote 1, T1-CONF-ESCOPO-REV)

Escopo lido: diff `87e32b6...b9426d8` (8 arquivos), com o pedido T1-CONF-ESCOPO e a DECISÃO TÉCNICA de 2026-10-29 12:06 (lote 1: E1, E2 parcial, E3, E4). Primeira rodada: sem parecer anterior, sem delta. Ficam para o T1-CONF-ESCOPO-2, fora deste review: a linha AR como anexo implícito e o `brief gerar --volta`.

## Achados
- A1 (bloqueante) bin/forge-check:1119 · requisito: na merge-integracao o ramo novo marca `ok` também `tests/config.json` e `docs/security/aceites/`, que o conferente.md:80 manda como `escopo: fora`; o novo texto (conferente.md:81) contradiz a linha anterior; faltam teste e mutante dos dois caminhos
- A2 (recomendado) bin/forge-check:1013 · o laço roda `git show` em todo arquivo do squash e fica com o pedido do último `docs/reviews/*` por nome; filtre por `docs/reviews/` antes do `show` e recuse mais de um review (mesmo ponto do A2 da segurança)
- A3 (recomendado) agents/conferente.md:80 · o texto e o comentário em bin/forge-check:1119 falam em review, QA e segurança aprovados, mas o `pr` exige QA só sem isenção e segurança só com gatilho; diga "os pareceres que o `forge-check pr` exige"
- A4 (recomendado) tests/test_conf_escopo.py:61 · uma linha em branco antes de `class AnexosImplicitos` e duas dentro da classe (linha 88): espaçamento do PEP 8 fora do resto da suíte

## Parecer
Reprovado por um bloqueante (A1, requisito).

**A1.** O ramo `elif revisados and not violacoes` (bin/forge-check:1119) vem antes de qualquer exceção, e o `ACEITES_DO_USUARIO` (1109) só zera o `tipo`. Com os pareceres exigidos aprovados no head, `tests/config.json` e `docs/security/aceites/*` saem `escopo: ok (merge-integracao: ...)`. A regra escrita é outra: o conferente.md:80 diz que `tests/config.json` nunca é anexo e que o aceite na entrega é `escopo: fora`. O pedido também exclui o arquivo que o "Entregar" não nomeia e que não é anexo implícito ("afrouxaria R-PROVA e iria ao dono"). O E1 confirmado amplia o escopo à branch, mas não revoga essas duas exceções, que protegem invariantes da fábrica e o aceite do usuário (`R-SEGURANCA`). O defeito é o mesmo do A1 do parecer de segurança (`docs/security/t1-conf-escopo.md`), provado lá por sonda com os três pareceres válidos; não o refaço, e a correção é uma só. Sugestão: o ramo E1 só vale com `not nome.startswith(ACEITES_DO_USUARIO) and nome != "tests/config.json"`; esses dois seguem `escopo: confira`. Faltam também o teste com ref viva e com mergeCommit e o mutante que tira a condição. Ajuste a frase do conferente.md:81 ("Arquivo de código que o Entregar não nomeia segue fora") para citar as duas exceções. Severidade: bloqueia.

**A2.** Sonda local (repositório temporário do `tests/test_conf_escopo.py`, script em `$TMPDIR/tech-lead-t1-conf-escopo/sonda_rev.py`): um squash que traz `docs/reviews/x.md` (pedido x, reprovado) e `docs/reviews/z.md` (pedido z, aprovado) roda o `pr` sobre o pedido `z` (saída: `qa: sem parecer para o pedido \`z\``). Não há caminho realista hoje: o squash vem de um PR que passou pela catraca do CI com o slug. Por isso fica como recomendação, como na segurança. Severidade: recomendado.

**A3.** O código está certo (`cmd_pr` decide o que é exigido); só o texto promete três pareceres. Severidade: recomendado.

**A4.** Formatação. Severidade: recomendado.

Conferido sem achado:
- E1, ref viva: sem parecer ou com parecer reprovado, a etapa reprova e o arquivo segue `confira`, com teste.
- E1, `--desde`: com ele, o delta segue lido como sempre (mutante M17 em `t1-conf-escopo-2.json`).
- E1, ref apagada: o head com um pai, contido na base, vira `de = pai` e o escopo passa a ser o que o squash traz; o `pr` roda com `base = pai`, com teste do caso aprovado e do caso sem parecer.
- E1, PQ `cmd` da ref apagada lido do mergeCommit: é instrução ao conferente (conferente.md:81), que é quem roda os PQ; cabe no E3.
- E2 parcial: o fragmento entra só com o nome exato `changelog.d/<slug>.md` (o de outra branch segue `confira`). O parecer conta como trazido por merge só com o primeiro pai sem o arquivo, o segundo pai com os mesmos bytes do head e o `pedido:` igual ao slug. A remoção segue `confira`. Tudo com teste.
- O A3 da segurança (o rótulo não atesta o parecer) fica com ela.
- Funções pequenas e nomeadas pelo que fazem: `pedido_do_parecer` foi extraída num lugar só.
- Commits: um por item, em Conventional Commits em português.
- `bin/forge-testes` e `tests/test_testes_tocados.py` mudam por consequência do módulo novo, como diz a DECISÃO TÉCNICA.

Teto (M14): `git diff --numstat --no-renames 87e32b6...b9426d8` dá `bin/` 51 linhas e `tests/*.py` 98, total 149. Ficam fora o `.md`, o fragmento e `tests/mutantes/`. Está abaixo de 400 e do teto de 150 do brief.

PA-7 (`docs/engineering/achados-recorrentes.md`), item a item:
- AR-1: lista de mutantes. Cabe ao QA; o ramo do A1 não tem mutante, o que está dito no A1.
- AR-2 a AR-9: sem ocorrência no diff. Não há trava de ambiente, `python` sem `-I`, máscara de shell, `cd` nem limite antigo no texto.
- Linha AR nova: nenhuma. A classe do A1 não se repetiu neste pedido no review.

Ferramentas: o Forge não tem `docs/engineering/praticas.md`. As regras de ferramenta são a suíte, o shellcheck e a validação do plugin, que rodam no pre-push e no CI do PR; não as rodo aqui (decisão do dono de 2026-10-24, corte 1). O resultado dos testes do item fica com o QA (`docs/qa/t1-conf-escopo.md`). A segurança está em `docs/security/t1-conf-escopo.md` (reprovado, A1) e é citada aqui sem refazer.
