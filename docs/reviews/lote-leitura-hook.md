---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: 8c4b7b510c1f2e6f25325e35417b38fbe4a03937
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: lote-leitura-hook

Escopo: `git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 8c4b7b510c1f2e6f25325e35417b38fbe4a03937`, commit a commit (C1 6b74a45, C2 f34a329, C3 bb77a84, C4 8c4b7b5). Revisor independente; não sou o autor. Segurança (E1.3) tem parecer próprio em `docs/security/`, não refeito aqui.

## Achados
- A1 (bloqueante) hooks/parecer.py:359 · o N2 relê "$(cat <<'EOF' … EOF)" sem tirar o heredoc; apóstrofo no corpo vira aspa sem par e recusa. Regressão (base libera): gh pr create --draft --body com heredoc e git commit com merge no texto. Tirar heredocs antes de leituras; fixture.

## Parecer
**Reprovado**, por um bloqueante. O resto do lote está correto e bem dividido.

### A1: falso positivo na forma mais comum de abrir PR (C3, N2)
Sonda em cópia própria (`git archive` da base e do HEAD em `$TMPDIR`, hooks rodados pelo `Fixture` e pelo `rodar` de `tests/test_hooks.py`, sessão do clone do Forge na branch `feature/x`):

| Comando | base | HEAD |
|---|---|---|
| `gh pr create --draft --base develop --title t --body "$(cat <<'EOF'⏎O hook don't quebra.⏎EOF⏎)"` | 0 | 2 (R-REVIEW, linha que o hook não lê) |
| ``gh pr create … --body "$(cat <<'EOF'⏎Usa `foo` e it's⏎EOF⏎)"`` | 0 | 2 |
| `BODY="$(cat <<'EOF'⏎it's ok⏎EOF⏎)"; gh pr create --draft … --body "$BODY"` | 0 | 2 |
| `git commit -m "$(cat <<'EOF'⏎fix: o merge don't quebra⏎EOF⏎)"` | 0 | 2 |
| o mesmo corpo sem apóstrofo, com crase ou com aspa dupla | 0 | 0 |
| os mesmos comandos no `conformidade` | 0 | 0 |

Causa: `conferir_linha` relê a palavra com `$(` (N2) e o corpo da crase (P4) com `leituras`, sem passar antes por `tirar_heredocs`. Fora das aspas duplas, o apóstrofo do corpo do heredoc literal fica sem par, e a linha cai no ramo de ilegível. O `conformidade` não tem o problema porque o `Guarda.bash` tira os heredocs antes de ler. O `parecer` já recusava `gh pr create --body-file - <<'EOF'⏎it's⏎EOF` na base (0 → 2 nas duas), e o N2 levou essa lacuna para a forma padrão de corpo de PR e de mensagem de commit. Isso trava o fluxo de todos os projetos (`R-NEUTRO`: texto em inglês ou com aspas no corpo é comum). Não afrouxa nada, mas bloqueia trabalho legítimo, e nenhum teste cobre esse caso.

Sugestão (o autor decide): em `conferir_linha`, antes de `leituras`, passar o texto por `tirar_heredocs` (agora em `_comum.py`). Com `ValueError`, recusar como hoje. Conferir também os corpos dos heredocs de `bash` e `sh`, como faz o `conformidade`, se o desenho pedir. A correção vale para o nível 0 e para a palavra relida. Fixtures que liberam: as duas primeiras linhas da tabela e a do `BODY=`. Que continuam recusando: o mesmo heredoc com `gh pr merge` no corpo de um `bash <<'EOF'`, se ele for seguido.

### Por commit
- **C1 6b74a45 (FICHAS-CORPUS-BASH):** o oráculo do bash está bem fechado: `PATH` inexistente, `-r`, ambiente mínimo, pasta nova, stdin vazio, prazo e grupo de processos morto (N3). A guarda do corpus vem antes do oráculo e tem um caso negativo por forma. O ajuste de `$[1 #x]` depois de `true ||` está justificado na mensagem. Nada a apontar.
- **C2 f34a329 (CRASE-ASPA-HOOK):** `conteudos_de_crase` vai para `_comum.py` sem mudar a lógica, com `so_os_fechados`. A recursão em `corpos_se_leem` tem teto em `PROFUNDIDADE`, que também foi para `_comum.py`, e a docstring explica por que a crase sem par sozinha não torna a linha ilegível. Correto.
- **C3 bb77a84 (CRASE-SESSAO-PROJETO, P4, N1, N2):** no `conformidade`, o corpo da crase é conferido em cada pasta vista (`vistas`) e a atribuição entra no laço de releitura (N1). No `parecer`, a recursão por estado com teto, e o excesso de profundidade recusa. O desenho está correto. O A1 nasce aqui.
- **C4 8c4b7b5 (HEREDOC-FURO-HOOK):** a varredura `heredocs` com pilha de contexto substitui a regex por linha física. `tirar_heredocs` passa para `_comum.py` e os três chamadores tratam o `ValueError` (`Guarda.bash` recusa; `alvos_de_escrita` lê a mais, o que é seguro para autoria). As três fixtures da ADR 0011 continuam em 2 e passam a ser recusadas pela regra específica (`R-MAIN`), o que é ganho de precisão e não afrouxamento. A função é longa (cerca de 150 linhas), mas é uma máquina de estados num lugar só e tem tabela de teste própria. Aceito.

### Invariante movido (`tests/config.json`)
Não é afrouxamento, e o título do PR não precisa do destaque pelos invariantes. A definição `def conteudos_de_crase` continua protegida, agora em `hooks/_comum.py`, onde ela mora. Em `hooks/conformidade.py`, o padrão passa a ser `conteudos_de_crase\(`, que exige o uso da função (linhas 709 e 1323). Com isso, a proteção cobre a definição e o uso, e o conjunto ficou igual ou mais estrito. O rótulo `afrouxa-regra` continua sendo exigido por outro motivo: o diff toca `hooks/conformidade.py`, que está em `PROTEGIDOS` (`R-CONTRIB`, E1.5 do pedido).

### Os 18 casos da matriz que saem 2 no HEAD
Todos são do `pesado`, que libera a linha ilegível pela tabela 2.4 da ADR 0013 e fica fora do T2 por essa ADR. Isso está coerente com o desenho e com `docs/hooks.md`, e não é regressão do lote.

### Recomendações (fora do bloco)
- O T1 pula duas formas com motivo (aspa dupla dentro de `"$(…)"` e `case` dentro de `$(…)`, o N4). O cartão HOOK-N4 precisa entrar no quadro com a severidade da segurança antes do merge, para o `skipTest` não ficar sem dono.
- O fragmento `changelog.d/lote-leitura-hook.md` está em uma linha longa. Quando o A1 for corrigido, dá para citar ali que o heredoc do corpo de PR continua aceito.
- Os commits são limpos, um por cartão, com Conventional Commits em português e mensagens que explicam o porquê.

### Ferramentas
Não as refiz. O relatório da E1.1 registra 1317 testes OK. O pre-push deste parecer roda a suíte de novo sobre o mesmo patch.
