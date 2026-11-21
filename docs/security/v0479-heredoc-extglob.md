---
tipo: revisao-seguranca
contrato: 1
pedido: v0478
branch: melhoria/v0479-heredoc-extglob
commit: 3f94b916db826bc28fe14920abb28bdc2412b52a
parecer: aprovado
revisor: forge:security-engineer
data: 2026-11-21
---
# Review de segurança: v0479-heredoc-extglob (v0478 E70.3)

Base `bead3e53`, head `3f94b916`. Mudança de controle: `corpos_de_dado` do hook `parecer` (HOOK-HEREDOC-EXTGLOB-E-CAIXA, E70.1).

## Gatilhos
Gatilhos: hook de controle do Forge (`hooks/parecer.py`, classificador de comando).

## Resumo
`hooks/parecer.py:307` recusa o alvo de redireção cujo texto cru termina em `+`, `@` ou `!` (o leitor corta a palavra no `(` do curinga estendido); `hooks/parecer.py:309` compara o nome do alvo com `casefold`. `corpos_de_dado` só decide se o corpo do heredoc vira `dado` (não marca); as duas mudanças só acrescentam saídas `False` e só aumentam a interseção `alvos & nomes` (`hooks/parecer.py:312`), e `nomes <= PROGRAMAS_DE_DADO` segue igual (os nomes da lista são minúsculos, então o casefold só do lado do alvo não abre caso). Com `False`, o corpo volta à classificação anterior (`hooks/parecer.py:273` em diante), a mais rígida.

Confirmação: só aperta — as duas linhas novas em `hooks/parecer.py:307` e `:309` só transformam em `False` (corpo não é dado, segue conferido) chamadas que antes davam `True`; nenhuma entrada que antes era conferida passa a ser dado, e o resto do diff é teste, fixture, mutante, mapa do `forge-testes`, peso e doc.

## Verificação
- Teste novo de abuso: `python3 -m unittest tests.test_hook_parecer_extglob` no head: 2 testes, OK (4 fixtures `tests/hooks/parecer/heredoc-dado-alvo-*-bloqueia.json`, todas código 2).
- Sondas diretas em `corpos_de_dado` (todas `False`, o esperado): `bin/@(ls)`, `bin/l@(s)`, `bin/?(ls)`, `bin/*(ls)`, `bin/\@(ls)`, `bin/@(ls)x`, `bin/!(cat)`, `bin/LS` com `ls`, `bin/Ls` com `LS`. Legítimo `cat > notas.txt` com corpo de palavra crítica segue `True`.
- `'bin/@'(ls)` dá `True`, mas o bash com extglob recusa a linha por erro de sintaxe (código 2, nada gravado; conferido em pasta temporária), então não há caminho de escrita.
- Custo aceito sem achado: alvo legítimo terminado em `+` (`cat > a+`) perde a classificação de dado e volta a ser conferido; é falso positivo conservador, sem caminho de ataque.
- Suíte: não há PR nem execução de CI nesta branch no momento do parecer; a bateria completa fica para o CI do PR (portão do merge, `R-FLUXO`); por brief, sem suíte local.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff, o módulo de teste novo e sondas locais em pasta temporária; varredura de segredos não aplicável (diff sem credencial).
