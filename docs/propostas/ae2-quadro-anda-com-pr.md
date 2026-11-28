# AE2: o quadro anda com o PR (desenho curto, E121.1 do v0478)

Cartão AE2-QUADRO-ANDA-COM-PR, com os juntados TRIAGEM-APLICA-NO-QUADRO, BACKLOG-SO-PELA-FERRAMENTA,
DIR-20-KANBAN-DESTINO e PR-TITULO-CONVENCIONAL. Item AE2 de `docs/pedidos/melhorias-anti-erro.md` (pasta de controle).

**O que muda em relação a `docs/propostas/v0479-ae2-contador.md`:** este desenho substitui as seções 3.1 a 3.3 e 4.3 e
os itens C4, C5 e C6 dele. Não há trailer de commit, conferência nova no envio ou no CI, nem `quadro sincronizar`: o
merge move o cartão dentro da ferramenta que já integra. Os itens C1 a C3 e C7 ficam com o cartão CONTADOR-DA-VERSAO, que
passa a contar a partir de `docs/kanban/historico.md` (movimentos para Pronto com `PR #N` no motivo) em vez de trailers.

**Troca da D1 (trailer) e da D3 (`Cartão-parcial`) aceitas pelo dono (DECISÃO DO DONO 20/11 13:51):** decidido pelo
time na ausência do dono (regra de 20/11 21:34), reversível, reabre quando o dono pedir o trailer de volta ou quando a
auditoria AE6 achar um merge na develop de projeto sem o movimento do cartão (a lacuna do risco da seção 8). O `--cartao`
faz o papel da D1 e o `--parte`, o da D3. Vai em uma linha na lista do dono de segunda. A volta ao trailer está na
reversão (seção 8).

**Afrouxa:** não. Nenhum texto de `docs/regras/` nem invariante de `tests/config.json` sai ou muda; o invariante
"Triagem termina com o `KANBAN.md` atualizado; ... conferida com a última triagem ..." fica como está.
**Merge automático:** nenhum. O movimento só acontece depois do MERGED provado, seja qual for a forma do merge que a
FECHAR-SEM-AUTO-MERGE (E114.1) deixar no passo 6.

## 1. Como o PR cita o cartão
- O `bin/forge-fechar` passa a exigir `--cartao ID` (entrega o cartão) ou `--parte ID` (entrega só uma parte) em todo
  fechamento para a develop, inclusive no `--limpar`; a promoção (`--promover`) fica de fora. Hoje o `--cartao` já existe
  (FECHAR-MOVE-CARTAO, `bin/forge-fechar:47-50`, `:119`, `:196`), mas é opcional, e por isso foi esquecido.
- Antes do passo 1, o ID tem de existir no quadro (`coluna_do_cartao` diferente de `—`, `:837`) e não pode estar em
  Fechado sem entrega. Hoje só se confere a forma do ID e a existência do `KANBAN.md`.
- O corpo do PR criado (`:290-303`) ganha uma linha `Cartão: ID` ou `Parte: ID` para cada um. No PR que é reusado
  (`:1447-1454`), a linha que falta é acrescentada por `gh pr edit --body`. É um registro para quem lê e para a
  auditoria (AE6). A fonte do movimento continua sendo o argumento, que já passou pela conferência.
- Em projeto (onde o `forge-fechar` não roda): o `templates/projeto/.github/pull_request_template.md` ganha a mesma linha
  `Cartão: ID` em `## Objetivo`.

## 2. Como o merge move o cartão
- No Forge, nada muda no mecanismo: `mover_cartoes` (`:847-859`) roda só depois do MERGED provado (`:1612-1623`) e
  chama `forge-check movimento ID --de <coluna atual> --para Pronto`, com `PR #N, merge <sha7>` no motivo.
- `--parte ID` faz um movimento na mesma coluna (`--de X --para X`), só como nota com o PR. Assim o cartão de várias
  partes (o próprio AE2) não vai para Pronto na primeira delas. X é a seção do cartão no `KANBAN.md` (a mesma que o P3
  confere), não o `coluna_do_cartao`, que pode devolver um estado do histórico sem seção e o `movimento` recusaria
  (`bin/forge-check:5065`).
- Quando o dono mescla pela interface, o passo depois do merge é o `forge-fechar <pedido> --ref <branch> --limpar
  --cartao ID`, que já existe (`:1347-1361`): ele lê o PR MERGED e move o cartão. Sem `--cartao`, o comando para.
