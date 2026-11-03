---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/lote-fc-seguranca
commit: e8b76448ca469e970529c0cd427f67ba7dd808e6
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: lote E2+E3 da 0.33 (FC-PEDIDO-FORA-DAS-RAIZES e FC-ENTREGA-GIT-FALHA-ABERTA)

Escopo da rodada 2: só o delta `9966b27..e8b7644` (`forge-check delta --parecer` sobre este parecer lê `ae4dacd..e8b7644`, o mesmo conteúdo, porque `9966b27` é só o parecer da rodada 1). São 8 arquivos (+557 / -28): `bin/forge-check`, o fragmento do changelog, os dois testes do lote e quatro listas de mutantes. Referência: as seções E2 e E3 de `~/.forge-contrib/docs/security/ameacas/versao-033.md`. A revisão é estática. As sondas e os mutantes rodaram em repositórios descartáveis e em cópias (`git archive`) em `$TMPDIR/security-engineer-lote-fc-seguranca/`. Não escrevi esta branch.

**Veredito: reprovado.** A1 a A4 da rodada 1 entraram resolvidos, e as refatorações sem mudança de comportamento mantêm rc e saída. Reprovo por um achado novo, A6, num passo que o delta retrabalhou. Uma falha do git em `base_da_entrega` ainda tira arquivo da lista com rc 0. A correção é pequena (esforço P).

## Gatilhos
`controles do Forge` (`bin/forge-check`), da R-SEGURANCA.

## Achados
- A5 (recomendado) bin/forge-check:6118 · anterior ao lote, fora desta volta (cartão FC-RAIZ-PEDIDOS-SUBPASTA): `--raiz-pedidos` aceita qualquer subpasta da raiz, e `<raiz>/x/docs/pedidos/` vira raiz aceita pelo E2
- A6 (bloqueante) bin/forge-check:516 · requisito (C-1/C-3 do E3): `arquivos_da_entrega` ainda cai para as BASES quando o rev-parse do Base-sha falha; com a falha só nessa 1ª chamada, a de :1255 acerta, nada vai a `falhas` e a lista sai do diff contra a develop, sem arquivo, com rc 0

## Rodada 2 (e8b7644)

### Achados da rodada 1
- **A1, resolvido.** `test_diff_do_merge_integrado_falha_e_reprova` (`tests/test_entrega_git_falha.py:66`) monta o squash na develop. Com o 2º diff `..` em falha, espera rc 1 e "diff do merge integrado". O mutante M30 (`if do_merge is None:` trocado por `if False:`) está na lista.
- **A2, resolvido.** `test_rev_list_dos_pais_do_head_do_cmd_entrega_tem_teste_proprio` usa a ordem 2 do padrão, que é a chamada de `cmd_entrega` (a 1ª é a de `diferem_dos_dois_pais`). Roda nas três etapas, com o mutante M29. Os rótulos continuam iguais. A ordem resolve o teste, e o rótulo distinto que sugeri não é necessário.
- **A3, resolvido.** `todos` (`bin/forge-check:1257`) guarda a lista anterior aos filtros. Com `falhas`, `:1308` devolve essa lista e tira a informativa "integração da base". Cobrem isso `test_falha_depois_de_um_filtro_saudavel_mostra_a_lista_inteira` e `test_filtro_e4_com_outro_passo_falho_nao_tira_arquivo`, com os mutantes M32 e M33.
- **A4, resolvido.** O id nu passa por `dentro_da_raiz` nas três raízes (`:877-888`), na ordem da C-4. O link para fora levanta `PedidoFora`. Em cada raiz, `test_id_nu_que_e_link_para_fora_e_recusado_em_cada_raiz` cobre o caso, com M10 e M11. Mutante meu: voltar ao `is_file` sem resolver o caminho. Morre em 4 testes de `test_pedido_fora`. As sondas com NUL, quebra de linha, nome de 300 caracteres, `.`, `..` e `...` não levantam exceção, e todas caem na leitura com rc 2.
- **A5, sem mudança.** Ficou fora da volta por DECISÃO TÉCNICA de 14:04 (cartão FC-RAIZ-PEDIDOS-SUBPASTA). Continua recomendado.

### A6 (bloqueante, requisito; severidade baixa)
**Evidência.** `cmd_entrega` chama `arquivos_da_entrega(raiz, head, base_sha, valido)` (`:1251`). Esta, em `:516`, chama `base_da_entrega(raiz, base)` sem `so_a_pedida`. Se o rev-parse do Base-sha falha, ela cai para `origin/develop` e lista `develop...head`. O delta pôs `so_a_pedida=True` só na 2ª chamada (`:1255`). A falha entra em `falhas` apenas quando as duas chamadas falham, e é isso que `test_base_pedida_que_falha_nao_cai_para_as_bases` (`tests/test_entrega_git_falha.py:95`, ordem `todas`) testa.

