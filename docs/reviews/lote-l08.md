---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-l08
commit: 874c89ec82a86840262c5c4a5b93eba48554eb5c
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033, lote L08

Primeira rodada: lida a branch inteira, de 4f53bde a 874c89e, um commit por item.

## Achados
- A1 (bloqueante) bin/forge-check:685 · E7: com --ref sha (como o forge-fechar chama) a ref fica sem branch, os briefs não são lidos e o pr aprova sem conferida. Sonda: rc 0 com o sha, rc 1 com a branch. Falha aberta no merge (D07). Ache a branch do sha ou exija o pedido.
- A2 (bloqueante) agents/conferente.md:85 · E12: o texto ainda exige que o Desde seja a última conferida do pedido e só aceita o Base-sha depois de squash. O Desde novo, da própria branch, sai como "diverge do Histórico". Alinhe aqui e em skills/briefs-e-conferencia/SKILL.md:10.
- A3 (recomendado) docs/regras/R-PROVA.md:14 · E7: a regra diz que depois da conferida só mudam pareceres e quadro, mas o código também libera changelog.d/<pedido>.md (bin/forge-check:722). Alinhe o texto ou o código.
- A4 (recomendado) bin/forge-check:720 · E7: o pedido sem ## Histórico só gera aviso, mas a R-PROVA diz que nada vai ao merge sem a linha. Escreva a exceção na regra ou recuse.
- A5 (recomendado) agents/jarvis.md:37 · E7: o texto diz que o forge-check pr cobra a linha, mas não diz que o forge-fechar para no passo 1 sem ela nem que a linha precisa estar gravada antes do fechamento. Cite isso também em docs/fechamento-integrador.md:14.
- A6 (recomendado) bin/forge-check:835 · E10: se o gh mentir com um head antigo da branch, presente no clone e com pareceres válidos, o pr passa. Compare o patch do head sobre a base com o do squash (patch-id).
- A7 (recomendado) tests/test_forge.py:5710 · E10: o gh falso ignora os argumentos e aceitaria outro número ou outros campos. Faça o falso conferir `pr view 7 --json state,headRefOid,headRefName` (checklist 12).
- A8 (recomendado) bin/forge-check:5671 · E19: o brief gerar não tem a etapa ato-github, então o Jarvis escreve o brief à mão. Abra um cartão para o gerar.

## Parecer
Reprovado: há dois bloqueantes.

Por item:
- E10 CONF-MERGE-APOS-SQUASH (Q13 = A): aprovado. O pr confere no headRefOid, nunca no squash. Com o gh falhando, com JSON quebrado, PR aberto, head curto ou ausente do clone, nome com caractere de controle ou estado que não é texto, sai rc 2 e não confere nada. É falha fechada, e os testes cobrem cada caso. O gh que mente com um head válido só é pego pelo A6, que fica como recomendado.
- E12 CONFERIDA-DESDE-POR-BRANCH: a lógica está certa e não afrouxa nada (R-CONFORMIDADE). (a) Quando a base do dono é igual ao head, o Desde cai no Base-sha. O intervalo Base-sha..head é maior que o delta zero que a P-N6 barrava, então a conferência fica mais larga, não mais curta. (b) A conferida que já está no Base-sha fica antes da base, então Base-sha..head cobre todo o trabalho da branch ainda não conferido. Além disso, a conferida própria que vem antes de uma conferida de outra branch passou a recusar o Base-sha, o que aperta. Reprovado pelo A2: o texto do conferente reprovaria o Desde novo, e o cartão pede justamente que as conferências paralelas não se reprovem pelo Desde.
- E16 QA-TESTE-E-PARECER-SEPARADOS (Q10 = A), com o C-4 do E9: aprovado. A recusa continua a do commit_vale, o código só explica o motivo, e o texto do QA e da skill segue a Q10.
- E7 TEMPO-B2 (D07 = A): reprovado pelo A1. A amarração por head está certa: a conferida precisa ser ancestral do head, e a mesma regra do commit_vale vale com a base. Só que o forge-fechar passa o sha, e no Forge, chamado com o slug, ele não acha o pedido e pula a amarração. A edição da R-PROVA mantém os invariantes: o conferente não recebe o relatório do autor e a divergência continua contando como retrabalho. A3 e A4 são divergências do texto. O efeito no Jarvis está no jarvis.md:37, mas sem citar o forge-fechar (A5).
- E19 ATO-GITHUB-ENTREGA (Q8 = A): aprovado. O tipo vem do brief, nunca do executor, e o resultado nunca é "nada a conferir" com rc 0.

Teto (M14): dispensado pela DECISÃO DO DONO de 2026-11-03 10:06 ("B"). O corpo do PR traz a linha `teto: excedido`, aceita aqui.
Segurança: o gatilho são os controles do Forge, e o parecer é do security-engineer (docs/security/lote-l08.md). Não refiz essa análise.
Testes rodados, um módulo por vez, com `python3 -I -m unittest discover -s tests -p <arq>`: test_forge, test_mensagem_conferente, test_volta_por_delta, test_conferencia_base_dono, test_erros_no_brief, test_etapa_do_brief e test_isencoes, todos com rc=0.
