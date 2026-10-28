---
tipo: review
contrato: 1
pedido: catraca-pr-mesclado
branch: melhoria/catraca-pr-mesclado
commit: 676dd62a3ae429574c961e3eebf0fb3a1b64ebc8
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: conferência do PR mesclado da catraca com o head no merge de teste (CATRACA-PR-MESCLADO)

Escopo: `git diff e833d3c...676dd62` (`tests/catraca.py`, `tests/test_catraca.py`, `changelog.d/catraca-pr-mesclado.md`), commits 19f3118 (correção), fb4270a (motivo) e 676dd62 (fragmento). Revisor diferente do autor (`R-REVIEW`). Parecer: **aprovado**, sem bloqueantes; duas recomendações.

## Achados
- A1 (recomendado) tests/catraca.py:1021 · "nenhum commit cita um PR" também sai quando o `git log` de `candidatos_mesclados` falha (devolve vazio); distinguir a falha do git do intervalo sem `#n` deixaria o motivo exato
- A2 (recomendado) tests/catraca.py:997 · ramo só alcançado sem base/head (nenhum chamador de produção): o motivo "não é ancestral" também cobre o S ausente no git local; texto pode dizer "ausente ou não ancestral"

## Causa provada
No CI (`.github/workflows/catraca.yml`) o checkout é o merge de teste do PR e `BASE=$(git rev-parse HEAD^1)`; o `--head` fica no padrão (HEAD). Então `git rev-list --first-parent base..head` devolve só o próprio merge de teste: o primeiro pai dele é a base, excluída. O merge M (squash) de cada PR da develop nunca estava nessa cadeia, e `prova_do_squash` voltava falso calada, pedindo o rótulo de novo no #310 e no #317. A causa bate com o código e com o teste novo.

## Correção (`ponta_promovida`)
- Devolve o segundo pai só quando o head tem exatamente dois pais e o primeiro é, sha por sha, a base resolvida (`rev-parse --verify`); qualquer falha do git ou outra forma devolve o próprio head (comportamento anterior). No CI a condição sempre vale, porque a base é definida como `HEAD^1`.
- Contenção: a ponta é pai do head, logo `base..ponta` está contido em `base..head`; a cadeia de primeiro pai de `base..ponta` é a cadeia de primeiro pai da develop, que é exatamente o que a regra (b8, #250) pretendia exigir. Os demais filtros não mudaram: M segue tendo de ser o `merge_commit_sha` da API dentro de `base..head` (intervalo de `candidatos_mesclados`), com um pai só, PR do próprio repositório para a `develop`, rótulo `labeled` pelo dono sem app, S ancestral do `head.sha` trazido de `refs/pull/<n>/head`, e blob e modo iguais ao do head rotulado com a mesma violação. Nada passa além do que a regra já liberava.
- Fora do CI (head com dois pais e o primeiro igual à base por coincidência, por exemplo a develop mesclando a homolog com a homolog em primeiro pai) a ponta também é o segundo pai; os commits continuam dentro de `base..head` e a API continua sendo a fonte do M. Não abre caminho novo.

## Motivo impresso (`motivos`, `sem`)
- `motivos` é opcional em `prova_do_squash`, `sha_rotulado_do_mesclado` e `liberado_por_pr_mesclado`; cada `return None/False` ganhou o texto, sem mudar o valor devolvido (conferido linha a linha no diff). Por PR candidato a lista é própria (`do_pr`) e entra como `#n: ...`.
- A troca da ordem de `None in arquivos` com `eh_promocao` não muda o resultado (None nos dois casos); só faz o motivo sair apenas em promoção. Fora da promoção nada é impresso (teste `test_fora_da_promocao_nao_fala_da_conferencia`).
- `liberado_por_pr_mesclado_ou_none` imprime uma linha só, pelo `aviso` existente ("vale como sem rótulo"), e só quando não liberou e há motivo. O texto traz número do PR, prefixo de sha, nome de ramo e de arquivo já listados como violação e o tipo da exceção; nada de token nem corpo da API.
- `except ... as e` passa a nomear o tipo: segue falhando fechado.

## Testes
- `test_promocoes_310_e_317_com_head_no_merge_de_teste_passam`: dois PRs (10 e 11) rotulados e mesclados por squash, cada um com um arquivo protegido, head no merge de teste construído com `commit-tree -p homolog -p develop`; espera rc 0 e "#11, #10". Guarda do b8: `test_merge_de_teste_com_merge_fora_da_cadeia_de_primeiro_pai_da_develop_pede` (o merge de teste não afrouxa o b8).
- Motivos: subtests para rótulo de intrusa, PR não mesclado, sem execuções; arquivo mudado depois do merge (pendente só `tests/catraca.py`); M fora da cadeia; sem `#n`; violação sem arquivo.
- Vermelho antes, verde depois (cópia em `$TMPDIR` com o `tests/catraca.py` de e833d3c e os testes do head): `Ran 27 tests ... FAILED (failures=7)`, entre eles `test_promocoes_310_e_317_com_head_no_merge_de_teste_passam`; no head, `python3 -m unittest tests.test_catraca.RotuloDePrSquash`: `Ran 27 tests in 13.683s` `OK`; módulo inteiro `tests.test_catraca`: `Ran 261 tests in 42.762s` `OK`. O pre-push da entrega (1936 OK) consta no pedido; a suíte completa não foi refeita aqui.

## Teto (decisão M14)
`git diff --numstat --no-renames origin/develop...HEAD`: `tests/catraca.py` 67+28, `tests/test_catraca.py` 77+1 = 173 linhas, abaixo de 400. O PR mexe em caminho de `PROTEGIDOS` (`tests/catraca.py`), então a exceção de teto não valeria; não é necessária. Nada em `hooks/`.

## Regras e checklist
- Faz o que o pedido pede (E1: diagnóstico, correção dentro da regra, motivo, teste das duas promoções), sem extras. `tests/config.json` intocado; invariantes preservados; sem custo (`R-CUSTO`), sem termo de projeto (`R-NEUTRO`), sem dependência nova. Fragmento novo em `changelog.d/`; `CHANGELOG.md` intocado (ADR 0006).
- `docs/engineering/praticas.md` não existe no Forge: nenhuma regra "leitura" ou "ferramenta" alcança o diff além do checklist da skill. `docs/engineering/achados-recorrentes.md` (PA-7) sem itens: nada a conferir.
- Commits em Conventional Commits em português, um por mudança coerente.
- Segurança (controle do Forge: a catraca) fica com o parecer do `security-engineer` (`docs/security/`); não refeito aqui. Nenhum achado de segurança visto.