**Sonda.** `git` falso com o padrão `*--verify --quiet <Base-sha>*` na ordem 1, num cenário em que a develop levou o 1º commit da branch e depois mudou `a.txt`. Na etapa `review`:
- com o git saudável, rc 0 e `confira "a.txt"` e `confira "b.txt"`;
- com a falha só na 1ª chamada, rc 0, só `confira "b.txt"` e nenhuma linha "o git falhou".

**Caminho.** A falha é ambiental, como a do ator do E3: timeout de 5 s sob carga, entre duas chamadas a milissegundos uma da outra. O passo "base_da_entrega sem base" está na lista do C-1. A falha tira arquivo sem reprovar, o que contraria a C-1 e a C-3 e cai na T-1. Existe desde a base `928e61b`, mas o delta retrabalhou exatamente este passo. Não vi isso na rodada 1.

**Correção mínima.** Uma única leitura da base na entrega, sem fallback:
- `arquivos_da_entrega` ganha `so_a_pedida` e, com ele e sem base, devolve `None` (falha), nunca `[]`;
- `cmd_entrega` passa `so_a_pedida=True`;
- a checagem de `:1255` sai ou fica redundante;
- um teste com o padrão do Base-sha na ordem 1, mais o mutante que tira o `so_a_pedida` da chamada.

Os outros chamadores (`gatilhos` via `cmd_pr` e `arquivos_por_branch`, `:1840`) seguem sem mudança (T-4). Esforço P. Dono: `tech-lead`.

### Refatorações sem mudança de comportamento
- **776706e** (`pais` com if/else, `:1284-1288`): é equivalente ao ternário. `pais` fica `[]` na falha e `split()[1:]` no sucesso.
- **218b44f, ramo `if mb:`.** Com `cod` 0, o `merge-base` sempre imprime um sha, e sem ancestral comum ele sai com 1, o que já virava "diff do merge da base". O ramo `else` era inalcançável, e tirá-lo não muda nada.
- **218b44f, as três guardas `not falhas`.** Com falha, os filtros agora rodam, mas `:1308` repõe `todos` antes de qualquer saída. Entre o filtro e `:1308`, nada depende de `arquivos`: `pareceres_da_integracao` e as contagens não leem a lista. As linhas de reprovação são as mesmas, e o rc também.
- **`desfeitos = set()` na falha.** Evita o `TypeError` que o filtro sem guarda daria. A lista volta inteira em `:1308`.
- **`igual_na_base`.** Com o git saudável, o resultado é o da base. Na base, duas falhas nunca eram iguais, porque o git ecoa `<rev>:<nome>` no stdout e o commit (sha) difere de `origin/develop` (conferi com `rev-parse HEAD:nao-existe`). A guarda explícita só torna isso independente do eco, e o M15 a cobre.
- **T-2.** Nenhum hook chama `cmd_entrega`, `escopo_pelo_primeiro_pai` ou `igual_na_base`: os hooks usam `fc.cmd_pr` e `fc.base_do_delta`. O `so_a_pedida` tem `False` por padrão, e `:516` e `:1840` seguem iguais.
- **T-3.** O `GIT_TIMEOUT_S` não mudou.

### As 3 condições "apagadas" da base
- **`928e61b:861`** (`(pasta / ...).is_file()` do id nu). Virou `achado is not None and arquivo_existe(achado)`, mais o escape (`:883-888`). Isso é mais estrito e cobre o mesmo legítimo: `test_dentro_das_raizes_e_o_id_nu_passam` passa. O link para fora agora recusa. O mutante que volta ao comportamento antigo morre (ver A4).
- **`928e61b:1196`** (`if dos_dois_pais := diferem_dos_dois_pais(...)`). A chamada saiu do `if` (`:1263`), e a condição virou `if dos_dois_pais:` (`:1267`), depois de converter `FalhaDoGit` em `None`. No sucesso, a verdade é a mesma. Cobrem o M26 (`IntegracaoNaBranch`), o M39 e o M40.
- **`928e61b:1228`** (`if not arquivos:`). Virou `if not arquivos and not falhas:` (`:1311`), como pede a C-2. O M34 a cobre.

As três reescritas cobrem o comportamento da base no caminho saudável, e não há regressão.

### PA-7 e testes
- **AR-4.** O `entrega` de `test_pedido_fora` passou a usar `ambiente_limpo()`.
- **AR-1.** São 40 mutantes novos.
- **AR-2.** O ramo de falha da 1ª leitura da base é justamente o que falta (A6).
- **Testes do brief.** `python3 -m unittest tests.test_forge tests.test_pedido_fora tests.test_entrega_git_falha`: 517 testes, OK (293,9 s).
- **Ferramentas.** `gitleaks` e `semgrep` seguem fora do PATH (lacuna). O delta não traz segredo nem dependência.

