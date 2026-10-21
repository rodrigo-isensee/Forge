### Alterado
- M16: regra única de marca na R-BRIEF e no `forge-check brief`: toda outra etapa do pedido vai ao Fora do escopo sem a marca, a marca só no corte real; etapa sem menção reprova para qualquer papel, duas etapas no mesmo Entregar reprovam (`etapa: junta delegações`), e o parser lê etapas com sufixo de letra (`E1.3b`) e de qualquer `E<n>` (afrouxa-regra: a marca deixa de ser exigida na etapa do mesmo papel).
- M13: uma regra só de isenção (`isencoes_da_entrega` no `forge-check`), usada pelo `forge-check pr`, pela catraca e pelo hook `parecer`: diff só de `.md` comum fica isento de QA e continua exigindo o review (o hook deixa de liberar `.md` sem parecer); `.md` de `agents/`, `skills/`, `stacks/*/agents|skills/` e `docs/regras/` não tem isenção; o `pr` imprime `pr: isento de QA` para o conferente copiar (destaque no título: estreita o hook e afrouxa a ferramenta no QA de `.md` comum).

### Adicionado
- P2: `forge-check brief gerar --cobre E<n>.<m>` escreve a linha `Etapa: ... Cobre: ...`, abre o Entregar com a etapa coberta e lista no Fora do escopo todas as outras etapas do pedido, sem a marca; sem `--cobre`, deduz a única etapa do destino e recusa (rc 2) quando ele tem mais de uma ou quando a etapa é de outro papel.
- M5 e P2 (tabela de pareceres): `brief gerar` recusa (rc 1, `brief gerar: recusado: <linha do forge-check pr>`) o brief das etapas `pr`, `merge-integracao` e `pedido-de-merge-ao-dono` sem os pareceres exigidos, e avisa no `qa` sem review; `forge-check brief` lê `Etapa:` e `Branch:` do cabeçalho e imprime `aviso: etapa:` por parecer que falta, pela mesma regra de isenção da M13.

### Corrigido
- M4: `forge-check brief` aceita como prova do conferente o PQ `merge` e o PQ `cmd` com `verificador: conferente` (antes só `sha`, `push` ou `arquivo`); o brief de merge que o próprio `brief gerar` monta deixa de reprovar com "forma: sem PQ que o conferente confira" (teste de ida e volta).