- Todo motivo de merge leva `PR #N`, para a contagem do CONTADOR-DA-VERSAO não perder o merge do dono:
  - `--limpar` (`:1357`): o N sai da mesma `lista` (`:1349`) que já prova o MERGED, o número do PR MERGED em `$alvo`
    (o mais recente, se houver mais de um). O motivo fica `mesclado em <alvo>: PR #N (forge-fechar --limpar)`. No
    caminho sem merge (`fim_sem_merge`, `:1354`) nenhum cartão é movido para Pronto: não houve entrega.
  - `ja_mesclado` (`:1622`): no caso do PR MERGED achado (`:1438`), o N sai da mesma linha da `lista`. No caso do head
    já contido na base (`:1432`), o P1 lê `gh pr list --head <ref> --state merged` e grava o N. Sem PR MERGED da
    própria branch (o head entrou por outro PR, como no lote), o motivo fica `sem PR próprio, head <sha7>` e não conta:
    o merge conta no PR que o levou.
- Em projeto, a política da skill `kanban-scrum` (Pronto só com o merge do usuário na main) continua valendo: o merge
  na develop vai para "Aguardando sua validação" pelo mesmo `forge-check movimento`, e o passo fica descrito no
  `agents/tech-lead.md`.

## 3. Como o cartão só nasce pela ferramenta
- Nascer é `forge-check movimento ID --de — --para <coluna>` (`bin/forge-check:5063`, que já existe).
- `forge-check kanban` (`cmd_kanban`, `:527`) passa a cruzar o quadro com o histórico. Para isso reaproveita o
  `montar_quadro` (`:4907`), o `linhas_de_cartao` (`:4986`) e o `_ler_regular` (`:4956`). São violações (rc 1):
  - cartão em coluna aberta sem nenhuma linha no histórico (`nasça pelo forge-check movimento --de —`);
  - cartão cuja seção no `KANBAN.md` não é o `Para` da última linha dele (destino divergente, TRIAGEM-APLICA-NO-QUADRO).
- A comparação usa só o ID e a seção. Cabeçalho, plano e Obs. continuam editáveis à mão, sem migrar texto.
  Cartões em Pronto ou em Fechado sem entrega sem histórico são legado e ficam fora da regra.
- **Só avisa até migrar (projetos e Forge).** O `cmd_kanban` é o que o hook `hooks/quadro.py:24` roda a cada Write ou
  Edit do `KANBAN.md`, e o hook barra por qualquer item da lista. Por isso as duas violações só entram na lista quando
  existe `docs/kanban/arquivo/KANBAN-antes-do-ae2.md`. Sem esse arquivo, elas saem como `aviso:` só no comando de
  linha, com `quadro não migrado: rode forge-check kanban --migrar`, e o hook não barra nada novo.
- `forge-check kanban --migrar` (no P3): copia o `KANBAN.md` para esse arquivo e, para cada cartão aberto sem histórico
  ou com destino divergente, grava `forge-check movimento ID --de <último Para, ou —> --para <seção>` com o motivo
  `migração do quadro (AE2)`. Roda por Bash (o hook não o vê) e grava o arquivo mesmo com zero cartões, o que liga a
  regra. É o P6 no Forge; nos projetos, o agile-coach o roda na primeira triagem depois da atualização (texto no P5).
  O projeto novo já nasce migrado: o modelo traz o arquivo (P4).
- No fim, `forge-check kanban` imprime uma linha `quadro: <seção> N · ... · abertos N`, contada pelo `montar_quadro`.
  Número de backlog dito ao dono sai só dessa linha, copiada (BACKLOG-SO-PELA-FERRAMENTA). Não é conferência: é saída.
  Ela sai só no comando de linha (`main` do `forge-check`), nunca na lista que o `cmd_kanban` devolve, senão o hook a
  trataria como violação e barraria toda edição do quadro.

## 4. Uma entra, uma sai (DECISÃO DO DONO 21/11 20:54, regra 3)
| Entra | Sai |
|---|---|
| `kanban`: ID e seção cruzados com o histórico (seção 3) | a conferência manual do agile-coach "com a última triagem" (`skills/kanban-scrum/SKILL.md:41`, com prazo escrito: "até o `forge-check kanban` recusar destino divergente") e o aviso "sem movimento no histórico" do `--gerar` (`:4923-4924`), que a violação cobre. O aviso "quadro editado fora do movimento" (`:5010-5012`) fica: compara todas as células, e sem ele o `--gerar` trocaria a Obs. editada à mão sem avisar |
| `--cartao` ou `--parte` obrigatório, com o cartão existindo no quadro | a trava manual da ORDEM DO DONO 20/11 08:44, "até o AE2 entrar, todo cartão novo ou movido ganha a linha no histórico no mesmo commit", que hoje o Jarvis e o agile-coach conferem à mão depois de cada merge. Ela sai pelo prazo escrito nela, quando o P1 e o P3 entram: o movimento do merge passa a ser do `forge-fechar` e o resto, do `kanban` |

