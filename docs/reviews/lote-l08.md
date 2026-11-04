---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-l08
commit: 318a4374a16a4662fcb1504565535f0caf92dcf4
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-04
---
# Review: versao-033, lote L08

Primeira rodada: lida a branch inteira, de 4f53bde a 874c89e, um commit por item.

## Achados
- A11 (recomendado) bin/forge-check:686 · A9: promocao lê origin/<integração> e, sem remoto, a branch local; com a ref forjada no clone (update-ref) ou sem remoto, uma branch de trabalho com --base homolog/main passa sem conferida. Use só a remota
- A12 (recomendado) docs/regras/R-PROVA.md:14 · A9: a regra diz que sem a linha o forge-check pr reprova; a exceção da promoção (base homolog/main, head na ponta da integração) está só no forge-check; cite-a na regra
- A6 (recomendado) bin/forge-check:835 · E10: se o gh mentir com um head antigo da branch, presente no clone e com pareceres válidos, o pr passa. Compare o patch do head sobre a base com o do squash (patch-id).
- A7 (recomendado) tests/test_forge.py:5710 · E10: o gh falso ignora os argumentos e aceitaria outro número ou outros campos. Faça o falso conferir `pr view 7 --json state,headRefOid,headRefName` (checklist 12).
- A8 (recomendado) bin/forge-check:5671 · E19: o brief gerar não tem a etapa ato-github, então o Jarvis escreve o brief à mão. Abra um cartão para o gerar.

## Parecer
Rodada 1 (874c89e): reprovado por dois bloqueantes, A1 (bin/forge-check:685, --ref sha sem branch, falha aberta) e A2 (agents/conferente.md:85, Desde da própria branch), com os recomendados A3 a A8. A1 a A5 foram resolvidos na volta 1 e saíram do bloco de achados. Rodada 2 (7925640): ver "Revalidação (volta 1)" no fim.

Por item:
- E10 CONF-MERGE-APOS-SQUASH (Q13 = A): aprovado. O pr confere no headRefOid, nunca no squash. Com o gh falhando, com JSON quebrado, PR aberto, head curto ou ausente do clone, nome com caractere de controle ou estado que não é texto, sai rc 2 e não confere nada. É falha fechada, e os testes cobrem cada caso. O gh que mente com um head válido só é pego pelo A6, que fica como recomendado.
- E12 CONFERIDA-DESDE-POR-BRANCH: a lógica está certa e não afrouxa nada (R-CONFORMIDADE). (a) Quando a base do dono é igual ao head, o Desde cai no Base-sha. O intervalo Base-sha..head é maior que o delta zero que a P-N6 barrava, então a conferência fica mais larga, não mais curta. (b) A conferida que já está no Base-sha fica antes da base, então Base-sha..head cobre todo o trabalho da branch ainda não conferido. Além disso, a conferida própria que vem antes de uma conferida de outra branch passou a recusar o Base-sha, o que aperta. Reprovado pelo A2: o texto do conferente reprovaria o Desde novo, e o cartão pede justamente que as conferências paralelas não se reprovem pelo Desde.
- E16 QA-TESTE-E-PARECER-SEPARADOS (Q10 = A), com o C-4 do E9: aprovado. A recusa continua a do commit_vale, o código só explica o motivo, e o texto do QA e da skill segue a Q10.
- E7 TEMPO-B2 (D07 = A): reprovado pelo A1. A amarração por head está certa: a conferida precisa ser ancestral do head, e a mesma regra do commit_vale vale com a base. Só que o forge-fechar passa o sha, e no Forge, chamado com o slug, ele não acha o pedido e pula a amarração. A edição da R-PROVA mantém os invariantes: o conferente não recebe o relatório do autor e a divergência continua contando como retrabalho. A3 e A4 são divergências do texto. O efeito no Jarvis está no jarvis.md:37, mas sem citar o forge-fechar (A5).
- E19 ATO-GITHUB-ENTREGA (Q8 = A): aprovado. O tipo vem do brief, nunca do executor, e o resultado nunca é "nada a conferir" com rc 0.

Teto (M14): dispensado pela DECISÃO DO DONO de 2026-11-03 10:06 ("B"). O corpo do PR traz a linha `teto: excedido`, aceita aqui.
Segurança: o gatilho são os controles do Forge, e o parecer é do security-engineer (docs/security/lote-l08.md). Não refiz essa análise.
Testes rodados, um módulo por vez, com `python3 -I -m unittest discover -s tests -p <arq>`: test_forge, test_mensagem_conferente, test_volta_por_delta, test_conferencia_base_dono, test_erros_no_brief, test_etapa_do_brief e test_isencoes, todos com rc=0.

