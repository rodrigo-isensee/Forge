---
tipo: review
contrato: 1
pedido: lote-leitura-hook
branch: melhoria/lote-leitura-hook
commit: dd9190992bbd107347a9cc8c206da73694fa8b72
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-21
---
# Review: lote-leitura-hook (revalidação)

Escopo: a entrega inteira, `git diff ad6d96ce6b19663f7695d361d61f59c7545bdca6 dd9190992bbd107347a9cc8c206da73694fa8b72`. A leitura foca no delta desde o parecer anterior, que revisou 8c4b7b5: `git diff 8c4b7b5 dd91909`, com f3e1267, fe14b2e, 8f9fbd7 e dd91909. Os commits C1 a C4 (6b74a45, f34a329, bb77a84, 8c4b7b5) foram lidos na rodada anterior e não mudaram, então ficam como "já lido", com o parecer da rodada anterior valendo para eles. Sou revisor independente, não o autor. A segurança (E1.3) tem parecer próprio em `docs/security/`, que não refiz aqui.

## Achados
- A1 (bloqueante) hooks/conformidade.py:665 · o teto conta conferências, não custo: 20 cd e 19 crases de 8 KB com `git push --no-verify` em crase no fim recusam em 14,2 s (timeout 10 s, falha aberta); a base recusa em 1,1 s. Orçar por tempo ou tamanho somado; fixture com corpo grande.
- A2 (bloqueante) hooks/_comum.py:717 · o fim do heredoc sem aspas ignora barra mais quebra, que o bash junta antes de comparar: cat <<X, a\, X, cat <<Y, X, gh pr ready feature/x, Y roda o ready no bash; o parecer vai de 2 (base) a 0 (fe14b2e). Juntar as linhas antes de comparar; fixture.

## Parecer
**Reprovado**, por dois bloqueantes. Os dois achados de A1 da rodada anterior (o meu e o da segurança) e os R1 e R2 da segurança foram tratados, mas a correção do A1 de segurança não fecha a classe dele (A1 acima), e a correção do A1 do review abriu uma regressão no `parecer` (A2 acima).

### Sondas
Fiz as sondas numa cópia própria: `git archive` da base e do HEAD em `$TMPDIR`, com o hook real rodado pelo `Fixture` e pelo `rodar` de `tests/test_hooks.py`. Usei como modelo as fixtures `conformidade/heredoc-fim-com-espaco-antes-repo-delete-bloqueia` e `parecer/forge-clone-pr-create-draft-heredoc-com-apostrofo-libera`.

| Caso | base | HEAD |
|---|---|---|
| `gh pr create --draft … --body "$(cat <<'EOF'⏎O hook don't quebra.⏎EOF⏎)"` (parecer) | 0 | 0 |
| `BODY="$(cat <<'EOF'⏎it's ok⏎EOF⏎)"; gh pr create --draft …` (parecer) | 0 | 0 |
| `gh pr create --draft … --body-file - <<'EOF'⏎it's⏎EOF` (parecer) | 2 | 0 |
| `sh <<'EOF'⏎gh pr ready feature/x⏎EOF`, sem parecer (parecer) | 2 | 2 |
| `cat <<X⏎a\⏎X⏎cat <<Y⏎X⏎gh pr ready feature/x⏎Y`, sem parecer (parecer) | 2 | **0** |
| a mesma forma com `gh pr create` sem `--draft` (parecer) | 2 | **0** |
| a mesma forma com `gh pr merge feature/x --merge` (parecer; o `conformidade` recusa pela rede da ADR 0011) | 2 | **0** |
| 60 cd e 60 crases aninhadas com `--no-verify` (fixture de orçamento, conformidade) | 2 | 2, rápido |
| 20 cd e 19 crases de 5 KB, depois `` `git push --no-verify origin feature/x` `` (conformidade) | 2 em 0,86 s | 2 em 8,65 s |
| 20 cd e 19 crases de 8 KB, depois a mesma crase (152 KB, conformidade) | 2 em 1,09 s | **2 em 14,22 s** |
| 15 cd e 25 crases de 20 KB, sem ação (conformidade) | não medido | mais de 30 s |
| linhas comuns: 20 grupos `cd … && x=$(git rev-parse HEAD) && echo \`date\``, e cd, `$(…)` e crase misturados | 0 | 0, em 0,14 s |

