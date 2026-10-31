---
tipo: review
contrato: 1
pedido: impl-pre-push
branch: melhoria/impl-pre-push-c5
commit: 31d4cf6704a0743aeb555cb96e2a7a359c72a8f0
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-31
---
# Review: impl-pre-push, branch c5 (namespace e texto da trava)

Diff lido: `234dbe0..31d4cf6` (3 commits: `8c7d7e9` namespace no texto, C5; `81f0400` texto limitado e imprimível, C-14; `31d4cf6` fragmento).

## O que entrega
Dois itens do pedido:
- E4 (C5 do desenho, C-16 do modelo): a trava grava `pid N ns <inode> desde HH:MM:SS` (`.githooks/pre-push:248`), mantendo `pid N` nos dois primeiros campos; `ns` sai `?` se a leitura falhar. Teste `test_texto_da_trava_traz_o_namespace_depois_do_pid` (`tests/test_pre_push_trava.py:260`).
- Parte do E3 (C-14 do modelo, T-C4h): `texto_da_trava` (`:42`) corta em 200 bytes e tira o que não é imprimível, no `--status` e no aviso de espera. Teste `test_texto_da_trava_sai_limitado_e_sem_controle` (`:494`).

O código dos dois está correto na leitura: `readlink` roda no mesmo namespace do hook; `LC_ALL=C tr -cd '[:print:]'` tira escape, BEL e bytes não ASCII; o limite cabe mesmo com a linha da dica da c3 (cerca de 305 caracteres para o teto de 320 do teste).

## M14 (decisão M14, agents/tech-lead.md:19)
- Linhas contadas (`git diff --numstat --no-renames 234dbe0 31d4cf6`): `.githooks/pre-push` 13, `tests/test_pre_push_trava.py` 28; total 41, abaixo de 150.
- Comportamentos: dois. O namespace muda o que o hook grava na trava (E4, C5); o C-14 é um controle de segurança sobre o que o hook exibe do texto lido (E3, C-14), com cartão, commit, teste e motivo próprios. O próprio commit `81f0400` diz que veio aqui por caber no teto, não por ser o mesmo comportamento. O modelo previa o C-14 no C4 ou num C6 próprio. Não cumpre.

## Regras de ferramenta
- Suíte: branch no `origin` com o head revisado; o pre-push rodou a suíte inteira no envio do autor. O CI do PR repete.
- shellcheck: ausente nesta máquina; fica para o CI. Pendência, não review manual.
- Mutação: sem `tests/mutantes/impl-pre-push*.json`. Pendência V2 do autor.

## Leitura
- R-NEUTRO, R-CUSTO e invariantes preservados. Compatibilidade com `scripts/suite-paralela.py:510-511` mantida pela ordem dos campos (C-16).
- Gatilho R-SEGURANCA no C-14: parecer do `security-engineer` (E1.3), não refeito aqui.

## Achados
- A1 (bloqueante) .githooks/pre-push:42 · Dois comportamentos num PR (M14): o C-14 (texto exibido limitado e imprimível, E3) e o namespace no texto gravado (C5, E4). Separar o `81f0400` e seu teste numa branch própria (c6, a partir da 234dbe0); a c5 fica só com `8c7d7e9` e o fragmento.
- A2 (recomendado) .githooks/pre-push:248 · Na volta, o PR do C-14 precisa entrar na develop antes ou junto da c4 (trava comum), senão o texto gravado no sandbox chega ao terminal de fora sem filtro.

## Parecer
Reprovado só pela M14 (A1): o código dos dois itens está certo e não precisa de mudança, só de divisão em duas branches, cada uma com o seu fragmento. Na revalidação, o delta esperado é a remoção do `81f0400` e do teste `:494` desta branch; a branch nova do C-14 recebe review próprio.