Sem trava nova no título: o P2 só troca o padrão. O título padrão deixa de ser o nome da branch (`titulo="$ref"`,
`:289`, causa do #682) e passa a ser o assunto do primeiro commit da branch. Não há recusa de título fora da forma,
porque nenhuma trava viva sai em troca. A recusa (o resto do PR-TITULO-CONVENCIONAL) vai em uma linha na lista do
dono de segunda.

## 5. Contas que tratam Fechado sem entrega como fim (TRIAGEM-APLICA-NO-QUADRO, DIR-20)
- `COLUNA_DO_ESTADO` (`bin/forge-check:4888`) ganha "fechado sem entrega" e "descartado" como estados finais.
  `montar_quadro` aplica a eles a mesma janela de 30 dias do Pronto (`:4942`).
- `forge-check metricas` (`bin/forge_governanca.py:320`): Fechado sem entrega encerra o trecho do cartão, que deixa de
  contar como aberto para sempre. `forge-check escape resumo` (`:6094`): só Pronto conta como pedido pronto.
- O `templates/projeto/KANBAN.md` ganha a seção "Fechado sem entrega" e a pasta `templates/projeto/docs/kanban/arquivo/`
  (com um LEIAME de uma linha), para plano ou pedido substituído.

## 6. Corte (até 150 linhas de código cada, sem contar testes)
`[G1]` = toca `bin/forge-check` e espera o G1 entrar na develop.

| Parte | Arquivos | Linhas | Depende de |
|---|---|---|---|
| P1 cartão obrigatório no fechar (seções 1 e 2: `--cartao`/`--parte` obrigatórios, existência no quadro, linha no corpo, `gh pr edit` no PR reusado, nota da parte na seção do quadro, `PR #N` no motivo do `--limpar` e do `ja_mesclado`) | `bin/forge-fechar`, `agents/tech-lead.md` (só o `--limpar --cartao` depois do merge do dono; a recusa da ferramenta ensina o resto), `tests/test_fechar_move_cartao.py`, `tests/test_forge_fechar.py`, `tests/mutantes/<spec do fechar>.json`, `changelog.d/<branch>.md` | ~110 | E114.1 (FECHAR-SEM-AUTO-MERGE, mesmo arquivo) |
| P2 título padrão pelo primeiro commit (seção 4, sem recusa) | `bin/forge-fechar`, `tests/test_forge_fechar.py` (o caso `melhoria/x` vira o assunto do commit), `changelog.d/<branch>.md` | ~15 | P1 (mesmo arquivo; depois dele) |
| P3 `[G1]` kanban cruza com o histórico só depois de migrado, `--migrar`, sai o aviso "sem movimento", entra a linha de contagem fora da lista (seções 3 e 4) | `bin/forge-check`, `tests/test_kanban*.py` (inclui o hook `hooks/quadro.py` sobre quadro não migrado: não barra), `tests/mutantes/<spec do kanban>.json`, `changelog.d/<branch>.md` | ~110 | G1; P6 pronta para rodar logo depois do merge |
| P4 `[G1]` Fechado sem entrega como fim (seção 5) | `bin/forge-check`, `bin/forge_governanca.py`, `templates/projeto/KANBAN.md`, `templates/projeto/docs/kanban/arquivo/LEIAME.md`, `templates/projeto/docs/kanban/arquivo/KANBAN-antes-do-ae2.md` (projeto novo nasce migrado), `tests/test_kanban*.py`, `tests/test_metricas*.py`, `tests/mutantes/<spec do P4>.json` (as condições de fim nas métricas e no `montar_quadro`, com teste do ramo de falha), `changelog.d/<branch>.md` | ~60 | G1 e P3 (mesmos `bin/forge-check` e `tests/test_kanban*.py`; depois dele) |
| P5 textos | `agents/tech-lead.md` (em projeto, o merge na develop vai para "Aguardando sua validação"), `skills/kanban-scrum/SKILL.md` (a linha 41 sai; cartão nasce por `movimento --de —`; o agile-coach roda `forge-check kanban --migrar` na primeira triagem depois da atualização), `agents/agile-coach.md` (número só da linha do `kanban`, sem mexer na frase do invariante), `templates/projeto/.github/pull_request_template.md`, `changelog.d/<branch>.md` (avisa os projetos do `--migrar`) | 0 (~25 de texto) | P1 e P3 |
| P6 migração do quadro do Forge (pasta de controle, sem PR, agile-coach) | `forge-check kanban --migrar --raiz ~/.forge-contrib` (grava `docs/kanban/historico.md` e `docs/kanban/arquivo/KANBAN-antes-do-ae2.md`) | 0 | logo depois do merge de P3 |

Ordem: P1 e P3 (esta, depois do G1) correm em paralelo; depois P2 (depois do P1) e P4 (depois do P3); P5 por último;
P6 junto com P3.
Cada parte é um PR com o fragmento de changelog dela.

## 7. Critério de parada
- bloqueia: fechamento para a develop sem cartão; e, em quadro migrado, cartão aberto sem nascimento e destino
  divergente do histórico. Quadro não migrado só avisa.
- sem-cartao · `forge-fechar` para a develop sem `--cartao` nem `--parte`, ou com ID ausente do quadro · oráculo: `tests/test_fechar_move_cartao.py` (para antes do passo 1; nada aberto)
- merge-sem-pr · motivo de merge do `--limpar` ou do `ja_mesclado` sem `PR #N` quando há PR MERGED da branch · oráculo: `tests/test_fechar_move_cartao.py` (os dois caminhos gravam `PR #N`)
- cartao-sem-nascimento · cartão em coluna aberta sem linha no histórico, com o quadro migrado · oráculo: `forge-check kanban` sobre quadro de teste (rc 1 e a linha da violação)
- destino-divergente · seção do quadro diferente do último `Para`, com o quadro migrado · oráculo: `tests/test_kanban*.py` (caso da triagem que não gravou o movimento)
- nao-migrado · quadro sem `docs/kanban/arquivo/KANBAN-antes-do-ae2.md` · oráculo: `tests/test_kanban*.py` (rc 0, a linha `aviso:`, e o `hooks/quadro.py` não barra a edição)
- gatilho · oráculo: um PR de teste fechado com `--cartao X` deixa X em Pronto com `PR #N` no motivo, e o `forge-check kanban` do mesmo quadro migrado sai com rc 0

## 8. Riscos e reversão
- Cartão errado citado: o motivo guarda o PR, e o cartão volta por `movimento`. A cópia em `arquivo/` (P6) guarda o quadro de antes.
- Merge do dono sem o `--limpar`: o cartão fica atrasado até o passo ser rodado. A auditoria AE6 o encontra (fora daqui).
- Lacuna em projeto: lá o `forge-fechar` não roda, e o movimento do merge fica só como texto no `agents/tech-lead.md`.
  É o mesmo esquecimento que motivou o AE2. O desenho aceito tinha a conferência no CI do modelo (C4), e este desenho a
  tira junto com o trailer. A lacuna é a condição do "reabre quando" do topo: merge de projeto sem movimento, achado
  pela AE6.
- Projeto atualizado e ainda não migrado: o hook não barra (seção 3), e o `forge-check kanban` avisa até o `--migrar`.
  Se alguém apagar a cópia `KANBAN-antes-do-ae2.md`, a regra volta a só avisar. O apagamento aparece no diff do PR.
- Primeira rodada do P3 no Forge: o P6 roda logo depois. Se a rodada sair vermelha mesmo assim, ela vira a lista do que
  falta migrar.
- **Critério de reversão:** duas entradas em `docs/kanban/escapes.md` em 14 dias com a causa "cartão movido pelo
  fechar sem entrega" levam o `--cartao` de volta a opcional (revert do P1). A primeira recusa falsa do `kanban` (cartão
  nascido pela ferramenta e recusado) reverte o P3. A primeira edição do `KANBAN.md` barrada pelo hook num quadro não
  migrado também reverte o P3.
- **Volta ao trailer (D1 e D3 do dono):** se o dono reabrir a troca, as seções 3.1 a 3.3 e 4.3 e os itens C4 a C6 de
  `docs/propostas/v0479-ae2-contador.md` (que este desenho não apaga) voltam a valer e são implementados como estão.
  O `--cartao` e o `--parte` ficam como fonte do movimento no Forge. O trailer `Cartão:`/`Cartão-parcial:` entra como
  fonte nos projetos, conferido no CI do modelo (C4). O CONTADOR-DA-VERSAO continua lendo o histórico, que os dois
  caminhos alimentam pelo `forge-check movimento`.

## 9. Gatilhos de segurança
São dois pontos: texto de argumento indo para o corpo do PR (`gh pr edit`, P1) e leitura de arquivo da pasta de controle
(P3, que já passa pelo `_ler_regular`, sem seguir link). O `--migrar` também grava: a cópia vai só para
`docs/kanban/arquivo/` sob a raiz, sem seguir link, e o histórico só pelo `forge-check movimento`. O `security-engineer` revisa P1 e P3 (`R-SEGURANCA`). O ID só
entra na forma `[A-Za-z0-9._-]` que já é conferida; nunca entra em `run:` de CI.
