---
tipo: revisao-seguranca
contrato: 1
pedido: versao-033
branch: melhoria/lote-fc-seguranca
commit: ae4dacd791edf104c21cbe2b79092e93591c659d
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-03
---
# Review de segurança: lote E2+E3 da 0.33 (FC-PEDIDO-FORA-DAS-RAIZES e FC-ENTREGA-GIT-FALHA-ABERTA)

Escopo: `git diff 928e61b66015f7ee2a2e585dc8178e07dc16be39...ae4dacd791edf104c21cbe2b79092e93591c659d`, 9 arquivos (+340 / -77), três commits (`a02cfc6`, `7cb82f3`, `ae4dacd`). Referência: as seções E2 e E3 de `~/.forge-contrib/docs/security/ameacas/versao-033.md` (controles C-n e mudanças proibidas T-n). Revisão estática. As sondas e os mutantes rodaram em repositórios descartáveis e em cópias (`git archive`) em `$TMPDIR/security-engineer-lote-fc-seguranca/`, fora da worktree. Não escrevi esta branch.

**Veredito: reprovado.** O código cumpre o E2 inteiro e o comportamento do E3. Reprovo por dois passos do C-1 do E3 que ficaram sem teste, o que a C-5 e a C-6 do modelo exigem. Nos dois, o mutante que a C-6 manda matar sobrevive à suíte. A correção é só de teste, sem mudar o código.

## Gatilhos
`controles do Forge` (`bin/forge-check`, `bin/forge-testes`), da R-SEGURANCA.

## Achados
- A1 (bloqueante) tests/test_entrega_git_falha.py:55 · requisito (C-5/C-6 do E3): o passo "diff do merge integrado" (bin/forge-check:1278, `nomes pais[0]..head`, squash em merge-integracao) não tem teste; o mutante `or []` nele sobrevive aos 614 testes e daria "sem commit (nada a conferir)" com rc 0
- A2 (bloqueante) tests/test_entrega_git_falha.py:55 · requisito (C-5/C-6 do E3): o `rev-list --parents -n 1` do head em bin/forge-check:1272 não tem teste próprio; o padrão casa antes a chamada homônima em :1108, de mesmo rótulo; o mutante que ignora `cod_pais` sobrevive aos 614 testes
- A3 (recomendado) bin/forge-check:1278 · C-3 do E3, só exibição: a falha de um passo posterior a um filtro saudável deixa a lista já filtrada (sonda: squash com o 2º diff `..` em falha mostra só a linha de falha, sem `a.txt`); o rc é 1, nada passa
- A4 (recomendado) bin/forge-check:877 · E2, id nu: na cópia principal e na raiz, `is_file` sem `realpath` aceita `docs/pedidos/<id>.md` como link para fora e devolve o caminho não resolvido (C-3); só quem já escreve em docs/pedidos/ consegue
- A5 (recomendado) bin/forge-check:6105 · anterior ao lote: `--raiz-pedidos` aceita qualquer subpasta da raiz (`<raiz>/x`), e `<raiz>/x/docs/pedidos/` vira raiz aceita pelo E2, fora de docs/pedidos/ guardada pelo hook

## Detalhe dos achados

**A1 (bloqueante, requisito; severidade média).** Evidência: o caminho `integrado` de `cmd_entrega` (`bin/forge-check:1276-1282`) trata o `None` do `nomes_do_intervalo(..., estrito=True)` e registra "diff do merge integrado". O código está certo. Mas nenhum teste de `tests/test_entrega_git_falha.py` monta o squash na base com a etapa `merge-integracao`. Mutante aplicado numa cópia: `do_merge = pais[0], (nomes_do_intervalo(...) or [])`. Ele passou, com rc 0, em `tests.test_forge`, `test_pedido_fora`, `test_entrega_git_falha`, `test_volta_por_delta`, `test_conferencia_base_dono` e `test_conf_escopo` (614 testes, OK). Caminho de ataque: falha ambiental do git (timeout, objeto ausente, PATH do conferente) na etapa de integração. Com o mutante, `arquivos` fica vazio sem falha registrada, e a entrega sai "escopo: sem commit (nada a conferir)", sem reprovar. É a ameaça T/R do E3 (T-1). Hoje o defeito não existe. O que falta é a trava que impede a sua volta. Correção mínima: um teste `reprova` com o repositório de squash (develop com o commit `S` de um pai só, `--branch <S>`, `--base-sha <pai de S>`, `--etapa merge-integracao`) e `PADRAO='*--name-only*[!.]..[!.]*'` na ordem 2. A ordem 1 é o diff de `escopo_pelo_primeiro_pai`. A sonda local deu rc 1 e a linha `escopo: o git falhou (diff do merge integrado); o escopo não foi lido`. Esforço P. Dono: `tech-lead` (implementação do lote), com o `qa-engineer` para a lista de mutantes.

