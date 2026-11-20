---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-bp3-s4-retomada
commit: 126e98b664c6229921f01a34a8dbc3c2d3fd5c74
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-20
---
# Review: v0478 E39.36 (BP3 S4, `forge-check retomada`), revalidação no head 126e98b6

## Escopo lido
Só o delta: `forge-check parecer delta docs/reviews/v0479-bp3-s4-retomada.md`, intervalo `687112b1..126e98b6` (volta da segurança, E39.39). No domínio: `bin/forge_retomada.py`, `changelog.d/v0479-bp3-s4-retomada.md`, `tests/mutantes/v0479-bp3-s4-retomada-{1,2,3,recomendados}.json`, `tests/test_forge_check_retomada.py`. O parecer anterior aprovou 687112b1 com o diff inteiro `cf097822..687112b1`; o resto não mudou e não foi relido.

## Ferramentas citadas
- Tamanho (H1): `forge-check pr v0478 --previo --base origin/develop` no head, só a linha de classe C, sem aviso de teto; `git diff --numstat origin/develop...HEAD -- bin/ hooks/` dá 137 (`bin/forge_retomada.py`) + 7 (`bin/forge-check`) + 2 (`bin/forge-testes`) = 146 linhas, dentro das 150.
- Teste do item: `python3 -m unittest tests.test_forge_check_retomada`, 45 testes OK em 45,8 s no head (4 novos). Suíte inteira: no CI do PR (`R-REVIEW`), não rerrodada.
- Mutantes do delta, `bin/forge-mutante --processos 1` no rev 126e98b664c6: M1, M2, M3, M4 (`-recomendados.json`) e M7, M15, M32, M33, M34 (alinhados) morreram todos.

## Leitura do delta
- `forma()` só deixa passar `tipo`, `id` e branch que casam a forma e não têm `..`; o que falta sai `?` (ou `sem id`), e a branch tem teto de 8 itens e 200 caracteres. Teste com texto de injeção, `a/../b` e campo de 900 KB.
- Retirada do M19 conferida: os campos interpolados na linha são agora todos de forma fechada (`TIPO`, `ID`, `REF`; `caminho` por `BRIEF_GRAVAVEL` e `sha256` por `HASH_GRAVAVEL` em `hooks/agentes.py:578-579`, via `briefs_validos`; `ACOES` fixo), sem caractere de controle possível; tirar o `sem_controle` não muda a saída, logo o mutante é equivalente. O `sem_controle` fica como defesa em profundidade, e o teste de linha forjada (`tests/test_forge_check_retomada.py:318`) continua.
- `suja()` com `--no-optional-locks`, testado pelo mtime do index da worktree (M4).
- `acao()`: juntar `sem_brief` e `vencido` num `if` é equivalente (`atual is None` sempre difere do sha gravado); M15 alinhado.
- `entregue()`: o `any()` testa o `--is-ancestor` antes do `git show`, o que resolve o A4 do parecer anterior; mesmo resultado, menos processos.
- Commits limpos, Conventional Commits em português.

## Achados
- A1 (recomendado) bin/forge_retomada.py:99 · segue do parecer anterior: a base que andou não leva a `vencido` (matriz 4.2 do desenho); implementar ou corrigir a tabela na S6.
- A2 (recomendado) bin/forge_retomada.py:100 · segue do parecer anterior: item `vencido` ou `sem_brief` com worktree suja não leva o "nunca descartar"; juntar o aviso quando `suja()` for verdadeiro.
- A3 (recomendado) bin/forge_retomada.py:3 · o changelog passou a "sem rede, até 3 s", mas a docstring e a ajuda do `--contar` (bin/forge-check:10202) ainda dizem "sem git", e `agentes.arquivo_de_estado` consulta o git; alinhar o texto.
- A4 (recomendado) tests/mutantes/v0479-bp3-s4-retomada-recomendados.json:2 · `pedido: v0478` difere dos outros três arquivos (`v0479-bp3-s4-retomada`) e os ids M1-M4 repetem os do `-1.json`; numerar a seguir (M37+) e usar o mesmo `pedido`, para o relatório do `forge-mutante` não ter dois M1.

## Parecer
Aprovado no head 126e98b6. Delta lido: forma dos campos, `--no-optional-locks`, M1-M4 novos, M7/M15/M32-M34 alinhados, M19 retirado por equivalente (conferido), módulo em 146 linhas de código. Nenhum defeito provado; o A4 anterior foi resolvido; os quatro achados são recomendados (`R-REVIEW`) e viram cartão depois do merge. Segurança e QA são portões à parte.
