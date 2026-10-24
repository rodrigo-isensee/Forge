---
tipo: review
contrato: 1
pedido: changelog-json-link
branch: melhoria/changelog-json-link
commit: 0eddfc2bb80b0d4d9a8fff045abe65ac6afcf81c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: changelog-json-link

Pedido CHANGELOG-JSON-LINK-REV, E1.1. Diff `d150ec8...705d5a9`, 4 commits (`80cf5bf` A1, `1acc698` A2, `e1ba013` fragmento, `705d5a9` teste), 3 arquivos: `bin/forge-changelog`, `tests/test_changelog.py`, `changelog.d/changelog-json-link.md`. Fecha A1 e A2 de `docs/security/release-dev-versao.md`.

## Achados
- A1 (recomendado) tests/test_changelog.py:220 · o teste "fora da raiz" do CHANGELOG.md usa link simbólico e cai no ramo is_symlink de conferir_caminho; a asserção casa pela mensagem comum. Sem link, o CHANGELOG.md da raiz não sai dela. Sugestão: registrar isso num comentário do teste; o código está certo.

## Parecer
**Aprovado.** Faz o que E1 e E2 pedem, sem mais nem menos.

- **A1, troca conferida por json antes de gravar** (`bin/forge-changelog:101-127`): `ler_manifestos(versao)` calcula o `novo_texto` de cada manifesto e o confere com `json.loads(..., object_pairs_hook=_recusa_chave_repetida)` e `["version"] == versao`, tudo antes da primeira escrita. Em `release` (`:157`), a chamada vem antes do `write_text` do CHANGELOG.md (`:163`) e de `gravar_versao` (`:164`). Por isso, quando o segundo manifesto (dev) falha, nada fica gravado pela metade. Os três testes de A1 usam `_dev_com` (o segundo manifesto é o inválido), e `_nada_gravado` confere que o CHANGELOG.md, o manifesto raiz e o fragmento ficam intactos. Casos: chave aninhada (`:181`), repetida (`:187`) e aspa escapada (`:193`). O ramo `isinstance(dados, dict)` de antes continua valendo. Depois da troca, o topo segue objeto, já que o `{` inicial não muda, e `conferido.get` não quebra.
- **A2, CHANGELOG.md com a mesma checagem dos manifestos** (`:95-98`, `:142`): `conferir_caminho` é a mesma função dos manifestos e roda antes do `read_text`. Ela recusa o link simbólico, inclusive o quebrado (`is_symlink` antes de `resolve`), e o caminho que resolve fora da raiz. Testes: link simbólico (`:199`), link para fora (`:212`, ver A1) e link quebrado (`:226`, que também confere que o alvo não foi criado). Os manifestos que resolvem fora da raiz por diretório-link já tinham teste (`:171`).
- **Fragmento** (`changelog.d/changelog-json-link.md`): diz o mesmo que o código (chave aninhada, repetida ou aspa escapada recusam sem gravar; CHANGELOG.md link ou fora da raiz recusado). O tipo `Corrigido` está certo.
- **Legibilidade:** a extração de `conferir_caminho` tira a duplicação entre os manifestos e o CHANGELOG.md. `gravar_versao` ficou só com a escrita. As docstrings foram atualizadas.
- **Commits:** um por item, cada um com o seu teste, em Conventional Commits em português.
- **Regras:** `R-NEUTRO` e `R-CUSTO` sem impacto. Nenhum invariante tocado (`tests/config.json` fora do diff).
- **Segurança:** o parecer é do `security-engineer` (E2.1) e não é refeito aqui.

## Evidência
- `python3 -m unittest tests.test_changelog -v` no head `705d5a9`: `Ran 41 tests`, `OK (skipped=1)`. O teste pulado é `test_fragmentos_novos_desta_branch_tem_o_nome_dela`, porque a worktree está destacada (`HEAD`), não numa `melhoria/*`.
- Sonda em `$TMPDIR` com chave `version` aninhada no manifesto **raiz** e o dev válido: rc=1, "a troca textual não acertou o 'version' de topo", e os dois manifestos, o CHANGELOG.md e o fragmento ficaram intactos.
- Sonda com `"version" :  "0.1.0"` (espaços) e um valor com `\"version\": \"1\"` escapado em outra chave: rc=0, só a `version` de topo trocada nos dois manifestos.
- Achados recorrentes (PA-7): a lista está vazia, sem item a conferir.

## Revalidação (volta 2)
Delta lido: `705d5a9..0eddfc2`, só `tests/test_changelog.py` (+8 linhas, commit `3f3b7de`); os pareceres de QA e segurança não são código. Já lido: o restante da branch, no parecer acima, sem mudança.
- Teste novo da `version` repetida com a versão nova no último valor (`:193`): usa `_dev_com` e `_nada_gravado`, e confere o manifesto intacto. Sem o gancho de chave repetida o último valor passaria; o teste cobre o mutante M1 do QA. Correto.
- Comentário do ramo `is_symlink` (`:220`): atende ao A1 recomendado, que fica resolvido.
- `python3 -m unittest tests.test_changelog` no head `0eddfc2`: `Ran 42 tests`, `OK (skipped=1)` (o pulado é o da branch `melhoria/*`, pela worktree destacada).
- Sem achado novo. Parecer segue **aprovado**.
