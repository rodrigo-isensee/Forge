---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-hook-decisao-aviso
commit: f2db561b4e2220f4ae8411f1f4432e3a35b813f0
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E172.28 (PR #857, hook decisao só avisa no Stop do Jarvis; revalidação por delta)

Revalidação pelo delta do parecer anterior (E172.10, reprovado no head `2ecd153c`). Delta lido: `forge-check parecer delta docs/reviews/v0480-hook-decisao-aviso.md`, intervalo `2ecd153c..f2db561b`, no domínio: `bin/forge-testes`, `docs/hooks-fixtures.md`, `tests/hooks/decisao/` (4 fixtures), `tests/pesos-d4.json`, `tests/test_hooks.py`. Nenhum arquivo de produção (`hooks/decisao.py`, `hooks/hooks.json`) mudou no delta.

## Achados anteriores
- A1 fechado: `tests/test_hooks.py:1546` admite `decisao.py` só no Stop, com o motivo (só aviso ao usuário, R-DECISAO; ADR 0003, item 1) no texto do assert; a checagem de saída (`tests/test_hooks.py:860`) exige Stop e nenhum `reason` para o decisao.
- A2 fechado: `tests/hooks/decisao/` traz `sem-forge-versao`, `erro-interno`, `duas-decisoes-avisa` e `uma-com-recomendo-silencio`; o decisao entrou na tupla dos que só avisam (`tests/test_hooks.py:1531`); o índice `docs/hooks-fixtures.md` foi regenerado (3520 fixtures).
- A3 fechado: `test_hook_decisao` com peso 0.7 em `tests/pesos-d4.json` (a troca de lugar de `test_fechar_limpar_clone` é só ordenação).
- A4 fechado: `bin/forge-testes:227` liga `hooks/decisao.py` e `hooks/hooks.json` a `RODAM_OS_HOOKS + test_hook_decisao`.
- A5 (recomendado, corte em 20.000 caracteres antes do `Recomendo`) segue aberto no código (`hooks/decisao.py:28`); vira cartão depois do merge, sem bloquear.

## CI do head f2db561b
Run 45436685276 (headSha `f2db561b`): as cinco partes da suíte nas duas versões do Python, `bateria (passos)`, `bateria (verificações longas)`, `instalação`, `teto de pulados` e `catraca` verdes. O `bateria` agregado está vermelho só por `PARECERES: failure` (log do job 138602195146: "passos: success; pareceres: failure; verificações: success; partes: success; pulados: success"), esperado com pareceres pendentes; o de segurança está reprovado e é do `security-engineer`.

Testes dos arquivos tocados, rodados aqui em `tests/` (com o `TMPDIR` do sandbox): `test_hook_decisao`, `test_hooks.Hooks.test_hooks_json`, `test_hooks.Hooks.test_cada_hook_tem_caso_que_passa_e_que_bloqueia`, `test_forge.PesosDaSuite.test_pr_nao_aumenta_os_modulos_sem_peso`: `Ran 14 tests ... OK`; `test_testes_tocados.MapaCobreOQueOsTestesLeem`: `Ran 6 tests ... OK`.