O bash confirma o A2: com `printf 'cat <<X\na\\\nX\ncat <<Y\nX\necho RODOU\nY\n' | bash`, ele imprime `RODOU`. A linha `a\` + `X` vira `aX`, então o primeiro `X` não fecha o heredoc, e quem fecha é o `X` seguinte, que o hook trata como corpo do `<<Y`.

### A1: o orçamento conta chamadas, e o custo de cada uma cresce com o corpo
O f3e1267 tem duas partes. A memória por (corpo, pasta, nível, `so_substituicoes`, ambiente) está correta: ela devolve o ambiente que a primeira conferência deixou, e o único outro estado que muda, `lancador_recusado`, persiste na linha. O teto de 400 também está correto. Com essas duas peças, a fixture adversária do A1 de segurança cai depressa. Mas cada conferência relê o corpo inteiro, então o tempo é aproximadamente conferências × tamanho do corpo, e o tamanho da linha não tem teto. Com corpos de alguns KB, as 400 conferências passam dos 10 s do `hooks/hooks.json`. Nesse caso o Claude Code mata o hook e o comando segue (falha aberta), que é a mesma consequência do A1 de segurança. A base recusava essa linha em cerca de 1 s pela rede da ADR 0011 (crase com marcador crítico).

O valor 400 é razoável como contagem: as linhas legítimas que medi ficam longe dele. O problema está na unidade, porque 400 chamadas sobre corpos grandes não cabem no prazo.

Sugestão (o autor decide):
- trocar ou complementar o teto por um prazo (`time.monotonic()` medido no nível 0, com recusa ao passar de cerca de metade do timeout) ou por um orçamento em caracteres somados das conferências;
- e/ou aplicar a rede barata do marcador crítico antes de descer pelas pastas, que era o que a base fazia.

O teste de orçamento precisa de uma fixture com corpo grande, além da de 60 × 60.

### A2: regressão do `parecer` vinda da correção do A1 do review
O fe14b2e passa a linha do `parecer` por `tirar_heredocs`. Isso corrige o falso positivo (as três formas do A1 anterior liberam, e `--body-file -` com apóstrofo também), mas leva para o portão de R-REVIEW e R-QA a leitura do fim de heredoc do `_comum.py:717`. Essa leitura compara cada linha física com o delimitador. Num heredoc sem aspas, o bash junta antes a barra final com a linha seguinte, e com isso um heredoc falso do hook esconde um `gh pr ready`, um `gh pr create` sem `--draft` ou um `gh pr merge` que o bash roda. A base recusava essas três formas, porque o `parecer` lia o texto inteiro. O R2 corrigiu espaço e tab, mas não a continuação.

Sugestão: em `heredocs`, com o delimitador sem aspas, juntar a linha que acaba numa quantidade ímpar de barras com a seguinte antes de comparar com o delimitador, como faz o bash. Com o delimitador literal, nada muda. Os casos de borda são `a\` (junta) e `a\\` (não junta), em `test_heredocs` e numa fixture `-bloqueia` do `parecer`.

O parecer de segurança da mesma rodada (5a4f450) chega ao mesmo achado por conta própria, como o A2 dele. O A1 dele (`source /dev/stdin`, `.` e `ksh` como dono do heredoc) é de lá e não o refiz.

### Delta lido, por commit
- **f3e1267 (orçamento):** a memória e o teto estão corretos, e a recusa do teto usa R-CONFORMIDADE com mensagem e correção numa linha. O teste `test_linha_adversaria_de_crases_e_pastas_recusa_dentro_do_orcamento` lê o timeout do `hooks.json` em vez de fixá-lo, o que é bom, mas só cobre o eixo número de crases × pastas (A1).
- **fe14b2e (parecer sem heredocs):** o A1 do review anterior está resolvido. As fixtures `forge-clone-*-heredoc-*` cobrem as formas da tabela anterior, e o controle `bash <<'EOF'` com `gh pr merge` continua recusando. O `ValueError` recusa por R-REVIEW, o que agora barra `--body "$(cat <<EOF⏎it's $(date)⏎EOF⏎)"` (era 0 na base). Isso é coerente com o `conformidade`, que já recusava essa forma, e a mensagem diz como corrigir. Aceito. O A2 nasce aqui.
- **8f9fbd7 (R1, R2):** `expandido()` está certo: a continuação some, o par de barras vira um caractere neutro, e `\\$(` e `$\`⏎`(` são achados. Os oito casos novos de `heredocs` cobrem as barras, o espaço em volta e o `<<-`. O fim do corpo na linha igual ao delimitador (com `<<-` só as tabs saem) resolve o R2. Falta a continuação no fim (A2).
- **dd91909 (corpus):** a fixture de orçamento sai do T5 porque recusa pelo teto e não pela leitura. O motivo está no comentário, e a constante `FIXTURE_DE_ORCAMENTO` é usada pelos dois testes. Correto.
- `docs/hooks.md` e `changelog.d/lote-leitura-hook.md` acompanham as mudanças. Quando o A1 for corrigido, o texto "recusada antes do timeout" e o "400 conferências" do `docs/hooks.md` precisam refletir a unidade nova do orçamento.

### Recomendações (fora do bloco)
- A recomendação anterior continua aberta: o cartão HOOK-N4 tem de entrar no quadro antes do merge, para o `skipTest` do T1 ter dono.
- O fragmento do changelog continua numa linha muito longa. Ao fechar a volta, vale enxugar.
- Os commits seguem limpos, um por achado, com Conventional Commits em português e o porquê na mensagem.

### Invariantes e ferramentas
O delta não toca em `tests/config.json`, e o que escrevi sobre os invariantes na rodada anterior continua valendo. Ainda é preciso o rótulo `afrouxa-regra` do dono no merge (E1.5), porque o diff toca em `hooks/conformidade.py`. Não refiz as ferramentas: o pre-push deste parecer roda a suíte sobre o mesmo patch.
