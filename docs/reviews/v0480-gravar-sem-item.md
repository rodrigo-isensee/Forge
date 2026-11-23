---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-gravar-sem-item
commit: e77e13e88b11df8c820004ec37392296ee174708
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 · G1.2a corte (a), gravar sem o alvo item: (E90.26)

Revisão completa única do head e77e13e8 (um commit sobre a base fc488261), contra o código já aprovado na `melhoria/v0479-sieg-g1-gravar` (head d4960f8e, pareceres de review, QA e segurança aprovados por delta).

## Conferência contra o revisado
`git diff d4960f8e e77e13e8 -- bin/` só remove: saem `ponta_do_ramo`, `commit_do_ramo`, a opção `--ramo` (bin/forge-check:10590) e o ramo `item:` de `concessao_lida`. `fora_do_revisado` volta ao texto da `develop` (a leitura da ponta inline em bin/forge_autorizacao.py:193, idêntica à base), por isso a spec `tests/mutantes/v0479-pv-a2-concessao-3.json` fica igual à da base. Nenhuma linha de código nova além da troca `if any(achados)` por `if achados:` (bin/forge_autorizacao.py:381), coerente com a lista que `problemas` devolve.

O alvo `item:` recusa sem caminho novo: sem `Commit`, o `do_item` (bin/forge_autorizacao.py:171) devolve "Commit não é sha de 40 caracteres" e `concessao_lida` levanta a Recusa antes de qualquer escrita (falha fechada). O comentário da linha 380 diz isso.

## O que é novo
- Teste do ramo de recusa: `EscopoPeloTextoTodo.test_o_que_o_leitor_recusaria_nao_e_gravado_alvo_item_nesta_etapa` (tests/test_autorizacao_gravar.py:339) grava com `alvos="item:PV-A2"` e confere rc, nada gravado e a mensagem do `do_item`. É de comportamento, não lê a fonte.
- Redeclaração da guarda `if achados:` em `tests/mutantes/v0479-sieg-g1-gravar-4.json`: o `de` inclui a linha do `raise Recusa("; ".join(achados))`, único no arquivo (a outra `if achados:`, linha 235, não casa), e aponta o teste novo. Morreu.
- Specs mantidas: em `v0479-sieg-g1-gravar-3.json` e `-6.json` saíram só as guardas do `commit_do_ramo` e do `item:` (com a isenção do `git show`, que perdeu o trecho); as que ficam mutam código presente e morreram. Em `-5.json` saiu só o teste apagado da lista; em `-4.json`, a guarda da ref local de `fora_do_revisado` perdeu a nota "linha movida" e segue no lugar.
- Classe `ConcessaoSolta` apagada inteira: ela testava o `item:` gravado, que sai deste corte; o PV-A2 do leitor segue em `tests/test_autorizacao.py` (`ItemPresoAoCommit`), intocado.
- ADR 0018 (docs/adr/0018-autorizacao-do-dono-gravada.md:44 e 61): o G1.2a cita E90.25, tira o `--ramo`, diz que o `item:` recusa nesta etapa e manda `--ramo`, `Commit` do parecer e `fora_do_revisado` para o G1.2b. Fragmento `changelog.d/v0480-gravar-sem-item.md` troca a concessão solta do `item:` por "fica para o G1.2b e, até lá, recusa"; o fragmento da branch antiga não vem junto. Os dois batem com o código.
- Fora do diff do revisado, vindo da base: `bin/forge-testes` põe `test_autorizacao_gravar` no grupo do forge-check, `tests/pesos-d4.json` ganha o peso, `docs/indice-forge.md` marca o G1.2, e a spec `v047-sieg-g1-autorizacao-6.json` alonga o `de` da hora da leitura para ficar único (a linha `agora or datetime.datetime.now(UTC)` passou a aparecer também em `cmd_gravar`).

## Verificação
- Testes dos arquivos tocados: `tests.test_autorizacao_gravar` e `tests.test_autorizacao`, 45 testes, verdes no head e77e13e8 com o `TMPDIR` da sessão. Suíte inteira: CI do PR (sem PR aberto; nada a citar).
- `bin/forge-mutante --processos 1` nas specs `v0479-sieg-g1-gravar-3.json`, `-4.json`, `-5.json` e `-6.json`: 24 mutantes, todos morreram (3 por erro sob o mutante, como já era).
- `bin/forge-mutante --conferir --base fc488261`: o trecho de cada spec do diff está no lugar. `--cobertura --base fc488261`: as guardas do diff (bin/forge_autorizacao.py:381, 383, 384, 393, 394, 401, 412) cobertas; só `tests/pesos-d4.json` sai como não coberto, e não tem guarda.
- Tamanho (H1): `git diff --numstat fc488261` em `bin/`: 142 linhas acrescentadas e 7 removidas (149), um comportamento só; dentro do teto de 150.
- Commit único em Conventional Commits, com a etapa e o corte no corpo.

## Achados
- A1 (recomendado) tests/test_autorizacao_gravar.py:99 · O GIT_CEILING_DIRECTORIES do teste não isola o subprocesso: o forge-check resolve a cópia principal com o git sem GIT_*. Com o TMPDIR dentro de um repo, os testes do forge-check gravam no .forge/autorizacoes desse repo (reproduzido) e falham por M- repetido.

## Parecer
Aprovado no head e77e13e8. O código é o já revisado menos o alvo `item:`: só remoção, mais o `if achados:`. O `item:` recusa por falha fechada antes de escrever, com teste do ramo de falha e a guarda redeclarada, que morre. As specs mantidas estão no lugar e morrem. ADR 0018 e fragmento descrevem o corte. A1 é recomendado: vem do código já aprovado e só acontece quando o diretório temporário fica dentro de um repositório git. Reproduzi com `TMPDIR` num `git init` descartável: a concessão e o marcador `M-` foram parar no `.forge/autorizacoes` desse repo, não na raiz do teste. Sugestão: o teste roda o forge-check com `--raiz` num diretório fora de qualquer repo, ou o gravar recusa raiz principal diferente da dada. Vira cartão depois do merge.
