---
tipo: review
contrato: 1
pedido: jarvis-forge-vigente
branch: melhoria/jarvis-forge-vigente
commit: b51cd3a
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