## Revalidação (volta 1)
Revisado: 7925640, o head da volta. `forge-check delta --parecer docs/reviews/lote-l08.md 7925640` deu o intervalo 874c89e..7925640, com 16 arquivos. Li só esses trechos; o resto da branch, lido na rodada 1, fica como "já lido". Nesta branch de review, o commit do parecer da rodada 1 (ac80ff0) foi reaplicado sobre 7925640, sem mudar o texto, antes da revalidação. O commit 4b43e23 (testes do QA, depois de 7925640) fica fora deste review.

Veredito: **reprovado**, com um bloqueante novo (A9). A1 a A5 foram resolvidos. A6 a A8 seguem recomendados e não devolvem.

Pontos pedidos:
- (a) Alcance da falha fechada. No `brief gerar`, o alcance é aceitável. Na etapa `qa`, `pareceres_da_etapa` (bin/forge-check:5707) fica só com as linhas `docs/reviews`, então a linha da conferência não trava o brief do QA. Nas etapas `pr` e de merge, e no `entrega --etapa merge-integracao` (via `pareceres_da_integracao`, bin/forge-check:1370), cobrar a conferida é o que a R-PROVA já manda; a mudança só antecipa a recusa do merge.
  O alcance vai além do que a volta descreve. O `pr_da_cli` também atende ao `scripts/promover-homolog.py:150`, que roda `forge-check pr release-<versão> --ref origin/develop --base main`. Sem `docs/pedidos/release-<versão>.md`, a promoção para em "sem o pedido": é o A9, defeito provado. Com o pedido presente, a promoção para mesmo assim pelo A10, que está latente desde 87d34cf.
  Reprodução: `python3 -I -m unittest discover -s tests -p test_promover_homolog.py` dá rc 1 em 7925640 (20 falhas, todas com `pr: conferência: sem o pedido de "release-0.2.0"`) e rc 0 em 874c89e.
  Correção mínima sugerida: a conferência do head não vale na promoção (`--base main` com ref `develop`), ou o promover-homolog trata a linha `pr: conferência:` como as de `PARECERES_DA_LEVA`, com teste. A escolha é do autor com o arquiteto, sem afrouxar o `forge-fechar`.
- (b) `tests/apoio_conferida.py` e o RepoComOrigem não mascaram teste.
  - O `gravar_conferida` grava a linha do head que vai ser lido, num pedido do HOME do teste.
  - As classes que testam a conferência desligam a gravação e gravam a própria linha: `ConferenciaPresaAoHead.CONFERIR = False`, e `conferir=False` em `test_pr_sem_pareceres`, `test_md_comum_sem_review_reprova_pela_r_review` e `PrMescladoPeloHead`.
  - Tirar `docs/pedidos/p1.md` do commit base não muda nenhuma asserção. O arquivo nunca entrava no diff, e o `LerDirigidoDoBrief` agora o grava na cópia. As classes que leem o pedido (`PrAposMergeDaBase`, `EntregaAtoGithub`, `BaseShaDoBrief`) já o escreviam no HOME, e as asserções delas não mudaram.
