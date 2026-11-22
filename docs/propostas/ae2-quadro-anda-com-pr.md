# AE2: o quadro anda com o PR (desenho curto, E121.1 do v0478)

Cartão AE2-QUADRO-ANDA-COM-PR, com os juntados TRIAGEM-APLICA-NO-QUADRO, BACKLOG-SO-PELA-FERRAMENTA,
DIR-20-KANBAN-DESTINO e PR-TITULO-CONVENCIONAL. Item AE2 de `docs/pedidos/melhorias-anti-erro.md` (pasta de controle).

**O que muda em relação a `docs/propostas/v0479-ae2-contador.md`:** este desenho substitui as seções 3.1 a 3.3 e 4.3 e
os itens C4, C5 e C6 dele. Não há trailer de commit, conferência nova no envio ou no CI, nem `quadro sincronizar`: o
merge move o cartão dentro da ferramenta que já integra. Os itens C1 a C3 e C7 ficam com o cartão CONTADOR-DA-VERSAO, que
passa a contar a partir de `docs/kanban/historico.md` (movimentos para Pronto com `PR #N` no motivo) em vez de trailers.

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
  partes (o próprio AE2) não vai para Pronto na primeira delas.
- Quando o dono mescla pela interface, o passo depois do merge é o `forge-fechar <pedido> --ref <branch> --limpar
  --cartao ID`, que já existe (`:1347-1361`): ele lê o PR MERGED e move o cartão. Sem `--cartao`, o comando para.
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
- No fim, `forge-check kanban` imprime uma linha `quadro: <seção> N · ... · abertos N`, contada pelo `montar_quadro`.
  Número de backlog dito ao dono sai só dessa linha, copiada (BACKLOG-SO-PELA-FERRAMENTA). Não é conferência: é saída.

