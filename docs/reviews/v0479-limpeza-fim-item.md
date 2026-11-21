---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-limpeza-fim-item
commit: 011d6e1b9db4f44d236988740619d1776b8922aa
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0478 (E68.4, E68.9, E68.14 e E68.18, melhoria/v0479-limpeza-fim-item)

Diff revisado: `bead3e53..71996730` (base `develop`), 3 commits: `bin/forge-copia` (+84/-4, subcomando `limpar`), `bin/forge-fechar` (+35/-1, `limpar_copias_sem_merge`), `skills/trabalho-em-paralelo/ritmo-e-corte.md` (+1), fragmento em `changelog.d/`, testes em `tests/test_forge_copia.py` e `tests/test_forge_fechar.py` e três specs de mutante (24 linhas de guarda).

## Achados
- A1 (recomendado) bin/forge-fechar:810 · a comparação do origin do clone com o url_aqui (`&& [ ... = "$url_aqui" ]`) é guarda sem mutante próprio e sem teste do ramo de falha: trocada por `true`, os 29 testes de tests/test_forge_fechar.py passam. Cartão: teste com clone de outro origin na mesma branch.
- A2 (recomendado) bin/forge-fechar:798 · a regra de fim do item (PR CLOSED com isCrossRepository false, ou `vazio: sim`) fica escrita em dois lugares, no fim_sem_merge (shell) e no forge-copia limpar (Python), e uma pode mudar sem a outra. Cartão: uma fonte só, por exemplo um `forge-copia fim <ref>` que o forge-fechar chame.

## Parecer
Aprovado (`R-REVIEW`).

- **Faz o que o cartão pede:** o LIMPEZA-AO-FIM-DO-ITEM pedia apagar a cópia também com PR fechado sem merge, com `vazio: sim` e nos projetos. O `forge-copia limpar` lê o fim do item (`gh pr list`: MERGED ou CLOSED sem OPEN; sem PR, `forge-check vazio`), e o `forge-fechar --limpar` sem merge e sem PR aberto passa a ele as cópias da branch. Nenhuma branch, local ou remota, é apagada. Não toca `bin/forge-check` nem `hooks/conformidade.py`, que estão pausados.
- **Só apaga o que é seguro:** a cópia precisa ficar em `~/.forge-contrib` (o `commonpath` sobre o `realpath` barra `..` e link), ser a raiz git e estar numa branch. Não pode ter mudança, commit fora das refs remotas nem, no caso do clone, stash ou worktree ligada. A worktree sai por `git worktree remove`, sem a opção que força (`R-VERIFY`); quando ela está travada, sai com código 1 e continua no lugar, e há teste disso. Na falha, cada `ler` devolve rc diferente de zero e vira recusa.
- **Sem custo (`R-CUSTO`):** nos testes, o `gh` é falso e fica no PATH, então nada sai para a rede.
- **Tamanho (H1):** cerca de 115 linhas de código e um comportamento só, abaixo do teto.
- **Testes e ferramentas:** rodei os testes novos, `tests.test_forge_copia.Limpar` e `tests.test_forge_fechar.LimparSemMerge`, e passaram os 26. A suíte inteira, o shellcheck, a catraca e a mutação valem pelo PQ do autor no histórico de 2026-11-21 07:04 (27 testes, 24 mutantes mortos). Não há PR, portanto não há CI para citar.
- **A1** é falta de teste numa guarda que já é redundante: mesmo sem ela, o `forge-copia limpar` relê o fim do item no repositório da própria cópia e exige a cópia limpa. Fica como recomendado e vira cartão.

## Revalidação no head 9aa1e723 (E68.9)
Delta lido: `forge-check parecer delta` (`71996730..8767adfe`, domínio código e testes): `bin/forge-copia`, `changelog.d/v0479-limpeza-fim-item.md`, `tests/mutantes/v0479-limpeza-fim-item-4.json`, `tests/test_forge_copia.py` e uma linha de `tests/test_forge_fechar.py`.

