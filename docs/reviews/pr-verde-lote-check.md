---
tipo: review
contrato: 1
pedido: pr-verde-lote-check
branch: melhoria/pr-verde-lote-check
commit: 044ef1d4ae7ce8f7136ef07fd4c0b810e8d91616
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: pr-verde-lote-check (PR-VERDE-LOTE-CHECK-REV E1.1, revalidação por delta)

Intervalo revisado: `1f7bd7f...044ef1d`. Rodada 1 sobre `26d2260` (parecer `e7b98ed`, reprovado por A1). Esta rodada lê só o delta `26d2260..044ef1d`; os commits do autor são `824f035` (correções) e `044ef1d` (mutante M4); os demais (`cc82b46`, `e7b98ed`, `db70d16`) são pareceres.

## Achados
- A2 (recomendado) tests/test_forge.py:4519 · segue da rodada 1: na etapa pr, falta afirmar que o commit do autor feito depois do merge que mexe em src/y.txt volta ao escopo
- A3 (recomendado) bin/forge-check:1051 · segue da rodada 1: no escopo pelo primeiro pai, as contagens +/- são as do intervalo inteiro (só informativo)
- A4 (recomendado) bin/forge-check:4384 · curinga no meio do segmento seguido de pasta da raiz ainda é cobrado: `ls x*bin/nao-existe` reprova (sonda); gatilho artificial; descartar o token com `*?[{` fecha
- A5 (recomendado) tests/test_etapa_do_brief.py:180 · o teste do corte legítimo da etapa de outro papel não afirma o `rc`; só a ausência da linha

## Parecer
**Aprovado.** O A1 da rodada 1 está corrigido e não há bloqueante novo no delta. A2 a A5 são recomendações e não devolvem a entrega.

Os achados da segurança (A1 `-s ours`, A2 prefixo do D4) e do QA (A1 a A5, guardas sem teste) são avaliados por esses portões, nos pareceres deles. Aqui só vale a qualidade do código que os corrige.

**Delta lido** (saída de `forge-check delta --parecer`, sobre o parecer anterior):
- `bin/forge-check`: 388-392, 416-423, 456, 991-994, 1151 e 4384.
- `tests/test_conferencia_base_dono.py`: 171-184.
- `tests/test_etapa_do_brief.py`: 180-192, 215-221 e 634-636.
- `tests/test_forge.py`: 4656-4665.
- `tests/test_portao_diff_proprio.py`: 109 e 121-152.
- `tests/mutantes/pr-verde-lote-check.json`: 39-40.
- `tests/mutantes/pr-verde-lote-check-2.json`: novo.

Ficou como já lido, sem nova leitura, o resto de `1f7bd7f...26d2260`, revisado na rodada 1.

**A1 (G1 b), corrigido.** O `CAMINHO_NO_PQ` ganhou o lookahead `(?![\w.@+/-]*[*?\[{])`. Com o backtracking, nenhum prefixo do segmento com curinga casa, e o lookbehind impede começar no meio. A sonda `$TMPDIR/tech-lead-pr-verde-lote-check/sonda_glob3.py` chama a função real:
- Não reprovam mais: `ls tests/test_*.py`, `ls src/a*b/c.py`, `tests/*/x.py`, `docs/reviews/{a,b}.md` e `docs/x/[ab]/y.md`.
- Continuam cobrados: `bin/forge-check`, `bin/forge-check:702`, `[ -f bin/forge-check ]` e `docs/a.md` antes de um glob na mesma linha.
- O resíduo é o A4. Ele vem da forma que eu mesmo sugeri na rodada 1 (lookahead no fim do segmento). O gatilho é artificial, e por isso fica como recomendação.
- O teste do glob cobre `*`, `?`, `[..]` e `{..}`, e o mutante M16 cobre o lookahead.

**`livre()`.** Troca o `startswith(tuple)` por igualdade, ou por prefixo só para a entrada que termina em `/`. A troca é consistente nos quatro usos: `arquivos_divergentes`, os conflitos dele, `commit_vale` e `cmd_delta`.
- O `KANBAN.md` de `LIVRES` (`bin/forge-check:125`) passa a ser exato. Fica mais estrito, e corretamente: antes `KANBAN.md.x` saía do hash.
- No `arquivos_divergentes`, a exclusão por pathspec (`:(exclude)`) deu lugar a um filtro em Python sobre o diff inteiro. O critério é o mesmo nos dois lados, e some a diferença entre a semântica do pathspec e a do prefixo.
- O `test_d4_so_o_caminho_exato_do_fragmento_sai_do_hash` cobre `.md.md`, `.mdx/` e `.md~`. O de `--base` cobre o merge simulado. Os mutantes são M13 e M15.

**`escopo_pelo_primeiro_pai`.** Os `descartados` são o que a base mudou desde o merge-base (`mb..pais[1]`) e que o merge não deixou igual à base.
- Merge limpo: o arquivo que só a base mudou sai do escopo (igual à base). O que os dois mudaram entra, e o autor já o tocava antes.
- `-s ours`: tudo o que a base mudou volta ao escopo (o teste novo cobre `src/app.txt` e `d.txt` nas etapas codigo, review e pr).
- Sem merge-base: cai em `da_base` inteiro, falha fechada.
- O mutante M4 foi atualizado para a linha nova e o M14 cobre os `descartados`.

**Testes novos.** São focados, um por achado, e citam o achado no comentário:
- os de QA A1, A2 e A4;
- o subcaso de outra branch do G6 (QA A3);
- os de D4 (segurança A2 e QA A5);
- o do `-s ours` (segurança A1).

O único ponto é o A5.

**Ferramentas e checklist.**
- Testes do item: `python3 -m unittest tests.test_etapa_do_brief tests.test_conferencia_base_dono tests.test_portao_diff_proprio tests.test_volta_por_delta tests.test_forge.PrAposMergeDaBase tests.test_forge.EntregasParalelas` deu `Ran 182 tests ... OK`. A suíte completa fica com o pre-push e o CI.
- Mutantes M9 a M16 e o M4 novo: o autor registrou todos mortos (histórico do pedido, 22:05), e não os refiz.
- Teto M14: `git diff --numstat --no-renames 1f7bd7f...044ef1d` dá 363 linhas (`bin/forge-check` 166 e `tests/*.py` 197), abaixo de 400. O PR não toca `hooks/` nem `tests/catraca.py`.
- `bin/forge-check` é controle do Forge, então o PR pede o rótulo do dono.
- Commits em Conventional Commits em português.
- `R-NEUTRO` e `R-CUSTO`: sem achado.
- PA-7 (`docs/engineering/achados-recorrentes.md`): a lista está vazia, então não há item a conferir.
