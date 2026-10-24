---
tipo: review
contrato: 1
pedido: lote-m8-prepush
branch: melhoria/lote-m8-prepush
commit: a15a5697609a207eb56aca0b0c64e6f26c1a1e1d
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-24
---
# Review: lote-m8-prepush (EST-M8, REVERSAO-MAPA, FORGE-TESTES-CAMINHOS)

Escopo: `git diff 3c66b881af31817ce5d2dde996c7ca56d54cb511...a15a5697609a207eb56aca0b0c64e6f26c1a1e1d` (3 commits, um por cartão): `.githooks/pre-push`, `bin/forge-testes`, `tests/test_pre_push_afetados.py` (novo), `tests/test_testes_tocados.py`, `changelog.d/lote-m8-prepush.md`. Pedido de review: LOTE-M8-PREPUSH-REV, E1.1.

## O que conferi
- **Decisão M8 do dono (2026-10-23, "A")**: o pre-push mantém os bloqueios de conteúdo e roda só os testes afetados; a suíte completa fica no CI do PR. Confere: `dirigido()` (`.githooks/pre-push:243-256`) só é chamada depois do laço de refs (`:106-132`: recusa de main, homolog, develop e do não fast-forward de branch e tag, com `exit 1` antes de qualquer teste), das saídas sem ref e só-remoção (`:136-147`) e da trava/fila. `--no-verify` não passa pelo pre-push por natureza; segue com o hook do Claude (fora do diff).
- **Recuo à suíte inteira, condição por condição** (`.githooks/pre-push:245-255`): mais de uma ref (`n_refs -eq 1`); ref que não é `refs/heads/*`; sha local inválido ou zerado; `bin/forge-testes` ausente ou link; HEAD diferente do enviado; árvore suja (`--untracked-files=all`); `origin/develop` ausente; `--listar` com erro ou saída que não começa em `forge-testes: dirigido (` (inclui "nada alterado", caminho sem mapa, `ALTERA_O_MAPA` e módulo mapeado inexistente). Qualquer `return 1` cai no `elif` seguinte, que é a suíte inteira em paralelo ou em série, como antes. Falha fechada.
- **Prova de árvore verde**: `completa=0` só no ramo dirigido e a anotação exige `completa = 1` (`:293`). O ramo `so_parecer` só é tomado se a árvore remota já está no `.verde`, e o `.verde` só nasce de uma suíte inteira, então a cadeia continua enraizada na suíte inteira (ver A3 sobre o texto do comentário).
- **Mapa**: `.githooks/` não tem regra (cai na completa) e `bin/forge-testes` está em `ALTERA_O_MAPA`, então mexer no próprio filtro ou no hook roda a suíte inteira. Conferido: `bin/forge-testes --listar --base 3c66b88` nesta branch dá `suíte completa (.githooks/pre-push sem mapa)`. REVERSAO-MAPA (`bin/forge-testes:90`) e `(dev/)?\.claude-plugin/` (`:94`) com teste próprio.
- **Caminhos (FORGE-TESTES-CAMINHOS)**: `caminhos_pedidos` resolve relativo à pasta de chamada, normaliza `..` e recusa o que sai do repositório (saída 2); não combina com `--completa` nem `--vermelho`; testes cobrem relativo, absoluto, `..`, subpasta, fora do repo, opção incompatível e `--`.
- **NaoEPortao contra a decisão M8**: a classe deixa de varrer `.githooks/` e passa a exigir que, ali, só `.githooks/pre-push` cite o script (lista fechada), e acrescenta a lista fechada de scripts de aviso em `scripts/` (`scripts/conferir-reversao.py`). CI (`.github`), `hooks/`, `scripts/ci-local` e `bin/forge-check` seguem vigiados. É exatamente o que a decisão M8 autoriza (o pre-push chamar o filtro) e nada além; a guarda fica mais estreita só no ponto decidido. `tests/config.json` (invariantes) não foi tocado.
- **Testes**: `tests/test_pre_push_afetados.py` roda o hook real num repositório descartável e exercita cada recuo, falha no módulo afetado (barra) e no não afetado (não barra), os bloqueios de conteúdo antes do filtro e a não anotação do `.verde`. Rodado aqui: `python3 -m unittest tests.test_pre_push_afetados tests.test_testes_tocados -q` → `OK` (13,3 s). `shellcheck .githooks/pre-push` → sem saída. A suíte inteira passou no pre-push da entrega (1958 OK, histórico do pedido); não a refiz.
- **Teto M14**: `git diff --numstat --no-renames` contáveis = 29 (`.githooks/pre-push`) + 44 (`bin/forge-testes`) + 155 + 83 (`tests/*.py`) = 311 linhas, abaixo de 400; nada em `hooks/`. `.githooks/` está em `PROTEGIDOS` (`tests/catraca.py:43`): o PR (E1.5) precisa do tratamento de caminho protegido da catraca.
- R-CUSTO, R-NEUTRO: nada pago, nenhum termo de projeto. Fragmento `changelog.d/lote-m8-prepush.md` presente. Commits em Conventional Commits, um por cartão.
- PA-7 (`docs/engineering/achados-recorrentes.md`): lista vazia, nada a conferir.

## Achados
- A1 (recomendado) README.md:68 · o README, docs/economia-de-tokens.md:10 e agents/tech-lead.md:22 ainda dizem que o pre-push roda a suíte inteira; com o M8 isso deixou de valer para o push dirigido. Atualizar os três (o cartão DOCS-REGRA5-PREPUSH cobre só a regra 5)
- A2 (recomendado) .githooks/pre-push:253 · o plano (`--listar`) e a execução (`:263`) resolvem `origin/develop` duas vezes; um fetch entre os dois que leve a branch para a develop faz a execução dizer "nada alterado" e sair 0 sem rodar teste. Resolver o sha uma vez e passar o mesmo `--base <sha>` aos dois
- A3 (recomendado) .githooks/pre-push:241 · os comentários (`:241` e `:290`) dizem que só a suíte inteira anota a prova, mas o ramo `so_parecer` também anota (completa=1), por herança da árvore remota já verde. Dizer isso no texto para não induzir uma futura mudança a quebrar a cadeia
- A4 (recomendado) bin/forge-testes:463 · a descrição do argparse ainda diz "(não é portão)"; alinhar com o docstring novo (filtro do pre-push, nunca portão de CI)

## Parecer
Aprovado. O lote faz o que a decisão M8 pede, sem afrouxar além dela: os bloqueios de conteúdo valem antes do filtro, toda dúvida cai na suíte inteira, a prova de árvore verde continua enraizada na suíte inteira e a mudança em NaoEPortao troca a varredura de `.githooks/` por uma lista fechada com só o pre-push. Os quatro achados são recomendações (texto desatualizado e uma corrida improvável de fetch durante o push) e não devolvem. Para o PR (E1.5): destacar no título ou no corpo que a guarda NaoEPortao foi estreitada por decisão do dono, e o caminho protegido `.githooks/`. Segurança e QA têm parecer próprio (E2.1, E3.1).
