---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-prepush-patch
commit: ccb7a0c3663dd98c3eae57186ea9612c9b21cc83
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-16
---
# Review: v047 (melhoria/v047-prepush-patch, E2.325; revalidações E2.367, E2.428, E2.490, E2.572 e E2.601)

## Revalidação (E2.601, head ccb7a0c3)
Delta lido: `forge-check parecer delta docs/reviews/v047-prepush-patch.md`, intervalo d03fb7e0..ccb7a0c3, no domínio só `tests/test_testes_tocados.py` (+10/-1). Duas mudanças: o `AMBIENTE` do teste passa a tirar o `GIT_*` herdado (um hook exporta `GIT_DIR` e `GIT_INDEX_FILE`, e o git do repositório de brinquedo cairia no do clone) e entra o caso `test_o_patch_do_pre_push_e_o_comum_dos_hooks_levam_ao_test_pre_push_patch` (mapa: `docs/devops/pp1-pre-push.patch` e `hooks/_comum.py` planejam `dirigido` com `test_pre_push_patch`). Sem guarda de controle nova; o patch e o `bin/forge-testes` seguem iguais.

Ferramentas no head ccb7a0c3: `python3 -m unittest tests.test_testes_tocados` na raiz do clone, sem `-I`, 162 testes, OK (1 pulado por sandbox, /proc de outro namespace; 62,3 s). Suíte completa: sem PR, fica para o CI. `git fetch`: o remoto da branch já está em ccb7a0c3, nada a mesclar. Sem achado novo; A4 e A5 seguem recomendados; sem recorrência nova.

## Revalidação (E2.572, head d03fb7e0)
Delta lido: `forge-check parecer delta docs/reviews/v047-prepush-patch.md`, intervalo 8079c5d4..d03fb7e0, no domínio só `bin/forge-testes` (3 linhas no MAPA: `test_pre_push_patch` entra na linha de `hooks/.*`, e nova linha para `docs/devops/pp1-pre-push.patch` com CONTEUDO). Mapa de testes, sem guarda de controle; o patch e o teste seguem iguais. Isso conserta o CI do PR 607 (o teste lê `hooks/_comum.py` e o patch).

Ferramentas no head d03fb7e0: `python3 -m unittest tests.test_testes_tocados tests.test_pre_push_patch` na raiz do clone, sem `-I`, 173 testes, OK (1 pulado por sandbox, /proc de outro namespace; 72,7 s). Suíte completa: sem PR, fica para o CI. `git fetch`: o remoto da branch já está em d03fb7e0, nada a mesclar. Sem achado novo; A4 e A5 seguem recomendados; sem recorrência nova.

## Revalidação (E2.490, head 8079c5d4)
Delta lido: `forge-check parecer delta docs/reviews/v047-prepush-patch.md`, intervalo 455f2597..8079c5d4, no domínio `bin/forge-mutante` (opção `--todas`, `texto_no_commit`) e `docs/engineering/achados-recorrentes.md` (AR-1, AR-2, AR-4, AR-12). Tudo veio da develop pelos merges de atualização: `git diff origin/develop...HEAD -- bin/forge-mutante` segue só a docstring do item (3 linhas), e `docs/devops/pp1-pre-push.patch`, `tests/test_pre_push_patch.py` e o fragmento do item estão iguais aos de 455f2597. Sem código nosso novo.

Ferramentas no head 8079c5d4: `python3 -m unittest tests.test_pre_push_patch` na raiz do clone, 12 testes, OK (25,8 s). Suíte completa: sem PR, fica para o CI do PR. Sem achado novo; A4 e A5 seguem recomendados; sem recorrência nova para `achados-recorrentes.md`.

