---
tipo: revisao-seguranca
contrato: 1
pedido: lote-forge-check-0.28.0
branch: melhoria/lote-forge-check-0.28.0
commit: 31e78cdc1419753daf4ca711211126f61e77dbcd
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-23
---
# Review de segurança: lote-forge-check-0.28.0

Entrega revisada: `ad6d96ce6b19663f7695d361d61f59c7545bdca6..1d001b1348dc915917f314eb99881e21dd1a4989`. Revalidação por delta sobre o parecer anterior (`389096e`, reprovado por A1 e A2): as voltas 1 e 2 (`c190356`, `56ae496`, `f49fd41`), o merge da develop (`24754c9`) e a ampliação da isenção de QA (`1d001b1`). Leitura estática e os módulos de teste do delta rodados na worktree (`test_isencoes`, `test_testes_tocados`, `test_anotar`, `test_citacao`: 56 testes, OK). Sem achado bloqueante.

## Achados

## Revalidação
- A1 anterior (`anotar` grava em qualquer arquivo), metade do `forge-check`: corrigida em `56ae496`. `cmd_anotar` (`bin/forge-check:1641-1644`) resolve o alvo por `pedido_para_anotar` e recusa o que está fora de `docs/pedidos/`, ausente ou link simbólico. A metade do hook `conformidade` (o `anotar` e o `brief gerar --gravar` tratados como escrita em pasta do jarvis) fica para a volta 3, com revalidação própria, como o pedido define; este parecer não a cobre.
- A2 anterior (`--citar .env:1`): corrigida em `c190356`. `linhas_da_fonte` (`bin/forge-check:3734` e `:3745`) só aceita documento `.md` cujo nome não é de `.env`, conferido no nome pedido e no nome real depois do `realpath` (um `.md` que é link para o `.env` não passa).
- Merge da develop (`24754c9`): toda linha que a develop acrescentou em `bin/forge-check` desde a base comum está no HEAD (conferido linha a linha); `cmd_fila` (P9) é idêntica à da develop e segue só leitura, sem rede; o `executar` mantém `anotar`, `fila` e o `brief gerar` com os argumentos novos. Em `bin/forge-testes`, `FORGE_CHECK` é a união das duas listas (19 módulos), sem perder `test_hooks`, `test_catraca` nem `test_guarda_*`; o pre-push dirigido não deixa de rodar teste de portão. `tests/test_testes_tocados.py` confere a união. A MODELOS-NO-FORGE (`test_modelos_citados` em `CONTEUDO`) está preservada.
- Isenção de QA (`1d001b1`): `MD_DE_CONTROLE` (`bin/forge-check:513`) passa a incluir `stacks/*/seguranca.md`, `stacks/*/pronto.md`, `templates/projeto/` e qualquer `CLAUDE.md`, conforme a decisão do dono de 2026-10-21 14:03; só reduz o que é isento (endurece), e a lista de arquivos segue `--no-renames`, então renomear um arquivo de controle para fora dele não escapa. A recomendação R3 do parecer anterior foi atendida.

## Gatilhos
- Controles do Forge: `docs/regras/R-BRIEF.md` e `tests/config.json` no diff (gatilho do `forge-check pr`).
- Portões: `hooks/parecer.py` (isenção do M13) e `bin/forge-check` (`pr`, `brief`, conferência do conferente), marcados no pedido.
- Leitura de caminho vindo de texto (P3, conferência de citação e `--citar`) e escrita nova em pastas de outro papel (P4 `anotar`, P6 `--gravar`).
- Rede: `gh pr view` no `brief gerar` (P5), gratuito (`R-CUSTO`).

## Item a item
- M16 (`5f3ae67`, `f49fd41`): aprovado. A correção do review (o item citado não cobre a etapa do papel do destino) só aperta a conferência.
- P2 (`84db057`), M4 (`9921db8`), M5 e P2 tabela (`3101c0d`), P5 (`158af43`), testes (`389096e`): aprovados no parecer anterior, sem mudança no delta.
- M13 (`8ccff9f`, `1d001b1`): aprovado; falha fechada com diff vazio ou base ausente, lista de controle ampliada pela decisão do dono.
- P6 (`bfed7d5`, `9ffd14c`): aprovado no que entrega; a escrita por papel que não é o jarvis fica com a metade do hook (volta 3).
- P4 (`c23ea30`, `56ae496`): aprovado na metade do `forge-check`.
- P3 (`8f8fa3c`, `c190356`): aprovado.