**A2 (bloqueante, requisito; severidade baixa).** Evidência: `test_passos_do_caminho_simples_em_toda_etapa` usa `*rev-list --parents -n 1*` na ordem 1. A primeira chamada que casa é a de `diferem_dos_dois_pais` (`bin/forge-check:1108`), não a de `cmd_entrega` (`:1272`). As duas gravam o mesmo rótulo, "rev-list dos pais do head", e por isso o teste passa sem exercitar `:1272`. Mutante aplicado numa cópia: `if cod_pais:` trocado por `if False:`. Ele sobreviveu aos mesmos 614 testes. Caminho: só essa chamada falha, e a falha não reprova. Em `merge-integracao`, o `pais` vazio desliga o escopo do squash, o que alarga a lista e é falha fechada. Mesmo assim, é um passo do C-1 que a C-5 manda testar um a um. Correção mínima: dar rótulos distintos aos dois passos (por exemplo "rev-list dos pais do head (entrega)") e um teste com o padrão na ordem 2, ou na ordem certa do caminho sem merge, que espere esse rótulo. Esforço P. Dono: `tech-lead`.

**A3 (recomendado; baixa).** Na sonda do squash com o segundo diff `..` em falha, `escopo_pelo_primeiro_pai` já tinha filtrado `a.txt`, e o passo `integrado` falhou depois. A saída traz a falha e nenhuma linha `escopo: confira`. O rc 1 garante que nada passa. A C-3 pede a lista sem filtro, e o conferente perde a lista que veria. O mesmo vale para as falhas de `cod_pais` e das contagens, que vêm depois dos filtros. Correção mínima: guardar a lista anterior aos filtros e, com `falhas`, mostrá-la inteira. Esforço P. Dono: `tech-lead`.

**A4 (recomendado; baixa).** Para o id nu, `bin/forge-check:876-878` lê `docs/pedidos/<id>.md` da cópia principal e da raiz com `is_file()`, que segue o link, e devolve o caminho literal. A C-4 manteve essa ordem de propósito. Só que a dimensão "link no último componente" da matriz, aplicada à forma "id nu", fica aberta, e a leitura usa um caminho não resolvido (C-3). Não há ganho realista: quem cria o link já escreve em docs/pedidos/. Correção mínima: passar as duas raízes por `dentro_da_raiz`, como já se faz nas `RAIZES_DE_BRIEF` em `:880`. Esforço P. Dono: `tech-lead`.

**A5 (recomendado; baixa; anterior ao lote).** `bin/forge-check:6104-6105` aceita como `--raiz-pedidos` qualquer pasta igual à raiz ou abaixo dela. Com `--raiz-pedidos <raiz>/tmp`, o `<raiz>/tmp/docs/pedidos/x.md` passa pelo E2 como raiz aceita. É o mesmo ator do E2: precisa que o Jarvis rode o argumento escolhido. Correção mínima: aceitar só a raiz, a cópia principal e as `RAIZES_DE_BRIEF` exatas. Esforço P. Dono: `tech-lead`, por decisão do arquiteto, porque mexe em uso documentado.

## Conferência dos controles

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

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, sondas com `git` falso no PATH e mutantes à mão em cópias. `gitleaks` e `semgrep` não estão no PATH (lacuna registrada). O lote não traz segredo nem dependência.
