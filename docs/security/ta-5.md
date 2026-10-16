---
tipo: revisao-seguranca
contrato: 1
pedido: ta-5
branch: melhoria/ta-5-fechamento
commit: 27f38686da3f52bcbd5cdd3aade87fc42e8c45ee
parecer: reprovado
revisor: forge:security-engineer
data: 2026-10-16
---
# Review de segurança: ta-5

Escopo: `git diff 15660a346640c165ddbe322a03511c1448db1a41...27f3868`, 6 arquivos; foco em `bin/forge-fechar` (faz merge pelo `gh`: controle do fluxo). Ameaça considerada: o script mesclar onde não deve (main), mesclar algo diferente do que os portões viram, executar entrada como shell, apagar fora do previsto, ou ter um desvio de portão em uso real.

## Gatilhos
`R-SEGURANCA`: script novo que mescla PR e apaga branch e worktree (controle do fluxo, `R-FLUXO`, `R-MAIN`).

## Resumo
**Veredito: reprovado**, por um achado médio (M-TA5-1) que quebra a garantia "nunca mescla na main"; correção de duas linhas. Dois achados baixos e duas observações informativas. Os testes do autor passam (`python3 -m unittest tests.test_fechar`: 10 testes, OK).

## Conferido
- **Main recusada na entrada.** `--base` só aceita `origin/develop` e `origin/homolog` (`bin/forge-fechar:34-39`); `main` e `origin/main` morrem com `R-MAIN`, e `--ref` não pode ser `main|develop|homolog` (`:33`). O alvo vem só dessa tabela (`:35-36`), nunca da entrada.
- **Sem rótulo, sem `--force`, sem `--no-verify`.** Nenhuma chamada `gh` aplica rótulo (só `view`, `create`, `checks`, `merge`); o único `gh label`/`--add-label` é ausente (o teste `:159` confere o texto). O passo 5 só lê.
- **Sem injeção.** Nenhum `eval`, `bash -c` nem `shell`; pedido, branch, base, título e corpo vão como argumentos de lista entre aspas (`:74`, `:86`, `:114`); o corpo é montado numa variável e passado por `--body`, sem reinterpretação. `--espera` é validado como número (`:40`). Testei `--ref 'x;touch ...'`, `x$(...)` e `x^`: param no passo 2 (`rev-parse`/`ls-remote` não acham a ref), nada executado.
- **Limpeza contida.** Só atua sobre a worktree que o próprio `git worktree list` associa à branch (`:121`), com `git worktree remove` sem `--force` (recusa árvore suja) e só depois do estado `MERGED` (`:116`); o passo 2 garante local = remoto, então o `branch -D` (necessário após squash) não perde commit. Falha de limpeza é aviso.
- **Falha fechada nos checks.** Qualquer estado fora de `pass|skipping|pending|queued|in_progress` para (`:96`); lista vazia ou ilegível para (`:93`, `:95`).
- **Dry-run** não roda `forge-check`, git remoto nem `gh` (`:58-68`, sai antes de `:70`).
- **Sem custo (`R-CUSTO`):** só `git` e `gh` já usados pelo fluxo.

## Achados
### M-TA5-1. PR aberto é reusado sem conferir a base; o merge pode cair na main (média)
- **Evidência:** `bin/forge-fechar:83-84` (só confere `state==OPEN`, não `baseRefName`), `:114` (`gh pr merge "$ref" --squash`, sem base explícita). O passo 1 valida pareceres contra `--base`, mas isso não prende o PR aberto a `$alvo`.
- **Caminho:** existe um PR aberto da mesma branch para a `main` (aberto à mão, por engano, ou por outro membro do time). O integrador roda `forge-fechar --base origin/develop`; o script diz "PR #N já aberto; reusado" e faz o merge desse PR na main, contrariando `R-MAIN` e o que a documentação promete ("nunca mescla na main", `docs/fechamento-integrador.md`). Só não acontece se a proteção de branch da main barrar o token; o script não pode contar com isso. Também vale para PR de develop quando se pediu homolog (método de merge errado).
- **Sugestão:** no passo 3 ler `--json number,state,baseRefName` e exigir `baseRefName == $alvo`, senão `die`; repetir a conferência antes do merge (passo 6) e recusar se `baseRefName` for `main`. Acrescentar teste com gh falso devolvendo PR aberto com base `main`.
- **Esforço:** P · **Dono:** tech-lead (autor).

