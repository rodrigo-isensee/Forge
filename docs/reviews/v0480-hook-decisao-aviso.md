---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-hook-decisao-aviso
commit: c517dbe315987b500310e684b95a1cafee385d68
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E172.40 (PR #857, hook decisao só avisa no Stop do Jarvis; revalidação por delta após trazer a develop)

Revalidação pelo delta do parecer anterior (E172.28, aprovado no head `f2db561b`). Delta lido: `forge-check parecer delta docs/reviews/v0480-hook-decisao-aviso.md`, intervalo `f2db561b..c517dbe3`; motivo apontado: `docs/hooks-fixtures.md` mudou depois do parecer (base `origin/develop` `ad113d8`).

## O que o delta traz
- `c517dbe3` é o merge de `origin/develop` (`ad113d80`) na branch. O `git show --cc c517dbe3` mostra conflito resolvido só em `docs/hooks-fixtures.md`; os demais arquivos vieram da develop sem resolução manual.
- O patch do PR contra a base (`git diff --stat ad113d80 c517dbe3`) segue o mesmo do parecer anterior: `hooks/decisao.py`, `hooks/hooks.json`, os 4 fixtures de `tests/hooks/decisao/`, `tests/test_hook_decisao.py`, `tests/test_hooks.py`, `tests/pesos-d4.json`, `bin/forge-testes`, docs e pareceres; nenhuma linha de produção mudou pela resolução.
- Índice regenerado: 3566 fixtures da develop mais 4 do decisao = 3570; a linha `conformidade` vem da develop (2705) e a linha `decisao` (4) da branch. `python3 -I scripts/indice-fixtures.py --conferir`: "docs/hooks-fixtures.md: em dia" (rc 0); regenerar na cópia deu arquivo idêntico ao commitado.

## Achados anteriores
- A1 a A4 seguem fechados (nenhum arquivo deles mudou no delta além do índice).
- A5 (recomendado, corte em 20.000 caracteres antes do `Recomendo`, `hooks/decisao.py:28`) segue aberto; vira cartão depois do merge, sem bloquear.

## CI do head c517dbe3
Run 45453207653 (headSha `c517dbe3`): as cinco partes da suíte nas duas versões do Python, `bateria (passos)`, `bateria (verificações longas)`, `bateria (python 3.14)`, `instalação`, `teto de pulados` e `árvore já provada na develop` verdes; `Catraca` (run 45453207826) verde. O `bateria` agregado está vermelho só por `bateria (pareceres)`, esperado com os pareceres desatualizados pelo merge.

Testes dos arquivos tocados, rodados aqui em `tests/` (com o `TMPDIR` do sandbox): `test_hook_decisao`, `test_hooks.Hooks.test_hooks_json`, `test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia`: `Ran 13 tests ... OK`.
