---
tipo: revisao-seguranca
contrato: 1
pedido: impl-fechar-c
branch: melhoria/impl-fechar-c-c3
commit: db42e846f81b40b7e118effac35d5234ed04efc5
parecer: aprovado
revisor: forge:security-engineer
data: 2026-10-31
---
# Review de segurança: impl-fechar-c (branch c3)

Diff lido: `234dbe0..db42e84` (bin/forge-fechar, tests/test_fechar.py, docs/fechamento-integrador.md, changelog.d/impl-fechar-c-c3.md). Conferido contra o caminho real: o passo 1 usa `sha_conferido` (`bin/forge-fechar:604`, `:621`), os passos 4 e 5 usam `pr_n` (`:684`, `:730`) e o passo 6 usa a ref (`:767`); o texto novo do `--dry-run` bate com isso.

**Item entregue:** E3 do pedido, FECHAR-B-REC-REVIEW item 2 (C3 do modelo de ameaças `docs/security/ameacas/fechar-c.md`, SEC-FECHARC-3).

**M14 (agents/tech-lead.md:19):** um comportamento (o texto do `--dry-run`); 27 linhas de código e teste, dentro do teto; nada em `hooks/` nem em `PROTEGIDOS`. Cumpre.

## Gatilhos
`R-SEGURANCA`: controles do Forge (`bin/forge-fechar`).

## Achados
- A1 (recomendado) bin/forge-fechar:559 · C3-3 do modelo: as linhas do --dry-run com cara de comando (passos 2, 3, 6 e 7) ainda imprimem a ref sem printf '%q'; uma ref com $, aceita pelo check-ref-format, sai sem escape para quem a copiar. Dono: tech-lead.

## Detalhe dos achados
- C3-1: o sha vem só de `git rev-parse --verify -q refs/heads/<ref>^{commit}` (`:557`), leitura local; o número do PR sai como marcador; nenhuma chamada a `gh`, `forge-check` ou ao servidor (o teste novo afirma zero chamadas).
- C3-2: sem branch local, sai o marcador "sha não lido" e o código 0; o aviso "não consegui conferir" continua.
- Casos AB-C3-1 e AB-C3-2 cobertos em `tests/test_fechar.py:387` e `:400`. Rodado aqui: `tests.test_fechar`, 89 testes OK (1 pulado).
- Detalhe do A1: severidade baixa. Caminho: quem cola uma linha do `--dry-run` de uma ref como `melhoria/a$b` vê o shell expandir `$b`; o `--dry-run` não executa nada e a ref já passou pelo `git check-ref-format`. Correção mínima: `$(printf '%q' "$ref")` nas linhas `:559`, `:561`, `:564` e `:566` (esforço P). Já era recomendação não bloqueante no modelo de ameaças; não devolve.

## Riscos aceitos e ferramentas
Nenhum risco aceito. Ferramentas: leitura do diff e do script, testes da suíte. Faltaram no PATH: `shellcheck`, `gitleaks` e `semgrep` (lacuna).
