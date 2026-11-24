---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0480-clone-nome-unico
commit: 56f3d992094b15b88b6210019abc1104ee4bcf1a
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-24
---
# Review: v0478 E172.31 (PR #860, revalidação por delta no head 56f3d992)

Base 5f1c6e97; parecer anterior reprovado no d33eb54d (A1 bloqueante, A2 recomendado). Volta única 56f3d992 (E172.22): `bin/forge-check` (+3/-3), `bin/forge-testes` (+1/-1), fragmento de changelog, spec de mutantes (M1 refeito, M8 novo), `tests/test_forge_copia.py` (+10/-2). Código bem abaixo do teto H1.

## Delta lido
`forge-check parecer delta docs/reviews/v0480-clone-nome-unico.md`: intervalo d33eb54d..56f3d992, cinco arquivos no domínio (`bin/forge-check`, `bin/forge-testes`, `changelog.d/v0480-clone-nome-unico.md`, `tests/mutantes/v0478-clone-nome-unico.json`, `tests/test_forge_copia.py`); li só esse diff.

- A1 (anterior) resolvido: `test_forge_copia` entrou na tupla `FORGE_CHECK` de `bin/forge-testes:160`; `test_testes_tocados.MapaDoForgeCheck` passa (3 testes OK).
- A2 (anterior) resolvido: o fragmento diz que o brief põe a marca a preencher no lugar do id fora da forma, que é o que o código faz (aviso e rc 0).
- Guarda do id (`bin/forge-check:9567`): troca `ID_DE_PEDIDO.fullmatch` por `valor_de_shell_seguro("pedido", ...)`, que usa `NOME_SEGURO_DE_BRIEF` (`[A-Za-z0-9][A-Za-z0-9._-]*`): mesmo alfabeto, só proíbe o hífen no início; fecha `--lote`/`-h` virando opção do `forge-fechar`. Teste de comportamento novo (`test_id_do_pedido_com_hifen_no_inicio_nao_vira_opcao`, subtestes `--lote` e `-h`) e mutante M8, que volta à guarda antiga, morre.
- Linha da cópia (`bin/forge-check:9629`): o comando na crase passa a ter um subcomando só (`clone`), com o worktree do Forge dito fora da crase; teste de igualdade do texto atualizado.

## Ferramentas (citadas, sem refazer a suíte)
- `bin/forge-mutante tests/mutantes/v0478-clone-nome-unico.json --rev 56f3d992 --processos 1`: M1 a M8 morreram (rc 0); 8 mutantes, dentro do limite do arquivo.
- `bin/forge-mutante --cobertura --base d33eb54d --rev 56f3d992`: guarda `bin/forge-check:9567` coberta por M1 e M8.
- `python3 -m unittest test_forge_copia` (pasta `tests`): 77 testes OK.
- CI do PR: a suíte em 5 partes estava pendente na leitura; `catraca` e `bateria (pareceres)` vermelhas, esperadas enquanto faltam os pareceres no head. O merge segue condicionado ao CI verde (`R-FLUXO`).

## Parecer
Aprovado: as duas pendências do review anterior e a A2/A3 da segurança estão corrigidas no delta, com teste de comportamento e mutante para a guarda mudada.
