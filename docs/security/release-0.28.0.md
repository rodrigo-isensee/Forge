---
tipo: revisao-seguranca
contrato: 1
pedido: release-0.28.0
branch: melhoria/release-0.28.0
commit: 450d7fa27e133cddbafd9ce09f19f63548f86a31
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-21
---
# Review de segurança: release-0.28.0

Leva inteira de origin/main 5e9b234 até 450d7fa: PRs #257 a #274 (18) e o commit da release. Cada PR já teve o seu parecer; aqui se confere o conjunto, a versão e o CHANGELOG.

## Gatilhos
Controles do Forge (`R-SEGURANCA`): hooks (`conformidade`, `parecer`, `pesado`, `agentes`, `_comum`), `.githooks/pre-push`, `bin/forge-fechar`, `bin/forge-check`, o workflow de CI e a regra da M1 (#270), que afrouxa a F6 com o rótulo do dono (`R-CONFORMIDADE`).

## Achados

## Detalhe dos achados
Sem bloqueante. O que foi conferido:

- **Código final igual ao revisado.** `git diff 2e1e712 450d7fa -- hooks/ .githooks/` vazio: os hooks que vão à main são exatamente os do commit revisado no parecer da M1 (conformidade-leitura), que já estava sobre o #269 (fa75b67 é ancestral de f4eb85c). `git diff e5ef160 450d7fa -- bin/forge-fechar` vazio (parecer lote-forge-fechar sobre o resultado de #261, #265 e #274 juntos). `git diff 862bf19 450d7fa -- .githooks/` vazio (parecer prepush-so-parecer).
- **#269 com #270 (hooks/conformidade.py).** `so_leitura` (hooks/conformidade.py:175) recusa de saída qualquer `$`, crase, `#` e quebra de linha antes de ler, e usa a mesma `leituras()` da ADR 0013 exigindo uma leitura só e legível; assim a folga da F6 não herda nenhuma ambiguidade de comentário do #269. Ela só dispensa a checagem da F6: o resto da linha segue por todas as outras checagens. Opções por lista branca (curtas por letra, longas pelo nome exato), `git` só com `log|show|diff` como primeiro argumento (`git -c ...` recusa). A linha ilegível agora barra fora do papel só de leitura (antes o `return` pulava tudo), e o `parecer` também barra: endurecimento, não folga.
- **#267 (pre-push curto) com os PRs seguintes.** O caminho curto só vale para delta inteiro em docs/{reviews,security,qa,devops}/, sem `_*`, ameaças, aceites, remoção nem renome, com prova da árvore remota verde; o #272 acrescentou um teste que lê `docs/security/_modelo.md`, mas arquivo começado em `_` já força a suíte inteira. `test_regra_so_na_fonte` está em `AntiDuplicacao`, que o caminho curto roda. O CI repete tudo.
- **#261, #265 e #274 (bin/forge-fechar).** Na espera do rótulo, o check `catraca` vermelho vira pendente, nunca verde: o merge só sai com o laço sem pendência e com `--match-head-commit`; head mudado na espera para. `--limpar` exige PR MERGED na base para a branch e só apaga branch cujo sha é o mesclado ou já está na base, sem forçar. Log em pasta por usuário (modo 700, sem link, dono conferido), arquivo por `mktemp` com umask 077, máscara de segredo.
- **#262 (erros no brief).** O texto que entra no brief vem só do catálogo fixo `CLASSES_DE_FALHA`, não do registro livre: sem canal de injeção.
- **#263 (agentes).** Só acrescenta recusa (forma da mensagem ao conferente).
- **#259 (CI).** Ações fixadas por SHA, ferramenta do CLI em versão fixa com scripts só do próprio pacote, binários de checagem baixados com conferência de sha256; sem `pull_request_target`.
- **Versão e CHANGELOG.** `.claude-plugin/plugin.json` e `dev/.claude-plugin/plugin.json` em 0.28.0. Os 18 fragmentos (um por PR, #257 a #274) foram apagados no commit da release e cada linha `- ` de cada um está, literal, na entrada [0.28.0] (conferido com `grep -F` por linha contra o conteúdo de 8b047d4): nenhum PR ficou de fora. A entrada traz a folga da F6 marcada como afrouxamento.

Recomendação (baixa, não bloqueia; dono: o autor do `forge-check fila`, por cartão na develop): `cmd_fila` (bin/forge-check:1471) imprime célula do KANBAN.md, IDs de pedido, nomes de branch e caminhos sem passar por `caminho_impresso`/`sem_controle`, ao contrário da convenção da própria ferramenta (bin/forge-check:893). Caminho: um cartão ou um nome de arquivo com separador de linha Unicode ou caractere bidi forja, na saída lida pelo Jarvis, uma linha `pode-comecar:`. Impacto baixo (o comando é informativo, rc 0, não decide portão), e o `sobreposicao` já se comporta igual. Correção mínima: passar cada campo impresso por `caminho_impresso` (esforço P).

## Riscos aceitos e ferramentas
Nenhum risco aceito. Revisão estática por `git diff`, `git show` e leitura do código final. Sem `gitleaks`, `shellcheck`, `actionlint` nem `zizmor` no PATH local (lacuna; o CI roda as checagens de workflow e de segredo).
