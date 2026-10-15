---
tipo: review
contrato: 1
pedido: portao-diff-proprio
branch: melhoria/portao-diff-proprio
commit: c0e8edf
parecer: reprovado
revisor: forge:tech-lead
data: 2026-10-15
---
# Review: portão de pareceres compara só o diff da branch (cartão 15a)

## Volta 1 (commit revisado c0e8edf)

Escopo: `git diff b5411e9..c0e8edf`, que cobre `bin/forge-check` (`diff_efetivo`, `arquivos_divergentes`, `mesmo_diff`, `commit_vale`), `tests/test_portao_diff_proprio.py`, a emenda do item 3 da ADR 0004 e a linha do `CHANGELOG.md`. Também li o uso em `tests/catraca.py:484` (`rotulo_vale_pelo_conteudo`). A emenda da ADR, a segurança e o QA ficam com o software-architect, o security-engineer e o qa-engineer, em pareceres próprios.

Parecer: **reprovado**. A correção resolve os dois casos reais, mas abre um furo: mover uma linha da branch depois do parecer passa pelo portão sem novo parecer.

### Ferramentas (sobre o c0e8edf, load 0.52)
- Suíte (`env -u FORGE_ABERTURA_FEITA python3 -m unittest discover -s tests`): `Ran 568 tests in 154.697s`, `OK`.
- `scripts/validar-plugin.sh`: `✔ Validation passed`.

### O que está certo
- Rodei os casos reais do pedido com base `b5411e9`. O `forge-check` da base recusa os dois (`da445ba`→`e5b7cfb` e `bbc658f`→`055859b`) com `desatualizado: .claude-plugin/plugin.json mudou`. O do c0e8edf aceita os dois (`None`).
- O merge maligno (caso c), a linha removida e a mudança de conteúdo depois do merge (caso b) continuam barrados, e a mensagem cita o arquivo que diverge em vez de `fora[0]`.
- Sem `base`, a comparação continua estrita, como antes.
- Se o git falhar, `arquivos_divergentes` devolve `None`, `mesmo_diff` dá `False` e `commit_vale` recusa com `fora[0]`. Falha fechada mantida.
- A catraca herda a comparação por `mesmo_diff` sem mudar de assinatura.

### Achados
1. **bloqueia.** `bin/forge-check:240-265` (`diff_efetivo` com `-U0` e `@@` sem números): mudar uma linha da branch de lugar no arquivo não é detectado. Sem contexto e sem número de linha, o diff só guarda o conteúdo das linhas adicionadas e removidas. Uma linha adicionada movida para outro ponto dá o mesmo texto normalizado. O mesmo vale para a remoção de outra cópia de uma linha repetida (`}`, `return x`).
   - Reprodução: na base, `def f(u): x = 1; acao(u); return x`. A branch insere `checa(u)` antes de `acao(u)` e recebe o parecer. Depois um commit move `checa(u)` para depois de `acao(u)`. O `commit_vale(..., base="develop")` do c0e8edf devolve `None` (vale). O da base devolve `desatualizado: a.py mudou depois do parecer`.
   - O caso viola o próprio pedido ("sensível a qualquer mudança de conteúdo da branch") e a ADR ("qualquer outra mudança depois do parecer pede novo parecer"). Também afrouxa o rótulo `afrouxa-regra` da catraca (`tests/catraca.py:484`): o rótulo do dono sobrevive à mudança de lugar de uma verificação.
   - Sugestão (a decidir com o software-architect, já que muda o texto da emenda): ancorar cada trecho na posição relativa ao conteúdo da base, sem usar o número absoluto. Duas formas possíveis:
     - (a) Mostrar que `HEAD` = nova base + patch do parecer, com `git merge-tree --write-tree --merge-base=<mb antigo> <mb novo> <commit>` comparado à árvore do `HEAD` fora de LIVRES. Arquivo com conflito, como o `CHANGELOG.md`, cai na comparação `-U0` só para ele.
     - (b) Manter a linha da base que antecede cada trecho como âncora. Pesar o custo: hoje uma entrada colada à da base no `CHANGELOG.md` mudaria a âncora.
   - Seja qual for a solução, entra um teste "mover linha da branch invalida".
2. **recomendado.** `tests/test_portao_diff_proprio.py:49` (`base_avanca(mexe_no_trecho=False)`): o parâmetro nunca é usado, e é código morto. Ele aponta para um caso que faz falta: a base altera a linha vizinha a um trecho da branch (o contexto muda, as linhas da branch não). Sugestão: um teste que use `mexe_no_trecho=True` e espere `None`, ou remover o parâmetro.
3. **recomendado.** O pedido pede "testes com os casos reais", mas os testes são sintéticos. Conferi os casos reais à mão (ver "O que está certo"). Sugestão: registrar essa conferência no parecer de QA ou num teste que pule quando os commits não existirem. Não bloqueia.
4. **nit.** `bin/forge-check:306`: a chave vem de `diff --git a/x b/x` e o caminho sai por `split(" b/", 1)`. Um caminho com ` b/` no nome, ou entre aspas (não ASCII), sai errado na mensagem. A comparação não é afetada. Sugestão: usar o caminho da linha `+++ b/` ou `--- a/` como chave.

### Commits
`fix(forge-check): ...` e `docs(adr): ...` estão no padrão, um por mudança coerente. A linha no `CHANGELOG.md` está em `## [Não publicado]`, com o rótulo `afrouxa-regra` destacado. O texto da linha e o da emenda precisam acompanhar a correção do achado 1.
