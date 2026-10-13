---
tipo: review
contrato: 1
pedido: jarvis-forge-vigente
branch: melhoria/jarvis-forge-vigente
commit: 6432242
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-13
---
# Code review: jarvis-forge com cópia vigente (ADR 0009, seção 4)

Escopo: `scripts/jarvis-forge`, classe `JarvisForgeVigente` em `tests/test_forge.py`, `README.md`, ADR 0009 e `CHANGELOG.md`, diff `origin/develop..b51cd3a`. Os 193 testes passam. O atalho não foi executado de verdade.

## Bloqueia
Nenhum.

## Recomendado
1. **Sessão do tmux reaproveitada ignora o modo.** `tmux new-session -A -s jarvis-Forge` anexa a uma sessão existente sem reexecutar o comando. Quem abriu com `--dev` e depois roda `jarvis-forge` (ou o contrário) continua no modo antigo, sem aviso. Isso também vale depois de `--atualizar-vigente`: a sessão aberta segue com os hooks antigos. Sugestão: nome de sessão por modo (`jarvis-Forge-dev`) e documentar que atualizar exige reabrir.
2. **`--dev` pouco visível.** O AVISO vai para o stderr e some quando o tmux ou o claude assumem a tela. Sugestão: refletir o modo em `--remote-control` (ex.: "Jarvis - Forge (DEV)").
3. **`"${repasse[@]}"` vazio com `set -u`** quebra em bash anterior à 4.4 (bash 3.2 do macOS). Sugestão: `${repasse[@]+"${repasse[@]}"}` ou montar a string de outra forma.
4. **`XDG_DATA_HOME` relativo.** O clone usa o caminho relativo ao diretório de origem, mas depois do `cd "$HOME/Forge"` o `--plugin-dir` passa a apontar outro lugar. A especificação XDG manda ignorar valor relativo; sugestão: cair no padrão quando não começar com `/`.
5. **Primeira vez sem rede.** O clone falha, a pasta parcial é removida e o script sai com erro claro; o Jarvis não abre. É seguro (nunca cai em silêncio para a cópia de trabalho), mas a mensagem deveria sugerir `--dev` como saída consciente. O `rm -rf "$vigente"` só roda se o clone falhou e o caminho é próprio da fábrica; aceitável.
6. **`fetch` sem rede em `--atualizar-vigente`** aborta por `set -e` com a mensagem crua do git e a cópia intacta. Correto; uma mensagem própria ajudaria.
7. **Teste.** Falta caso para `--dev` com `--atualizar-vigente` (sai 2) e para caminho com espaço em `XDG_DATA_HOME`.

## Conferido, sem ressalvas
- A cópia vigente só é alterada em `--atualizar-vigente`; o fluxo normal só clona se faltar (teste confirma que não há chamada de git na segunda execução).
- `reset --hard` e `fetch` usam sempre `git -C "$vigente"`; o `~/Forge` só recebe `remote get-url`. A recusa com `status --porcelain` sujo vem antes do `fetch` e do `reset`. Arquivos ignorados pelo git não contam como sujeira; aceitável.
- O clone é independente: `.git/config` próprio, sem compartilhar o do `~/Forge`. Só a URL da origin é copiada.
- Caminhos com espaço: todas as expansões estão entre aspas e o tmux recebe a linha escapada com `printf '%q '`.
- Continua no tmux, com `--remote-control` e canal do Telegram. `--continue` depende de `$PWD`, que segue sendo `~/Forge` nos dois modos, então a conversa retomada é a mesma.

## Revalidação (6432242)
Diff `65b4884..6432242`; 202 testes passam. O atalho não foi executado de verdade.

| Item | Situação | Conferência |
|---|---|---|
| JFV-01 (apagava diretório sem `.git`) | corrigido | O `rm -rf` foi removido; `conferir_vigente` recusa, sem tocar em nada, qualquer caminho existente que não seja clone com a mesma origin do `~/Forge`. Vale para o fluxo normal e para `--atualizar-vigente`. |
| JFV-02 (commit local descartado) | corrigido | `rev-list origin/develop..HEAD` não vazio recusa antes do `fetch` e do `reset`. |
| JFV-03 (sem origin) | corrigido | Mensagem própria, sugere `--dev`, sai 1. |
| 1. Sessão por modo | corrigido | `jarvis-Forge` e `jarvis-Forge-dev`; aviso de reinício após atualizar, só quando o HEAD mudou. |
| 2. `--dev` visível | corrigido | `--remote-control "Jarvis - Forge (dev)"`. |
| 3. bash 3.2 | corrigido | `${repasse[@]+"${repasse[@]}"}`. |
| 4. XDG relativo | corrigido | Recusado com saída 2 (em vez de cair no padrão; aceitável e mais explícito). |
| 5. Primeira vez sem rede | corrigido | Mensagem sugere `--dev`. |
| 6. `fetch` sem rede | corrigido | Mensagem própria, cópia intacta. |
| 7. Testes | corrigido | Casos novos para `--dev` + `--atualizar-vigente`, espaço em `XDG_DATA_HOME`, relativo, modo por sessão, outra origin. |

### Achados novos
Nenhum bloqueia. Não há caminho do script que apague ou sobrescreva arquivo do usuário: não há mais `rm`; o `reset --hard` só ocorre em clone validado, sem mudanças nem commits locais; o `git clone` não sobrescreve diretório não vazio.
1. **Recomendado, baixo: `--dev` também é barrado por `conferir_vigente`.** Se o caminho da cópia vigente for estranho (ou o `~/Forge` sem origin e a cópia já existir), `--dev` sai 1, embora a mensagem aponte `--dev` como saída em outros casos. Sugestão: pular a conferência quando `dev=1`.
2. **Observação, baixo: link simbólico para um clone da mesma origin** passa na conferência. Se apontar para a cópia de trabalho limpa, em `develop`, o `--atualizar-vigente` faria `reset --hard` nela. Exige ação deliberada do usuário e a checagem de mudanças e commits locais protege o trabalho em andamento; sem ação.
3. **Observação, baixo:** a checagem de commits locais usa o `origin/develop` anterior ao `fetch`; é conservadora (pode recusar a mais, nunca a menos). Sem ação.
