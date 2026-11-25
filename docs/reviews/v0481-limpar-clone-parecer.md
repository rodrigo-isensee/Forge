---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-limpar-clone-parecer
commit: 86f50b244f7b814d8733a656aae8c1d9111c1df5
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481 (E14.11, #890, revalidação por delta da volta E14.10)

Delta lido: `fe1f2275..86f50b24`, o commit E14.10 (código, doc, changelog, testes e specs; os pareceres de QA, segurança e review que vieram no meio não entram na leitura). Código: `bin/forge-fechar:651` e `:691-693` (3 linhas, dentro do H1). Clone de revisão: `/root/.forge-contrib/wt/v0481-limpar-clone-parecer-rev`, no head `86f50b24`.

## Delta contra o parecer anterior (fe1f2275, reprovado)
- A1 (bloqueante) resolvido: `bin/forge-fechar:693` passou a `--exclude='refs/tags/arquivo/*'`. O comentário das linhas 691-692, o da 651, o passo 7 de `docs/fechamento-integrador.md` e o fragmento do changelog dizem a mesma coisa: só a `arquivo/*` sai da conta, e outra tag local prende o clone.
- A2 (bloqueante) resolvido: o M18 de `tests/mutantes/v0474-mp6-disco-3.json` tem o `de` novo (1 ocorrência no fonte) e aponta de novo para `test_commit_so_em_tag_local_fica`. Ele morre (`:693`). `forge-mutante --conferir --todas` dá a mesma saída no head e na base `8833d0f6` (`diff` vazio, 26 linhas, todas de specs de fora deste diff).
- A3 (recomendado) atendido: `test_commit_so_em_tag_local_fica` voltou idêntico ao da base (o `git diff 8833d0f6..86f50b24` desse teste é vazio), e `test_commit_so_em_tag_arquivo_nao_prende_o_clone` cobre o outro lado. O M1b (exclusão ampla) morre por esse teste, e com isso o afrouxamento do A1 fica coberto por mutante declarado.
- `tests/test_fechar_limpar_clone.py`: o `tag_com_ref_velha` e a docstring voltaram ao texto da base (tag `v9`, que sai pelas pontas). O diff contra a base fica só com os 2 testes do parecer mesclado.

## Sondas
- S1 · clone em melhoria/x, commit com arquivo novo só na tag leve `wip-meu`, `--limpar` · espera: rc=3, clone=pendente, clone existe (como na base) · obtido: rc=3, clone=pendente, clone existe
- S2 · igual à S1, com a tag `wip-meu` anotada · espera: fica · obtido: fica
- S3 · tag `arquivoX` (prefixo parecido sem a barra) · espera: fica · obtido: fica
- S4 · tag `meu/arquivo/x` (o `arquivo/` no meio do nome) · espera: fica · obtido: fica
- S5 · tag anotada `arquivo/a/b` (aninhada) · espera: rc=0, clone apagado · obtido: rc=0, clone apagado
- S6 · tag `arquivo/z` e um stash · espera: fica (o stash segue na conta) · obtido: fica

## Parecer
Aprovado.

As sondas estão em `sonda_v0481_rev2.py`, no scratchpad da sessão, e herdam o ambiente de `LimparClones`. Rodaram 6 testes, OK.

**Afrouxa regra?** Não, no escopo que o cartão pede. A garantia do MP6 para a tag local de qualquer outro nome voltou a ser a da base (S1 a S4, teste restaurado, M18 e M1b mortos). Só a `arquivo/*` sai da conta, e esse é o caso medido. Resta um caso de borda que o desenho aceita: um commit só numa tag `arquivo/*` criada à mão no clone, nunca enviada, seria apagado. O prefixo pertence ao fluxo de arquivamento da origin e não ao trabalho do clone, a doc diz isso no passo 7, e não vejo gatilho no fluxo que crie essa tag no clone. Por isso não é achado.

**Verificadores:**
- `bin/forge-mutante tests/mutantes/v0481-limpar-clone-parecer.json`: M1, M1b (`:693`) e M2 (`:697`) morreram. Em `v0474-mp6-disco-3.json`, o M18 (`:693`) morreu.
- `bin/forge-mutante --conferir --todas`: rc 1, saída idêntica à da base `8833d0f6`. O A2 saiu.
- Testes do item, `python3 -m unittest tests.test_fechar_limpar_clone tests.test_forge_fechar.LimparClones` em ambiente limpo: 29 testes, OK.
- `tests/catraca.py --modo regras --base 8833d0f6 --head HEAD`: rc 0, sem violação.
- Suíte inteira: só no CI. Na leitura, o #890 (rascunho, head `86f50b24`) tinha a `catraca` verde e a `bateria (passos)` verde. A suíte estava em andamento, e a `bateria (pareceres)` estava vermelha porque os pareceres do head ainda eram os reprovados de `fe1f2275`. O merge espera o CI verde no head com os três pareceres. O `shellcheck` fica com o CI.

**Commits:** um commit de volta, `fix(fechar): ...` em Conventional Commits, com a etapa na mensagem.
