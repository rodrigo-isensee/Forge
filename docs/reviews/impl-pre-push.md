---
tipo: review
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c5
commit: 7cb63e2fe16ff8b45e2c4181007274aafa05a415
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-pre-push, branch c5 (namespace no texto da trava), revalidação da volta 1

Diff da branch: `234dbe0..7404c26` (`8c7d7e9` namespace no texto, C5; `81f0400` C-14; `31d4cf6` fragmento; `1972519` parecer anterior; `7404c26` revert do `81f0400`).

## Delta lido (volta 1)
`forge-check delta --parecer docs/reviews/impl-pre-push.md`: intervalo `31d4cf6..7404c26`; `.githooks/pre-push` +2 -6 (`:40`, `:98`, `:218`) e `tests/test_pre_push_trava.py` +0 -17 (`:493`). Lido: o `7404c26` é o revert exato do `81f0400` (some `texto_da_trava`, as duas chamadas voltam a `cat "$trava"` e some o teste do C-14). O C-14 foi para a c6, com review próprio.

Já lido na rodada anterior (não relido): `8c7d7e9` (namespace em `.githooks/pre-push:241-244`, teste em `tests/test_pre_push_trava.py:260`), correto.

## O que entrega
E4 do pedido (C5 do desenho, C-16 do modelo): a trava grava `pid N ns <inode> desde HH:MM:SS`, mantendo `pid N` nos dois primeiros campos.

## M14 (agents/tech-lead.md:19)
- Linhas contadas (`git diff --numstat --no-renames 234dbe0 7404c26`, sem parecer e fragmento): `.githooks/pre-push` 5, `tests/test_pre_push_trava.py` 11; total 16, abaixo de 150.
- Comportamentos: um (namespace no texto gravado). A1 da rodada anterior resolvido. Cumpre.

## Regras de ferramenta
- Suíte: o `origin` tem o head revisado (`git ls-remote`: `7404c26`), então o pre-push rodou no envio do autor; o CI do PR repete.
- shellcheck: ausente nesta máquina; fica para o CI. Pendência, não review manual.
- Mutação: sem `tests/mutantes/impl-pre-push*.json`. Pendência V2 do autor.

## Delta lido (volta 2)
`forge-check delta --parecer docs/reviews/impl-pre-push.md`: intervalo `7404c26..7cb63e2`; só `changelog.d/impl-pre-push-c5.md:2` (+1 -1). Lido: o fragmento agora diz só "o texto da trava traz o namespace depois do pid", sem o C-14. Já lido (não relido): `8c7d7e9`, `7404c26`, `.githooks/pre-push` e `tests/test_pre_push_trava.py`.

## M14 (agents/tech-lead.md:19)
Cumpre: 16 linhas de código e teste (5 em `.githooks/pre-push`, 11 em `tests/test_pre_push_trava.py`), um comportamento.

## Regras de ferramenta
Sem mudança de código no delta: suíte pelo pre-push do autor e CI do PR; shellcheck ausente nesta máquina (CI); mutação sem spec (pendência V2 do autor).

## Achados
- A1 (recomendado) changelog.d/impl-pre-push-c5.md:2 · A1 da volta 1 resolvido: o fragmento descreve só o namespace.

## Parecer
Aprovado. O código estava certo desde a volta 1 e o fragmento agora bate com ele.
