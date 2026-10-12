# Verificar sessões sem custo

Propósito: conferir o comportamento real dos agentes a partir de sessões gravadas, sem IA e sem rede (ADR 0007, `R-CUSTO`). Público: quem mantém ou contribui com o Forge. Revisão: 2026-10-12.

## O que é verificado
`forge-check transcricao verificar <arquivo.jsonl> [--teto N]` lê uma transcrição anonimizada e imprime uma linha por violação (`transcricao: R-ID: problema`); sai com 1 se houver alguma.
- `R-TETO`: no máximo `N` agentes simultâneos em segundo plano (padrão 3), contando início e fim.
- `R-MAIN`: nenhum `git push` para a main nem `commit`, `merge`, `push`, `rebase`, `reset` ou `cherry-pick` estando nela.
- `R-REVIEW` e `R-QA`: `gh pr create` só depois de haver delegação ao `tech-lead` e ao `qa-engineer`. Aproximação: vale a sessão inteira, não o pedido, e não lê o conteúdo dos pareceres (isso é do `forge-check pr`).
- `PROMPT-PADRAO`: toda delegação traz as seis seções do prompt-padrão do Jarvis.

## Anonimizar e contribuir
1. Localize a sessão em `~/.claude/projects/<projeto>/<sessão>.jsonl`.
2. `forge-check transcricao anonimizar <sessão>.jsonl tests/transcricoes/<caso>.jsonl`.
3. Abra o arquivo gerado e confira: só tipo de evento, horário, tipo de agente, comandos reduzidos (`git push <branch>`, `gh pr create`) e as seis seções como verdadeiro/falso. Nunca versione a transcrição original.
4. `forge-check transcricao verificar tests/transcricoes/<caso>.jsonl`. Se violar uma propriedade, registre o caso como falha esperada no teste `Transcricoes` e proponha um hook ou ajuste de agente.
5. Abra o PR na `develop` (ADR 0006, `scripts/verificar-contribuicao.sh` sem achados).

A anonimização é por lista de permissão: texto de usuário, saídas de ferramenta, prompts, caminhos, e-mails e nomes de projeto nunca são copiados. Nomes de branch viram `<branch>` (exceto `main`, `develop`, `homolog`) e agentes que não são `forge:*` viram `<agente>`. Eventos de subagentes (sidechain) ficam de fora: confira a sessão principal.

## Limites
O verificador olha o passado e só vê o que o formato registra. Agente em segundo plano sem aviso de término conta como ainda ativo. O leitor do `.jsonl` do Claude Code está só em `ler_eventos_brutos` (`bin/forge-check`); o arquivo anonimizado tem formato próprio (`forge-transcricao/1`) e guarda a versão de origem.