## Revalidação (E2.428, head 455f2597)
Delta lido: `forge-check parecer delta docs/reviews/v047-prepush-patch.md`, intervalo 5016852d..455f2597, no domínio só `docs/engineering/achados-recorrentes.md` (AR-2 de 2 para 3 vezes, última `docs/devops/pp1-pre-push.patch:32`, gravada com o A5 deste parecer em d1bcbc1f). O resto do intervalo são os pareceres de QA e segurança e merges da própria branch; `git diff 5016852d 455f2597` fora de `docs/reviews`, `docs/qa` e `docs/security` muda só essa linha. Patch, teste, `bin/forge-mutante` e fragmento iguais aos aprovados.

Ferramentas no head 455f2597: `python3 -m unittest tests.test_pre_push_patch` na raiz do clone, 12 testes, OK (60 s). Suíte completa: sem PR, fica para o CI do PR. Sem achado novo; A4 e A5 seguem recomendados; sem recorrência nova para `achados-recorrentes.md`.

## Revalidação (E2.367, head 5016852d)
Delta lido: `forge-check parecer delta docs/reviews/v047-prepush-patch.md`, intervalo 805a0a10..5016852d, no domínio `bin/forge-mutante` (docstring), `changelog.d/v047-prepush-patch.md` e `tests/test_pre_push_patch.py`. O delta não listou `docs/devops/pp1-pre-push.patch` (+50/-17), que é o código do item; li o diff dele no mesmo intervalo.

- A1 resolvido: o patch tira a lista fixa e filtra a saída do `--cobertura` com `COBERTURA_FILTRO_PY` (patch:23-42), que aplica `fc.motivo_de_controle(arq, listas) and not fc.TESTE.search(arq)` com PROTEGIDOS, SENSIVEIS e FORMA_COMPILADA da catraca, a mesma expressão de `tests/catraca.py:842` (`guardas_do_diff`) e o mesmo `FALTAS_DE_MUTANTE` (linha 766). Os testes novos provam: condição em `tests/catraca.py` com `hooks/_comum.py` no diff passa (S2); falta em `bin/x.py` reprova; falta mista só lista `hooks/h.py`.
- A2 resolvido: `test_saida_2_da_ferramenta_e_so_aviso` (spec malformada) prova o aviso e o envio seguindo.
- A3 resolvido: a guarda `[ -e /proc/self/fd/9 ]` saiu e o comentário diz a falha fechada pelo `head`.
- A4 segue recomendado: 252 linhas de código e teste (250 do teste).

Ferramentas no head 5016852d: `python3 -m unittest tests.test_pre_push_patch`, 12 testes, OK (14,5 s); `git apply --check` limpo; hook da base 1b88640e remendado: `bash -n` ok e `shellcheck` sem saída. Suíte completa: sem PR, fica para o CI do PR.

Parecer completo (não havia parecer anterior) do head 805a0a10 contra a base 1b88640e: `docs/devops/pp1-pre-push.patch` (63 linhas), `tests/test_pre_push_patch.py` (219) e o fragmento `changelog.d/v047-prepush-patch.md`. O `.githooks/pre-push` em vigor não muda; o patch é para o dono aplicar.

## Achados
- A1 (bloqueante) docs/devops/pp1-pre-push.patch:36 · resolvido em 5016852d: escopo diferente da catraca (R-REVIEW); o --cobertura julgava todo Python do diff e barrava tests/catraca.py e tests/apoio_*.py que a catraca do CI aceita (S1, S2). Filtrar pela lista da catraca.
- A2 (recomendado) docs/devops/pp1-pre-push.patch:45 · resolvido em 5016852d: O ramo de aviso (saída 2 do --cobertura, ex.: spec inválida) não tem teste de comportamento (R-QA); um caso com spec malformada no repo de teste prova que o envio segue com o aviso.
- A3 (recomendado) docs/devops/pp1-pre-push.patch:13 · resolvido em 5016852d: a guarda `[ -e /proc/self/fd/9 ] || return 0` era equivalente (sem ela o head falha calado e a saída é vazia igual); declarar equivalente ou tirar.
- A4 (recomendado) tests/test_pre_push_patch.py:1 · 219 linhas de teste (250 no head 5016852d) passam a orientação de 150 (M14); o PR, quando abrir, traz `teto: excedido, <n> linhas, <motivo>`.

