---
tipo: review
contrato: 1
pedido: v0481
branch: melhoria/v0481-prazo-forge
commit: ecb13af6dac68a1f57c173c7000e03bbb5a71054
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-25
---
# Review: v0481

Review por delta (E7.50, volta E7.49) de 4ab16b74 a ecb13af6. Li o delta pelo `forge-check parecer delta docs/reviews/v0481-prazo-forge.md` (intervalo 4ab16b74..ecb13af6). Do autor: o merge da develop 43937681 (traz o #885, o #898 e o #874) e ecb13af6 (`tests/mutantes/v0481-prazo-forge.json`). O `hooks/conformidade.py` e o `tests/test_hooks.py` que o delta lista são do #885, revisado no PR de origem (ordem do dono de 25/11): o `git diff-tree --cc 43937681` só mostra a mão do autor em `docs/hooks-fixtures.md`.

## Parecer
Aprovado: a volta faz só o que o brief da E7.49 pede.

- **Conflito.** A resolução em `docs/hooks-fixtures.md` é o índice gerado (3590 fixtures, `conformidade` 2716). `python3 -I scripts/indice-fixtures.py --conferir`: "em dia", e `ls tests/hooks/*/*.json | wc -l` dá 3590. Os outros arquivos entraram no merge sem conflito, sem mudança do autor.
- **Isenção com motivo verdadeiro.** A guarda da base (`hooks/_comum.py:2875`, `if critico is None and evento != "PreToolUse": return`, depois do `return` no `PostToolUse`) foi reescrita, não apagada: `recusa = evento != "PostToolUse" and (critico is not None or evento == "PreToolUse")` (`hooks/_comum.py:2924`) é a mesma condição pelo De Morgan, com o `PostToolUse` da linha de cima incluído. O M2 da spec (`recusa = True`) morre no head. A isenção não afrouxa nada: a linha nova tem mutante próprio.
- **Catraca no head.** O motivo "guarda apagada" saiu. Ficam a mudança em `hooks/_comum.py` e `hooks/conformidade.py`, que espera o rótulo do dono (controle, R-CONFORMIDADE), e o aviso de valor esperado trocado, que não barra. O afrouxa na margem foi aceito pelo dono em 25/11 21:15.

Verificadores que rodei no Revisar-sha:
- `bin/forge-mutante --cobertura --base 34ab6714`: rc 0. A 2875(base) aparece como `isenta`, com o motivo, e as guardas do diff estão cobertas. `--conferir --base 34ab6714`: "o trecho de cada spec do diff está no lugar".
- `bin/forge-mutante tests/mutantes/v0481-prazo-forge.json --ids M2 --processos 1`: `M2 · morreu · hooks/_comum.py:2924`.
- Não rodei nenhum módulo de teste: o delta do autor não muda código nem teste, só a spec e o índice.
- CI do head (check-runs de ecb13af6): as 10 partes da suíte, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, os tetos de pulados, a instalação e a `árvore já provada` estão verdes. `bateria (pareceres)` e `bateria` estão vermelhas porque falta o parecer, e a `catraca` espera o rótulo. Nenhum dos três conta para o G3.
- Tamanho H1: o delta não tem código, só JSON da spec e o índice gerado.

- ci: ecb13af6dac68a1f57c173c7000e03bbb5a71054 verde
