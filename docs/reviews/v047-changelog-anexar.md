---
tipo: review
contrato: 1
pedido: v047
branch: melhoria/v047-changelog-anexar
commit: f7f7f28fa5c798f7714b270a4d948ec8bd41b54c
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-14
---
# Review: v047 (E1.261, changelog-anexar)

Intervalo `origin/develop..f7f7f28f` (3 commits: feat, test, test). Escopo do pedido (E1.256): `bin/forge-changelog release --anexar <versão>` junta os fragmentos a uma versão que já está no `CHANGELOG.md`. Classe C (código de controle da catraca).

## Achados
- A1 (recomendado) bin/forge-changelog:265 · entrada publicada vazia seguida de linha em branco perde a linha em branco antes da próxima `## [`: a sobra "\n" vira o único separador (sonda: `## [0.2.0]\n\n## [0.1.0]` vira `- c\n## [0.1.0]`). Só estética; a release nunca grava entrada vazia.
- A2 (recomendado) changelog.d/README.md:5 · o README da pasta descreve só `release <versão> <data>`; citar `release --anexar <versão>` para reabrir versão, como já diz o uso do script.

## Sondas

## Parecer
**Aprovado.** Faz o que o E1.256 pede, nem mais: modo novo no subcomando `release`, sem tocar nos manifestos nem em `[Não publicado]`, com as mesmas defesas da release (`conferir_caminho` no CHANGELOG, `conferir_pasta_de_fragmentos`, leitura de todos os fragmentos antes de gravar e apagar só depois da escrita). A troca de `versao`/`data` para opcionais é guardada pelo uso explícito (linha 186) e pela recusa de posicional junto com `--anexar` (linha 182), ambas com teste do ramo de falha. A regex da entrada (`^## \[v\]...(?=^## |\Z)`) não confunde `###` com `## ` e usa `re.escape`; versão fora de X.Y.Z é recusada antes.

Leitura (checklist `engineering-practices`): nomes claros, funções pequenas (`anexar_por_tipo` separada de `anexar`), erros com mensagem e saída 1, sem código morto. Estilo da saída igual ao da release (seções sem linha em branco entre si), conferido no `CHANGELOG.md` atual.

Ferramentas (citadas, não refeitas):
- Testes novos: `python3 -m unittest tests.test_changelog.ReleaseAnexar` → `Ran 13 tests ... OK` (rodado neste review). Suíte completa: fica no CI do PR (ainda sem PR).
- Mutantes: `bin/forge-mutante --processos 1` nas 3 specs → M1 a M17 `morreu`, um por linha de guarda (`R-REVIEW`, classe C).
- Cobertura: `bin/forge-mutante --cobertura --base c5c3a449` → toda guarda mudada `coberta`, nenhuma descoberta.
- Shell: nada de shell no diff.

Tamanho (M14): 172 linhas de código e teste (61 em `bin/`, 111 em `tests/test_changelog.py`); passa de 150 e o corpo do PR precisa trazer `teto: excedido, 172 linhas, <motivo>`. Comportamento único; risco baixo (ferramenta de release, sem hook).

Commits: Conventional Commits em português, um por mudança coerente; fragmento `changelog.d/v047-changelog-anexar.md` com o nome da branch (`R-FLUXO`).
