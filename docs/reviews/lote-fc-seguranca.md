---
tipo: review
contrato: 1
pedido: versao-033
branch: melhoria/lote-fc-seguranca
commit: dd441fa8cf8788b15188b604d0c2877c46da1742
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-03
---
# Review: versao-033 (lote E2+E3, `bin/forge-check`)

Rodada 3 (head dd441fa8cf8788b15188b604d0c2877c46da1742): aprovado; o A6 da segurança da rodada 2 está resolvido, sem regressão; A1 e A6 deste parecer seguem como recomendados; sem achado novo. As rodadas 1 (head ae4dacd) e 2 (head e8b7644) ficam abaixo, como foram escritas.

Revisor: outra instância do `tech-lead`, não o autor (D-ETAPAS-INST = A). Base 928e61b66015f7ee2a2e585dc8178e07dc16be39, head ae4dacd791edf104c21cbe2b79092e93591c659d, 3 commits (a02cfc6 E3, 7cb82f3 E2, ae4dacd mapa do E3).

## Achados
- A1 (recomendado) bin/forge-testes:73 · o E3 ficou em dois commits (a02cfc6 e ae4dacd): em a02cfc6 sozinho o test_testes_tocados falha e o revert conflita; a develop integra por squash, então não devolve; cortado na volta pelo Jarvis (14:04), segue como lição de processo
- A6 (recomendado) bin/forge-check:1 · o lote passa de 150 linhas de código e teste (decisão M14); o corpo do PR, aberto na E1.7, precisa da linha teto: excedido com o motivo ou citar a decisão do dono de 10:06; segue pendente para a E1.7

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

## Rodada 2
Delta lido: `bin/forge-check delta --parecer` sobre este parecer, intervalo ae4dacd..e8b7644 (o 9966b27 é só o parecer de segurança): `bin/forge-check` +38 -23 (linhas 501-504, 877-888, 1138-1143, 1163, 1171-1175, 1255-1309), `tests/test_entrega_git_falha.py` +78 -3, `tests/test_pedido_fora.py` +13 -1, `changelog.d/lote-fc-seguranca.md` +1 -1 e as quatro specs `tests/mutantes/lote-fc-seguranca-{1..4}.json` (38 mutantes, 3 isentas). Já lido na rodada 1 e fora do delta: o resto de `bin/forge-check`, `bin/forge-testes`, `tests/test_forge.py`, `tests/test_volta_por_delta.py`, `tests/test_conferencia_base_dono.py` e `tests/test_testes_tocados.py`.

**Achados da rodada 1.**
- A2 resolvido: `base_da_entrega(..., so_a_pedida=True)` (`bin/forge-check:501`) não cai para as BASES quando o Base-sha falha; os outros chamadores seguem com o padrão. Teste `test_base_pedida_que_falha_nao_cai_para_as_bases`, nas três etapas.
- A3 resolvido: `igual_na_base` (`bin/forge-check:1138`) exige código 0 nos dois `rev-parse`; `test_rev_parse_do_objeto_que_falha_nos_dois_lados_nao_tira_o_arquivo` prova o par saudável (nada a conferir) e o que falha (`a.txt` à vista).
- A4 resolvido: `PedidoForaDasRaizes.entrega` parte de `ambiente_limpo()`.
- A5 resolvido: `test_git_saudavel_nao_muda` confere o rc (1 só na `merge-integracao`, pelos pareceres ausentes no head do repositório de teste).
- A1 e A6 não entraram, pelo corte do Jarvis de 14:04; seguem recomendados.

**Itens da segurança na volta (conferidos contra C-n e T-n, sem refazer o parecer dela).** E2: o id nu passa pela `dentro_da_raiz` em cada raiz, na ordem de hoje (C-4), e o link para fora de `docs/pedidos/` recusa com rc 2 (C-2, C-3), teste `test_id_nu_que_e_link_para_fora_e_recusado_em_cada_raiz` na raiz e na raiz de brief; `os.path.lexists` com NUL dá False, sem exceção. E3: `todos` (`bin/forge-check:1257`) guarda a lista antes dos filtros e, com qualquer falha, volta inteira no fim e a informativa "integração da base" sai (C-3, exibição), também quando a falha vem depois do filtro saudável (`diff do merge integrado`, teste próprio). Novos testes cobrem o `rev-list --parents` do `cmd_entrega`, o `desfeitos` no `--desde`, o E4 com outro passo falho, o merge de outra coisa, a integração limpa e a `sobreposicao` com a branch cujo git falhou (C-4).