### B-TA5-1. Merge sem fixar o head verificado (baixa)
- **Evidência:** `bin/forge-fechar:114` (`gh pr merge` sem `--match-head-commit`); o head conferido é `remoto_sha` (`:78`).
- **Caminho:** entre os passos 2 e 6 (a espera dos checks chega a 1800 s) alguém com push na branch envia outro commit; os checks do passo 4 podem ser do commit antigo e o merge leva código sem parecer nem check. Exige acesso de escrita ao repositório e janela longa, mas anula a ligação parecer-commit (`R-SEGURANCA`).
- **Sugestão:** `gh pr merge "$ref" "$metodo" --match-head-commit "$remoto_sha"`.
- **Esforço:** P · **Dono:** tech-lead.

### B-TA5-2. `FORGE_CHECK` e `FORGE_GH` sobrescrevem o portão em uso real, em silêncio (baixa)
- **Evidência:** `bin/forge-fechar:42-43`.
- **Caminho:** uma variável herdada do ambiente (por exemplo `FORGE_CHECK=true` esquecida de um teste ou de um perfil de shell) troca o `forge-check pr` por um comando que sempre passa, e o script mescla sem parecer, sem nenhum aviso. Não há atacante remoto (quem controla o ambiente já executa código), mas é desvio de portão por descuido.
- **Sugestão:** quando qualquer das duas (ou `FORGE_FECHAR_INTERVALO`) estiver definida, imprimir em stderr `aviso: FORGE_CHECK/FORGE_GH substituídos (só para teste)`; opcionalmente exigir `FORGE_FECHAR_TESTE=1` para honrá-las e recusar o `--base`/merge reais nesse modo.
- **Esforço:** P · **Dono:** tech-lead.

### I-TA5-1. `ref` com `-` inicial e `push --delete` sem `refs/heads/` (informativa)
- **Evidência:** `bin/forge-fechar:119`, `:128`, `:83`, `:92`; o `--ref` não é validado por `git check-ref-format`.
- **Caminho:** `--ref -x` chegaria como opção ao `gh`/`git` se o passo 2 não parasse antes (para: `refs/heads/-x` não existe), e um nome de branch igual a uma tag faria o `push --delete` recusar por ambiguidade. Sem ganho de privilégio; entrada é do operador.
- **Sugestão:** `git check-ref-format --branch "$ref"` na entrada e `git push origin --delete "refs/heads/$ref"`.
- **Esforço:** P · **Dono:** tech-lead.

### I-TA5-2. Passo 5 depende de texto livre (informativa)
- **Evidência:** `bin/forge-fechar:109`.
- **Caminho:** o pedido de rótulo só é percebido se o título ou corpo contém `afrouxa-regra`; um PR que afrouxa regra sem citar o rótulo passa por aqui. O controle real do rótulo é o CI (a catraca), que continua exigido nos checks do passo 4; nenhum portão saiu. Registro apenas.
- **Esforço:** P · **Dono:** tech-lead (opcional).

## Riscos aceitos e ferramentas
- Riscos aceitos: nenhum. M-TA5-1 e B-TA5-1 devem ser corrigidos; os demais podem virar cartão.
- Ferramentas: revisão estática do diff; execução do `--dry-run` e de entradas incomuns de `--ref` em repositório temporário (o script nunca rodou sem `--dry-run` contra o GitHub real); testes do autor. Lacuna: `gitleaks`, `zizmor`, `shellcheck` e `semgrep` não estão no PATH (nada varrido por eles; o diff não toca workflow nem traz segredo, conferido por leitura).
