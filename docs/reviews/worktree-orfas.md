---
tipo: review
contrato: 1
pedido: worktree-orfas
branch: melhoria/worktree-orfas
commit: ecb20794664e3eedb0e4b61261ab1d55bad5d85d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-30
---
# Code review: a lista do prune vai só ao log do forge-fechar (WORKTREE-ORFAS, F1)

Escopo: pedido WORKTREE-ORFAS-REV, E1.1 (`R-REVIEW`). Rodada 3 (revalidação por delta do merge, abaixo; a rodada 2 também); o texto da rodada 1 segue valendo para o que não mudou. Li o diff inteiro, `git diff 31257c14c8d245d66e7806edb7cd65e22b3aeb04...398791ade119ef41e35c5b7d5b279190122a656e`: são 4 commits, de `13a8c35` a `398791a`, em 5 arquivos. O QA (E3.1) roda em paralelo, em `docs/qa/`, e não o refaço. O pedido não tem parecer de segurança: a decisão técnica de 2026-10-29 23:29 registra que não há gatilho, porque é só saída de terminal do script de fechamento.

## Achados
- A1 (recomendado) bin/forge-fechar:415 · com saída vazia do prune, o here-string entrega uma linha vazia e o log ganha um registro `[prune] ` sem texto; sugestão: `[ -z "$prune_saida" ] ||` antes do laço
- A2 (recomendado) tests/test_fechar_orfao.py:99 · o teste passa só `LANG` e herda `LC_ALL` do ambiente; com `LC_ALL=C` no executor, o falso já escreve `Removing` e o mutante M4 sobrevive (classe AR-4, teste herda o ambiente do CI); sugestão: passar também `LC_ALL="pt_BR.UTF-8"`

## Revalidação por delta (rodada 2, head `e590cc1`)
- **Delta lido:** `forge-check delta --parecer docs/reviews/worktree-orfas.md` listou o intervalo `398791a..e590cc1` com só `tests/mutantes/worktree-orfas.json:55-64` (+10) e `tests/test_fechar_orfao.py:110-123` (+14). O `049ab3d` é o parecer do QA, fora do meu escopo. Já lido na rodada 1 e sem mudança: `bin/forge-fechar`, `docs/fechamento-integrador.md`, o fragmento e os outros testes.
- **Teste novo (`test_worktree_ocupada_com_o_diretorio_presente_nao_roda_o_prune`):** com `wt_busy=persiste` o `worktree remove` falha e o diretório fica; com `prune_muitos=5` o falso teria o que podar. O teste exige código 3, nenhuma chamada `git worktree prune` (`marcas` é por prefixo, então pega também o `-v`), nenhum `prune tirou` na tela, nenhum `[prune]` no log, o diretório de pé, `limpeza: remota=ok worktree=pendente branch=pendente` e o `git worktree remove` entre os comandos pendentes. Prova a guarda `[ ! -d "$arvore" ]` (`bin/forge-fechar:412`), que era o A1 do QA (classe AR-1, lista de mutantes incompleta, e AR-2, ramo de guarda sem teste; só citadas, sem linha AR nova, pela decisão técnica de 2026-10-29 15:28, T1-CONF-ESCOPO-REV).
- **Vermelho com o mutante:** troquei a guarda por `if true` na worktree de review e o teste deu FAIL (`Lists differ: [24] != []`, o prune rodou); arquivo restaurado, `git status` limpo. Com o head, `python3 -m unittest tests.test_fechar_orfao` dá `Ran 18 tests … OK`.
- **Mutante Q1 na spec:** o `de` (`if [ ! -d "$arvore" ]`) aparece uma vez só no `bin/forge-fechar`, então a troca é inequívoca; aponta o teste novo. A mutação completa é do QA e não a refiz.
- **Teto M14:** `git diff --numstat --no-renames 31257c1...e590cc1` dá `bin/forge-fechar` 22+10 e `tests/test_fechar_orfao.py` 38+0, 70 linhas, abaixo de 150; a spec, os pareceres, o fragmento e o `.md` ficam fora. Um comportamento só.
- **Commit:** `e590cc1` em Conventional Commits, em português, só teste e spec.
- **Achados A1 e A2 da rodada 1:** não tratados no delta; seguem como recomendação, sem devolver.

