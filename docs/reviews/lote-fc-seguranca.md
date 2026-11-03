---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-fc-seguranca
commit: ae4dacd791edf104c21cbe2b79092e93591c659d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: versao-033 (lote E2+E3, `bin/forge-check`)

Revisor: outra instância do `tech-lead`, não o autor (D-ETAPAS-INST = A). Base 928e61b66015f7ee2a2e585dc8178e07dc16be39, head ae4dacd791edf104c21cbe2b79092e93591c659d, 3 commits (a02cfc6 E3, 7cb82f3 E2, ae4dacd mapa do E3).

## Achados
- A1 (recomendado) bin/forge-testes:73 · o E3 ficou em dois commits (a02cfc6 e ae4dacd): em a02cfc6 sozinho o test_testes_tocados falha (módulo fora do mapa) e o revert de a02cfc6 conflita; a develop integra por squash, então não devolve; nos próximos lotes, o mapa no commit do item
- A2 (recomendado) bin/forge-check:1246 · a segunda chamada a base_da_entrega quase nunca dá None: se o rev-parse do Base-sha falha, ela cai nas BASES e o diff passa a ser sobre a develop; o C-1 fica cumprido no caso sem base nenhuma; sugestão: com base pedida, não cair para as BASES no entrega
- A3 (recomendado) bin/forge-check:1151 · no filtro do primeiro pai, dois rev-parse que falham iguais (os dois objetos ausentes) contam como "igual à base" e tiram o arquivo; linha anterior ao lote e fora da lista do C-1, mas toca o C-3; sugestão: exigir código 0 nos dois lados
- A4 (recomendado) tests/test_pedido_fora.py:86 · o teste novo herda o os.environ inteiro (classe do AR-4), como o Raiz de test_voltas; sugestão: partir de ambiente_limpo()
- A5 (recomendado) tests/test_entrega_git_falha.py:104 · test_git_saudavel_nao_muda não confere o rc; sugestão: assertEqual(rc, 0) junto da linha
- A6 (recomendado) bin/forge-check:1 · o lote soma 414 linhas de código e teste (decisão M14); o corpo do PR, aberto na E1.7, precisa da linha teto: excedido com o motivo (lote por arquivo, E21) ou citar a decisão do dono de 10:06

## Parecer
Aprovado. Síntese por controle do modelo de ameaças (seções E2 e E3 de `docs/security/ameacas/versao-033.md`):

**E2 (FC-PEDIDO-FORA-DAS-RAIZES).**
- C-1, C-3: o caminho com cara de caminho (absoluto, `~/`, relativo) passa pela `dentro_da_raiz` em cada raiz (principal, raiz, `RAIZES_DE_BRIEF`, com a de `--raiz-pedidos` na frente) e devolve o caminho resolvido; o atalho "existe no cwd" saiu, também para o id nu (aperta).
- C-2: `PedidoFora` sobe até o `main`, que imprime a linha da regra e sai com rc 2. Os nove chamadores passam pelo `main`; nenhum hook chama `caminho_do_pedido` (o `parecer.py` usa só `cmd_pr`, `isencoes_da_entrega`, `pedidos_da_branch`, `base_do_delta` e `avaliar_versao`), então a exceção nova não alcança hook.
- C-4: a ordem do id nu ficou igual; o `~usuario` não é expandido (caso no `EntregasParalelas`).
- C-5, C-6: os testes que punham o pedido em `$TMPDIR` montam `docs/pedidos/` num HOME por teste; `PedidoForaDasRaizes` cobre os seis casos que recusam, mais a própria pasta `docs/pedidos`, e os dois que passam.
- T-1 a T-4: nenhuma raiz nova, nenhuma aceitação com aviso, `dentro_da_raiz` intacta, a leitura segue na cópia principal.

**E3 (FC-ENTREGA-GIT-FALHA-ABERTA).**
- C-1: `arquivos_da_entrega`, `desfeitos_da_entrega`, `contagens_do_intervalo(estrito)` devolvem None na falha; os dois filtros devolvem `FalhaDoGit` com o passo; `cmd_entrega` junta os passos em `falhas` e reprova em toda etapa com `escopo: o git falhou (<passo>); o escopo não foi lido`.
- C-2: `sem commit (nada a conferir)` só sai com `falhas` vazia.
- C-3: com falha, nenhum filtro (dois pais, primeiro pai, E4) roda; ressalva no A3, em linha anterior ao lote.
- C-4: `gatilhos` com None exige os dois portões; `isencoes_do_diff(None)` dá conjunto vazio (sem isenção, sem `TypeError`); `arquivos_por_branch` deixa de fora a branch cujo git falhou; o `delta` (`contagens_do_intervalo` sem `estrito`) não mudou.
- C-5, C-6: o `git` falso por padrão e ordem cobre cada passo nas etapas `codigo`, `review` e `merge-integracao`, com e sem `--desde` e com merge da base; os mutantes da lista (None por `[]`, `or []`, só na `codigo`, filtro com vazio) caem nos testes de passo, de etapa e em `test_filtro_que_falha_nao_tira_arquivo`.
- T-1 a T-4: sem `or []` nem `except` que vire vazio; sem exceção nova no caminho do hook; `GIT_TIMEOUT_S` intacto; com o git saudável o caminho de sucesso é o mesmo (a ordem dos cálculos mudou, o resultado não).

**Testes e mapa.** O `bin/forge-testes` lista `test_entrega_git_falha` (37 módulos, `test_testes_tocados` ajustado). Rodados no head ae4dacd: `python3 -m unittest tests.test_forge tests.test_pedido_fora tests.test_entrega_git_falha`, 507 testes, OK (124 s, 8 núcleos). A suíte inteira fica com o QA (D-5).

**Commits.** Três commits em Conventional Commits; E2 se reverte sozinho; E3 não (A1). Fragmento `changelog.d/lote-fc-seguranca.md` presente.

**Segurança e devops.** O parecer de segurança (E1.4) roda em paralelo e não é refeito aqui; o lote não toca `.github/` nem o pre-push (sem E1.5).
