---
tipo: revisao-seguranca
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c2
commit: 8f74566f2af8aa503238072fffb61188d8b22799
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-fechar-c (branch c2)

Diff lido: `234dbe0..8f74566` (tests/test_fechar.py, tests/test_fechar_tmp.py, changelog.d/impl-fechar-c-c2.md).

**Item entregue:** E2 do pedido, FECHAR-B-REC-REVIEW item 1 (C2 do modelo de ameaças `docs/security/ameacas/fechar-c.md`, SEC-FECHARC-3).

**M14 (agents/tech-lead.md:19):** um comportamento (a limpeza das pastas `fechar-*` dos subtestes); 34 linhas de teste, dentro do teto; nada em `hooks/` nem em `PROTEGIDOS`. Cumpre.

## Gatilhos
`R-SEGURANCA`: controles do Forge (a suíte do `forge-fechar`); a superfície é só de teste.

## Achados

## Detalhe dos achados
- C2-1: a limpeza é registrada logo depois do `mkdtemp` (`tests/test_fechar.py:118`), sobre o caminho que ele devolveu, ignorando pasta já ausente; nunca sobre caminho montado a partir do ambiente. A limpeza dupla com o `tearDown` (`:156`) é inofensiva.
- C2-2: `tests/test_fechar_tmp.py` cria a própria pasta por `mkdtemp`, roda os dois testes de laço num processo filho com `TMPDIR` nela e só lê (`glob`); a remoção é por lista de argumentos, sem shell, e só da pasta criada. Nada é listado nem apagado no `$TMPDIR` real.
- C2-3: `tests/test_fechar_pr_numero.py` e `tests/test_fechar_vars_vazias.py` não mudam.
- Rodado aqui: `tests.test_fechar_tmp` OK.

Sem caminho de ataque: é código de teste, que só cria e apaga pastas próprias.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e teste da suíte. Faltaram no PATH: `shellcheck`, `gitleaks` e `semgrep` (lacuna).