## Revalidação por delta (rodada 3, head `ecb2079`)
- **O que é o delta:** `ecb2079` é merge de `origin/develop` (`3bd1d84`) sobre `167ec0d`, sem mudança própria do autor (DECISÃO TÉCNICA 2026-10-30 01:31, conflito de caminho com o #378 no passo 2b do `forge-fechar`). `forge-check delta --parecer docs/reviews/worktree-orfas.md` listou o intervalo `e590cc1..ecb2079` com 23 arquivos, todos vindos da `develop` (`bin/forge-check`, `scripts/promover-homolog.py`, `skills/esperar-estado/SKILL.md`, testes e pareceres dos pedidos PN3, PN5 e PN6), já revisados nos PRs deles; não os relio. Do delta, li só `docs/fechamento-integrador.md`, o arquivo que o F1 e o #378 tocam.
- **Trecho mesclado de `docs/fechamento-integrador.md`:** a linha 28 é a do #378 (segundo plano com log terminado em `rc=` e espera no mesmo turno, skill `esperar-estado`) e a linha 46 é a do F1 (`LC_ALL=C`, marca `[prune]`, só a contagem na tela, aviso quando o prune falha). As duas vêm intactas, em seções diferentes (corte do passo 7 e registro órfão), e não se contradizem: nenhuma fala da saída da outra. `git diff 167ec0d ecb2079 -- docs/fechamento-integrador.md` dá só a linha 28; `git diff 3bd1d84 ecb2079 -- docs/fechamento-integrador.md` dá só a linha 46.
- **Patch do F1 igual ao revisado:** `git diff 3bd1d84 ecb2079` e `git diff 31257c1 167ec0d`, comparados sem as linhas `index` e os cabeçalhos `@@`, são idênticos, e o `--numstat` bate arquivo a arquivo. Contra `origin/develop` (`bd8f2f1`, que contém o `3bd1d84`), `git diff --numstat --no-renames origin/develop...ecb2079` lista só os 7 arquivos do F1 (`bin/forge-fechar` 22+10, `tests/test_fechar_orfao.py` 38+0, a spec, o fragmento, os dois pareceres e o `.md`).
- **Ferramentas no head:** `python3 -m unittest tests.test_fechar_orfao` dá `Ran 18 tests … OK`; `shellcheck bin/forge-fechar` sai com rc 0.
- **Teto M14:** o mesmo da rodada 2, 70 linhas (22+10 e 38+0), abaixo de 150; um comportamento só.
- **Já lido, sem mudança:** `bin/forge-fechar`, `tests/test_fechar_orfao.py`, `tests/mutantes/worktree-orfas.json`, `changelog.d/worktree-orfas.md` e a linha 46 do `.md`.
- **Classe:** nenhuma classe de achado nova nesta rodada; sem linha AR nova (DECISÃO TÉCNICA 2026-10-29 15:28, T1-CONF-ESCOPO-REV). A1 e A2 seguem recomendação.

## Parecer
**Aprovado** no head `ecb2079` (rodada 3; na rodada 2, no `e590cc1`; na rodada 1, no `398791a`). A entrega faz o que o E1 e o E2 pedem: a lista do `git worktree prune -v` deixa de ir para a tela, e a linha `limpeza: …` continua sendo a última do passo 7. Os dois achados são recomendações e não devolvem a entrega.

- **A1:** o problema é só cosmético no log. A contagem não muda, porque `grep -c` sobre o texto vazio dá 0, e a tela também não muda.
- **A2:** nos executores do GitHub o `LC_ALL` vem vazio, então hoje o M4 morre. É a classe AR-4 (`teste herda o ambiente do CI`). Pela decisão técnica de 2026-10-29 15:28 (T1-CONF-ESCOPO-REV), nesta rodada fica só a citação da classe, sem linha AR nova nem contagem nova.

## Conferência por item do Entregar
- **Passo 7, comportamento da limpeza:**
  - A ordem não mudou: worktree, depois a branch local e por último a remota.
  - A conferência do sha (`sha_confere` antes do `worktree remove`) e o "nunca força" ficam intactos.
  - O prune continua rodando só quando o `worktree remove` falha e o diretório já não existe (`[ ! -d "$arvore" ]`, `bin/forge-fechar:412`).
  - O `prune_rc` não entra no `arv_st` nem na `pendencia`. O estado continua vindo do `git worktree list --porcelain`, como antes com o `|| true`, então os códigos de saída são os mesmos.
  - Os testes do registro órfão confirmam isso: o `prune_nega` sai com código 3 e mantém a branch pendente.
- **Linha `limpeza:` como última do passo:** o teste novo exige que, depois de `limpeza: remota=ok worktree=ok branch=ok`, venham só `Entrega p1 fechada em develop.` e `fim: código 0`. A linha `registro: prune tirou 301 …` aparece antes dela.
- **Contagem com LC_ALL=C:** o prune roda como `LC_ALL=C git worktree prune -v 2>&1` (`:414`), e a contagem é `grep -c '^Removing '` (`:416`). O falso de `git` traduz para `Removendo` fora do `LC_ALL=C` e o teste roda com `LANG=pt_BR.UTF-8`, então a guarda é provada (ressalva no A2). O falso confere o argumento exato `worktree prune` (checklist 12).
- **Aviso só quando o prune falha:** `[ "$prune_rc" = 0 ] || echo "aviso: …" >&2` (`:417`), conforme a DECISÃO TÉCNICA de 2026-10-30 00:15. No sucesso, a tela mostra só a contagem. O teste do `prune_nega` exige o aviso com `código 1` e exige que o `cannot prune` não apareça na tela.
- **`gravar_linha`:** é a extração da escrita no log que o `registrar` já fazia, com a mesma máscara (`mascarar`), o mesmo `flock` e o mesmo formato de data. O `registrar` passa a chamá-la sem mudar o comportamento. O `$log` está sempre definido antes do passo 7 (`:193`).
- **`docs/fechamento-integrador.md:46`:** o texto bate com o código: `LC_ALL=C`, a marca `[prune]`, a lista fora da tela, a mensagem da contagem e o aviso com o código e o caminho do log. O cabeçalho do script (`:32`) também foi atualizado. Não sobrou outro texto que diga que a lista do prune vai para a tela (procurei `prune -v` nos `.md`; os pareceres antigos descrevem o comportamento da época deles).
- **Teste novo, vermelho antes do verde:** troquei o `bin/forge-fechar` da base `31257c1` na worktree de review e rodei `test_prune_com_centenas_de_orfas_conta_na_tela_e_a_lista_fica_so_no_log`. Deu FAIL (`'orfa-' unexpectedly found`), e o arquivo foi restaurado em seguida. Com o head, `python3 -m unittest tests.test_fechar_orfao` dá `Ran 17 tests … OK`. O `shellcheck bin/forge-fechar` sai com rc 0.
- **Spec de mutantes:** `tests/mutantes/worktree-orfas.json` tem 5 mutantes (M1 a M5), um por guarda nova, cada um com o teste que o mata. Quem roda a mutação é o QA, e eu não a refiz.
- **Teto M14:** pelo `git diff --numstat --no-renames 31257c1...398791a`, contam `bin/forge-fechar` (22+10) e `tests/test_fechar_orfao.py` (24+0), num total de 56 linhas, abaixo de 150. A spec, o fragmento e o `.md` ficam fora da conta. O diff não toca `hooks/` nem caminho de `PROTEGIDOS`. A entrega traz um comportamento só.
- **Fragmento:** `changelog.d/worktree-orfas.md` está em `### Corrigido`, e a entrega não edita o `CHANGELOG.md`.
- **Regras:** `R-NEUTRO` sem termo de projeto e `R-CUSTO` sem nada pago. Nenhuma regra com ID e nenhum item de `invariantes` foi tocado.
- **Commits:** são 4 em Conventional Commits, em português. O E1 saiu em dois commits (`13a8c35` com o código e `398791a` com a documentação), e a divisão foi aceita pela DECISÃO TÉCNICA de 2026-10-30 00:15, porque juntá-los pediria `--force` (`R-VERIFY`).
- **`docs/engineering/praticas.md`:** o repositório do Forge não tem esse arquivo, então não há regra "decidida por" a citar. As ferramentas que valem para o diff são o `shellcheck` e a suíte do item, citadas acima.
