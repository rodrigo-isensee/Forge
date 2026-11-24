---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-fechar-busca-pareceres
commit: be7d10f412d3814a7a4d60f3ee447f3d752da164
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478 (E132.3, busca dos pareceres conferidos no forge-fechar, PR #817)

Lido o diff inteiro `0e59c446..be7d10f4` (7 arquivos; código só em `bin/forge-fechar:1418-1448` e na opção `--principal`, `:123` e `:139`).

Gatilhos: controle do Forge (`bin/forge-fechar`, integrador), `git fetch` de fonte dada por argumento (pasta local) com sha lido de arquivo (o pedido).

## Neutro, por escrito
O item é **neutro** para a segurança: não afrouxa nenhuma conferência nem aperta nenhuma. Motivos:
- O veredito do passo 1 segue só do `forge-check pr` (`bin/forge-fechar:1463`), que não muda neste PR. Antes, um `parecer conferido` sem commit legível fazia o `forge-check` falhar fechado (`bin/forge-check:2014`, `:2469`, "rode git fetch"); a busca só faz, antes do passo 1, o `git fetch` que essa mensagem pede. Depois dela, o `forge-check` confere o mesmo blob, a mesma ancestralidade e o mesmo frontmatter de antes.
- O objeto buscado é preso ao sha40 que o Jarvis gravou no `## Histórico`: o git recalcula o hash de cada objeto recebido, e a fonte não troca o conteúdo sem trocar o sha. Fonte hostil (origin, rede de forks do servidor, `--principal` de outro repositório) só entrega o objeto exato ou nada; nada mais entra no veredito.
- Sem ref nova, sem `FETCH_HEAD`, sem manutenção automática, sem tags (`bin/forge-fechar:1426-1427`); só objetos, que o `gc` pode podar. Não há push. No `--dry-run` a busca não roda (o modo seco sai antes, `:1315-1330`), e no `--lote` a opção é recusada (`:139`).

## Entrada hostil, dimensão por dimensão
- **Sha lido do pedido:** o filtro só aceita `[0-9a-f]{40}` (`bin/forge-fechar:1439`), e só dentro do `## Histórico`. Texto com forma de opção (`--upload-pack=...`) não passa: sondado, a linha sai do filtro e só o sha40 legítimo é extraído. Sem injeção de opção nem de refspec.
- **Pasta `--principal` como link:** `cd` mais `git rev-parse --show-toplevel` (`:1432`) resolve o link na pasta física; o fetch usa o caminho absoluto, que começa com `/` (o git não o lê como `host:caminho`). Pasta que não é cópia git, ou que o git recusa por dono diferente (`safe.directory`), para antes do passo 1 sem nada buscado (teste `test_principal_que_nao_e_repositorio_para_antes_do_passo_1`).
- **Pasta com configuração e hooks hostis:** sondado com `uploadpack.packObjectsHook` e `core.fsmonitor` na configuração do repositório e hooks `pre-upload-pack`, `post-checkout`, `reference-transaction` e `post-index-change` apontando para um script que cria um arquivo marcador. Resultado: o resolve e o fetch rodaram, o commit foi lido, nenhum script executou, nenhuma ref nova, sem `FETCH_HEAD`. O git ignora o `packObjectsHook` vindo da configuração do repositório, e o fetch local não roda hooks da fonte.
- **Objetos forjados:** sondado com um objeto solto gravado sob um sha40 que não é o hash do conteúdo. O fetch falhou (`bad object`, `did not send all necessary objects`, rc 1) e o objeto não entrou na cópia.
- **Pasta de outro repositório:** sondado; o fetch de um sha que a fonte não tem falha (`not our ref`) e o sha sai no aviso, sem mudar o veredito (teste `test_busca_da_origin_e_da_principal_e_diz_o_que_nao_existe`).
- **Nome do pedido:** `$pedido` entra no caminho do arquivo lido (`:1437-1438`) sem filtro de `/`; é argumento do próprio integrador, só leitura, e o que sai dele é só sha40 para busca presa ao hash. Sem ganho para um atacante.

## Sondas

## Como as sondas rodaram
Nenhuma prova bloqueante. As sondas de entrada hostil acima rodaram fora do repositório (roteiro em `$TMPDIR`), com o mesmo comando de fetch do `bin/forge-fechar:1426`, no git 2.43.0.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum.
Ferramentas: leitura do diff; no head, `python3 -m unittest tests.test_fechar_busca_pareceres` deu 8 testes OK; `forge-mutante` com as duas specs do PR deu 11 de 11 mortos. A suíte inteira não rodou (o brief pede sem suíte local); vale o CI do PR #817, que na hora deste parecer tinha as partes da suíte em andamento e `catraca` e `bateria (pareceres)` vermelhas pelo texto do PR (seção "Projeto de origem") e pelos pareceres ainda por vir, nada de segurança; o CI verde é obrigatório para o merge. `shellcheck` não está nesta estação (fica com o CI).
