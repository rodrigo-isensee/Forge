---
tipo: review
contrato: 1
pedido: v0474
branch: melhoria/v0475-ci-cota
commit: 19e7b93fe4b59d2883128e17482ce3e1829955f4
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-17
---
# Review: v0474 (E3.155, branch melhoria/v0475-ci-cota)

Revalidação pelo delta `e0ac8508..19e7b93f` (`forge-check parecer delta`): `bin/forge-cota-ci`, `tests/test_cota_ci.py`, `tests/mutantes/v0475-ci-cota-2.json` (16 mutantes), skills `ci-cd` e `esperar-estado`. Li só o delta.

## Achados
- A1 (bloqueante) tests/test_cota_ci.py:38 · `tests.test_ambiente_git` reprova: `git init` (:38) e `git remote add` (:40) no repositório temporário rodam sem o `env=` de `ambiente_git.sem_manutencao()`. O módulo está na suíte do CI, então o head fica vermelho. Monte o ambiente do `git` por `sem_manutencao()`.
- A2 (recomendado) changelog.d/v0475-ci-cota.md:2 · o fragmento diz que "o Jarvis a roda no marco (skills ci-cd e esperar-estado)" e fala em "comando para o dono", mas o delta tirou o Jarvis da ci-cd, a menção da esperar-estado e o comando sugerido virou a tela de cobrança. Alinhe o texto ao que a skill diz agora.
- A3 (recomendado) bin/forge-cota-ci:92 · segue o A4 anterior: o endpoint legado `settings/billing/actions` pode não existir nas contas da cobrança nova (`settings/billing/usage`). Não conferi contra a API, porque não há rede aqui. A dica da tela de cobrança atenua o problema. Registre no PR.

## Sondas
- S1 · `python3 -m unittest tests.test_ambiente_git` no head 19e7b93f · espera: OK · obtido: `FAIL test_nenhum_modulo_roda_git_sem_o_ponto_unico (modulo='test_cota_ci.py')`: `test_cota_ci.py:38` e `:40` `git sem env= do ponto único`

## Revalidação
- A1 anterior (guardas sem mutante): resolvido. A `python3 -I tests/catraca.py --base origin/develop` deu rc 0. O `bin/forge-mutante tests/mutantes/v0475-ci-cota-2.json` mata M12 a M27 (16 de 16). Há teste de comportamento para os ramos :22, :37 e :78 de antes (origin fora do GitHub, resposta que não é objeto, dono desconhecido).
- A2 anterior (motivo apagado): resolvido. Os motivos dos dois endpoints aparecem juntos, e há teste para o caso 403 mais 404.
- A3 anterior (`FORGE_COTA_CI_ENDPOINT` sem teste): resolvido. Há dois testes, e sem dono a saída não imprime `/users//`.
- A1 e A2 da segurança (validar o formato do login, tirar `gh auth refresh -s user`): o delta os resolve com teste e mutante. Cito sem refazer o parecer da segurança.
- `tests.test_cota_ci` e `tests.test_metricas_texto` passam. O único vermelho é o `test_ambiente_git` (A1).

**A regra continua dita?** Em parte. A `ci-cd` ainda diz o essencial: medir os minutos por release com `forge-cota-ci`, rc 1 acima de 80%, cartão de melhoria e não pedir escopo (`R-CUSTO`). O corte tirou duas coisas. Saiu quem roda (o Jarvis). Saiu também o segundo gatilho: "antes de esperar um CI longo", que estava na `esperar-estado`. Agora o aviso só vem uma vez por release. O caso do pedido gastou a cota num dia (163 envios), e com um aviso por release esse caso passa sem aviso. A decisão do dono pede "aviso de minutos perto do fim". Não promovo a bloqueante, porque o dono não definiu a cadência e falta evidência. Recomendo devolver à `ci-cd` o dono e o marco em poucas palavras. Para caber no teto, corte texto em outro trecho, não a regra.

## Parecer
Reprovado por A1: um teste da suíte do CI falha no head. Para o PR: 312 linhas de código e teste (`bin` 108 + `tests` 204). O corpo do PR leva `teto: excedido, 312 linhas, <motivo>` (M14). Na volta, revalido pelo delta.