## Rodada 1 (ae4dacd)

Escopo: `git diff 928e61b66015f7ee2a2e585dc8178e07dc16be39...ae4dacd791edf104c21cbe2b79092e93591c659d`, 9 arquivos (+340 / -77). Veredito da rodada: reprovado (A1 e A2). Os números de linha abaixo são os de `ae4dacd`.

Achados da rodada (texto original):
- A1 (bloqueante): o passo "diff do merge integrado" não tinha teste, e o mutante `or []` sobrevivia.
- A2 (bloqueante): o `rev-list --parents -n 1` de `cmd_entrega` não tinha teste próprio.
- A3 (recomendado): a falha tardia deixava a lista filtrada.
- A4 (recomendado): o id nu era lido sem `realpath`.
- A5 (recomendado): `--raiz-pedidos` aceitava subpasta.

### Detalhe dos achados (rodada 1)

**A1 (bloqueante, requisito; severidade média).** Evidência: o caminho `integrado` de `cmd_entrega` (`bin/forge-check:1276-1282`) trata o `None` do `nomes_do_intervalo(..., estrito=True)` e registra "diff do merge integrado". O código está certo. Mas nenhum teste de `tests/test_entrega_git_falha.py` monta o squash na base com a etapa `merge-integracao`. Mutante aplicado numa cópia: `do_merge = pais[0], (nomes_do_intervalo(...) or [])`. Ele passou, com rc 0, em `tests.test_forge`, `test_pedido_fora`, `test_entrega_git_falha`, `test_volta_por_delta`, `test_conferencia_base_dono` e `test_conf_escopo` (614 testes, OK). Caminho de ataque: falha ambiental do git (timeout, objeto ausente, PATH do conferente) na etapa de integração. Com o mutante, `arquivos` fica vazio sem falha registrada, e a entrega sai "escopo: sem commit (nada a conferir)", sem reprovar. É a ameaça T/R do E3 (T-1). Hoje o defeito não existe. O que falta é a trava que impede a sua volta. Correção mínima: um teste `reprova` com o repositório de squash (develop com o commit `S` de um pai só, `--branch <S>`, `--base-sha <pai de S>`, `--etapa merge-integracao`) e `PADRAO='*--name-only*[!.]..[!.]*'` na ordem 2. A ordem 1 é o diff de `escopo_pelo_primeiro_pai`. A sonda local deu rc 1 e a linha `escopo: o git falhou (diff do merge integrado); o escopo não foi lido`. Esforço P. Dono: `tech-lead` (implementação do lote), com o `qa-engineer` para a lista de mutantes.

**A2 (bloqueante, requisito; severidade baixa).** Evidência: `test_passos_do_caminho_simples_em_toda_etapa` usa `*rev-list --parents -n 1*` na ordem 1. A primeira chamada que casa é a de `diferem_dos_dois_pais` (`bin/forge-check:1108`), não a de `cmd_entrega` (`:1272`). As duas gravam o mesmo rótulo, "rev-list dos pais do head", e por isso o teste passa sem exercitar `:1272`. Mutante aplicado numa cópia: `if cod_pais:` trocado por `if False:`. Ele sobreviveu aos mesmos 614 testes. Caminho: só essa chamada falha, e a falha não reprova. Em `merge-integracao`, o `pais` vazio desliga o escopo do squash, o que alarga a lista e é falha fechada. Mesmo assim, é um passo do C-1 que a C-5 manda testar um a um. Correção mínima: dar rótulos distintos aos dois passos (por exemplo "rev-list dos pais do head (entrega)") e um teste com o padrão na ordem 2, ou na ordem certa do caminho sem merge, que espere esse rótulo. Esforço P. Dono: `tech-lead`.

**A3 (recomendado; baixa).** Na sonda do squash com o segundo diff `..` em falha, `escopo_pelo_primeiro_pai` já tinha filtrado `a.txt`, e o passo `integrado` falhou depois. A saída traz a falha e nenhuma linha `escopo: confira`. O rc 1 garante que nada passa. A C-3 pede a lista sem filtro, e o conferente perde a lista que veria. O mesmo vale para as falhas de `cod_pais` e das contagens, que vêm depois dos filtros. Correção mínima: guardar a lista anterior aos filtros e, com `falhas`, mostrá-la inteira. Esforço P. Dono: `tech-lead`.

