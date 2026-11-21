---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-heredoc-extglob
commit: 3f94b916db826bc28fe14920abb28bdc2412b52a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 E70.4 (HOOK-HEREDOC-EXTGLOB-E-CAIXA)

Base `bead3e53`, head revisado `3f94b916`, 3 commits (E70.1). Código de controle: 4 linhas em `hooks/parecer.py` (`corpos_de_dado`), dentro do teto H1; o resto é fixture, teste, mutantes, índice e documentação.

## Achados
- A1 (recomendado) hooks/parecer.py:307 · o `endswith("!")` também recusa alvo literal terminado em `!` sem extglob (`cat > bin/x!`, sonda: False); só aperta (o corpo volta a ser conferido como comando), falso positivo raro; se aparecer, olhar o caractere seguinte no texto cru (`(`)

## Sondas

## Parecer
Aprovado. O diff faz o que E70.1 pede, nem mais: o alvo de redireção cujo texto cru termina em `@`, `+` ou `!` (o leitor corta a palavra no `(` do extglob) tira o corpo do caminho "dado", e o nome do alvo se compara com `casefold`.

Sondas de leitura em `corpos_de_dado`, com `ls` na chamada: `bin/@(ls)`, `bin/@(ls)x`, `bin/l@(s)`, `'bin/'@(ls)`, `bin/@(ls|x)`, `bin/LS` e `bin/lS` dão False; `bin/ok.txt` segue True; `?(` e `*(` já caíam na regra do curinga.

Guardas: 2 linhas mudadas, 5 mutantes declarados em `tests/mutantes/v0478-hook-extglob-caixa.json`, todos mortos (`bin/forge-mutante`, rev 3f94b916db82: M1 a M4 em :307, M5 em :309). O teste novo `tests.test_hook_parecer_extglob` roda as 4 fixtures do ramo de falha pelo processo do hook, com mínimo de itens: 2 testes OK em 0,7 s, ambiente limpo.

Registro em `bin/forge-testes` e peso em `tests/pesos-d4.json` coerentes; `docs/hooks.md` traz a premissa do shell; fragmento em `changelog.d/`. Commits em Conventional Commits, um propósito cada. Suíte inteira: sem PR aberto ainda, fica com o CI do PR (`R-REVIEW`), sem rerrodar aqui. Segurança: parecer E70.3 aprovado no mesmo head (72f3e2a3), citado sem refazer (`R-SEGURANCA`).
