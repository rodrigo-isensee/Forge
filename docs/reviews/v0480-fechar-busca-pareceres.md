---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-busca-pareceres
commit: be7d10f412d3814a7a4d60f3ee447f3d752da164
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-23
---
# Review: v0478 (E132.2, forge-fechar busca os pareceres citados, FECHAR-BUSCA-PARECERES-CITADOS)

Revisão completa do PR #817 no head be7d10f4 (um commit sobre a base 0e59c446). Diff: `bin/forge-fechar` (+40/-3), `bin/forge-testes` (1 linha do mapa), `tests/test_fechar_busca_pareceres.py` (8 testes), duas specs de mutante em `tests/mutantes/`, fragmento em `changelog.d/` e peso em `tests/pesos-d4.json`. Código abaixo do teto H1 (43 linhas), um comportamento só.

## O que foi conferido
- Requisito da E132.1: a busca roda antes do passo 1 (`bin/forge-fechar:1448`), só por leitura (`git fetch` por sha40 com `--no-write-fetch-head`, sem refspec de destino, sem `--tags`, sem manutenção automática), primeiro da origin e depois da pasta do `--principal`; o que falta em todas as fontes sai em `aviso:` no stderr; o veredito continua sendo o do `forge-check pr` (teste `test_o_veredito_do_passo_1_nao_muda`).
- Leitura do pedido: só as linhas de lista do `## Histórico` com `parecer conferido <sha40>` delimitado; o sha citado em outra seção fica fora (teste com `FORA_DO_HISTORICO`). Raízes na ordem `~/.forge-contrib`, depois a cópia principal pelo `--git-common-dir`, a mesma precedência do `RAIZES_DE_BRIEF` do `forge-check`.
- Caminhos que saem antes da busca: `--dry-run` (sai em `:1315`, sem servidor, conforme o contrato dele), `--limpar`, `--lote` (recusa `--principal` em `:139`) e `--promover`. Sem sha faltando, nenhum fetch: a guarda de `:1425` evita a refspec padrão.
- Guardas do diff: as 11 linhas de guarda novas têm um mutante cada nas duas specs de `tests/mutantes/v0480-fechar-busca-pareceres*.json`, cada uma com teste do ramo de falha por comportamento (subprocesso real do script, `git` real, sem falso de `git`).
- Commit único `feat(fechar): ...` em português, com o ID do cartão no comentário e no fragmento do changelog.

## A opção `--principal` explícita
É o desenho certo. As cópias de trabalho do Forge são clones (`--git-common-dir` desta cópia é a própria `.git`), então a cópia principal não pode ser deduzida pelo git: a `origin` é o GitHub, e o único jeito de achar a pasta seria adivinhar um caminho do ambiente, o que fere `R-NEUTRO`. Na worktree ligada o problema nem existe (a cópia principal já divide os objetos). A opção explícita deixa a fonte local sob controle de quem fecha, é validada antes do passo 1 (`rev-parse --show-toplevel`, para com código 1 sem abrir nada) e o lote a recusa. A sonda abaixo mostra que a cópia local entrega o commit mesmo com a branch apagada nela, enquanto o gc não o remover.

## Provas lidas e rodadas
- Teste novo: `python3 -m unittest test_fechar_busca_pareceres` (em `tests/`, ambiente limpo): `Ran 8 tests ... OK`.
- Mutantes das duas specs, 1 processo: os 11 morreram (`bin/forge-fechar:123`, `:139`, `:1422`, `:1425`, `:1426`, `:1427`, `:1431`, `:1432`, `:1433`, `:1437`, `:1446`).
- `bin/forge-mutante --cobertura --base 0e59c446`: rc 0 (lista `bin/forge-fechar` e `tests/pesos-d4.json` como sem medida de cobertura de linha, sem condição descoberta).
- `shellcheck`: ausente nesta estação; fica com o CI (bateria).
- CI do PR #817 no head be7d10f4: catraca e bateria (pareceres) vermelhas pela falta dos pareceres; partes da suíte ainda em andamento na leitura. Não rerrodei a suíte.
- Sonda de fonte local: repositório com o commit de parecer só como objeto inalcançável (branch apagada), clone `--no-local`, `git fetch --no-write-fetch-head <pasta> <sha>`: rc 0 e o commit passa a existir no clone.
- Sonda de escala no pedido real: o `## Histórico` do v0478 cita 402 shas de parecer conferido; 266 não existem nesta cópia. Um fetch em lote dos 266 da origin, em repositório vazio e raso, levou 0,85 s e trouxe todos. Um fetch por sha custa cerca de 0,6 s (20 em 12,4 s); um sha inexistente custa 0,58 s até o `not our ref`.

## Achados
- A1 (recomendado) bin/forge-fechar:1427 · Se um único sha citado não existe na origin, o fetch em lote falha e o recuo faz um fetch por sha de todos os que faltam: no v0478 seriam 266 fetches, uns 160 s no primeiro fechamento numa cópia nova. Sugestão: recuo por metades ou o aviso do tempo.
- A2 (recomendado) bin/forge-fechar:160 · `--principal` com `--promover` (e com `--limpar`) é aceito e ignorado em silêncio, ao contrário do `--lote`, que o recusa em `:139`; `--principal ""` também passa como ausente. Sugestão: incluir `$copia_principal` na recusa do `--promover` e recusar o valor vazio.

## Parecer
Aprovado. O código faz o que a E132.1 pede, sem ref nova, sem FETCH_HEAD e sem mexer no veredito do passo 1; a opção `--principal` explícita é o desenho certo pelo motivo acima. Os dois achados são recomendados (custo do recuo medido em sonda, sem defeito de resultado; opção ignorada sem efeito colateral) e viram cartão depois do merge, conforme `R-REVIEW`.
