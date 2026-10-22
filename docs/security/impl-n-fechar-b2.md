---
tipo: revisao-seguranca
contrato: 1
pedido: RET-FECHAR-B2
branch: melhoria/impl-n-fechar-b2
commit: 2587662dd0a7aa4905be9a7e1beae1be36dcc034
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-22
---
# Review de segurança: RET-FECHAR-B2

Escopo: os commits de `melhoria/impl-n-fechar-b2` desde `38c58247fdae5482ed441db4dd21bff4d55471d7` (cf4ff32 a 2587662): `bin/forge-fechar`, `docs/fechamento-integrador.md`, testes `tests/test_fechar*.py` e o fragmento `changelog.d/impl-n-fechar-b2.md`. Revisão defensiva e estática; o merge da `develop` feito em paralelo pelo `tech-lead` fica fora.

## Gatilhos
- Controles do Forge (`bin/forge-fechar`, o script de integração): merge na `develop`, `--match-head-commit`, guarda de base (`R-MAIN`, `R-FLUXO`), espera do rótulo `afrouxa-regra` e da Catraca (`R-CONFORMIDADE`).

## Achados
- A1 (bloqueante) bin/forge-fechar:657 · As guardas do passo 6 (base, fork, head) leem o PR pelo número pr_n, mas gh pr ready e gh pr merge (linhas 667 e 670) agem no PR que o gh resolve pelo nome da branch; um 2º PR aberto do mesmo head para main ou homolog é mesclado sem a guarda
- A2 (recomendado) bin/forge-fechar:296 · A espera do rótulo reconhece a Catraca só pelo nome do check (catraca); outro workflow com job de mesmo nome e gatilho labeled em pass libera a velha mapeada antes da execução real do evento do rótulo

## Detalhe dos achados
**A1 · regressão da guarda de base do passo 6 (severidade média, esforço P, dono: o autor da branch / `tech-lead`).**
Evidência: `bin/forge-fechar:657-662` lê `gh pr view "$pr_n"` e confere `pre_base` (recusa `main` e base diferente de `develop`), `pre_fork` e `pre_head`; em seguida `bin/forge-fechar:667` (`gh pr ready "$ref"`) e `:670` (`gh pr merge "$ref" ... --match-head-commit "$remoto_sha"`) seguem pelo nome da branch. O `gh` resolve um nome de branch para o PR **aberto mais recente** com aquele head (o finder ordena por criação, decrescente, e prioriza os abertos), não para `#pr_n`. Antes desta branch, a releitura do passo 6 também era por nome, então guarda e merge olhavam para o mesmo PR; agora olham para PRs possivelmente diferentes. O `docs/fechamento-integrador.md` (passo 3, "dois PRs do mesmo head não se confundem") afirma o contrário para o merge.
Caminho de ataque (erro operacional mais provável que má-fé): durante a espera dos passos 4 e 5 (até 7200 s com `--esperar-rotulo`), outra sessão ou agente com escrita abre um segundo PR da mesma `melhoria/*` para `main` ou `homolog` (o `gh pr create` dentro de outro script não passa pelo hook `parecer`). O passo 6 aprova `#pr_n` (base `develop`) e o `gh pr merge <branch>` mescla o PR novo, com o mesmo head, logo passando no `--match-head-commit`: entrega na `main` ou na `homolog` pulando degrau, contra `R-MAIN` e `R-FLUXO`. A conferência depois do merge (`estado_do_pr`, `:677-682`) só detecta o erro quando o merge já saiu. O que resta como barreira é a proteção de branch do GitHub, que o script não pode presumir.
Correção mínima: imediatamente antes do `gh pr ready` e do `gh pr merge`, ler o PR pela mesma resolução que eles usam (`ler "$gh" pr view "$ref" --json number,baseRefName,headRefOid --jq ...`) e parar se o número não for `$pr_n` (ou se a base não for `$alvo`); alternativa, parar quando `gh pr list --head "$ref" --state open` trouxer mais de um PR. O hook `parecer` continua satisfeito, porque o merge segue por nome. Teste: dublê do `gh` com dois PRs abertos do mesmo head (o mais novo com base `main`) e prova de que o script para antes de `pr ready`/`pr merge`. A janela que sobra entre essa leitura e o merge é de milissegundos (risco residual a registrar no doc).

