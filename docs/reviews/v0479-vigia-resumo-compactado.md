---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-vigia-resumo-compactado
commit: 8b7f670d5aa188ec3be78ff7c4e5d4cb63349396
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-vigia-resumo-compactado

Etapa E93.11 (revalidação, H3): `forge-check parecer delta` em `9ec21d93..8b7f670d`, sem o que veio da base; no domínio só `docs/hooks-fixtures.md` (3379 → 3382, as 3 fixtures `autor-*` do #775) e `docs/hooks.md`, cujo trecho do item é o mesmo. O head é o merge da `develop` 9d5dcb6e; o patch do item, sem pareceres e índice, tem o mesmo `git patch-id` (5adf7b4c) antes e depois; `scripts/indice-fixtures.py --conferir`: `docs/hooks-fixtures.md: em dia`; `python3 -I tests/test_vigia.py`: `Ran 12 tests ... OK`. Parecer mantido.

Antes, etapa E93.7 (revalidação, H3), cartão FALA-DO-DONO-RESUMO-COMPACTADO. Delta lido: `forge-check parecer delta` no intervalo `06a0220a..9ec21d93`, 7 arquivos no domínio (`hooks/vigia.py`, `tests/test_vigia.py`, 2 fixtures novas de `vigia`, `tests/mutantes/v0479-vigia-resumo-compactado.json`, `docs/hooks-fixtures.md`, fragmento em `changelog.d/`). Código: `hooks/vigia.py`, +5 −2, dentro do teto H1.

## Parecer
Aprovado.

- **A1 do review anterior (resolvido):** a marca passa a ser `is` seguido de maiúscula (`re.compile(r"is[A-Z]")` com `marca.match`), então `issueRef` ou `isolado` não tiram mais o registro. Teste de comportamento `test_campo_que_comeca_com_is_sem_maiuscula_nao_e_marca`, fixture `entrada-campo-issue-ref-nao-e-marca-avisa` (registro digitado com `issueRef` avisa) e mutante M7 (`is[A-Z]` → `is`) declarado e morto. O `de` do M2 acompanha a linha nova.
- **A1 da segurança (forma da IDE):** a docstring registra que a ausência de `origin` é também a forma atual da extensão de IDE (com `promptId`), não legado a remover; teste `test_forma_da_ide_sem_origem_com_prompt_id_conta` e fixture `entrada-forma-da-ide-sem-origem-avisa` cobrem. O parecer de segurança decide o mérito; aqui só confiro o código e o teste.
- **Documentação:** índice `docs/hooks-fixtures.md` (3379, vigia 56) e fragmento do changelog atualizados.
- **Commit:** um só, Conventional Commits em português, com a etapa.
- **Suíte:** inteira só no CI do PR; aqui rodei só o recorte do brief.

Provas (rodadas no head 9ec21d93, `env -i` e TMPDIR de `mktemp -d`):
- `python3 -m unittest tests.test_vigia`: `Ran 12 tests ... OK`.
- fixtures `vigia` e `meta` pelo runner `fixtures.py` (`Sub.test_vigia_e_meta`, `executar_em_lote` do `test_hooks`): `fixtures: 88`, `OK`.
- `bin/forge-mutante --processos 1 tests/mutantes/v0479-vigia-resumo-compactado.json`: M1 a M7 `morreu` (vigia.py:308, 311, 310, 313, 316, 315, 322).
