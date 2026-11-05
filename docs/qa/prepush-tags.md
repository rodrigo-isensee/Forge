---
tipo: qa
contrato: 1
pedido: prepush-leve
branch: melhoria/prepush-tags
commit: f835f66f87b32e523aa2f5e9c391f23f8004116e
parecer: aprovado
escopo: completo
bugs_criticos: 0
bugs_altos: 0
bugs_medios: 0
bugs_baixos: 0
data: 2026-11-05
---
# QA: prepush-tags (PR-a do pedido prepush-leve)

Parecer sobre o código f835f66 (base do delta fixada pelo dono em 24e055c). A suíte rodou na árvore em 6c14cf6, que só soma pareceres de docs sobre f835f66. Sem push real ao GitHub.

## Achados

## Critério → teste → resultado
| Critério (Escopo E2, tag) | Teste | Fronteira protegida | Resultado |
|---|---|---|---|
| Só tags de commit já em `refs/remotes/<remoto>/*`: sem teste, sem fila | sonda 1 e `test_tags_de_commit_ja_no_remoto_saem_sem_teste_e_sem_fila` | tag anotada e leve, duas refs | passou |
| Falha fechada: tag de commit fora do remoto | sonda 2 e 8, `test_falha_fechada_entra_na_fila` | commit novo; commit só em outro remoto | passou |
| Falha fechada: mais de uma ref (tag mais branch) | sonda 3 | refs mistas | passou |
| Falha fechada: ref que não é branch nem tag | sondas 4 e 5 (`refs/notes`, `refs/pull`, sozinha e junto de tag) | ref de outro tipo | passou |
| Remoto por URL segue o caminho de sempre | sonda 6 | nome de remoto não simples | passou |
| Recusa de develop, homolog, main e tag movida vale antes | sonda 7, `test_tag_nao_abre_develop_homolog_main_nem_tag_movida` | destino protegido | passou |

## Cenários e resultado real
Repositório descartável `/tmp/qa-prepush-tags-MLR7` (sonda em `.githooks/pre-push` real, refs por stdin, trava da suíte presa por fora, `FORGE_TRAVA_ESPERA=2`; quem entra na fila é barrado em 2 s, e o arquivo `rodou-*` mostra se algum teste rodou):
- Sonda 1, duas tags de commit já no remoto: rc=0, nenhum teste rodou, "só leva tags ... a bateria não roda (PREPUSH-TAGS)", sem "esperando a vez".
- Sondas 2, 3, 4, 5, 6 e 8: rc=1, "a vez não chegou em 2 s", nenhum teste rodou (entraram na fila e foram barradas pela trava).
- Sonda 7 (tag mais push para develop): rc=1, "envio direto para develop bloqueado".

Vermelho antes do verde: `forge-testes --vermelho b45e40aff486 --modulos test_pre_push_tags`, rc=0, 3 testes "prova (API ausente)" (a base também não tem o apoio). Prova mais forte, cópia em `/tmp` com só `.githooks/pre-push` da base: `test_tags_de_commit_ja_no_remoto_saem_sem_teste_e_sem_fila` cai (FAIL), os outros dois passam, como esperado de regressão de falha fechada.

`tests/test_pre_push_tags.py` no HEAD: 3 testes, OK (8,5 s).

Suíte inteira (`.githooks/pre-push --suite`, esperou a trava do outro QA; log `/tmp/qa-prepush-tags-suite.log`): 2563 testes em 91 módulos, 4 processos, 1061 s, OK (skipped=30), rc=0. Nenhuma falha, logo nenhuma falha de ambiente do pid namespace a listar nem a provar na origin/develop. Skips não são do diff (`actionlint` ausente do PATH, avisos de ambiente).

Mutação: o diff é uma função de guarda em shell; o `forge-mutante` não cobre shell e a spec de mutantes não é do PR. As guardas foram exercidas pelas sondas (commit novo, outro remoto, URL, mistas), sem mutante rodado.
