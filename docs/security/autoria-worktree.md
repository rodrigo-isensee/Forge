---
tipo: revisao-seguranca
contrato: 1
pedido: autoria-worktree
branch: melhoria/autoria-worktree
commit: 531b131c9c8503b4d4de1328d1fbc86da373f97a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-15
---
# Review de segurança: autoria-worktree (volta 3)

Escopo: `git diff develop..531b131 -- hooks/ tests/hooks/conformidade/ docs/hooks.md` (`diretorio_comum`, `raiz_do_parecer`, `autoria`, nove fixtures, `docs/hooks.md`). Análise estática, mais a execução local dos testes `conformidade` (passam) e um teste passivo de `diretorio_comum` em diretório temporário. Substitui o parecer da volta 2 (commit 02cb437, hoje 1d82a22, o rebase foi só de identidade). `gitleaks` e `semgrep` não rodados: o diff não toca segredo, dependência nem workflow; o CI os executa.

## Gatilhos
`R-SEGURANCA`: controle do Forge em `hooks/` (hook `conformidade`, que alimenta a conferência de autoria do `forge-check pr`, ADR 0009, 6.4).

## Achados anteriores
- **A1 (`.git` forjado conta como worktree), baixa: resolvido.** `diretorio_comum` (`hooks/conformidade.py:992-1011`) só aceita `.git` que é diretório real (não symlink) ou arquivo `gitdir:` cujo alvo está em `<comum>/worktrees/<n>` e cujo `gitdir` de volta aponta para esse mesmo `.git`. Um `.git` que aponta para o repositório real, ou para uma entrada `worktrees/<n>` real, falha na volta (a entrada registra outro caminho). Um repositório alheio com `.git` de verdade dá comum diferente. Fixtures `autoria-git-forjado-nao-registra`, `-forjado-comum-nao-registra`, `-symlink-nao-registra` e `autoria-outro-repositorio-nao-registra` cobrem. Resto: quem forja `.git/worktrees/<n>/gitdir` já escreve dentro do `.git`; está documentado em `docs/hooks.md` como limite e não amplia nada, porque o papel vem de `agent_type` e o hash do conteúdo.
- **A2 (janela entre escrita e hash), baixa a média: resolvido.** O `sha256` é calculado logo após o filtro de caminho e antes de `diretorio_comum` e de qualquer outra leitura (`:1027`). Não há mais subprocesso entre a decisão e o hash; a janela voltou ao mínimo inerente ao PostToolUse. A parte "escrita em `docs/qa/` de outra worktree não é barrada ao papel errado" já existia e continua fora do escopo (o registro leva o papel real do autor; o `forge-check pr` confere).
- **A3 (git em diretório escolhido pelo agente), informativa: resolvido por remoção.** Não há mais chamada a git; a conferência é só leitura de arquivos. `GIT_DIR` e afins no ambiente do hook deixam de importar (fixture `autoria-git-dir-no-ambiente-registra`).
- **A4 (lacuna de teste), informativa: resolvido.** Há fixtures de `.git` forjado, symlink, `GIT_DIR`, worktree aninhada, fora de `docs/` e caminho relativo.