## 4. Uma entra, uma sai (regra do dono de 20/11 citada no brief; regra 3 de 21/11 20:54)
| Entra | Sai |
|---|---|
| `kanban`: ID e seção cruzados com o histórico (seção 3) | os dois avisos do `kanban --gerar`, "sem movimento no histórico" (`:4923-4924`) e "quadro editado fora do movimento" (`:5010-5012`), que a violação cobre; e a conferência manual do agile-coach "com a última triagem" (`skills/kanban-scrum/SKILL.md:41`, que tem prazo escrito: "até o `forge-check kanban` recusar destino divergente") |
| `forge-fechar`: título fora de `tipo(escopo): descrição` para no passo 3 (PR novo) e no passo 5 (PR reusado), na mesma leitura de título e corpo que o passo 5 já faz (`:1554`) | o título padrão pelo nome da branch (`titulo="$ref"`, `:289`, causa do #682). O padrão passa a ser o assunto do primeiro commit da branch, e a recusa só ocorre quando nem `--titulo` nem esse assunto estão na forma |
| `--cartao` ou `--parte` obrigatório, com o cartão existindo no quadro | nada a tirar: é a opção que já existe passando a obrigatória, e a conferência da forma do ID já existe (`:196`) |

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
| P1 cartão obrigatório no fechar (seções 1 e 2: `--cartao`/`--parte` obrigatórios, existência no quadro, linha no corpo, `gh pr edit` no PR reusado, nota da parte) | `bin/forge-fechar`, `tests/test_fechar_move_cartao.py`, `tests/test_forge_fechar.py`, `tests/mutantes/<spec do fechar>.json`, `changelog.d/<branch>.md` | ~90 | E114.1 (FECHAR-SEM-AUTO-MERGE, mesmo arquivo) |
| P2 título na forma (seção 4, linha 2) | `bin/forge-fechar`, `tests/test_fechar_rascunho.py` (PR reusado), `tests/test_forge_fechar.py`, `changelog.d/<branch>.md` | ~40 | P1 (mesmo arquivo; depois dele) |
| P3 `[G1]` kanban cruza com o histórico, saem os avisos do `--gerar`, entra a linha de contagem (seções 3 e 4) | `bin/forge-check`, `tests/test_kanban*.py`, `tests/mutantes/<spec do kanban>.json`, `changelog.d/<branch>.md` | ~70 | G1; P6 pronta para rodar logo depois do merge |
| P4 `[G1]` Fechado sem entrega como fim (seção 5) | `bin/forge-check`, `bin/forge_governanca.py`, `templates/projeto/KANBAN.md`, `templates/projeto/docs/kanban/arquivo/LEIAME.md`, `tests/test_kanban*.py`, `tests/test_metricas*.py`, `changelog.d/<branch>.md` | ~60 | G1; em paralelo com P3 em outra branch, ou na mesma branch, depois dela |
| P5 textos | `agents/tech-lead.md` (fechar sempre com `--cartao`/`--parte`; o `--limpar` depois de merge do dono), `skills/kanban-scrum/SKILL.md` (a linha 41 sai; cartão nasce por `movimento --de —`; merge em projeto vai para "Aguardando sua validação"), `agents/agile-coach.md` (número só da linha do `kanban`, sem mexer na frase do invariante), `templates/projeto/.github/pull_request_template.md`, `changelog.d/<branch>.md` | 0 (~25 de texto) | P1 e P3 |
| P6 migração do quadro do Forge (pasta de controle, sem PR, agile-coach) | `~/.forge-contrib/docs/kanban/historico.md`, por `forge-check movimento --de — --para <seção atual>` para cada cartão aberto sem histórico; antes, cópia do `KANBAN.md` em `docs/kanban/arquivo/` | 0 | logo depois do merge de P3 |

Ordem: P1 e P3 (esta, depois do G1) correm em paralelo; depois P2 e P4; P5 por último; P6 junto com P3.
Cada parte é um PR com o fragmento de changelog dela.

## 7. Critério de parada
- bloqueia: fechamento para a develop sem cartão, cartão aberto no quadro sem nascimento, quadro com destino divergente
  do histórico, e PR com título fora da forma.
- sem-cartao · `forge-fechar` para a develop sem `--cartao` nem `--parte`, ou com ID ausente do quadro · oráculo: `tests/test_fechar_move_cartao.py` (para antes do passo 1; nada aberto)
- cartao-sem-nascimento · cartão em coluna aberta sem linha no histórico · oráculo: `forge-check kanban` sobre quadro de teste (rc 1 e a linha da violação)
- destino-divergente · seção do quadro diferente do último `Para` · oráculo: `tests/test_kanban*.py` (caso da triagem que não gravou o movimento)
- titulo-fora-da-forma · título nem `--titulo` nem primeiro commit em `tipo(escopo): descrição` · oráculo: `tests/test_forge_fechar.py` (o caso `melhoria/x` reprova)
- gatilho · oráculo: um PR de teste fechado com `--cartao X` deixa X em Pronto com `PR #N` no motivo, e o `forge-check kanban` do mesmo quadro sai com rc 0

## 8. Riscos e reversão
- Cartão errado citado: o motivo guarda o PR, e o cartão volta por `movimento`. A cópia em `arquivo/` (P6) guarda o quadro de antes.
- Merge do dono sem o `--limpar`: o cartão fica atrasado até o passo ser rodado. A auditoria AE6 o encontra (fora daqui).
- Primeira rodada do P3 no Forge vermelha: por isso o P6 roda junto. Se a rodada sair vermelha mesmo assim, ela vira a
  lista do que falta migrar.
- **Critério de reversão:** duas entradas em `docs/kanban/escapes.md` em 14 dias com a causa "cartão movido pelo
  fechar sem entrega" levam o `--cartao` de volta a opcional (revert do P1). A primeira recusa falsa do `kanban` (cartão
  nascido pela ferramenta e recusado) reverte o P3.

## 9. Gatilhos de segurança
São dois pontos: texto de argumento indo para o corpo do PR (`gh pr edit`, P1) e leitura de arquivo da pasta de controle
(P3, que já passa pelo `_ler_regular`, sem seguir link). O `security-engineer` revisa P1 e P3 (`R-SEGURANCA`). O ID só
entra na forma `[A-Za-z0-9._-]` que já é conferida; nunca entra em `run:` de CI.
