---
tipo: revisao-seguranca
contrato: 1
pedido: t1-conf-escopo
branch: melhoria/t1-conf-escopo
commit: b9426d8b35215c985c91ced3d571e61504876346
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-29
---
# Review de segurança: t1-conf-escopo (lote 1, T1-CONF-ESCOPO-REV)

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-check entrega` (conferência de escopo) e `agents/conferente.md`. Escopo lido: diff `87e32b6...b9426d8` (8 arquivos); PA-7 conferido item a item (AR-1 a AR-9): sem recorrência nova além do A1 abaixo (classe: lista negativa em trava, AR-3).

## Achados
- A1 (bloqueante) bin/forge-check:1119 · a etapa merge-integracao marca `ok` qualquer arquivo, inclusive `docs/security/aceites/*` (do usuário) e `tests/config.json` (nunca anexo); a regra de `agents/conferente.md` diz que ambos são `escopo: fora`
- A2 (recomendado) bin/forge-check:1015 · no mergeCommit o pedido vem do `pedido:` do último review do diff, não do brief; um review aprovado de outro pedido satisfaz o portão
- A3 (recomendado) bin/forge-check:1036 · parecer da branch trazido por merge vira anexo `ok` sem checar `parecer:` nem o autor; o rótulo só prova o mesmo pedido e os mesmos bytes do segundo pai

## Detalhe dos achados
**A1.** Evidência: o ramo `elif revisados and not violacoes` (1119) vem depois do `ACEITES_DO_USUARIO` (1109), que só zera o `tipo` do aceite, e antes de qualquer exceção. Sonda local (repositório temporário do `tests/test_conf_escopo.py`, sem rede): branch com `docs/security/aceites/x.md`, `tests/config.json`, três pareceres aprovados e válidos no head, etapa merge-integracao, sem `--desde`, saiu rc=0 com `escopo: ok (merge-integracao: branch com os pareceres aprovados no head)` para os dois. Caminho de ataque: autor (ou agente de código) com a mão no aceite forja `aceite: sim` com `commit:` igual ao do seu parecer `riscos-aceitos`; o `forge-check pr` o aceita (lê o aceite da ref) e a conferência, que era a segunda camada além do hook, passa a copiar `ok` em vez de `escopo: fora`. O mesmo vale para `tests/config.json` (invariantes e termos proibidos): afrouxar item protegido passa sem o "Entregar" nomeá-lo. A regra escrita no `conferente.md` (linha 80) contradiz o código e o texto novo do mesmo parágrafo. Severidade: alta (enfraquece controle de aceite do usuário, `R-SEGURANCA`/`R-DECISAO`). Correção mínima: no laço de `cmd_entrega`, o ramo E1 só vale se `not nome.startswith(ACEITES_DO_USUARIO)` e `nome != "tests/config.json"`; os dois seguem `escopo: confira` (e o `conferente.md` já os manda como `fora`); teste novo nos dois caminhos (ref viva e mergeCommit) e mutante que remove a condição. Esforço: P. Dono: tech-lead (código) com o qa-engineer (teste e mutante).

**A2 (recomendado).** No caminho do mergeCommit (1013-1017) o pedido é o do último `docs/reviews/*` do diff, em ordem de nome, e o `forge-check pr` roda só sobre ele. Sem caminho realista direto: o PR passou antes pela catraca do CI com o slug verdadeiro e o `--branch <mergeCommit>` é escolhido pelo Jarvis; vira defeito se o conferente for a única barreira. Correção: exigir que o `pedido:` do review seja o slug da linha `Branch:` do brief (`pedido_do_pr` já o calcula) ou reprovar com mais de um review no diff.

**A3 (recomendado).** `anexo_implicito` (1036) herda a regra antiga (parecer de `docs/reviews|qa|security` por acréscimo é anexo), com os bytes do segundo pai como prova de "trazido por merge"; parecer editado depois do merge e remoção continuam `confira` (testado em `tests/test_conf_escopo.py`). Parecer forjado em branch lateral e mesclado sai `ok`; quem barra é o `forge-check pr` (autoria, `commit:`) e o hook, não este rótulo. Aceitável como é; o texto do `conferente.md` pode dizer que o rótulo não atesta o parecer.

Conferido sem achado: código de arquivo não nomeado fora de merge-integracao segue `confira` (teste `test_fragmento...`); fragmento de outra branch e remoção em anexo seguem `confira`; sem parecer ou com parecer reprovado a etapa reprova e mantém `confira`; refs são sempre sha e o `git` é chamado sem shell; sem entrada que vire opção do git.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura estática e a sonda acima (repositório temporário, local); `gitleaks`, `semgrep` e demais varreduras não rodadas neste parecer (o diff não toca segredo, dependência nem workflow); sem lacuna de instalação registrada.