- **A1 da segurança (PR de fork):** o `gh pr list` passa a ler `state,isCrossRepository`, e só o PR do próprio repositório (`false`) conta como fim do item. PR de fork com o mesmo nome cai no `forge-check vazio`. O `gh` falso do teste recusa a chamada sem `isCrossRepository`, então ele é tão estrito quanto o script (checklist 12).
- **A2 da segurança (escrita durante a consulta):** a conferência de limpeza vira `sujeira()`, sem mudar o comportamento, e roda de novo logo depois do `gh`, antes de apagar. A janela que sobra, entre a segunda conferência e a remoção, é curta, e o `git worktree remove` sem força recusa worktree suja.
- **Mutantes:** rodei `bin/forge-mutante tests/mutantes/v0479-limpeza-fim-item-4.json` e morreram os 3 (M25 `bin/forge-copia:120`, M26 `:167`, M27 `:161`). O M27 só morre porque o teste trava o `gh`, e assim prova que a cópia suja fica antes de qualquer consulta.
- **Testes:** `tests.test_forge_copia.Limpar` e `tests.test_forge_fechar.LimparSemMerge` passaram os 28. A suíte inteira fica para o CI do PR.
- O A1 recomendado (`bin/forge-fechar:810`) fica como estava, porque o delta não toca nessa linha.

Parecer mantido: aprovado (`R-REVIEW`).

## Revalidação no head 70115210 (E68.14)
Delta lido: `forge-check parecer delta` (`9aa1e723..70115210`, domínio código e testes): `bin/forge-fechar`, `changelog.d/v0479-limpeza-fim-item.md`, `tests/mutantes/v0479-limpeza-fim-item-5.json` e `tests/test_forge_fechar.py`.

- **O contrato antigo volta:** sem PR MERGED nem aberto, o `--limpar` só passa as cópias ao `forge-copia limpar` se o `fim_sem_merge` achar prova, isto é, um PR CLOSED do próprio repositório ou um `forge-check vazio` com rc 0 e `vazio: sim`. Sem prova, sai com a mesma mensagem da base `bead3e53` (`bin/forge-fechar:1270` de lá) e não apaga nada. O `test_c3` de `tests/test_fechar.py` não mudou e continua passando.
- **Testes:** são 5 novos, um para cada ramo (sem PR, PR de fork, `vazio: não`, `vazio` com rc 2 e `vazio: sim`). O falso do `forge-check` devolve a linha e o rc escolhidos, e a lista do `gh` ganhou a 5ª coluna, a mesma que o script lê (checklist 12). Rodei `tests.test_fechar`, `tests.test_forge_fechar` e `tests.test_forge_copia`: 202 testes, OK (1 pulado).
- **Mutantes:** rodei `bin/forge-mutante tests/mutantes/v0479-limpeza-fim-item-5.json` e morreram os 4 (M28 `bin/forge-fechar:1311`, M29 `:798`, M30 `:799`, M31 `:800`). Cada linha de guarda do delta tem o seu mutante.
- O shellcheck não está instalado nesta cópia, então vale o do CI do PR, assim como a suíte inteira.
- O A1 fica como estava. O A2 é novo e recomendado: não há defeito hoje, só risco de as duas cópias da regra se desencontrarem.

Parecer mantido: aprovado (`R-REVIEW`).

## Revalidação no head 011d6e1b (E68.18)
Delta lido: `forge-check parecer delta` (`70115210..011d6e1b`, domínio código e testes, sem o que veio da base): só `skills/trabalho-em-paralelo/ritmo-e-corte.md`. O commit `05bf2146` trouxe a `develop` `a6baf239` sem conflito, e o que veio da base fica fora do parecer. A `develop` já está em `b18d3ea3` e entra na hora da integração (`R-FLUXO`).

- **Linha 44:** o comando passa a `forge-fechar <pedido> --ref <branch> --limpar`, que bate com o uso de `bin/forge-fechar:3-4` (`<pedido>` e `--ref` obrigatórios, `--limpar` existe). As linhas 22 e 31 com a mesma forma vieram da `develop`.
- **Testes:** rodei `tests/test_comando_pronto.py` (3, OK) e `tests/test_metricas_texto.py` (2, OK), com o ambiente limpo e `python3 -I`. A suíte inteira fica para o CI do PR.
- O A1 e o A2 recomendados ficam como estavam, porque o delta não toca nessas linhas.

Parecer mantido: aprovado (`R-REVIEW`).
