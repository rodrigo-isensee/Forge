---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-teto-fora-desenho
commit: 604f8c560274c5854ff3fc2fd42599b79ef39aa0
parecer: reprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 · desenho TETO-FORA-DO-GIT, volta (E159.4, PR #842)

Review por delta do head 604f8c56 (volta E159.3), base develop 789fc141. Delta lido por `forge-check parecer delta docs/reviews/v0480-teto-fora-desenho.md`: intervalo `2234208a..604f8c56`, no domínio só `docs/propostas/teto-fora-do-git.md` (13 linhas a mais, 8 a menos). Classe T, só texto: sem código, guarda nem mutante. Testes dos arquivos tocados: `test_clareza` e `test_changelog`, 100 testes, OK; a suíte inteira fica no CI do PR. Instância que não escreveu a volta.

## Achados
- A5 (bloqueante) docs/propostas/teto-fora-do-git.md:40 · "de uma cópia em `.forge/wt/<item>` chega à cópia principal" é falso: no projeto a cópia é clone (`bin/forge-copia:3`) e `diretorio_comum` de um clone é o `.git` dele (S2); o script lê o `limites.json` do clone. C1 (:79) e a medida (2) de :68 não fecham.
- A6 (bloqueante) docs/propostas/teto-fora-do-git.md:80 · o `.git` forjado só dá None se for incoerente: um `gitdir:` para `<x>/.git/worktrees/w` com `gitdir` de volta e `commondir` `../..`, tudo em pasta gravável, passa em `diretorio_comum` (S3) e o leitor lê `<x>/.forge/limites.json`. Diga o que ancora a cópia principal.

## Sondas
- S1 · `echo "CPD=${CLAUDE_PROJECT_DIR:-<vazio>}"` no Bash da sessão (de novo, no head 604f8c56) · espera: vazio, a premissa da volta para os scripts · obtido: `CPD=<vazio>`
- S2 · `diretorio_comum("/root/.forge-contrib/wt/v0480-teto-fora-desenho-rev")` (um clone, `.git` pasta) · espera: a cópia principal `/workspaces/Forge/.git`, pela linha 40 · obtido: `/workspaces/.forge-contrib/wt/v0480-teto-fora-desenho-rev/.git`
- S3 · `diretorio_comum(<scratch>/wt)` com `wt/.git` = `gitdir: <scratch>/evil/.git/worktrees/w`, `w/gitdir` = `<scratch>/wt/.git`, `w/commondir` = `../..` · espera: None, pela linha 80 · obtido: `<scratch>/evil/.git`

## Conferência pedida no brief
- **A1 (raiz fora da sessão):** fechado para a cópia principal e a worktree vinculada: o hook segue pela `raiz_declarada()` e os scripts partem de `git rev-parse --show-toplevel` (:37-38). S1 rodada de novo: o Bash segue sem `CLAUDE_PROJECT_DIR`, e a volta já parte disso. O resto do A1 (clone) virou A5.
- **Worktree forjada impondo teto:** o hook não é alcançado (lê a raiz da sessão, que o subagente não muda). Os scripts sim: de um clone (A5) ou de uma worktree forjada coerente (A6), `forge-check fila`, `suite-partes` e `forge ritmo` leem um `limites.json` que o agente grava. Hoje o `forge-check` já lê o `config.json` da pasta (`bin/forge-check:497`), então não piora o que existe; mas o desenho diz que fecha (:40, :79, :80), e o caso de abuso escrito daí reprova a implementação. Sugestão: nos scripts, cortar `.forge/wt/` do topo como o `bin/forge-copia:36-45` (projeto) e dizer o que vale no clone do Forge, fora da cópia principal; ou declarar o valor do script só informativo, com o hook como autoridade, e reescrever C1 e a medida (2).
- **A2 a A4:** fechados. A2: a linha "ficam" (:20) traz `meta.py:72`, `doutor.py:305`, `pre-push:231-248`, `forge-init:233-240` e a mensagem de `conformidade.py:4195` (linhas conferidas no head). A3: os padrões vão à `RESERVA` (:41) e a C2 diz que o modelo perde `pesados` e `ritmo` (:51). A4: a D1 (:72) diz que o `git clean -fdx` apaga o arquivo e que só o `denyWrite` protege, dentro do sandbox.

## Parecer
Reprovado por A5 e A6. A volta fecha o A1 para a cópia principal e a worktree e fecha A2 a A4; mas a frase que garante "o arquivo de uma cópia não vale" para os scripts é falsa no caso normal do projeto (a cópia em `.forge/wt/` é clone) e no `.git` forjado coerente, e os dois casos de abuso da C1 (:79, :80) foram escritos sobre ela. Basta o texto dizer qual pasta vale para o clone e o que ancora a cópia principal, ou rebaixar os scripts a informativos e ajustar C1 e a medida (2).
