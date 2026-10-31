---
tipo: review
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c5
commit: 7404c2673564e67949e8caf88aa2612d89530a05
parecer: reprovado
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

## Achados
- A1 (bloqueante) changelog.d/impl-pre-push-c5.md:2 · Com o revert, o fragmento descreve um comportamento que a c5 não tem mais (200 bytes e só imprimíveis, C-14, agora na c6 com fragmento próprio): a release publicaria o C-14 duas vezes. Deixar só o namespace depois do pid.

## Parecer
Reprovado só pelo A1, achado novo que nasce do delta (o revert tornou falso o fragmento já lido): o código está certo. Na revalidação, o delta esperado é só a linha 2 do fragmento.
