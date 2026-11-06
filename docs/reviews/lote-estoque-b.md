---
tipo: review
contrato: 1
pedido: versao-034
branch: melhoria/lote-estoque-b
commit: 84472bfa6c63406c46a6c86ce6353939a39a53dc
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-06
---
# Review: versao-034 (E2.2, junção do lote B)

Escopo: a junção `d9b26bb..84472bf` na primeira linha de pais: 7 merges `--no-ff` e o commit 84472bf (changelog). Cada item já tem review e QA aprovados no próprio parecer; aqui não se revê o item, só a resolução de conflitos, o commit fora de merge e o que a soma traz para a develop (sobreposição, duplicação, contradição).

## Itens
`git show --remerge-diff` de cada merge veio vazio: nenhum merge teve conflito nem resolução manual.

| Ordem | Merge | Item (head) | Entrou | Conflito | O que trouxe |
|---|---|---|---|---|---|
| 1 | 4ae41ca | catraca-ramo-cmd-pr (e736881) | sim | não | `tests/catraca.py` passa a branch ao `cmd_pr` (E11); testes E11 alinhados à mensagem da develop |
| 2 | f3810c2 | catraca-fork (934947d) | sim | não | `violacao_de_fork` em `tests/catraca.py`; `HEAD_REPO`/`BASE_REPO` no passo da catraca do `ci.yml` |
| 3 | f1ea0ca | ci-comentario-rapida (687f1aa) | sim | não | comentário do topo do `ci.yml` e teste em `tests/test_ci_local.py` |
| 4 | 7e250b5 | ci-env-argv0-v2 (1767534) | sim | não | passo do env com `-a` (uutils) nos jobs de bateria do `ci.yml` |
| 5 | 5d63b29 | ci-ubuntu-26 (094d0a1) | sim | não | runners `ubuntu-26.04` em `ci.yml`, `catraca.yml`, `release.yml` |
| 6 | 04e1304 | release-pr-so-parecer (27f7fff) | sim | não | `e_parecer` e atalho de PR só de parecer em `bin/forge-changelog` |
| 7 | 7ee4a7b | lote-cilista-v2 (0414ae4) | sim | não | lista fechada do que roda antes do actionlint/zizmor em `tests/test_ci_local.py` |

Nenhum item ficou fora.

## Os dois avisos da conferência de 17:31
- **Ordem dos merges (catraca-ramo antes de catraca-fork, inversa ao brief -12).** A branch catraca-fork foi criada sobre a catraca-ramo-cmd-pr: o merge-base das duas é 088a1e1, um commit da catraca-ramo, e a fork traz o c012446 e os pareceres dela. A catraca-ramo seguiu depois (586d77d junta a develop, e736881 alinha os testes E11). Na ordem do brief a fork entraria primeiro com a versão antiga da catraca-ramo e conflitaria em `cmd_pr` (Histórico, 14:56); na ordem da dependência os dois entram limpos. Conferi o resultado: `git diff 934947d 84472bf -- tests/catraca.py` é vazio e o de `tests/test_catraca.py` só traz o e736881; `git diff e736881 84472bf -- tests/catraca.py` é só o `violacao_de_fork` e o env. As duas mudanças estão inteiras, sem contradição. A chamada `fc.cmd_pr(..., base, ramo)` é posicional e casa com a assinatura da develop (`branch=None`, `bin/forge-check:896`). Aceito; o único defeito é de registro: a linha de 14:56 diz "na ordem do brief", e foi a ordem inversa (A1).
- **Consolidação do changelog (84472bf).** O commit é a volta do brief -16 (DECISÃO TÉCNICA de 14:56) e só mexe em `changelog.d/`: apaga os 7 fragmentos dos itens e cria `changelog.d/lote-estoque-b.md`. Conferi linha a linha: as 7 entradas estão no arquivo novo com o texto igual ao dos fragmentos, nas seções certas (5 em `### Corrigido`, 2 em `### Alterado`), sem título repetido. É o único fragmento novo da branch, o que o `tests.test_changelog` exige. Aceito como commit da junção; ele não é anexo solto, porque tem brief próprio.

## Sobreposição entre itens
- `ci.yml` é tocado por 4 itens (catraca-fork, ci-comentario-rapida, ci-env-argv0-v2, ci-ubuntu-26); os trechos são disjuntos (comentário do topo, `runs-on`, um passo novo, duas chaves de env) e o resultado tem cada um uma vez só. O passo do env com `-a` aparece em `testes` e em `bateria`, como no item aprovado; não é duplicação da junção.
- `tests/test_ci_local.py` (4 itens), `tests/test_catraca.py` e `tests/test_changelog.py`: sem classe nem método de teste com nome repetido no resultado (conferido por AST), então nenhum teste de um item apaga outro em silêncio.
- Os fragmentos de ci-comentario-rapida e ci-ubuntu-26 vinham também nas branches de ci-env-argv0-v2 (empilhadas); entraram uma vez só.

## Testes
- Módulos tocados pela junção: `python3 -m unittest tests.test_catraca tests.test_changelog tests.test_ci_local` em 84472bf: `Ran 388 tests in 91.816s`, `OK`. O `bin/forge-testes` com `.github/workflows/ci.yml` aponta a suíte completa (sem mapa) e com `--modulos` exige `--vermelho`, por isso o unittest direto.
- Suíte inteira (não rodada aqui, D-5): log do push de 84472bf, `/tmp/push-lote-b2.log`, `Ran 2632 tests in 1466.210s (2 processos)`, `OK (skipped=30)`, `push_rc=0`.
- Pareceres irmãos na mesma branch: devops (E2.4) e segurança (E2.3) aprovados sobre 84472bf; o A1 da segurança (rótulo do dono por release-pr-so-parecer) segue para a E2.6.

## Teto (M14)
O lote soma 536 linhas de código e teste (`git diff --numstat --no-renames d9b26bb 84472bf`) e toca `tests/catraca.py` (PROTEGIDOS), onde a linha de exceção não vale. Quem dá o PR único por lote é a DECISÃO DO DONO de 2026-11-05 14:37, com cada item no próprio teto e com os próprios pareceres. Não é achado da junção; o corpo do PR precisa citar a decisão (A2).

## Achados
- A1 (recomendado) docs/reviews/lote-estoque-b.md:31 · o Histórico do pedido (14:56) diz que os itens entraram na ordem do brief; foi catraca-ramo antes de catraca-fork, o inverso. Corrigir a linha no pedido.
- A2 (recomendado) docs/reviews/lote-estoque-b.md:45 · 536 linhas e PROTEGIDOS tocado: o corpo do PR do lote (E2.6) cita a decisão do dono de 2026-11-05 14:37 como base do PR único, para o review da M14 não ler falta de exceção.
- A3 (recomendado) changelog.d/lote-estoque-b.md:3 · a entrada da catraca-ramo cita a recusa como `sem parecer ... com branch:`, mas a mensagem é `sem parecer da branch <b> para o pedido` (bin/forge-check:919); ajustar o texto na release.

## Parecer
Aprovado. Os 7 itens entraram sem conflito; a ordem inversa da catraca é a ordem da dependência entre as branches e o resultado contém as duas mudanças inteiras; a consolidação do changelog preserva as 7 entradas. Os três achados são de registro e de texto e não devolvem a junção.
