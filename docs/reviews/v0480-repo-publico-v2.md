---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-repo-publico-v2
commit: 85f870f554dd9e67093a5b7a1f0c0ad8b89530fe
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0480-repo-publico-v2 (PR #837, CONFORMIDADE-REPO-CREATE-PUBLICO, v0478 E148.2)

Review do redesenho que substitui o PR #829 (cortado na 3ª volta), no head `85f870f5` contra a base `20630351`. O commit traz de `melhoria/v0480-repo-publico-fix` o código, as fixtures e os mutantes da trava, sem os pareceres, e troca o marcador: as formas do gh que decidem a visibilidade saem do `CRITICO` e entram só em `MarcadorDaPolitica.marca` (`hooks/conformidade.py:4419`), por `visibilidade_do_gh` (:354 a :361), uma busca própria por termo em cada linha.

## Parecer
**Aprovado.** Fecha a A1 do meu último parecer na branch antiga (`67cc41cb`, head `eebdfef6`) e a A9 da segurança (`815cfc28`), sem reabrir nenhum bloqueante das três rodadas.

**A1 (o marcador ampliava demais): fechada.** O `CRITICO` (:61 a :64) volta ao texto da base, sem a alternativa das formas de visibilidade; as formas ficam só no marcador do prazo vencido e do erro interno, que não liga a recusa de construção não modelada. As sondas S1 a S4 da branch antiga viraram fixtures `-libera` com o comando literal do parecer antigo (`trava-gh-leitura-variavel-libera` e `-variavel-tech-lead-libera` para S1 nos dois papéis, `-chave-libera` S2, `-graphql-variavel-libera` S3, `-crase-libera` e `-barra-quebra-libera` S4) e saem 0 no head, rodadas pelo `test_fixtures_do_repo_publico`.

**A9 da segurança (custo cúbico): fechada.** Cada termo é um `re.search` sem quantificador aninhado sobre a linha, então o custo é linear; a continuação `\` + quebra já chega juntada numa das `formas` (`texto_da_acao`, `hooks/_comum.py:2781`). A fixture `trava-gh-marcador-linear-libera` (8 KB de `gh repo ` repetido) decide abaixo de metade do prazo, medida no próprio teste.

**Nenhum bloqueante reabre.** As 79 fixtures do item na branch antiga estão no head byte a byte (`git diff --quiet` de cada uma entre `origin/melhoria/v0480-repo-publico-fix` e `85f870f5`), mais as 7 novas; entre elas as nove `trava-prazo-*-bloqueia` (o marcador ainda cobre `gh repo create`/`new`, `user/repos`, `orgs/<o>/repos`, `.../generate`, `repos/<o>/<r>` com PATCH e `gh api graphql`, inclusive pela continuação), a S18 e a string aberta sob o prazo, e as S8 a S17 da segurança. O código de `api_publica`, `graphql_publica` e do ramo `repo create` é o da branch antiga. A forma nova casa termos em qualquer ordem na linha (`gh repo view x && echo new` marca): é mais larga que o regex antigo, mas só pesa quando o prazo vence, então só aperta.

**Mutante, rodado:** RP57 (`if False and any(map(visibilidade_do_gh, formas)):`, `tests/mutantes/v0480-repo-publico-fix-8.json`) numa cópia por `git archive`: o `test_fixtures_do_repo_publico` falha em 8 fixtures `trava-prazo-*-bloqueia`; morto. RP58 a RP60 cobrem os termos do marcador; não rerrodados (verificador do autor).

**Teto H1:** `hooks/conformidade.py` soma 149 linhas no item (`git diff --numstat HEAD~1 HEAD -- hooks/`: 149 +, 0 −), dentro de 150; o resto são fixtures, mutantes, teste, índice e fragmento do changelog.

**Ferramentas (citadas, não refeitas):** `tests.test_hooks.Hooks.test_fixtures_do_repo_publico` no head, ambiente limpo: OK (1 teste, 40,5 s; piso de 83 fixtures e as duas medidas de tempo). Junto com `test_prazo_do_merge`: a primeira rodada deu 1 falha com a máquina em carga (load 12, 12 CPUs; a saída não guardou qual), a segunda OK (2 testes, 88 s, com as linhas `PRAZO-CARGA` do próprio teste); o diff não toca o hook `parecer` dessas fixtures, e o CI decide. CI do PR #837 no head, na leitura: `bateria (passos)`, `bateria (verificações longas)`, `instalação (python 3.14)`, `árvore já provada na develop`, suíte 3.12 parte 2 e 3.14 parte 1 verdes; as outras partes da suíte pendentes; `bateria (pareceres)` e `catraca` vermelhos à espera dos pareceres.