- (c) O conflito com a develop em `skills/briefs-e-conferencia/SKILL.md:10` não é achado. As duas edições caem em trechos diferentes da mesma linha: a develop (TEMPO-B1, #441) mexe no formato da mensagem, e o E12 mexe no `Desde:`. O `git merge-tree 7925640 origin/develop` mostra conflito só nesse arquivo. A resolução que já está no L09 (3a09c5a) junta os dois lados; conferi os dois trechos no resultado. O conflito se resolve no merge (R-FLUXO), e o `forge-check pr` aponta se a resolução invalida os pareceres.

Volta 1, por commit:
- ac8921c (E7): resolve o A1 e o A4. A forma estrita `- <data> <hora>: entrega conferida <sha40>` aperta o portão, e a branch ambígua falha fechada.
- 1a4bc84 (E12): texto alinhado.
- b8d2aad (E19): o tipo da PQ em minúsculas está certo e testado.
- 7925640: a develop no mesmo sha não tira a branch de trabalho.

Testes e mutantes desta rodada, em 7925640, um módulo por vez (`python3 -I -m unittest discover -s tests -p <arq>`):
- test_fechar: rc=0, 91 testes
- test_isencoes: rc=0, 5
- test_volta_por_delta: rc=0, 67
- test_etapa_do_brief: rc=0, 65
- test_forge: rc=0, 509
- test_promover_homolog: rc=1, 20 falhas. Rodei por dúvida sobre o alcance do item (a).
- `bin/forge-mutante tests/mutantes/lote-l08-{e7,e7b,e10,e19}.json`: rc=0 nas quatro specs, todos os mutantes mortos.

## Teste do QA (4ed6e44)
O parecer passa a citar 4ed6e44. Esse commit só acrescenta `tests/test_qa_lote_l08.py` (256 linhas, 19 testes) sobre 7925640. Li o arquivo inteiro.
- O que cobre: E7 (ciclo conferida, código novo e nova conferida; commit do QA depois da conferida; ref por sha com e sem pedido ou Histórico; ref `origin/`; formas inválidas da linha), E10 (squash), E12 (`Desde` da própria branch), E16 (parecer que cita o commit anterior ao teste) e E19 (ato-github). Usa o `forge-check` e o `forge-fechar` reais. O `load_tests` evita rodar de novo os testes herdados.
- Não muda nada do que foi lido na revalidação. O A9 continua, porque o arquivo não exercita o `scripts/promover-homolog.py`.
- Sobre os testes do QA, sem achado novo: `test_dois_briefs_reprova` e `test_pq_de_commit_junto_de_pq_do_github_reprova` afirmam só o rc, não a linha. O gh falso do `QaE10PrMesclado` ignora os argumentos, a mesma classe do A7.
- Rodada: `python3 -I -m unittest discover -s tests -p test_qa_lote_l08.py` deu rc=0 (19 testes, OK).
- Pela regra do próprio E7, o commit do teste fica depois da `entrega conferida` de 7925640. Por isso o `forge-check pr` cobra uma conferida que cubra 4ed6e44 (`test_commit_de_teste_do_qa_depois_da_conferida_exige_nova_conferencia`).

## Revalidação (volta 2: A9 e A10)
Revisado: a46eab7 (a correção), mais o teste do QA 318a437. O parecer cita 318a437, que é o teste mais recente (E16). Delta lido: 63c49f2..a46eab7 (`bin/forge-check` +14, `tests/test_forge.py` +19, `tests/mutantes/lote-l08-e7b.json` +30) e 318a437 (`tests/test_qa_lote_l08.py` +33). O resto fica como "já lido". Os commits de segurança 2a47613 e 3839cf9 são pareceres e ficam fora.

Veredito: **aprovado**. O A9 está resolvido: `promocao()` dispensa a conferência só com base `homolog` ou `main` e head igual, commit a commit, à ponta de `origin/develop` (ou `origin/homolog` para a main), e avisa no stderr. O A10 está resolvido junto, porque a promoção não cobra mais a conferida. A6, A7 e A8 seguem recomendados; A11 e A12 são novos e também recomendados.

Sonda de bypass (unittest descartável sobre o `RepoComOrigem`, branch de trabalho com pareceres e sem conferida):
- `origin/develop` forjada no head de trabalho com `update-ref`: `--base homolog` e `--base main` dão rc 0, com o aviso de promoção. `--base develop` segue rc 1 (conferência).
- Sem remoto, com a `develop` local no head: `--base homolog` e `--base main` dão rc 0. Isso vem do fallback local de `ref_da_base`.
- `develop` local à frente da remota: rc 1 com `--base homolog` e `--base main`, e também com `--ref develop`. Não é bypass.

Os dois primeiros casos não abrem caminho para mesclar uma entrega sem conferida. O `forge-fechar` só aceita `origin/develop` (bin/forge-fechar:77), e com `--base develop` a conferência continua cobrada. Além disso, forjar ref exige escrever no `.git` do próprio clone, o mesmo nível de confiança das outras leituras de `origin/<base>`. Por isso o A11 fica como recomendado: na promoção, ler só a remota.

O A12 é texto: a exceção da promoção está no `forge-check`, mas não na R-PROVA.

Mutante rc=2 da rodada anterior: o `forge-mutante` saiu com "a árvore de trabalho mudou durante a rodada; resultado descartado". A segurança e o QA fizeram commits na mesma worktree (2a47613 e 318a437) enquanto ele rodava, e ele descarta o resultado quando a árvore no fim difere da do início. Não foi defeito da spec: numa worktree isolada em a46eab7, e de novo agora em 3839cf9 com a árvore parada, deu rc=0.

Testes e mutantes desta volta:
- `python3 -I -m unittest discover -s tests -p test_promover_homolog.py`: rc=0 (36).
- `python3 -I -m unittest discover -s tests -p test_forge.py -k ConferenciaPresaAoHead`: rc=0 (9).
- `python3 -I -m unittest discover -s tests -p test_qa_lote_l08.py`: rc=0 (21).
- `bin/forge-mutante tests/mutantes/lote-l08-e7b.json`: rc=0 em 3839cf9, com M36, M37, M50, M51 e M52 mortos.
