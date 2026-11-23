---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0480-g1-2-delta
commit: bdd44bc03d942aa8e119a16db562def9d3eb9a43
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-23
---
# Review de segurança: v0478, G1.2 sozinho (E122.14)

Primeira rodada nesta branch. O item é um corte da `melhoria/v0480-g1-2-3`, cuja segurança aprovou o head 17c4ba57 (bd9a7852). Li o diff inteiro de `5cff9f6a..bdd44bc0` (16 arquivos). Conferi que o código do G1.2 é o mesmo do head aprovado: o bloco de `bin/forge-check` que vai do comentário `# G1.2` até `blocos_literais` é igual byte a byte entre 17c4ba57 e bdd44bc0, e as duas chamadas (`cmd_docs`, `:480`, e `cmd_pr`, `:2045`) também. `tests/test_parecer_fora_do_delta.py` não tem diff entre os dois heads. Reli inteiras `mesmo_commit`, `parecer_anterior` (`:4129`), `trechos_do_delta` (`:4142`) e `fora_do_delta` (`:4150`).

Gatilhos: controles do Forge (`docs/regras/`), `PROTEGIDOS` (`bin/forge-check`).

## Só aperta? Não. O item afrouxa uma regra.
O que afrouxa, para o rótulo `afrouxa-regra`:
1. **Revalidação de review e QA.** Um `bloqueante` novo fora dos trechos mudados desde o `commit:` anterior (margem de 3 linhas) que não repete um bloqueante da rodada anterior faz o `forge-check pr` e o `forge-check docs` recusarem o parecer (`bin/forge-check:4172`). Esse achado passa a ser `recomendado` e vira cartão depois do merge. Antes, um defeito provado achado tarde bloqueava o merge em qualquer linha.
2. **Revalidação de segurança.** Um bloqueante novo fora do delta só vale com `explorável: S<n>` e a sonda em `## Sondas` (`:4167`). A recomendação nova fora do delta vira cartão e não é mais corrigida antes do merge (`docs/regras/R-SEGURANCA.md:17`, `agents/security-engineer.md:17`).
3. **Textos que acompanham a mudança.** `docs/regras/R-REVIEW.md:17`, `skills/engineering-practices/rigor-por-classe.md:11` e os três agentes de portão. O `verificada_por` de `R-REVIEW` e `R-SEGURANCA` ficou mais curto, mas o mecanismo não mudou: os gatilhos continuam em `R-SEGURANCA.md:14`. Nenhum trecho de `invariantes` em `tests/config.json` foi tocado. As outras edições nos agentes são só redação, sem regra a menos. O ponteiro do `tech-lead` para H8 diz "exceções", e o detalhe (`hooks/` em classe C e o caminho curto que não alcança `hooks/`) continua em `tamanho-por-item.md:17` e `:28`.

O que aperta dentro do mecanismo novo: `LARGURA_DA_FAIXA` (`:4121`). Uma faixa de 20 linhas ou mais não conta como cruzando o delta, o que fecha o truque `arquivo:1-99999`.

O mecanismo falha a favor do bloqueio, que é o lado seguro. Se não há rodada anterior, se o sha não resolve (`:4158`) ou se o diff do git falha (`:4172`, `trechos is None`), o achado continua bloqueante. O diff usa `--literal-pathspecs`, `--no-ext-diff` e `--no-textconv`. Um arquivo renomeado aparece como inteiro novo, o que também mantém o bloqueio. A revalidação depois de um rebase compara as árvores, então o delta fica maior, nunca menor. O texto do parecer só seleciona; o git recebe argumentos, não um shell.

Risco residual, sem achado: `parecer_anterior` (`:4129`) escolhe a rodada anterior só pelo frontmatter (`pedido`, `branch`, `commit`) de uma versão antiga do arquivo no histórico. Não confere quem gravou essa versão. Para forjar uma rodada anterior com `commit:` recente e estreitar o delta, alguém teria de escrever em `docs/security/` ou `docs/reviews/` com outro papel. O hook `conformidade` barra isso, e a autoria do parecer atual continua exigida. Não há caminho realista com a trava ativa. Se o dono quiser fechar o caso também no CI, a sugestão é um cartão: exigir que a versão anterior tenha sido gravada pelo mesmo papel.

A autorização do rótulo (DECISÃO DO DONO 2026-11-23 15:25, Decisão 2a) cita a branch `melhoria/v0480-g1-2-3`, que inclui o G1.2. Esta branch é um corte dela e afrouxa a mesma coisa. Cabe ao Jarvis confirmar que a autorização cobre o corte. A regra fixa até 27/11 só vale para item que só aperta, e este não é o caso.

## Riscos aceitos e ferramentas
Nenhum risco aceito. A branch está sem PR, e a suíte inteira fica para o CI do PR. Rodei localmente só os testes dos arquivos tocados, `test_parecer_fora_do_delta` e `test_testes_tocados`: 217 testes, OK, 1 pulado. Os mutantes FD1 a FD22, FL1 e FL2 são do QA. Ferramentas usadas: git e o `forge-check` do head. Nenhuma varredura externa e nenhuma ferramenta instalada.
