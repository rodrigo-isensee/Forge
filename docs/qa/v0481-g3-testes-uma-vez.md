---
tipo: qa
contrato: 1
pedido: v0481
branch: melhoria/v0481-g3-testes-uma-vez
commit: ef45eec579f148d70ee8b885b183087351817fbc
parecer: reprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-25
---
# QA: v0481 (G3 primeira fatia: review e QA leem o CI do head, #893, E8.3)

Classe C. Diff lido contra a base `220ba3fa27fe`: `bin/forge-check` (cerca de 45 linhas), duas skills, os testes `test_forge_check_pr`, `test_pre_envio_brief`, `test_fechar_forge_check_real`, três specs antigas realinhadas e duas novas (M1 a M14). O código faz o que o autor descreve e só aperta; o que reprova é a regra nova não poder ser cumprida com honestidade no sha que ela manda ler (A1).

## Achados
- A1 (bloqueante) bin/forge-check:2167 · A linha `- ci: <Revisar-sha> verde` exige todos os checks verdes no sha revisado, mas `bateria (pareceres)` (ci.yml:739) e o agregador `bateria` ficam vermelhos nesse sha até existir o parecer, que só nasce num commit novo. Lida à risca, a linha nunca é verdadeira.

## Critério → teste → resultado
| Critério (do brief) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| (1) Nada que barra hoje deixa de barrar | leitura de `suite_do_parecer`: `sem_ci` só soma à lista; o ramo `falta is None` devolvia `[]` e agora devolve `sem_ci`; fora do Forge e a catraca (`suite=None`) seguem `[]` | parecer sem a linha, com e sem prova `- suíte:`, com e sem `adiar` | passou: só aperta; `test_sem_a_linha_recusa_com_ci_verde_ou_com_a_prova`, `..._tambem_no_adiar`, `test_a_linha_nao_dispensa_o_ci_verde_do_head` |
| (1) A linha escrita sem CI verde solta algo? | `test_linha_de_outro_sha_ou_vermelha_recusa`, `test_a_linha_nao_dispensa_o_ci_verde_do_head` | outro sha, `vermelho`, texto depois de `verde`, `commit:` vazio ou fora da forma | passou; a linha é conjunta com o ramo antigo: sem a prova `- suíte:`, o `ci_verde_no_head` ainda lê o gh (fora do `adiar`); com a prova, passava só com ela antes e agora precisa também da linha. Nada solto, mas a linha é autodeclarada: sob `adiar` (previo e passo 1 do fechar) só o texto a sustenta, e os passos 4 e 6 do fechar seguem exigindo o CI |
| (2) Branches em andamento com parecer aprovado sem a linha | leitura: `leu_o_ci` vale para qualquer parecer de review ou QA aprovado, sem corte por data; os PRs de `develop` abertos (#874 a #892, 11 hoje) | parecer aprovado antes da regra | efeito real: cada um precisa regravar o parecer (um commit e um CI novos) assim que a regra chega à develop; não achado (o autor declara que aperta), mas o Jarvis deve contar com a rodada extra |
| (3) Mutantes antigos realinhados mantêm a guarda | diff das specs: só os trechos `de`/`para` mudaram para a forma nova do código; mesma condição trocada por `False`/`True`, mesmo `testes` | mp1311 M6 e M7, v0479 M13, M16, M17 | passou: continuam `morreu` |
| Esqueleto do parecer novo traz a linha | `test_pre_envio_brief` (esqueleto de review e QA; segurança sem a linha) | segurança e autor sem a linha | passou |
| Brief de review e QA manda ler o CI; sem PR não aprova | `LeOCiNoBrief` | sem PR, `gh` ausente, etapa de segurança | passou |

## Cenários e resultado real
- Módulos tocados: `test_forge_check_pr` (58), `test_pre_envio_brief` (24), `test_fechar_forge_check_real` (5), todos `OK`.
- Mutantes (uma chamada por pedido, `--processos 3`, `rev=ef45eec579f1`): `v0481-g3-testes-uma-vez` + `-2`: M1 a M14 todos `morreu`; `mp1311-pre-envio-fabrica`: M1 a M7 e M10 `morreu`; `v0479-forge-check-ci-verde` `-2` e `-3`: M9 a M21 `morreu`. Nenhum sobrevivente, nenhum equivalente. Linhas de guarda mudadas no diff (`leu_o_ci`, `sem_ci`, `return sem_ci`, `PORTOES_QUE_LEEM_O_CI`, `SEM_PR_NO_PORTAO`, `saida +=`) todas com mutante.
- Vermelho: `bin/forge-testes --vermelho 220ba3fa27fe68bf9f7d52c703fffaeaaf8de41d --modulos test_forge_check_pr,test_pre_envio_brief,test_fechar_forge_check_real` → rc 0; `vermelho: 3 módulos em duas cópias`; `contagem: não prova (passa na base)=77; prova (API ausente)=5; prova (asserção)=5`.
- CI do head `ef45eec5` (PR #893, run 45572219351), lido por `gh pr checks`: `bateria (pareceres)` `fail`, `catraca` `fail` (o log não pôde ser baixado do sandbox), as 10 partes da suíte `pending`, `bateria (passos)`, `bateria (verificações longas)`, `instalação` e `árvore já provada` `pass`. O CI não está verde nesse sha; por isso este parecer não traz a linha de CI e reprova. Primeiro parecer que a regra cobra: ele mostra o circular de A1 (o `bateria (pareceres)` só fica verde depois deste commit).

## Notas sem bloqueio
- `agents/qa-engineer.md:15` e `agents/tech-lead.md:16` ainda dizem "cite o CI verde ou o PQ do autor"; a regra nova não admite o PQ do autor: texto desalinhado (recomendado, vira cartão).
- O `forge-copia clone --revisao` do brief não existe na 0.47.15 do plugin instalado; usei `clone <caminho> --origem <url> --branch` e `git reset --hard FETCH_HEAD` (o clone nasce na base).
- O head do PR já andou para `109f24f4` durante a leitura (commit de outro portão); o `commit:` deste parecer segue o Revisar-sha do brief.
