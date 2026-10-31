---
tipo: review
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c6
commit: 113635c491fb1b880b16cf9714ae8fb20b076166
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-pre-push, branch c6 (texto da trava limitado e imprimível)

Diff lido: `234dbe0..113635c` (`ee86b7f` C-14; `113635c` fragmento).

## O que entrega
Parte do E3 do pedido (TRAVA-SANDBOX, C-14 do modelo, T-C4h): `texto_da_trava` (`.githooks/pre-push:42`) lê no máximo 200 bytes da trava e tira o que não é imprimível (`LC_ALL=C tr -cd '[:print:]'`: escape, BEL e bytes não ASCII), usado no `--status` (`:102`) e no aviso de espera (`:222`). Teste `test_texto_da_trava_sai_limitado_e_sem_controle` (`tests/test_pre_push_trava.py:483`) grava escape, BEL e 1 MiB na trava e confere as duas saídas. É o mesmo código revisado na c5 (`81f0400`), agora sozinho, como pediu o A1 do parecer da c5.

## M14 (agents/tech-lead.md:19)
- Linhas contadas (`git diff --numstat --no-renames 234dbe0 113635c`, sem fragmento): `.githooks/pre-push` 8, `tests/test_pre_push_trava.py` 17; total 25, abaixo de 150.
- Comportamentos: um (o que o hook exibe do texto lido da trava). Cumpre.

## Regras de ferramenta
- Suíte: o `origin` tem o head revisado (`git ls-remote`: `113635c`), então o pre-push rodou no envio do autor; o CI do PR repete.
- shellcheck: ausente nesta máquina; fica para o CI. Pendência, não review manual.
- Mutação: sem `tests/mutantes/impl-pre-push*.json`. Pendência V2 do autor.

## Leitura
- R-NEUTRO, R-CUSTO e invariantes preservados; fragmento próprio em `changelog.d/impl-pre-push-c6.md`.
- Gatilho R-SEGURANCA (controle do Forge): parecer do `security-engineer` (E1.3), não refeito aqui.

## Achados
- A1 (recomendado) .githooks/pre-push:42 · Ordem de integração: esta branch entra na develop antes ou junto da c4 (trava comum), senão o texto gravado no sandbox chega ao terminal de fora sem filtro (A2 do parecer da c5, mantido aqui).

## Parecer
Aprovado.