## Riscos novos da leitura direta de `.git` e `gitdir`
- **Arquivo enorme ou especial, baixa.** `marca.read_text` (`:1000`) e `(pasta / "gitdir").read_text` (`:1002`) leem tudo sem limite. Um agente com escrita fora do repositório pode criar um `.git` ou um `gitdir` gigante, um FIFO ou um symlink para `/dev/zero`, e depois gravar um `docs/qa/x.md` ali: o hook trava até o `timeout` de 10 s (`hooks/hooks.json`) ou esgota memória (`MemoryError` não é capturado; cai na falha fechada seletiva, que não bloqueia sem marcador crítico). Ganho do atacante: só negar o registro da própria autoria (o `forge-check pr` então recusa o parecer, o que é seguro) e atrasar o próprio hook. Sem escalonamento. Correção mínima: `open(...).read(4096)` em vez de `read_text`, e `is_file()` antes. Esforço: P. Dono: `software-architect` (quem implementa o cartão), sem urgência.
- **Caminho com `..`, resolvido.** O alvo de `gitdir:` passa por `realpath` (`:1000`), que normaliza `..` e symlinks; a volta também (`:1008`). O filtro final usa `p.relative_to(raiz)` sobre caminho já resolvido. Não encontrei escape. Detalhe: o teste `startswith("gitdir:")` vem depois do fatiamento (`:1000-1006`), então um `.git` sem o prefixo faz o hook ler `<lixo>/gitdir`; só é lido e comparado, nunca exibido nem gravado, e o resultado é descartado. Informativo.
- **Corrida entre a leitura do `.git` e a do `gitdir`, baixa.** A conferência é de estado, não de transação: trocar o `.git` entre as duas leituras só pode fazer a conferência passar se o atacante já controlar as duas pontas, e nesse caso ele forja de qualquer jeito, como no limite documentado. O que se registra (caminho relativo à pasta, hash lido antes, papel do harness) não depende da conferência. Sem elevação.
- **`gitdir` relativo, informativa (funcional, falha fechada).** O `.git` relativo (`gitdir: ../r/.git/worktrees/w`) é tratado: resolve contra `topo`. Já a volta `<comum>/worktrees/<n>/gitdir` é resolvida contra o diretório do hook (`os.path.realpath(os.path.dirname(volta))`, `:1008`); com `extensions.relativeWorktrees` (git 2.48 ou mais novo, `worktree add --relative-paths`) a volta é relativa e a comparação não bate, então a worktree não é reconhecida e o parecer não é registrado. Falha fechada (o `forge-check pr` recusa; não é desvio). Deduzido pela leitura do código: não consegui criar o caso, porque o sandbox protege o `.git/config`. O fixture `autoria-worktree-relativo-registra` cobre só `file_path` relativo, não `gitdir` relativo. Correção mínima, se a funcionalidade importar: resolver `dirname(volta)` contra `pasta`. Esforço: P. Dono: quem implementa o cartão.
- **Worktree aninhada, sem desvio.** `topo in raiz.parents` ou `topo == raiz` devolve `raiz` só se `raiz in p.parents`; um repositório com `.git` próprio, dentro da sessão, tem comum diferente e não registra; um `.git` forjado dentro da sessão falha na volta. Fixture `autoria-worktree-aninhada-registra` cobre o caso legítimo.

## O filtro por caminho abre um desvio?
Não. A condição `("docs", reviews|qa|devops|security)` consecutivo em `p.parts` (`:1024`) é um superconjunto de "o relativo começa com `docs/<pasta>/`": quem passava antes continua passando, e o teste final por `startswith` sobre o relativo à raiz do parecer continua valendo (`:1030`), com `rel = ""` quando a raiz não é reconhecida. O filtro só decide quando ler o arquivo, não o que registrar, então não há parecer que deixe de ser registrado nem outro que passe a ser. Custo residual: um `.md` com esse formato de caminho fora de qualquer worktree reconhecida agora é lido e hasheado antes de ser descartado (o hash não é gravado nem exibido; erro de leitura ou de UTF-8 vai ao `erros.log`, já era assim para o que estava na raiz). Informativo.

## Casos de abuso para o QA
1. `.git` como FIFO ou `gitdir` gigante num diretório externo, depois gravar `docs/qa/x.md` nele (o hook deve terminar no tempo e não registrar).
2. Worktree com `gitdir` de volta relativo (`worktree add --relative-paths`), se a versão do git permitir: hoje não registra.
3. `.git` sem o prefixo `gitdir:` que aponta para um caminho existente (não registra).

## Veredito
Aprovado. Os achados A1 a A4 estão resolvidos. Os riscos novos são de baixa severidade ou informativos e nenhum forja autoria de outro papel nem redireciona o `.forge/run/`. Recomendo um cartão pequeno (leitura limitada e `gitdir` relativo), sem bloquear.

## Riscos aceitos e ferramentas
Riscos aceitos: nenhum registrado (parecer `aprovado`; o que sobra é recomendação, sem aceite do usuário). Ferramentas: análise manual, `git` local e os testes do repositório; `gitleaks` e `semgrep` não usados (sem segredo nem dependência no diff; o CI roda as varreduras).