**A2 · Catraca reconhecida só pelo nome do check (severidade baixa, esforço P a M, dono: autor da branch; recomendação, não bloqueia).**
Evidência: `bin/forge-fechar:296` e `:309` tratam como Catraca toda linha cujo nome é `catraca`; com o rótulo lido e uma execução "nova" em `pass` ou pendente, a velha em `fail` vira `skipping` (`:312-314`). Caminho: uma mudança que acrescenta um workflow com job chamado `catraca`, disparado em `labeled` e sempre verde, faz a linha falsa aparecer em `pass` antes da execução real do evento do rótulo; com a velha mapeada como `skipping`, o laço sai e o merge acontece sem a Catraca real ter concluído. Realismo baixo: mexer em `.github/workflows/` já dispara a própria Catraca (rótulo do dono, que revisa o diff) e o token do bot não tem o escopo `workflow`; a regra antiga (10 leituras) tinha fragilidade parecida. Correção sugerida: amarrar a linha da Catraca ao workflow (por exemplo `gh pr checks --json name,state,link,workflow` e exigir o nome do workflow da Catraca) ou exigir que a execução nova seja de `run_id` maior que todos os de `run_antes`; e manter a Catraca como check obrigatório na proteção da `develop`.

Conferido sem achado:
- B5, cadeia do sha: `sha_conferido` é lido com `rev-parse --verify -q "refs/heads/$ref^{commit}"` antes do passo 1, passado ao `forge-check pr --ref <sha>` (que lê pareceres e diff por `git show`/`git diff` sobre a ref, sem depender do nome da branch; `bin/forge-check:555-621`), relido depois do passo 1 e no passo 2, igualado ao remoto e usado no `--match-head-commit`. Fecha a troca de head entre parecer e merge.
- B3, MERGED preso: `estado_do_pr` exige head, base e commit de merge de `#pr_n`; `pr_n` só vem de número validado (`^[0-9]{1,9}$`) ou de uma única URL `/pull/<n>`; PR de fork (`isCrossRepository`) para nos passos 3 e 6.
- B4, `dicas_de_log`: só imprime; só o número da execução (dígitos, regex ancorada no padrão `/runs/<n>/job/<j>`) entra no comando; o `TMPDIR` vai entre aspas simples com `'` escapado como `'\''`; o nome do check não entra.
- B1, `aviso_do_rotulo`: nomes sem C0 (exceto tab e LF), DEL e C1 em UTF-8, o que barra sequência de escape de terminal na frase montada; a lista crua do `gh` segue como antes (documentado).
- B2, `estados_da_espera`: o merge continua exigindo tudo `pass`/`skipping` na última leitura; execução nova em `fail`, `cancel` ou outra conclusão para; nada reexecuta a Catraca.
- R2 do lote a: `tmp2b` e `dorme_pid` nascem vazios no topo (`bin/forge-fechar:36`); valor do ambiente não vira alvo do `rm -rf` nem do `kill`.

## Riscos aceitos e ferramentas
Nenhum risco aceito.
Ferramentas: `shellcheck` (no PATH): 3 avisos, os mesmos 3 da base `38c5824` (SC2034, SC2015, SC2086), nenhum novo. `python3 -m unittest` dos 7 módulos `tests/test_fechar*`: 124 testes, OK. Lacunas: `gitleaks` e `semgrep` não estão no PATH (não instalados, `R-CUSTO`); a diferença não traz segredo nem credencial (leitura manual).
