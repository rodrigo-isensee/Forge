---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.33.0
branch: melhoria/release-0.33.0
commit: c004a70a01459b483322b006a012bac382bb36e6
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-05
---
# Review de segurança: release-0.33.0

A leva da 0.33.0 (`1b62cfd..c004a70`: #436 a #445 e o commit de release) foi lida contra a main 0.32.0. A pergunta foi uma só: a soma dos PRs abre, nos controles do Forge, um caminho que nenhum PR abria sozinho? Cada PR já tem o próprio parecer em `docs/security/`. Reli só onde a leva junta mudanças do mesmo arquivo ou da mesma função.

## Gatilhos
`R-SEGURANCA`: controles do Forge (`hooks/conformidade.py`, `hooks/conformidade.json`, `hooks/parecer.py`, `hooks/agentes.py`, `bin/forge-check`), mais o modelo de pre-push dos projetos e o workflow Release (este fica com o parecer de devops). O `bin/forge-fechar` não mudou na leva. Ele chama `forge-check pr --ref <sha> --base` (`bin/forge-fechar:687`), e esse caminho foi conferido.

## Achados
- A1 (recomendado) bin/forge-check:768 · a conferência do head (L08) reusa LIVRES, que o PARECER-UX-LIVRE ampliou com docs/ux/: commit só em docs/ux/ após a entrega conferida também não pede nova conferência, e a mensagem (:773) omite essa pasta. Diga-o na mensagem e na ajuda.

## Detalhe dos achados
**Sobreposições conferidas.**
- `bin/forge-check`, cinco PRs (#437, #439, #441, #442, #445):
  - #439 (parecer pela branch) e #445 (`branch_do_sha`, `promocao`, conferência do head) compõem bem. Com o sha ambíguo, o `pr` volta ao mais recente do pedido, que é o comportamento anterior à leva e não um afrouxamento novo (já registrado no parecer do L08). A `promocao` compara sha40; o A4 do L08 (ref remota movida localmente) segue recomendado e não piora com a leva.
  - #437 (falha do git fechada) e #445: o `conferencia_do_head` depende de `commit_vale` (`:472-494`), e esse caminho já falha fechado quando o `rev-parse` ou o `diff` falham. O `ato-github` não lê diff e não grava `entrega conferida`. Por isso não serve de atalho para o merge.
  - #437 (`PedidoFora`) e #445 (`pedido_da_conferencia`, `:694-728`): um `--pedido` fora das raízes cai na busca pelos briefs. O pedido citado por eles também passa por `caminho_do_pedido`, que levanta `PedidoFora`, e daí sai a violação. Não há leitura fora das raízes.
  - #442 e #445: é o A1. A decisão do dono (Q12 = A) põe `docs/ux/` em LIVRES do `forge-check pr`, e a conferência agora faz parte desse comando. Por isso o efeito segue a letra da decisão. Só que o parecer do #442 (T-2) partiu da premissa de que LIVRES valia apenas para pareceres. O impacto é baixo: `docs/ux/` é escrita só do papel de UX e nada no Forge a executa, mas ela é lida como critério pelo QA e pelo papel de front. Correção mínima: a mensagem de `:773` e a ajuda do `pr` listam LIVRES inteira (`docs/reviews/`, `docs/qa/`, `docs/devops/`, `docs/security/`, `KANBAN.md`, `docs/kanban/`, `docs/ux/` e `changelog.d/<pedido>.md`). Se a conferência não deve isentar `docs/ux/`, a decisão volta ao dono (`R-DECISAO`). Severidade baixa. Esforço P. Dono: `forge:tech-lead`.
- `hooks/conformidade.py`, dois PRs (#438 GH-MERGE-ADMIN, #444 CONFERENTE-LEITURA-GIT): as duas mudanças são disjuntas. `forma_de_leitura_git` só vale no papel só de leitura e recusa criar, apagar ou mover branch e qualquer subcomando de `worktree` além de `list`. O `gh_admin` roda antes de toda saída antecipada de `gh`. A lista do conferente não ganhou `gh pr merge` nem `gh api`.
- `hooks/parecer.py` (#438) e `cmd_pr` (#439, #445): o hook chama `cmd_pr(raiz, pedido, ref, base)` (`hooks/parecer.py:419`). A branch é inferida por `branch_da_ref`, e a assinatura nova só acrescenta parâmetros no fim, sem deslocar os que já existiam.
- `hooks/agentes.py` (#441) e a gramática do conferente (#444): a mensagem leva só o cabeçalho e o hash. O hook continua conferindo o hash contra o arquivo em `docs/briefs/`, que é escrita só do Jarvis.
- Modelo de pre-push (#436): pula só o `pre-push.local` do projeto, e o bloqueio da `main` e do push não fast-forward seguem antes. Não interage com os controles do Forge.

**Versão (E3).** `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` estão em 0.33.0, e o `CHANGELOG.md` tem `[0.33.0] - 2026-11-05` com Adicionado, Alterado e Corrigido, sem quebra declarada. Os fragmentos de `changelog.d/` foram consumidos (sobra o `README.md`). Minor bate com a leva: melhorias compatíveis e correções.

## Riscos aceitos e ferramentas
Nenhum risco aceito novo. A isenção de `docs/ux/` é a decisão Q12 = A do dono. Rodei `test_forge.py` nas classes `ConferenciaPresaAoHead` e `PareceresComDocsUx` (17, OK) e `test_guarda_conferente.py` (OK). `gitleaks`, `semgrep`, `zizmor`, `actionlint` e `osv-scanner` não estão no PATH, e isso fica registrado como lacuna. A leva não traz dependência nova; o workflow é do parecer de devops.
