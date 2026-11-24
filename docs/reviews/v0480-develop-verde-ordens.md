---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-develop-verde-ordens
commit: 6ce3a41a8ec8219ace8da853b0540eaaea47edd9
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E127.2, conserto da develop vermelha, PR #814)

Diff contra a base 0e59c446: `hooks/conformidade.py` (1 linha vira 2), `tests/mutantes/v0480-ordens-guarda.json` (o mutante da cópia principal passa a mutar a condição nova) e o fragmento `changelog.d/v0480-develop-verde-ordens.md`. Primeira revisão, completa.

## O filtro não muda decisão (hooks/conformidade.py:1612)
- `PELA_COPIA_PRINCIPAL` tem uma entrada só, `.forge/ordens/`, sem curinga e terminada em `/` (hooks/conformidade.py:3823).
- `relativos_a_copia_principal` devolve `[rel]` com `posix = <pai do .git> + "/" + rel` (`relativo_ao_pai`), ou `[]`.
- `casa(rel, ".forge/ordens/")` sem curinga é `rel.startswith(".forge/ordens/")` ou `rel == ".forge/ordens"`. No primeiro caso o `posix` contém `/.forge/ordens/`; no segundo, `posix + "/"` termina em `/.forge/ordens/`. Nos dois, `em_qualquer_lugar(posix, c)` é verdadeiro; com o pai sendo `/`, o prefixo é `/` e vale o mesmo.
- Logo `em_qualquer_lugar` falso implica o `any(casa(...))` falso: o filtro só corta a leitura do disco, sem trocar nenhum `achou`. A ordem do `and` mantém o curto-circuito antes de `diretorio_comum`.
- Teto e teste intactos: `git diff 0e59c446 HEAD -- tests/test_hooks.py hooks/` não toca o orçamento nem o limite de 3 s.

## Verificações do revisor
- Mutante da guarda da cópia principal (`bin/forge-mutante tests/mutantes/v0480-ordens-guarda.json`, só esse id): morreu, em hooks/conformidade.py:1612, rev 6ce3a41a8ec8. O `de` é único no arquivo (`grep -c` = 1).
- `python3 -m unittest tests.test_hooks.GuardaDasOrdens tests.test_hooks.Hooks.test_muitos_heredocs_recusam_dentro_do_orcamento`, ambiente limpo: `Ran 5 tests`, `OK`; a forma de 3000 heredocs mediu 0,99 s de CPU, limite 3 s.
- CI do PR #814 no head: suíte pendente; `catraca` e `bateria (pareceres)` vermelhas por falta dos pareceres da classe C (mudança em `hooks/conformidade.py`), o que este parecer e o da segurança resolvem. O merge espera a suíte verde no CI.
- Commit único, Conventional Commits em português, com o motivo e o run do CI que mediu 3,02 s. Fragmento de changelog presente. Tamanho dentro do teto H1.
