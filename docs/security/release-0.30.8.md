---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.30.8
branch: melhoria/release-0.30.8
commit: 57baeb676fede745474850105479ca726ca30a5a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: release-0.30.8

Leva inteira contra a main: `git diff 6c17ca7...57baeb6`, PRs #373 a #398 (22 commits, o último é o commit da release). Cada PR que tocou controle teve parecer de segurança próprio; aqui se confere o conjunto: se o código que chega à main é o revisado, o que os PRs sem parecer de segurança mudam em controle, e o que muda quando os PRs se juntam.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): `docs/regras/` (#385), `hooks/_comum.py` e `hooks/parecer.py` (#384, #395), `.githooks/pre-push` (#397), `bin/forge-check` (#375, #376, #380, #381, #389, #395), `bin/forge-fechar` (#379), `bin/forge-mutante` (#382, #383), `bin/forge-testes` (#373, #387) e `scripts/promover-homolog.py` (#374, #377). `bin/forge-check pr release-0.30.8 --ref HEAD --base main` pede este parecer pelo gatilho de `docs/regras/R-DECISAO.md`.

## Achados
- A1 (recomendado) scripts/promover-homolog.py:157 · o filtro descarta toda linha do forge-check pr que começa por docs/security ou docs/devops, inclusive a de parecer da release que existe mas tem commit vencido; o passo 2 só confere `parecer: aprovado`. A segurança da leva fica só no processo.
- A2 (recomendado) hooks/conformidade.json:1 · segue aberto o A2 de pn4-decisao-aprovacao: docs/kanban/conferencias.md, que o forge-check brief lê para decidir (#380), continua sem dono no hook e pode ser escrito por qualquer papel.
- A3 (recomendado) bin/forge-check:1297 · segue aberto o A1 do parecer de #389: intervalo com mais de 4300 dígitos faz o int() levantar ValueError (saída opaca, rc 1). Falha fechada, não passa achado.

## Detalhe dos achados
Sem bloqueante. O que foi conferido:

- **O código que chega à main é o revisado.** Para cada PR com parecer de segurança, comparei as linhas mudadas do squash na develop com as do commit do parecer, sem `docs/{reviews,security,qa}/` nem `changelog.d/`: diferença zero em todos. São eles: #375 (23a66bb), #376 (fab197c), #380 (e2f3390), #384 (cec2b42), #385 (ad3c5a5), #387 (21a4caa), #389 (8e8fe8d, parecer anterior de `docs/security/k164-mesma-base.md`), #390 (c91d055), #392 (41e3d2f), #394 (4bed454), #395 (6fa601f) e #397 (5de4830). Os pareceres de #389, #390 e #392 foram sobrescritos no mesmo arquivo pelos PRs seguintes; os achados deles foram lidos pelo histórico.
- **Hooks no conjunto.** `git diff 6fa601f 57baeb6 -- hooks/` é vazio, e 6fa601f (#395) está sobre 8c07b44 (#384): os hooks que vão à main são exatamente os que o parecer k164-mesma-base revisou, já somados à folga do `"$?"` da P-N7. Depois de 6fa601f só entram o C-14 do pre-push (#397), o intervalo `a-b` do achado (#389) e o filtro do `--vermelho` (#387), cada um revisado sobre o próprio código. O C-14 fecha o A1 do parecer impl-pre-push (ordem c6 junto da c4).
- **PRs sem parecer de segurança que tocam código de controle**, lidos aqui:
  - #381 (`bin/forge-check`): só acrescenta uma linha `aviso:` no `forge-check brief`, com o nome da branch passado por `caminho_impresso`; não decide portão.
  - #379 (`bin/forge-fechar`): a saída do `git worktree prune -v` vai ao log pela mesma `gravar_linha`, com máscara de segredo e trava; a tela recebe só uma contagem. Reduz o que chega ao terminal; o código de saída do prune vira aviso, como antes.
  - #382 e #383 (`bin/forge-mutante`): o `--cobertura` é checagem do autor (nenhum hook, pre-push nem CI o chama). O equivalente declarado deixou de valer como prova, e o declarado com `testes` que morre vira inválido (rc 2): endurecimento. A troca de `casa()` só muda que mutante conta como "declarado", e a rodada do QA continua sendo a prova.
  - #373 (`bin/forge-testes`): só põe o módulo novo no mapa, o que faz rodar mais testes. A skill `esperar-estado` (#373, #378) não usa `sh -c`, `--watch` nem `run_in_background` na espera, e o número do PR vai entre aspas.
  - #374 e #377 (`scripts/promover-homolog.py`): a leitura dos checks passa a JSON, filtra o evento `pull_request` e para com saída que não seja lista. O `forge-check pr` contra a main roda em modo isolado, com prazo, e falha fechada quando não roda. O script continua sem mesclar e sem aplicar rótulo. A1 é o que fica.
- **A1 em detalhe.** Evidência: `scripts/promover-homolog.py:41` e `:157-158`; `bin/forge-check:722-725` (`cmd_pr` emite `<caminho>: commit: <motivo>` para parecer vencido); `scripts/promover-homolog.py:118` (o passo 2 não lê o `commit:`). Caminho: depois deste parecer, um PR que muda controle entra na develop antes da promoção, e o `promover-homolog.py` imprime que review e QA valem contra a main sem dizer que a segurança da leva venceu. Quem ganha: só o que já passou pelos portões do próprio PR chega à homolog sem o olhar do conjunto. O dono ainda mescla a main à mão. Severidade baixa. Correção mínima: no filtro, descartar só a linha `sem parecer` de devops e segurança, e manter as de parecer da release que existe (commit, autoria, formato); ou exigir o de segurança quando o `forge-check pr` aponta gatilho de controle. Esforço P. Dono: o autor do `promover-homolog.py` (tech-lead), por cartão na develop.
- **A2 e A3** vêm dos pareceres de cada PR e não mudam no conjunto: o A2 falha para o lado do processo (a linha errada na tabela faz o brief ser comparado com as decisões erradas) e é tratado no cartão KANBAN-DONO-HOOK; o A3 falha fechado.
- **Seguem rastreados, sem mudança no conjunto:** A5, A6, A8 e A9 de pn7-dolar-interrog (cartão HOOK-SAIDA-CODIGO e pedido HOOK-EXTGLOB), A1 de k164-mesma-base (ref remota local no modo de merge simulado), A1 e A2 de pn1-desde-base, A3 de pn4-decisao-aprovacao, A1 de pn6-base-recusada, A2 de impl-pre-push e A1 e A2 de impl-catraca-2 (#392, #394). Nenhum deles vira caminho novo com os outros PRs da leva.
- **Afrouxamentos.** O único que afrouxa controle de segurança é o #384 (P-N7). A entrada dele no CHANGELOG diz "afrouxa, rótulo afrouxa-regra" e cita a emenda H1-1 da ADR 0011. Os demais PRs rotulados mexem em caminho protegido, e o parecer de cada um os julgou.
- **Versão e CHANGELOG.** `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.30.8; seção `[0.30.8] - 2026-10-31` com 21 entradas e `[Não publicado]` vazio (a contagem fragmento a fragmento está no review da leva). Nenhuma entrada traz segredo nem caminho de máquina.
- **Custo e neutralidade.** Nenhum script novo chama serviço pago. O `promover-homolog.py` só chama `gh` e o `forge-check` local (`R-CUSTO`).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática por `git diff`, `git show`, leitura do código final e `bin/forge-check pr release-0.30.8 --ref HEAD --base main`. Sem `gitleaks`, `shellcheck`, `actionlint`, `zizmor`, `semgrep` nem `osv-scanner` no PATH local (lacuna; as checagens de segredo e de shell rodam no CI). A leva não toca `.github/`, contêiner, IaC nem manifesto de dependência.
