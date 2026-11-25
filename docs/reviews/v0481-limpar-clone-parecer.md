---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-limpar-clone-parecer
commit: fe1f22755cdaf735ba4738b0f59cb7e1b0eb2068
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.6, #890: forge-fechar --limpar reconhece o clone de parecer já mesclado)

Diff lido: `8833d0f6..fe1f2275`, um commit (E14.1), 6 arquivos, +74 e -12. Código: `bin/forge-fechar:691-696` (5 linhas, dentro do H1). Clone de revisão: `/root/.forge-contrib/wt/v0481-limpar-clone-parecer-rev` (o `forge-copia` da develop local não tem `--revisao`; criado com `clone --branch --origem`).

## Achados
- A1 (bloqueante) bin/forge-fechar:692 · `--exclude='refs/tags/*'` tira da conta toda tag, não só a `arquivo/*` que o comentário e o teste citam: commit único numa tag local qualquer, nunca enviado, some no `rm -rf` (S1). Afrouxa o MP6. Estreite para `refs/tags/arquivo/*` e mantenha o teste antigo.
- A2 (bloqueante) tests/mutantes/v0474-mp6-disco-3.json:19 · AR-12: o M18 (guarda "commit só em tag local fica") ficou com o trecho `rev-list --all --not --remotes` 0 vezes no fonte e aponta para `test_commit_so_em_tag_local_fica`, que o diff renomeou; `forge-mutante --conferir --todas` acusa só no head. Atualize o M18.
- A3 (recomendado) tests/test_forge_fechar.py:152 · o teste renomeado usa `arquivo/t-local` e prova só esse nome; com o código amplo, nenhum teste diz o que acontece com a tag de outro nome. Com o A1, um teste para cada lado: `arquivo/*` sai, outro nome fica.

## Sondas
- S1 · clone em melhoria/x, commit com arquivo novo só na tag leve ou anotada `wip-meu` (sem push), `--limpar` (sonda no scratchpad, ambiente de `LimparClones`) · espera: rc=3, clone=pendente, clone existe (como na base 8833d0f6) · obtido: rc=0, clone=ok, clone apagado

## Parecer
Reprovado.

**Afrouxa regra?** Sim. O MP6 garantia que o clone com "commit fora das refs do origin (branch, tag, stash, nota)" fica pendente, e o M18 da `v0474-mp6-disco-3.json` guardava esse ramo da tag. Com o diff, a tag sai inteira da conta: a S1 mostra o mesmo cenário que fica na base e é apagado no head. O PR diz que "as tags são da origin" e que o fluxo não cria tag em clone de parecer. Mas o `limpar_clones` alcança todo clone da branch em `~/.forge-contrib/wt` (o do autor também), e a tag que ainda está na origin já sai pelas `pontas` (o `remoto_exato --pontas` lê `refs/tags/*`). Então a exclusão só muda o resultado para a tag que a origin não tem: a `arquivo/*` apagada lá (o caso do cartão) ou a criada só no clone (trabalho perdido). Estreitar para `refs/tags/arquivo/*` resolve o caso medido (as 9 tags do `v0481-d2-resto-rev`) e mantém a garantia para o resto.

**A catraca pede o rótulo?** Não. `tests/catraca.py --modo regras --base origin/develop --head HEAD` local sai com rc 0 e sem violação: o teste foi renomeado e não removido (a contagem de `test_*` sobe 2), as asserções crescem, e `bin/forge-fechar` e `docs/fechamento-integrador.md` não estão em `invariantes` nem nos protegidos. O afrouxamento passa pela catraca sem sinal. Se o dono quiser a exclusão ampla, a decisão é dele (`R-DECISAO`), com o destaque `afrouxa-regra` no título, e o M18 fica aposentado de forma explícita.

**O que está certo:** a segunda parte, `$merged_heads` no `rev-list --stdin` (linha 696), está correta e não afrouxa nada. O commit que vale como mesclado é ancestral de um `headRefOid` de PR MERGED que esta cópia já buscou. O commit feito depois do head fica pendente, como prova `test_commit_do_clone_depois_do_head_mesclado_fica`. O stash continua na conta (`--exclude` antes de `--all` não toca `refs/stash`). A doc do passo 7 e o fragmento do changelog acompanham a mudança. O commit é único e a mensagem está em Conventional Commits.

**Verificadores:**
- `bin/forge-mutante tests/mutantes/v0481-limpar-clone-parecer.json`: rc 0, M1 morreu (`bin/forge-fechar:692`), M2 morreu (`:696`).
- `bin/forge-mutante --conferir --todas`: rc 1 com 25 linhas no head e 24 na base 8833d0f6. A diferença é só o M18 do A2; as outras 24 já falhavam na base e não são deste diff.
- Testes do item, `python3 -m unittest tests.test_fechar_limpar_clone tests.test_forge_fechar.LimparClones` em ambiente limpo: 28 testes, OK.
- Suíte inteira: só no CI. No momento da leitura, o #890 (rascunho) tinha o `catraca` pendente e nenhum resultado da bateria. O `shellcheck` não está instalado nesta máquina; fica com o CI.

**Volta (autor):**
1. A1: linha 692 com `--exclude='refs/tags/arquivo/*'`, o comentário da 691 e o passo 7 da doc alinhados.
2. Restaurar `test_commit_so_em_tag_local_fica` (tag `t-local` fica) e manter o teste novo com `arquivo/t-local` (sai).
3. M1 da spec nova com o trecho estreito.
4. A2: M18 da `v0474-mp6-disco-3.json` com o `de` novo e o teste certo.