- A5 (recomendado) docs/devops/pp1-pre-push.patch:32 · O filtro sai 2 (catraca não carrega, linha 32, ou linha sem `arq:L`, linha 39) e vira aviso, ramo novo sem teste de comportamento (R-QA, AR-2); um caso com `tests/catraca.py` quebrado no repo de teste prova o aviso.

## Sondas
- S1 · repo temporário com o hook remendado: diff muda hooks/h.py sem condição e tests/apoio_x.py `if a` -> `if a and b`, sem spec · espera: pre-push rc=0, como catraca.regra_guardas_dos_hooks == [] · obtido: pre-push rc=1 "sem mutante · tests/apoio_x.py:2"; catraca []
- S2 · mesmo repo, tests/catraca.py `if a` -> `if a and b` com hooks/h.py sem condição, sem spec · espera: pre-push rc=0, como a catraca ([]) · obtido: pre-push rc=1 "sem mutante · tests/catraca.py:2"; catraca []

## Parecer
Aprovado no head ccb7a0c3 (E2.601): delta só no teste do mapa e no ambiente dele, sem bloqueante aberto; A4 e A5 recomendados.

Aprovado no head d03fb7e0 (E2.572): delta só no mapa do `forge-testes`, sem bloqueante aberto; A4 e A5 recomendados.

Aprovado no head 8079c5d4 (E2.490): delta só da develop, sem bloqueante aberto; A4 e A5 recomendados.

Aprovado no head 455f2597 (E2.428): delta sem código, sem bloqueante aberto; A4 e A5 recomendados.

Parecer no head 5016852d: aprovado, A1 resolvido, sem bloqueante aberto; A4 e A5 recomendados.

Parecer anterior (head 805a0a10): reprovado por A1. Os três consertos fazem o que o item pede e o teste prova cada um contra o original (o original é o mutante): leitura da trava pelo fd 9 (conferi à parte que `/proc/self/fd/9` lê também o fd aberto com `9>>`, como no hook real, linha 466), `FORGE_FILA_INTERVALO` 0/00/000 recusado antes da fila, e o envio leve reprovando condição mudada em `hooks/*.py` sem mutante. O patch aplica limpo no `.githooks/pre-push` da base (`git apply --check`, blob f9443600), `bash -n` ok, modo executável mantido; o teste limpa `GIT_*`/`FORGE_*` do ambiente (AR-4) e chama o `forge-mutante` com `-I` (AR-5).

O defeito do A1: o gatilho do patch (linhas 34 a 38) olha uma lista própria de caminhos, mas a análise roda sobre o diff inteiro, e o `--cobertura` só exclui `tests/test_*.py` e `.md`. A catraca (`tests/catraca.py`, `guardas_do_diff`) usa `motivo_de_controle` do `forge-check` e tira tudo o que casa `TESTE` (qualquer coisa em `tests/`). Com isso o envio local reprova o que o CI aprova, o contrário do "nunca afrouxa, o CI roda as mesmas checagens" do bloco PREPUSH-BARATAS, e a lista fixa (`templates/projeto/*`, `tests/catraca.py`, `tests/neutralidade.py`) diverge da fonte única. Sugestão: no lugar da lista e do `--cobertura` cru, chamar `catraca.regra_guardas_dos_hooks` (uma fonte só, já carrega o `forge-mutante` da base) ou filtrar as linhas `sem mutante|só equivalente|apagada` pelo mesmo `motivo_de_controle` sem `TESTE`; e um caso de teste com helper em `tests/` que tem de passar.

Ferramentas: `python3 -m unittest tests.test_pre_push_patch` na raiz do clone, 8 testes, OK (11,3 s). Suíte completa: sem PR ainda, o CI não rodou neste head; fica para o CI do PR. Shellcheck do hook remendado e mutação do diff: não citados pelo autor; o diff não muda shell nem Python de controle do repositório (o hook é texto num `.patch`), e o próprio teste faz o papel do mutante (original contra remendado).
