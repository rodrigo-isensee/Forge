---
tipo: review
contrato: 1
pedido: ta-6-pa-3-pa-9
branch: melhoria/ta-6-sobreposicao-fila-quadro
commit: f257b67d7c0405f133980382fff7b5f06bb8591b
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-16
---
# Review independente: sobreposição, fila de integração e registro do quadro (TA-6, PA-3, PA-9)

Escopo: `origin/develop...c7a2b6af58a9` (base 1fd122f; o autor não é este revisor). 8 arquivos, 4 commits.

Veredito: **APROVADO**, com 4 ajustes recomendados (nenhum bloqueia). Eles voltam ao autor e podem entrar antes do PR ou num cartão seguinte.

## Conferido
- **E1 `forge-check sobreposicao`** (`bin/forge-check:544-572`): junta as branches `melhoria/*` locais e remotas pelo nome curto (sem repetir), compara cada par uma vez por `git diff --name-only --no-renames <base>...<branch>` (reaproveita `arquivos_da_entrega`) e devolve uma linha por par com sobreposição, em ordem (nomes e arquivos ordenados), mais uma linha de resumo com a base usada. O rc é 0 sempre, inclusive sem base. Testei à mão uma branch que só existe no remoto (cai em `origin/<nome>`): o par foi listado com rc 0. A regra está em `agents/jarvis.md:44` ("Trabalho em paralelo"): rodar antes de disparar e serializar os pares com sobreposição.
- **E2, fila (PA-3)**: `docs/regras/R-FLUXO.md:16` diz um PR por vez, em ordem de chegada, que o próximo só atualiza a base depois que o anterior entrou e que quem não sobrepõe não espera. Também diz "nenhum check nem parecer é dispensado", então não afrouxa nada (decisão do dono de 2026-10-15 ~23h58). Isso é coerente com a regra que já existia: "Depois do QA só se atualiza se houver conflito real". `agents/tech-lead.md:25` cita o ID e o subcomando.
- **E3 `forge-check movimento`** (`bin/forge-check:575-593`): só acrescenta linhas, com hora real ISO 8601 com fuso (`astimezone().isoformat(timespec="seconds")`). Troca `|` e quebras de linha para não quebrar a tabela, recusa campos vazios (rc 1, sem gravar) e cria o arquivo com o mesmo cabeçalho do modelo `templates/projeto/docs/kanban/historico.md`. Usado em `skills/kanban-scrum/SKILL.md:61-64` e `agents/jarvis.md:46`, inclusive para "Aguardando o dono" e "Sem credencial".
- **Determinismo**: a saída de `sobreposicao` só depende do estado do git. A hora de `movimento` é real de propósito, e os testes a conferem por regex, sem depender do relógio.
- **Testes** (`tests/test_sobreposicao_quadro.py`, 11 casos): pares e resumo, branch fora do padrão ignorada, determinismo em 3 execuções, nenhuma branch, local mais remota contadas uma vez, base inexistente, criação do arquivo com hora e fuso, preservação do que já existe e proteção da tabela, campo vazio. Também conferem as regras em texto. Saída de `python3 -m unittest tests.test_sobreposicao_quadro -q`: `Ran 11 tests in 0.822s` / `OK`. A suíte completa fica com o QA.
- **`tests/config.json`**: o diff só acrescenta linhas (8 invariantes novos em 4 arquivos); nenhum trecho sai.
- **R-NEUTRO / R-CUSTO**: o texto não traz nome de projeto, regra de negócio nem stack. Usa só o git local, sem rede nem serviço pago.
- **Changelog**: o fragmento `changelog.d/ta-6-sobreposicao-fila-quadro.md` tem o nome da branch e está em "Adicionado". O `CHANGELOG.md` não foi editado.
- **Commits**: 4 commits em Conventional Commits em português (feat, docs, test, chore), com trailers.
- **Segurança**: o diff toca `bin/forge-check` (controle do Forge, R-SEGURANCA). O parecer é do `security-engineer`, que roda em paralelo; não refaço a análise aqui.

## Ajustes recomendados (não bloqueiam)
1. `bin/forge-check:585-590` · **Problema**: se o `historico.md` existir sem quebra de linha no fim (edição à mão), a linha nova gruda na última. Reproduzi: `| a | b | c | d | e || 2026-10-16T09:42:46-03:00 | K | a | b | — |`. Isso corrompe a fonte das métricas. · **Sugestão**: antes de acrescentar, ler o último byte e escrever `\n` se faltar; incluir um teste para esse caso. · **Severidade**: recomendado.
2. `agents/tech-lead.md:25` · **Problema**: a regra da fila ficou em "No Forge e nos projetos", mas ela é da `develop` e o `sobreposicao` só enxerga `melhoria/*`. Num projeto o subcomando mostraria "0 pares" e daria a impressão de que nada precisa esperar. · **Sugestão**: mover o item para "No repositório Forge (a fábrica)", como fez o `jarvis.md:44` ("no Forge"). · **Severidade**: recomendado.
3. `bin/forge-check:544-572` · **Problema**: uma branch `melhoria/*` já mesclada por squash e ainda não apagada continua mostrando o próprio diff contra a `develop`, porque o merge-base é antigo. Isso gera falsos pares e serialização desnecessária. O erro vai para o lado seguro, e a limpeza pós-merge de R-FLUXO reduz o caso. · **Sugestão**: documentar isso na docstring ou na ajuda (ou ignorar branches cujo `git cherry` não traz nada novo), se o falso par aparecer na prática. · **Severidade**: recomendado.
4. `tests/test_sobreposicao_quadro.py` · **Problema**: nenhum teste cobre uma branch que só existe no remoto (o ramo `origin/{nome}` de `bin/forge-check:563`). Conferi esse caso só à mão. · **Sugestão**: no teste de local e remota, apagar uma branch local depois do `fetch` e conferir que o par continua listado. · **Severidade**: recomendado.

## Pendências
- Nenhuma regra "ferramenta" sem comando: a validação do plugin e a suíte completa ficam com o QA (R-QA).

## Revalidação após a volta do autor
Escopo: `c7a2b6a..f257b67` em `bin/`, `agents/` e `tests/` (2d94038 e f257b67). Veredito mantido: **APROVADO**.
- Ajuste 1 corrigido (`bin/forge-check`, `cmd_movimento`): lê o último byte e escreve `\n` se faltar; teste `test_arquivo_sem_quebra_final_nao_cola_a_linha_nova`.
- Ajuste 2 corrigido: a fila de integração foi para "No repositório Forge (a fábrica)" em `agents/tech-lead.md`; só moveu a linha, sem mudar o texto.
- Ajuste 4 corrigido: `test_branch_so_no_remoto_continua_listada` apaga a branch local depois do `fetch` e confere o par.
- Ajuste 3 (falso par por branch já mesclada por squash) segue como estava: era recomendado, o erro cai para o lado seguro e a limpeza pós-merge o reduz. Não bloqueia.
- Itens I-TA6-1 e I-TA6-2 da segurança: controle de caracteres de controle removidos e recusa de link simbólico em `historico.md`, ambos com teste. Sem efeito colateral: o `limpo` só retira `[\x00-\x1f\x7f]` depois de normalizar espaços, e o caminho normal não mudou.
- `python3 -m unittest tests.test_sobreposicao_quadro -q`: `Ran 15 tests in 1.198s` / `OK`. A suíte completa fica com o QA.