**Refatorações sem mudança de comportamento.**
- 776706e, `pais` em if/else (`:1284-1288`): mesma lista nos dois ramos; rc e saída iguais.
- 218b44f, `if mb:` removido (`:1171-1175`): com `cod` 0 o `git merge-base` sempre imprime o sha; com `cod` diferente de 0 a função já devolve `FalhaDoGit` antes; o ramo `else` era inalcançável com o git real.
- As três guardas `not falhas` removidas (`:1267`, `:1270`, `:1280`): entre os filtros e o fim, `arquivos` não é lido (`pareceres_da_integracao`, `contagens` e `autorias` não o usam) e, com falha, `:1308` o troca por `todos` e tira a informativa que só o filtro punha; sem falha, o caminho é o de antes. Saída igual.
- `desfeitos = set()` na falha (`:1262`): só evita o `None` nos filtros que agora rodam; a reprovação vem de `falhas` e a lista final é `todos`.

**As três condições "apagada" do `forge-mutante --cobertura` (base 928e61b).**
- `:861` (`is_file` do id nu na principal e na raiz): virou `achado is not None and arquivo_existe(achado)` com a `dentro_da_raiz` no laço único (`:877-888`); mesma ordem e mesmo arquivo achado, mais o aperto do link; isenta na spec 4 com motivo.
- `:1196` (`if dos_dois_pais := ...`): a chamada saiu do `if` para o passo falho ser lido; `diferem_dos_dois_pais` devolve tupla (verdadeira) ou None ou `FalhaDoGit`, e o `if dos_dois_pais:` depois da troca da falha por None decide igual; o primeiro pai só roda com None (`M39` mata o `if True`).
- `:1228` (`if not arquivos:`): virou `if not arquivos and not falhas` (`:1311`), o C-2; coberto pelos testes de passo em toda etapa.

**Testes.** No head e8b7644: `python3 -m unittest tests.test_forge tests.test_pedido_fora tests.test_entrega_git_falha`, 517 testes, OK (137 s). O `bin/forge-testes --listar` cai na suíte completa por causa das specs em `tests/mutantes/` (fora do mapa, como desenhado); a suíte inteira fica com o QA (D-5). Mutação: o autor relata 38 mutantes mortos (conferido na entrega de 16:03); não refeita aqui.

**Commits.** Onze commits de E3 e quatro de E2 na volta, Conventional Commits em português; os de E2 (7f3a70c, 35fcc59, 2a33b77, 7903caf) só tocam o caminho do pedido, o teste dele, o fragmento e a isenta da spec 4. Achados recorrentes (PA-7) conferidos: AR-4 não volta (A4 resolvido); nenhuma classe repetida neste parecer.

## Rodada 3
Delta lido: `bin/forge-check delta --parecer` sobre este parecer, intervalo e8b7644..dd441fa (o 655424f, o b25f05b e o 626595e não mudam código): `bin/forge-check` +4 -4 (linhas 516, 518, 1253-1256), `tests/test_entrega_git_falha.py` +5 (100-104) e `tests/mutantes/lote-fc-seguranca-4.json` +10 (26-35). Um commit, dd441fa, que se reverte sozinho. Já lido nas rodadas 1 e 2 e fora do delta: o resto dos arquivos.

**A6 da segurança (rodada 2): resolvido.**
- `arquivos_da_entrega` (`bin/forge-check:516`) lê a base uma só vez com `so_a_pedida=True`: com o Base-sha dado, as BASES não entram, e a lista nunca sai do diff contra a develop (C-1, C-3 do E3; T-1 sem `or []`).
- `:518` devolve None com base dada que não lê e `[]` só sem base nenhuma; `cmd_entrega` (`:1252-1256`) leva o None a `falhas` ("diff da entrega") e só rotula "base da entrega" se a 2ª leitura também falha. Com a falha só na 1ª leitura, reprova com rc 1 (C-2).
- Teste `test_base_pedida_que_falha_so_na_primeira_leitura_reprova` nas três etapas: o padrão casa só a leitura sem `--end-of-options`, então o `sha_do_commit` do início não consome a ordem 1, e a falha cai mesmo em `arquivos_da_entrega`.
- M40 conferido à mão, numa cópia do head em `$TMPDIR`: sem `so_a_pedida`, o teste cai nas três etapas (3 falhas).

**Regressão: nenhuma.** O None novo alcança os outros chamadores com base dada: `gatilhos` exige os dois portões e `isencoes_do_diff(None)` não isenta (C-4, fecha); `arquivos_por_branch` passa a base já resolvida, que lê. No `pr` com base ilegível, o resultado agora fecha em vez de cair para a develop: aperta, não afrouxa.

**Testes.** No head dd441fa: `python3 -m unittest tests.test_forge tests.test_pedido_fora tests.test_entrega_git_falha`, 518 testes, OK (125 s). A suíte inteira fica com o QA (D-5). Achados recorrentes (PA-7) conferidos: nenhuma classe repetida nesta rodada.