**Recomendações (não bloqueiam):**
- R1. `gh pr view` no `brief gerar`: passe `--` antes da branch (uma branch que começa com `-` vira opção do `gh`). Baixa.
- R2. P6: o `0444` do brief aprovado não é trava (a ferramenta Write sobrescreve); abra o cartão da P6b (hook `conformidade`, com parecer de segurança) e não o cite como proteção até lá.
- R4. `CONTROLES_DO_FORGE` não inclui `hooks/`, `bin/forge-check` nem `agents/`: o gatilho de segurança deste lote veio da marcação no pedido, não do diff. Anterior ao lote; vale um cartão.
- R5. `cmd_anotar` reescreve o pedido inteiro depois de checar o link simbólico; prefira arquivo temporário e renomear, para não truncar o pedido numa falha.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: `gitleaks`, `semgrep`, `zizmor`, `actionlint`, `osv-scanner` e `shellcheck` não estão no PATH deste ambiente (lacuna registrada; nada foi instalado). O delta não toca workflow, dependência nem contêiner. Nenhum segredo real foi lido nem exibido.

## Revalidação por delta (REVAL-288)
Delta `1d001b1..e08438f` (o parecer anterior vale para `1d001b1`): dois merges da `develop` (`e83da9f`, com a 0.28.0 e #279 a #287, e `0b8a307`, com o #288), pareceres de review e QA e o `.claude-plugin/plugin.json` da release. Decisão do dono "C" (2026-10-23): revalidar por delta, sem afrouxar. Conferi que o que é da branch não mudou: o diff da branch contra a base (`ad6d96c..1d001b1`) e contra a `develop` atual (`7423c44..HEAD`) tem o mesmo conjunto de arquivos (a diferença é só `docs/qa/lote-forge-check-0.28.0.md`) e as mesmas linhas alteradas em `bin/`, `hooks/`, `agents/`, `.githooks/`, `.github/` e `tests/config.json`. Ou seja, `bin/forge-check`, `hooks/parecer.py`, `bin/forge-testes` e `agents/conferente.md` estão como foram revisados.
- `.claude-plugin/plugin.json:3`: só a versão da release 0.28.0, vinda da `develop`, que a revisou; sem permissão, hook nem dependência nova.
- O resto do delta (`bin/forge-doutor`, `bin/forge-fechar`, `.githooks/pre-push`, `.github/workflows/ci.yml`, testes) veio da `develop` pelos merges e passou pelos portões do PR de origem; não é entrega desta branch e não muda a superfície que o parecer cobre. Os controles do Forge tocados pela branch (R-BRIEF, `tests/config.json`, `hooks/parecer.py`, conferente) seguem como revisados.
Veredito: aprovado, sem achado novo; as recomendações R1, R2, R4 e R5 acima seguem valendo. Ferramentas: `forge-check delta` e comparação dos diffs; `gitleaks`, `semgrep`, `zizmor`, `actionlint` fora do PATH (lacuna igual à anterior).

## Revalidação por delta (INTEG-LOTE-FC-REV)
Delta `e08438f..8649439`: os pareceres do REVAL-288 (`d4bc926`, `ad6a9bd`) e o merge `8649439` da `develop` (`daf2ffa`, com a M14b do #291 e #292 a #296). O `forge-check delta` lista o que a `develop` trouxe (`.githooks/pre-push`, `bin/forge-atualizar`, `bin/forge-fechar`, `bin/forge-check` da M14b, agentes e docs), que passou pelos portões do PR de origem; a revisão aqui é a resolução dos conflitos.
- `bin/forge-check`: o conjunto de linhas que cada lado mudou desde a base comum (`7423c44`) está inteiro no merge, dos dois lados (conferido pela diferença de cada pai para o merge). O `executar` (`bin/forge-check:4988-5004`) despacha `anotar` (lote) e `escape`, `afrouxamentos`, `esperas`, `corrigidos` (M14b, só leitura, exceto `escape registrar`); os parsers de `conferencia`, `brief`, `entrega` e `pr` (`:4850`, `:4906`, `:4920`, `:4924`) e as funções deles seguem como no lote revisado. Nenhum subcomando de controle perdeu o comportamento do lote nem da M14b.
- Superfície da branch contra a `develop`: `bin/`, `hooks/`, `.githooks/`, `.github/`, `tests/config.json` e `agents/conferente.md` têm o mesmo diff de antes do merge (`7423c44..ad6a9bd` e `daf2ffa..8649439`), com uma linha de diferença, a de `FORGE_CHECK` em `bin/forge-testes:61-64`, que é a união (20 módulos, com `test_medidas_m14b`, `test_hooks`, `test_catraca` e `test_guarda_*`). O pre-push dirigido segue rodando os testes de portão. `tests/test_testes_tocados.py:57-63` confere os 20. `docs/hooks.md` veio por merge automático.
- Nada no merge afrouxa portão: `hooks/`, `.githooks/`, `.github/` e `tests/config.json` iguais aos da `develop` mais o lote já revisado.
- Testes do delta rodados na worktree com `HOME` isolado: `test_testes_tocados`, `test_medidas_m14b`, `test_anotar` (106 testes, OK).
Veredito: aprovado, sem achado novo; R1, R2, R4 e R5 seguem valendo. Ferramentas: `forge-check delta`, comparação de diffs por pai; `gitleaks`, `semgrep`, `zizmor`, `actionlint` fora do PATH (lacuna igual).

## Revalidação por delta (INTEG-LOTE-FC-2-REV)
Delta `8649439..31e78cd` (o `forge-check delta` sobre este parecer): o merge `31e78cd` da `develop` (`139a3b4`, com o #294), base comum `daf2ffa`. O delta toca controle do Forge (`hooks/agentes.py`, `bin/forge-check`, `.github/workflows/ci.yml`, `docs/hooks.md`); a revisão aqui é a resolução e a convivência, não o #294, que passou pelos portões do PR de origem.
- `docs/hooks.md` (conflito): `git show --cc` mostra a linha do `agentes` (`docs/hooks.md:11`) igual à da `develop` e a do `parecer` (`docs/hooks.md:12`) igual à da branch; desde a base comum, a `develop` só mudou a linha do `agentes` e a branch só a do `parecer`, então nenhuma das duas descrições perdeu texto. Cada linha descreve o código do head: `hooks/agentes.py` é idêntico ao da `develop` (forma do cabeçalho, recálculo do sha256, `realpath` em `docs/briefs/` da raiz ou de `~/.forge-contrib`, só arquivo regular, 256 KiB, `hooks/agentes.py:207-272`) e `hooks/parecer.py` é idêntico ao da branch (isenção do M13 pela `isencoes_da_entrega`). A linha 65 (estado do `agentes` no diretório comum do git no clone do Forge) veio da `develop` por mesclagem automática e bate com `arquivo_de_estado` (`hooks/agentes.py:178`).
- Mesclagem automática: `bin/forge-check:1512-1526` (`agentes_vigentes` passa a ler `agentes.arquivo_de_estado`, com o caminho antigo de reserva) é a única mudança no lado da branch, só leitura de contagem, sem tocar portão. `.github/workflows/ci.yml` e `hooks/agentes.py` iguais aos da `develop`.
- Superfície da branch: o diff da branch contra a base comum (`daf2ffa..b8c19b9`) e o do merge contra a `develop` (`139a3b4..31e78cd`) têm as mesmas linhas alteradas em `bin/`, `hooks/`, `.githooks/`, `.github/`, `tests/config.json`, `agents/` e `docs/regras/`: nada do lote sumiu nem afrouxou, e nada do #294 foi tirado.
- Testes do delta na worktree com `HOME` isolado: `test_agentes_clone`, `test_agentes_hash_brief`, `test_guarda_conferente`, `test_isencoes` (51 testes, OK).
Veredito: aprovado, sem achado novo; R1, R2, R4 e R5 seguem valendo. Ferramentas: `forge-check delta`, `git show --cc`, comparação de diffs por pai; `gitleaks`, `semgrep`, `zizmor`, `actionlint` fora do PATH (lacuna igual).

Sem achado novo nesta revalidação.

## Achados
