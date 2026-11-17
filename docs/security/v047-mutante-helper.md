---
tipo: revisao-seguranca
contrato: 1
pedido: v047
branch: melhoria/v047-mutante-helper
commit: e44d303e087c963d577abfbbf30c04e97a3e0771
parecer: reprovado
revisor: forge:security-engineer
data: 2026-11-16
---
# Review de segurança: v047 (E2.111, melhoria/v047-mutante-helper, lote MU1)

Escopo: `git diff bf475209..4d2a9b7d` (5 arquivos: `bin/forge-mutante`, `tests/test_forge_mutante.py`, `tests/mutantes/v047-mutante-helper.json`, `tests/mutantes/v047-mutante-helper-2.json`, `changelog.d/v047-mutante-helper.md`). Parecer completo (primeira rodada desta branch). A entrega fecha o A5 do parecer `docs/security/v046-mutacao-bench.md` (E7.11, sondas S5 e S6): helper dentro de `tests/test_*.py` importado por outro teste e `.py` de `tests/mutantes/` ficavam fora do apoio de teste da `--base`. Nada em `.github/` nem em `.githooks/`.

## Gatilhos
Controle do Forge (`R-SEGURANCA`): `bin/forge-mutante --base` decide quais mutantes rodam na revalidação do QA (portão `R-QA`).

## Achados
- A2 (bloqueante) tests/mutantes/v047-mutante-helper-2.json:20 · `linha_base` da isenta é 810, mas na base 86ac0fcb a condição está em bin/forge-mutante:919; `--cobertura` sai 2 (S4) e `--conferir` aponta o desencontro (S5). Trocar 810 por 919 e rodar os dois de novo.
- A1 (recomendado) bin/forge-mutante:811 · o grep é por linha: import em várias linhas (parênteses ou barra) e import dinâmico de test_*.py não marcam apoio (S1-S3); a suíte hoje não usa essas formas (corpus 176/176 igual à leitura sintática). Baixa; tratar se a forma aparecer.

## Sondas
- S4 · `bin/forge-mutante --cobertura --base 86ac0fcb9495d11343049b8cdecb25419aed1cf9` · espera: rc 0 ou 1 · obtido: rc=2, `isenta que não cruza condição listada ou cujo trecho não casa uma vez: ...v047-mutante-helper-2.json`
- S5 · `bin/forge-mutante --conferir --base 86ac0fcb9495d11343049b8cdecb25419aed1cf9` · espera: `conferidas: ...` rc 0 · obtido: `v047-mutante-helper-2.json: isenta 1 · linha_base 810 de bin/forge-mutante sem condição com o trecho na base`

## Detalhe dos achados
**Fechamento do A5 da v046 E7.11.** `apoio_de_teste` (`bin/forge-mutante:819-830`) passa a tratar como apoio todo arquivo de `tests/mutantes/` que não é `.json` e todo `tests/test_*.py` mudado que outro `.py` de `tests/` importa no `rev` (`importado_por_teste`, `:807-816`), cobrindo as quatro formas pedidas na correção mínima (`import <stem>`, `from <stem> import`, `from tests.<stem> import`, `from tests import <stem>`) e ainda `from .<stem>`, `import a, <stem>` e `as`. O `git grep` com rc > 1 vira `RuntimeError`, capturado em `dirigir` (`:841-846`), que sai 2: falha fechada, não "nada achado". O `--help` (`:20-22`) foi ajustado (AR-9). Os testes S5 e S6 de `MutacaoDirigida` esperam rc 1, a linha `apoio de teste no diff` e `M1 · sobreviveu`; o terceiro cobre as formas de import, o falso positivo de prefixo (`test_so` vs `test_soma`, nome em string) e o grep que falha. `sha` vem de `resolver` (commit resolvido), e o padrão vai por `-e`, sem injeção de opção; o stem passa por `re.escape`, e nomes de módulo importáveis só têm `[A-Za-z0-9_]`.

**Conferência contra o corpus de legítimos.** Para os 176 `tests/test_*.py` do head, `importado_por_teste(..., "HEAD")` coincide com a leitura sintática dos imports de todos os `.py` de `tests/` (24 importados, 0 divergência). Sem falso negativo na suíte atual; o falso positivo possível (linha que começa com `import`/`from` dentro de string) só põe mais mutantes para rodar, o lado seguro.

**A1, resíduo da mesma classe (baixa, recomendado).** Evidência: `bin/forge-mutante:811`, padrão por linha. Sondas numa repo temporária, chamando `apoio_de_teste({"tests/test_<x>.py"}, "HEAD")`: (S1) `from tests import (\n    x,\n    test_m,\n)` dá `[]`; (S2) `from tests import x, \\\n    test_n` dá `[]`; (S3) `importlib.import_module('tests.test_o')` dá `[]`. Caminho: o autor, entre o head aprovado e a revalidação, esvazia um helper de `test_*.py` importado só por uma dessas formas e mexe em outro arquivo da spec; a dirigida pula o mutante. Por que não bloqueia: nenhuma dessas formas existe hoje na suíte (`tests/*.py` sem `from ... import (` multilinha, sem continuação por barra em import e sem carga dinâmica de `test_*.py`), o `test_*.py` mudado aparece no delta lido por review, segurança e QA, e a 1.ª rodada do QA é a spec inteira, como no A5. Correção mínima, se a forma aparecer: trocar o grep por leitura sintática dos imports (`ast`) dos `.py` de `tests/` no `rev` via `git show`, ou ampliar o padrão para o bloco entre parênteses. Esforço: P. Dono: `tech-lead`.

**Revalidação por delta no head e44d303e (2026-11-16).** `forge-check parecer delta` traz `bin/forge-mutante` e três specs, mas o diff do item contra a develop (`git diff origin/develop...HEAD -- bin/forge-mutante`) tem as mesmas linhas +/- do aprovado em 4d2a9b7d (comparadas, iguais): o resto do delta veio da develop (`--conferir`, `teste_no_commit`, `anotar`). Nada novo em `hooks/`, `.githooks/`, `.github/`, `scripts/` no item. O realinhamento de M41, M19 e M20 em `guarda-sem-mutante-7.json` e `v046-mutacao-bench-3.json` troca só `de`/`para` pelo texto atual da fonte, sem afrouxar guarda. A1 segue recomendado, sem mudança.

**A2, bloqueante.** O merge da develop deslocou a condição velha de `apoio_de_teste` da linha 810 para a 919 da base; a isenta do `-2.json` guarda `linha_base: 810`. Efeito: a checagem do autor `--cobertura --base <Base-sha>` sai 2 em vez de informar a cobertura (S4). Não é ataque: é controle do Forge (`R-SEGURANCA`) que falha fechado e deixa o portão R-QA sem a conferência de condição sem mutante até o ajuste. Correção mínima: `linha_base` 919 (conferir com S4 e S5). Esforço: P. Dono: `qa-engineer`.

## Riscos aceitos e ferramentas
Nenhum risco aceito. `tests.test_forge_mutante.MutacaoDirigida` rodado no clone em `e44d303e`: 11 testes, OK (os três novos incluídos). A suíte inteira roda no CI do PR. Sondas S1 a S3 e a conferência do corpus rodadas com um script em `$TMPDIR`, carregando `bin/forge-mutante` do clone, sem escrita na árvore do autor. Ferramentas ausentes no PATH (lacuna, não instaladas): gitleaks, semgrep, zizmor, actionlint; o delta não toca workflow nem traz segredo.
