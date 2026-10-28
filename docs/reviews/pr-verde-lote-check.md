---
tipo: review
contrato: 1
pedido: pr-verde-lote-check
branch: melhoria/pr-verde-lote-check
commit: 10c5b7fc05792a515db5c69b9765d35bc540718a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-10-27
---
# Review: pr-verde-lote-check (PR-VERDE-LOTE-CHECK-REV E1.1, revalidação por delta da volta 2)

Intervalo revisado: `1f7bd7f...10c5b7f`. Rodada anterior sobre `044ef1d` (parecer `3dfb280`, aprovado). Esta rodada lê só o delta `044ef1d..10c5b7f`. O único commit do autor é `10c5b7f`: dois testes e a spec de mutantes `-3`, que respondem aos A1 e A2 do QA (`041a6f9`). Os outros commits do intervalo (`10e4eef`, `3dfb280`, `041a6f9`) são pareceres.

## Achados
- A2 (recomendado) tests/test_forge.py:4527 · segue da rodada 1: na etapa pr, falta afirmar que o commit do autor feito depois do merge que mexe em src/y.txt volta ao escopo
- A3 (recomendado) bin/forge-check:1051 · segue da rodada 1: no escopo pelo primeiro pai, as contagens +/- são as do intervalo inteiro (só informativo)
- A4 (recomendado) bin/forge-check:4384 · segue: curinga no meio do segmento seguido de pasta da raiz ainda é cobrado (`ls x*bin/nao-existe`); gatilho artificial
- A5 (recomendado) tests/test_etapa_do_brief.py:180 · segue: o teste do corte legítimo da etapa de outro papel não afirma o `rc`

## Parecer
**Aprovado.** O delta não traz bloqueante. Ele só acrescenta testes e mutantes, e o `bin/forge-check` não mudou desde `044ef1d`. Os A2 a A5 seguem como recomendações, sem promoção. O único ajuste é o A2: a linha passou de 4519 para 4527 porque o teste novo entrou antes dela.

**Delta lido** (saída de `forge-check delta --parecer docs/reviews/pr-verde-lote-check.md`, rc 0):
- `tests/mutantes/pr-verde-lote-check-3.json`: 1-26 (novo).
- `tests/test_forge.py`: 4452-4459.
- `tests/test_volta_por_delta.py`: 458-462.

Já lido, sem nova leitura: o resto de `1f7bd7f...044ef1d`, revisado nas rodadas anteriores (`e7b98ed` e `3dfb280`).

**`test_conflito_em_arquivo_livre_nao_invalida` (QA A1, M17).**
- A branch e a develop mudam `docs/qa/x.md`, e o conflito é resolvido com `--ours`.
- O `src/y.txt` da develop faz o merge rodar de fato (o teste afirma `rc 1` do merge).
- O `pr --base develop` precisa sair com `(0, "")`.
- O teste prende a guarda `if livre(nome, ignorar): continue` dos conflitos (`bin/forge-check:423`).

**`test_arquivo_de_nome_parecido_com_o_livre_aparece_no_delta` (QA A2, M18).**
- O commit tem `KANBAN.md.x` e `KANBAN.md`.
- O delta lista só o primeiro, o que prende a igualdade de `livre()` no `cmd_delta` (`bin/forge-check:1151`).
- O `[:3]` limita a checagem às linhas do arquivo que importa, sem depender da ordem do resto.

**Ferramentas e checklist.**
- Testes do item: `python3 -m unittest tests.test_forge.PrAposMergeDaBase tests.test_volta_por_delta` deu `Ran 74 tests ... OK`. A suíte completa fica com o pre-push e o CI.
- Mutantes: `bin/forge-mutante tests/mutantes/pr-verde-lote-check-3.json` (rev `10c5b7fc0579`) deu `M17 · morreu · bin/forge-check:423` e `M18 · morreu · bin/forge-check:1151`, rc 0.
- Teto M14, pela minha conta: `git diff --numstat --no-renames 1f7bd7f...10c5b7f` dá 376 linhas de código e teste, abaixo de 400:
  - `bin/forge-check`: 166.
  - `tests/test_conferencia_base_dono.py`: 44.
  - `tests/test_etapa_do_brief.py`: 70.
  - `tests/test_forge.py`: 42.
  - `tests/test_portao_diff_proprio.py`: 45.
  - `tests/test_volta_por_delta.py`: 9.
  - Ficam fora as specs de `tests/mutantes/`, as fixtures, os pareceres, o fragmento e o `.md` (`agents/conferente.md`). O PR não toca `hooks/` nem `tests/catraca.py`.
- `bin/forge-check` é controle do Forge, então o PR pede o rótulo do dono.
- O commit `10c5b7f` está em Conventional Commits em português e cita os achados.
- `R-NEUTRO` e `R-CUSTO`: sem achado.
- PA-7 (`docs/engineering/achados-recorrentes.md`): a lista está vazia, então não há item a conferir.
