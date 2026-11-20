---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-pp1-aplicado-dono
commit: 58da41ec48c1d6fc8f05e9b41788d44a7ec6d4d0
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-20
---
# Review de segurança: v0479-pp1-aplicado-dono (v0478 E52.3, revalidação)

Volta por delta sobre o parecer reprovado em `4aadad19` (a rodada anterior fica no git). Delta lido (`forge-check parecer delta`, `4aadad19..58da41ec`): no domínio, só `bin/forge-check` (`isencao_do_dono`, `emails_do_dono`, `patch_revisado_do_dono`, `parecer_cita_o_patch` e o texto de ajuda). Fora do domínio, lidos para as sondas: `tests/test_conf_escopo.py` (classe `PatchRevisadoDoDono`) e o fragmento do changelog. Já lido e sem mudança: o resto de `0f6034ea..4aadad19`. Decisão do dono de 20/11 12:33 (pedido v0478:753): limite do e-mail aceito, opção (a). Suíte: não rodada (brief). Rodadas: a classe `PatchRevisadoDoDono` (sem falha) e as sondas S1 a S4.

Gatilhos: guarda da conferência de entrega, arquivo em vigor (.githooks/, .claude/, .forge/config.json, .forge/versao), identidade do autor do commit.

## Achados anteriores
- A1 (bloqueante): **resolvido.** `bin/forge-check:2272-2277` exige que cada caminho do commit do dono seja igual no pai, no Base-sha e na develop atual. A develop que não se resolve e o git que falha recusam. S1 refeita: recusada.
- A2 (recomendado): **resolvido.** `bin/forge-check:2234-2246` lê a lista da árvore do Base-sha. Se a lista está versionada só na branch, nada isenta. Se ela falta no Base-sha e na branch (caso do Forge), vale o disco da raiz. O limite (o e-mail é declarável e não prova autoria) está no comentário (`bin/forge-check:2215-2216`), na ajuda e no changelog, como decidiu o dono em 20/11. S2 refeita: recusada.
- A3 (recomendado): **resolvido em parte.** `bin/forge-check:2289-2301` exige um parecer de segurança aprovado no head que cite o sha256 do `.patch` como palavra. O acoplamento é bom, mas largo demais: ver A4.

## Tamanho do afrouxamento que sobra
Contra a base `0f6034ea`, o afrouxamento no código continua zero: a base já isentava o arquivo em vigor só com a `DECISÃO DO DONO`, e esta branch só aperta. Contra uma política sem exceção para arquivo em vigor, sobra isto, e só isto. Sai do escopo um arquivo em vigor quando todas estas condições valem:
- o conteúdo é exatamente o de um `.patch` versionado na branch, aplicado sobre caminhos intocados desde o Base-sha e iguais na develop atual;
- o commit não é merge e a `DECISÃO DO DONO` o cita pelo sha40;
- autor e committer declaram um e-mail da lista do Base-sha;
- algum arquivo de `docs/security/` do head, com frontmatter `tipo: revisao-seguranca` e `parecer:` aprovado ou riscos-aceitos, cita o sha256 do `.patch`.

Ficam dois furos medidos:
1. O e-mail não prova autoria. O dono aceitou esse limite. Com (a), forjar o e-mail só produz os bytes revisados, e quem decide é a DECISÃO com o sha40, que só o Jarvis grava.
2. A citação do sha256 não precisa vir do parecer desta branch nem de um parecer válido (A4, S3 e S4).

Nenhum dos dois deixa passar byte que não esteja no `.patch` da branch.

## Acoplamento ao sha256 do `.patch`
A ideia é boa: amarra os bytes aplicados ao que a segurança leu, sem custo e sem rede, e um `.patch` trocado depois do parecer deixa de isentar. O defeito é a largura. Vale qualquer parecer aprovado no head, de qualquer branch ou pedido, inclusive o que chega da develop por merge. Vale também qualquer arquivo sob `docs/security/` (até em `aceites/`) com o frontmatter mínimo, e `riscos-aceitos` vale sem o aceite do usuário.

Por isso este parecer **não** cita como palavra o sha256 do caso real (`docs/devops/v0479-sandbox-controle.patch`, sha256 que começa por `28d1a534`, conferido no `origin/melhoria/v0479-sandbox-controle`). Este review leu o `forge-check`, não aquele patch. Depois do merge na develop, essa citação isentaria o patch na outra branch sem que ninguém o tivesse lido (é a sonda S3). A citação cabe no parecer de segurança da branch `melhoria/v0479-sandbox-controle`, depois de ler o patch.

## Achados
- A4 (recomendado) bin/forge-check:2297 · (c) aceita qualquer arquivo de docs/security/ no head com frontmatter aprovado: parecer de outra branch ou pedido (S3), arquivo em aceites/ (S4), riscos-aceitos sem aceite. Exigir `branch:` igual à conferida, fora de aceites/ e ameacas/, e o veredito do parecer válido.

### Detalhe
**A4.** Caminho de ataque: um parecer aprovado de outra entrega cita o sha256 como exemplo ou referência e chega ao head pela develop. Assim, um `.patch` que nenhum revisor de segurança leu passa pela condição (c). Sem adversário, é erro honesto. Com adversário, ainda são precisas a DECISÃO com o sha40 e a escrita de um arquivo em `docs/security/` (escrita do papel, conferida no escopo). Severidade baixa, esforço P.

Correção mínima em `parecer_cita_o_patch`:
- descartar o que estiver sob `docs/security/aceites/` e `docs/security/ameacas/`;
- exigir `campos["branch"]` igual à branch conferida;
- para `riscos-aceitos`, exigir `aceite_do_usuario` (ou aceitar só `aprovado`).

Teste: S3 e S4 recusados. Dono: tech-lead.

## Sondas
- S1 · commit de outro autor cria .githooks/pre-push com `echo NAO-REVISADO`; o .patch revisado só acrescenta `# revisado`; o dono o aplica · espera: não isenta · obtido: não isenta ("difere entre o pai do commit do dono, o Base-sha e a develop atual")
- S2 · `.mailmap` `Dono <dono@exemplo> <agente@x>` e commit com autor e committer agente@x · espera: não isenta · obtido: não isenta ("autor ou committer não é o dono")
- S3 · parecer aprovado com `pedido: outro`, `branch: melhoria/outra` e `commit:` zerado, que só cita o sha256 do .patch · espera: não isenta · obtido: `escopo: ok (patch do dono 1f6b2bd…)` (A4)
- S4 · só `docs/security/aceites/y.md` com `tipo: revisao-seguranca`, `parecer: riscos-aceitos` e o sha256 · espera: não isenta · obtido: `escopo: ok (patch do dono e171bc8…)` (A4)

## Plano em cartões
- A4: tech-lead, em `bin/forge-check` e `tests/test_conf_escopo.py`; volta por delta a este parecer.
- Commit assinado no lugar do e-mail: cartão aberto pela decisão do dono de 20/11.

## Riscos aceitos
Nenhum neste parecer. O limite do e-mail é decisão do dono de 20/11 12:33 (pedido v0478:753), não risco aceito por este review.
