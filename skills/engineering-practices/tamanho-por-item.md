# Tamanho por item (H1)

Parte da skill `engineering-practices`, num arquivo próprio porque o texto inteiro não cabe no teto de caracteres da
`SKILL.md` nem do `tech-lead` (diretriz 25 do dono: regra existente não se apaga nem se resume; o que não cabe muda de
arquivo, com ponteiro). Vale no Forge e em todo projeto (`R-REVIEW`).

**Decisão do dono (17/11, H1):** até 150 linhas de código por item; testes e documentação não contam. Substitui a
orientação do M14 (150 linhas de código e teste, sem trava por volume).

- **Contagem:** `git diff --numstat --no-renames origin/develop...HEAD`, adições mais remoções, só dos arquivos de código.
  Fora: testes, documentação e texto `.md`, pareceres, fragmentos de changelog, corpus e fixtures.
- **No Forge** contam `bin/`, `hooks/`, `scripts/`, `.github/` e `.githooks/`; ficam fora `tests/` inteira (com
  `tests/config.json` e `tests/mutantes/`), `changelog.d/`, corpus, fixtures e o texto `.md`.
- **Um comportamento só** por item; vale uma classe de comportamento por PR em `hooks/`, com corpus próprio.
- **Antes de começar:** item acima do teto é cortado pelo tech-lead em partes que ficam verdes sozinhas; partes que mexem
  nos mesmos arquivos seguem no mesmo agente, uma depois da outra (diretriz 33).
- **Passar do teto:** só se cortar mais deixa a suíte vermelha (um pedaço não fica verde sozinho). O tech-lead explica o
  motivo no corpo do PR, com `teto: excedido, <n> linhas, <motivo>`.
