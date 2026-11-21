---
tipo: review
contrato: 1
pedido: v0478
branch: melhoria/v0479-vigia-resumo-compactado
commit: 9ec21d93d609fc49aa696f796236f59586529572
parecer: aprovado
revisor: forge:tech-lead
data: 2026-11-21
---
# Review: v0479-vigia-resumo-compactado

Etapa E93.7 (revalidação, H3), cartão FALA-DO-DONO-RESUMO-COMPACTADO. Delta lido: `forge-check parecer delta` no intervalo `06a0220a..9ec21d93`, 7 arquivos no domínio (`hooks/vigia.py`, `tests/test_vigia.py`, 2 fixtures novas de `vigia`, `tests/mutantes/v0479-vigia-resumo-compactado.json`, `docs/hooks-fixtures.md`, fragmento em `changelog.d/`). Código: `hooks/vigia.py`, +5 −2, dentro do teto H1.

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