**A4 (recomendado; baixa).** Para o id nu, `bin/forge-check:876-878` lê `docs/pedidos/<id>.md` da cópia principal e da raiz com `is_file()`, que segue o link, e devolve o caminho literal. A C-4 manteve essa ordem de propósito. Só que a dimensão "link no último componente" da matriz, aplicada à forma "id nu", fica aberta, e a leitura usa um caminho não resolvido (C-3). Não há ganho realista: quem cria o link já escreve em docs/pedidos/. Correção mínima: passar as duas raízes por `dentro_da_raiz`, como já se faz nas `RAIZES_DE_BRIEF` em `:880`. Esforço P. Dono: `tech-lead`.

**A5 (recomendado; baixa; anterior ao lote).** `bin/forge-check:6104-6105` aceita como `--raiz-pedidos` qualquer pasta igual à raiz ou abaixo dela. Com `--raiz-pedidos <raiz>/tmp`, o `<raiz>/tmp/docs/pedidos/x.md` passa pelo E2 como raiz aceita. É o mesmo ator do E2: precisa que o Jarvis rode o argumento escolhido. Correção mínima: aceitar só a raiz, a cópia principal e as `RAIZES_DE_BRIEF` exatas. Esforço P. Dono: `tech-lead`, por decisão do arquiteto, porque mexe em uso documentado.

### Conferência dos controles (rodada 1)

**E2.** As sondas rodaram com `entrega` num repositório descartável, com o cwd fora da raiz:
- Recusados com rc 2 e a linha da C-2: `/tmp/.../fora/x.md` (existente), `~/notas-inexistente/x.md`, `docs/pedidos/../propostas/x.md` (existente), `docs/pedidos/l.md` (link para fora), `docs/pedidos/dir/x.md` (pasta intermediária com link para fora), `docs/pedidosX/x.md`, `./y.md` e `y.md` (existentes no cwd e na raiz), o absoluto com `..`, `docs/pedidos`, `docs/pedidos/`, `Docs/Pedidos/x.md` e `~root/x.md`.
- Quebra de linha, nome longo e `~` só dão rc 2 pela leitura ("não consegui ler").
- Passam: `x`, `docs/pedidos/x.md`, `./docs/pedidos/x.md`, o absoluto dentro da raiz, `~/.forge-contrib/docs/pedidos/versao-033.md` e o id nu `versao-033`.

O que se lê é o `realpath` (C-3). `PedidoFora` só é tratada em `main` (`:6127`), e nenhum dos nove chamadores a captura como "sem pedido" (C-2). Os hooks não chamam `caminho_do_pedido`: usam só `cmd_pr`, `isencoes_da_entrega`, `pedidos_da_branch`, `base_do_delta` e `avaliar_versao`. Por isso a exceção nova não chega a um hook (T-2 do E3). T-1 a T-4 não foram violadas, e nenhuma raiz nova foi acrescentada.

**E3.**
- C-1: os passos levam a `falhas`, e com qualquer falha a entrega reprova em toda etapa (o mutante "só na `codigo`" morre: 17 falhas).
- C-2: "sem commit" só sai sem falha (`:1296`).
- C-3: os filtros dos dois pais e do primeiro pai não rodam com falha (A3 é só exibição).
- C-4: `gatilhos` com `None` exige os dois portões (`:544`). `isencoes_do_diff(None)` não isenta nada, e o hook `parecer` não recebe exceção nova. `arquivos_por_branch` tira a branch da comparação informativa.
- `delta` e `commit_vale` não mudaram de contrato (`contagens_do_intervalo` e `nomes_do_intervalo` seguem com `estrito=False` por padrão).
- T-3: o `GIT_TIMEOUT_S` não mudou.
- A comparação `rev-parse <commit>:<n>` × `<base>:<n>` do L08 não iguala duas falhas, porque o git ecoa o argumento no stdout.

Mutantes da C-6, cada um sobre o `test_entrega_git_falha`: `return None` trocado por `[]` morre; `or {}` nas contagens morre; sem a checagem da base, morre; filtro com falha (`if dos_dois_pais:`) sobrevive, mas hoje o `None` já vem da conversão do `FalhaDoGit`, e isso não é bloqueante. A1 e A2 sobrevivem.

Testes do brief: `python3 -m unittest tests.test_forge tests.test_pedido_fora tests.test_entrega_git_falha`, 507 testes, OK (149,9 s).

### Ferramentas (rodada 1)
Nenhum risco aceito. Ferramentas: leitura do diff, sondas com `git` falso no PATH e mutantes à mão em cópias. `gitleaks` e `semgrep` não estão no PATH (lacuna registrada). O lote não traz segredo nem dependência.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, `forge-check delta`, sondas com `git` falso no PATH e mutantes à mão em cópias. `gitleaks` e `semgrep` não estão no PATH (lacuna registrada).
