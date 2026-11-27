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
- **Até 10 arquivos por item** (META85, ordem do dono 18/11): o `forge-check classe` sai com rc 1 e `item: <n> arquivos`
  acima disso; o corte vem no desenho, antes de começar. Contam código, documentação, agente e skill; ficam fora testes
  (com `tests/mutantes/`; os módulos do portão em `tests/` contam), fragmentos de `changelog.d/` e pareceres e quadro.
- **Um comportamento só** por item; vale uma classe de comportamento por PR em `hooks/`, com corpus próprio.
- **Antes de começar:** item acima do teto é cortado pelo tech-lead em partes que ficam verdes sozinhas; partes que mexem
  nos mesmos arquivos seguem no mesmo agente, uma depois da outra (diretriz 33).
  O aviso de tamanho do `forge-check pr` (e do `pr --previo`) traz o corte sugerido: os PRs de até o teto por arquivo
  e, no arquivo maior que o teto, por função tocada; é sugestão, quem corta é o tech-lead.
- **Passar do teto:** só se cortar mais deixa a suíte vermelha (um pedaço não fica verde sozinho). O tech-lead explica o
  motivo no corpo do PR, com `teto: excedido, <n> linhas, <motivo>`.
  No clone do Forge, o hook `parecer` recusa o `gh pr create` para a `develop` (com ou sem `--draft`) acima do teto, com o
  corte sugerido; a linha só vale no `--body-file` (arquivo comum da cópia, até 64 KiB), com `<n>` igual ao total ou maior.

## Caminho curto para o pequeno (H8)
- **A classe decide** (`forge-check classe`, `R-REVIEW`): na T (só documentação comum, só testes, ou até 20 linhas fora dos
  caminhos de controle) o caminho é localizar, corrigir, validar por teste e uma revisão, sem QA separado; a segurança entra
  só com gatilho (`R-SEGURANCA`). O `brief gerar` avisa quando a classe não exige o portão da etapa: não dispare o agente.
- **Nenhum portão sai de classe nenhuma sem decisão do dono.** No Forge, texto de skill e de agente e correção em `bin/` e
  `hooks/` são caminhos de controle (classe C): o caminho curto não os alcança.
